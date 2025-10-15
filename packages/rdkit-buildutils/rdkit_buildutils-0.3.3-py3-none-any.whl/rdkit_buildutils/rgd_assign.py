# rdkit_buildutils/rgd_assign.py
# =============================================================================
# R-group decomposition helpers + scoring + code mapping
# =============================================================================
from __future__ import annotations

from typing import Dict, Optional, List, Tuple
import re

import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdRGroupDecomposition as RGD
from rdkit.Chem import rdMolDescriptors as Descr

__all__ = [
    "best_rgd_row_with_scoring",
    "normalize_rgroup_smiles_anchor",
    "site_atom_symbol",
    "map_with_site",
    "to_anchored_smiles",
    "build_code_map",
]

# -----------------------------------------------------------------------------
# Fragment normalization / mapping helpers
# -----------------------------------------------------------------------------

def normalize_rgroup_smiles_anchor(rmol: Chem.Mol | None) -> Optional[str]:
    """
    Normalizza lo SMILES di un frammento R-group per il lookup:
      - rimuove AtomMapNum dai dummy ([*:n] -> [*])
      - radica lo SMILES sul dummy
      - ritorna SMILES canonico
    """
    if rmol is None:
        return None
    rw = Chem.RWMol(rmol)
    for a in rw.GetAtoms():
        if a.GetAtomicNum() == 0:
            a.SetAtomMapNum(0)  # [*:n] -> [*]
    m = rw.GetMol()
    dummy_idx = next((a.GetIdx() for a in m.GetAtoms() if a.GetAtomicNum() == 0), None)
    smi = (Chem.MolToSmiles(m, rootedAtAtom=dummy_idx, canonical=True)
           if dummy_idx is not None else Chem.MolToSmiles(m, canonical=True))
    # normalizza eventuali [*:<n>] in [*]
    smi = re.sub(r"\[\*\:\d+\]", "[*]", smi)
    m2 = Chem.MolFromSmiles(smi)
    return Chem.MolToSmiles(m2, canonical=True) if m2 else None


def to_anchored_smiles(raw: str | None) -> Optional[str]:
    """
    Converte vocabolari tipo '-C', '-OC' in SMILES ancorati '*C', '*OC'.
    Ritorna SMILES canonico (radicato su '*') o None se non parsabile.
    """
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    s = s[1:] if s.startswith("-") else s
    if not s:
        return None
    m = Chem.MolFromSmiles("*" + s)
    return Chem.MolToSmiles(m, canonical=True) if m else None


def site_atom_symbol(core_mol: Chem.Mol | None, r_label: str) -> Optional[str]:
    """
    Simbolo dell’atomo del core connesso al dummy [*:n] che rappresenta Rn (es. 'O','S','N','C').
    """
    if core_mol is None:
        return None
    try:
        n = int(r_label[1:])
    except Exception:
        return None
    for a in core_mol.GetAtoms():
        if a.GetAtomicNum() == 0 and a.GetAtomMapNum() == n:
            nbrs = list(a.GetNeighbors())
            return nbrs[0].GetSymbol() if nbrs else None
    return None


def map_with_site(frag_smi: str | None, site_symbol: str | None, code_map: Dict[str, str]) -> Optional[str]:
    """
    Heuristica di mapping:
      1) match diretto su code_map
      2) se il sito è O/S e il frammento inizia con '*', prova anche '*O...' / '*S...'.
    """
    if not frag_smi:
        return None
    if frag_smi in code_map:
        return code_map[frag_smi]
    if site_symbol in ("O", "S") and frag_smi.startswith("*"):
        tail = frag_smi[1:]
        cand = f"*{site_symbol}{tail}"
        if cand in code_map:
            return code_map[cand]
    return None


# -----------------------------------------------------------------------------
# Mass helpers + scoring
# -----------------------------------------------------------------------------

def _mol_mw(m: Optional[Chem.Mol]) -> float:
    return float(Descr.CalcExactMolWt(m)) if m is not None else 0.0


def _row_mass_gap(row_dict: Dict[str, Chem.Mol], mol: Chem.Mol) -> float:
    """
    gap = |MW(mol) - (MW(Core) + Σ MW(Ri))|  (massa monoisotopica)
    """
    mw_mol = _mol_mw(mol)
    mw_core = _mol_mw(row_dict.get("Core"))
    mw_R = sum(_mol_mw(v) for k, v in row_dict.items() if k.startswith("R") and v is not None)
    return abs(mw_mol - (mw_core + mw_R))


def _score_row(
    row_dict: Dict[str, Chem.Mol],
    code_map: Dict[str, str],
    core_mol: Chem.Mol | None,
) -> Tuple[int, int, float, int]:
    """
    Ritorna (known_codes, total_R, mass_gap_placeholder, unknowns).
    La mass_gap reale è calcolata separatamente.
    """
    known = total = unknowns = 0
    for k, frag in row_dict.items():
        if not k.startswith("R"):
            continue
        total += 1
        if frag is None:
            continue
        frag_smi = normalize_rgroup_smiles_anchor(frag)
        site_sym = site_atom_symbol(core_mol, k) if core_mol is not None else None
        code = map_with_site(frag_smi, site_sym, code_map) if frag_smi else None
        if code is not None:
            known += 1
        else:
            unknowns += 1
    return (known, total, 0.0, unknowns)


# -----------------------------------------------------------------------------
# Code map from DB helpers
# -----------------------------------------------------------------------------

def build_code_map(
    df_rgroups: pd.DataFrame,
    *,
    code_col: str = "code",
    smiles_col: str = "smiles",
    mode: str = "robust",
) -> Dict[str, str]:
    """
    Converte la tabella RGroup in una mappa {SMILES_ancorato -> codice}.
    """
    cmap: Dict[str, str] = {}
    if df_rgroups is None or (hasattr(df_rgroups, 'empty') and df_rgroups.empty):
        return cmap
    if mode not in {"robust", "strict"}:
        mode = "robust"
    # Support also list-of-dicts for tests
    it = df_rgroups
    if hasattr(df_rgroups, 'itertuples'):
        it = df_rgroups.itertuples(index=False)
    for row in it:
        code = getattr(row, code_col, None) if hasattr(row, code_col) else row.get(code_col)
        smi  = getattr(row, smiles_col, None) if hasattr(row, smiles_col) else row.get(smiles_col)
        if not code or not isinstance(smi, str):
            continue
        normalized: Optional[str] = None
        if mode == "strict":
            if smi.startswith("-"):
                normalized = to_anchored_smiles(smi)
        else:
            if smi.startswith("-"):
                normalized = to_anchored_smiles(smi)
            if normalized is None:
                try:
                    m = Chem.MolFromSmiles(smi)
                    normalized = normalize_rgroup_smiles_anchor(m) if m is not None else None
                except Exception:
                    normalized = None
        if normalized:
            cmap[normalized] = str(code)
    return cmap


def best_rgd_row_with_scoring(
    core_entries: List[Tuple[str, Chem.Mol, str]],
    mol: Chem.Mol,
    code_map: Dict[str, str],
) -> Tuple[
    Optional[Dict[str, Chem.Mol]],
    Optional[str],
    Optional[str],
    Optional[Tuple[int, int, float, int]],
]:
    params = RGD.RGroupDecompositionParameters()
    params.removeHydrogensPostMatch = True
    params.alignment = RGD.RGroupCoreAlignment.MCS
    if hasattr(params, "onlyMatchAtRGroups"):
        params.onlyMatchAtRGroups = True
    best_row = None
    best_core_smi = None
    best_origin = None
    best_score = (-1, -1, 1e9, 1e9)
    for core_smi, core, origin in core_entries:
        if core is None:
            continue
        try:
            rgd = RGD.RGroupDecomposition(core, params)
            rgd.Add(mol)
            rgd.Process()
        except Exception:
            continue
        rows = rgd.GetRGroupsAsRows()
        if not rows:
            continue
        row = rows[0]
        known, total, _, unknowns = _score_row(row, code_map, core)
        mgap = _row_mass_gap(row, mol)
        score = (known, total, mgap, unknowns)
        bk, bt, bmg, bu = best_score
        replace = False
        if (known, total) > (bk, bt):
            replace = True
        elif (known, total) == (bk, bt):
            if mgap < bmg - 1e-6:
                replace = True
            elif abs(mgap - bmg) <= 1e-6 and unknowns < bu:
                replace = True
        if replace:
            best_row, best_core_smi, best_origin, best_score = row, core_smi, origin, score
    return best_row, best_core_smi, best_origin, best_score


from rdkit import Chem
_PATT_ALPHA_N = Chem.MolFromSmarts("[$([N;!a;H0,H1,H2]);!$([N+])]-[CH0,CH1,CH2]-[C](=O)")

def to_peptidic_scaffold(asis_scaffold: str) -> str:
    s = (asis_scaffold
         .replace('[C@H]', 'C').replace('[C@@H]', 'C')
         .replace('[C@]', 'C').replace('[C@@]', 'C'))
    s = re.sub(r'\[R(\d+)\]', r'[*:\1]', s)
    m = Chem.MolFromSmiles(s)
    if m is None:
        return asis_scaffold
    rw = Chem.RWMol(m)
    rw.UpdatePropertyCache(strict=False)
    base = Chem.Mol(rw)
    base.UpdatePropertyCache(strict=False)
    def _is_alpha_backbone_N(n_idx: int) -> bool:
        for match in base.GetSubstructMatches(_PATT_ALPHA_N, useChirality=False):
            if n_idx == match[0]:
                return True
        return False
    dummy_idxs = [(a.GetIdx(), a.GetAtomMapNum()) for a in rw.GetAtoms() if a.GetAtomicNum() == 0]
    for d_idx, _ in dummy_idxs:
        for n_atom in list(rw.GetAtomWithIdx(d_idx).GetNeighbors()):
            if n_atom.GetAtomicNum() != 7:
                continue
            n_idx = n_atom.GetIdx()
            if not _is_alpha_backbone_N(n_idx):
                continue
            already = False
            for nn in n_atom.GetNeighbors():
                if nn.GetAtomicNum() != 6:
                    continue
                c_idx = nn.GetIdx()
                has_c_equals_o = any(
                    b.GetBondType() == Chem.BondType.DOUBLE and
                    rw.GetAtomWithIdx(b.GetOtherAtomIdx(c_idx)).GetAtomicNum() == 8
                    for b in rw.GetAtomWithIdx(c_idx).GetBonds()
                )
                if has_c_equals_o and rw.GetBondBetweenAtoms(c_idx, d_idx):
                    already = True; break
            if already:
                continue
            c_idx_new = rw.AddAtom(Chem.Atom(6)); o_idx_new = rw.AddAtom(Chem.Atom(8))
            if rw.GetBondBetweenAtoms(d_idx, n_idx): rw.RemoveBond(d_idx, n_idx)
            rw.AddBond(d_idx, c_idx_new, Chem.BondType.SINGLE)
            rw.AddBond(c_idx_new, o_idx_new, Chem.BondType.DOUBLE)
            rw.AddBond(c_idx_new, n_idx, Chem.BondType.SINGLE)
    for d_idx, _ in list(dummy_idxs):
        for c_atom in list(rw.GetAtomWithIdx(d_idx).GetNeighbors()):
            if c_atom.GetAtomicNum() != 6:
                continue
            c_idx = c_atom.GetIdx()
            is_carbonyl = any(
                b.GetBondType() == Chem.BondType.DOUBLE and
                rw.GetAtomWithIdx(b.GetOtherAtomIdx(c_idx)).GetAtomicNum() == 8
                for b in rw.GetAtomWithIdx(c_idx).GetBonds()
            )
            if not is_carbonyl:
                continue
            is_amide = any(nb.GetAtomicNum() == 7 for nb in rw.GetAtomWithIdx(c_idx).GetNeighbors())
            if is_amide:
                continue
            if not rw.GetBondBetweenAtoms(c_idx, d_idx):
                continue
            o_idx_new = rw.AddAtom(Chem.Atom(8))
            rw.RemoveBond(c_idx, d_idx)
            rw.AddBond(c_idx, o_idx_new, Chem.BondType.SINGLE)
            rw.AddBond(o_idx_new, d_idx, Chem.BondType.SINGLE)
    m_out = rw.GetMol()
    m_out.UpdatePropertyCache(strict=False)
    Chem.SanitizeMol(m_out)
    smi_maps = Chem.MolToSmiles(m_out, canonical=True)
    return re.sub(r'\[\*\:(\d+)\]', r'[R\1]', smi_maps)
