from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from rdkit import Chem
from rdkit.Chem import rdRGroupDecomposition as RGD
from rdkit.Chem import rdMolDescriptors as Descr
import re

def to_core(smiles_with_R: str) -> Optional[Chem.Mol]:
    """Converte uno scaffold con [Rk] in un Mol RDKit con dummy [*:k]."""
    if not isinstance(smiles_with_R, str) or not smiles_with_R.strip():
        return None
    s = (smiles_with_R
         .replace('[C@H]','C').replace('[C@@H]','C')
         .replace('[C@]','C').replace('[C@@]','C'))
    s = re.sub(r'\[R(\d+)\]', r'[*:\1]', s)
    return Chem.MolFromSmiles(s)

def normalize_rgroup_smiles(rmol: Chem.Mol) -> Optional[str]:
    """Rimuove mappe dai dummy e radica lo SMILES sul dummy '*'."""
    if rmol is None:
        return None
    rw = Chem.RWMol(rmol)
    for a in rw.GetAtoms():
        if a.GetAtomicNum() == 0:
            a.SetAtomMapNum(0)
    m = rw.GetMol()
    dummy_idx = next((a.GetIdx() for a in m.GetAtoms() if a.GetAtomicNum()==0), None)
    smi = Chem.MolToSmiles(m, rootedAtAtom=dummy_idx, canonical=True) if dummy_idx is not None else Chem.MolToSmiles(m, canonical=True)
    smi = re.sub(r'\[\*\:(\d+)\]', '[*]', smi)
    m2 = Chem.MolFromSmiles(smi)
    return Chem.MolToSmiles(m2, canonical=True) if m2 else None

def to_peptidic_scaffold(asis_scaffold: str) -> str:
    """Converte uno scaffold 'as-is' in 'peptidic' amide/ester-aware."""
    s = (asis_scaffold
         .replace('[C@H]','C').replace('[C@@H]','C')
         .replace('[C@]','C').replace('[C@@]','C'))
    s = re.sub(r'\[R(\d+)\]', r'[*:\1]', s)
    m = Chem.MolFromSmiles(s)
    if m is None:
        return asis_scaffold
    rw = Chem.RWMol(m)
    rw.UpdatePropertyCache(strict=False)

    def _is_alpha_backbone_N(n_idx: int) -> bool:
        patt = Chem.MolFromSmarts("[$([N;!a;H0,H1,H2]);!$([N+])]-[CH0,CH1,CH2]-[C](=O)")
        for match in rw.GetMol().GetSubstructMatches(patt):
            if n_idx == match[0]:
                return True
        return False

    def _is_amide_carbonyl(c_idx: int) -> bool:
        c = rw.GetAtomWithIdx(c_idx)
        for n in c.GetNeighbors():
            if n.GetAtomicNum() == 7:
                b = rw.GetBondBetweenAtoms(c_idx, n.GetIdx())
                if b and b.GetBondType() == Chem.BondType.SINGLE:
                    if any(b2.GetBondType()==Chem.BondType.DOUBLE and
                           rw.GetAtomWithIdx(b2.GetOtherAtomIdx(c_idx)).GetAtomicNum()==8
                           for b2 in rw.GetAtomWithIdx(c_idx).GetBonds()):
                        return True
        return False

    dummy_idxs = [a.GetIdx() for a in rw.GetAtoms() if a.GetAtomicNum()==0]

    for d_idx in dummy_idxs:
        d_atom = rw.GetAtomWithIdx(d_idx)
        for n_atom in list(d_atom.GetNeighbors()):
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
                    b.GetBondType()==Chem.BondType.DOUBLE and rw.GetAtomWithIdx(b.GetOtherAtomIdx(c_idx)).GetAtomicNum()==8
                    for b in rw.GetAtomWithIdx(c_idx).GetBonds()
                )
                if has_c_equals_o and rw.GetBondBetweenAtoms(c_idx, d_idx):
                    already = True
                    break
            if already:
                continue
            c_idx_new = rw.AddAtom(Chem.Atom(6))
            o_idx_new = rw.AddAtom(Chem.Atom(8))
            if rw.GetBondBetweenAtoms(d_idx, n_idx):
                rw.RemoveBond(d_idx, n_idx)
            rw.AddBond(d_idx, c_idx_new, Chem.BondType.SINGLE)
            rw.AddBond(c_idx_new, o_idx_new, Chem.BondType.DOUBLE)
            rw.AddBond(c_idx_new, n_idx, Chem.BondType.SINGLE)

    for d_idx in list(dummy_idxs):
        d_atom = rw.GetAtomWithIdx(d_idx)
        for c_atom in list(d_atom.GetNeighbors()):
            if c_atom.GetAtomicNum() != 6:
                continue
            c_idx = c_atom.GetIdx()
            is_carbonyl = any(
                b.GetBondType()==Chem.BondType.DOUBLE and rw.GetAtomWithIdx(b.GetOtherAtomIdx(c_idx)).GetAtomicNum()==8
                for b in rw.GetAtomWithIdx(c_idx).GetBonds()
            )
            if not is_carbonyl or _is_amide_carbonyl(c_idx):
                continue
            if not rw.GetBondBetweenAtoms(c_idx, d_idx):
                continue
            o_idx_new = rw.AddAtom(Chem.Atom(8))
            rw.RemoveBond(c_idx, d_idx)
            rw.AddBond(c_idx, o_idx_new, Chem.BondType.SINGLE)
            rw.AddBond(o_idx_new, d_idx, Chem.BondType.SINGLE)

    m_out = rw.GetMol()
    Chem.SanitizeMol(m_out)
    smi_maps = Chem.MolToSmiles(m_out, canonical=True)
    return re.sub(r'\[\*\:(\d+)\]', r'[R\1]', smi_maps)

def _site_atom_symbol(core_mol: Chem.Mol, r_label: str) -> Optional[str]:
    try:
        n = int(r_label[1:])
    except Exception:
        return None
    for a in core_mol.GetAtoms():
        if a.GetAtomicNum()==0 and a.GetAtomMapNum()==n:
            nbrs = list(a.GetNeighbors())
            if nbrs:
                return nbrs[0].GetSymbol()
    return None

def anchored_smiles(raw: str) -> Optional[str]:
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.startswith('-'):
        s = s[1:]
    m = Chem.MolFromSmiles('*'+s)
    return Chem.MolToSmiles(m, canonical=True) if m else None

def build_code_map(rgroups: Dict[str, str]) -> Dict[str, str]:
    cmap = {}
    for code, raw in rgroups.items():
        smi = anchored_smiles(raw)
        if smi:
            cmap[smi] = code
    return cmap

def _map_with_site(frag_smi: str, site_symbol: Optional[str], code_map: Dict[str,str]) -> Optional[str]:
    if frag_smi in code_map:
        return code_map[frag_smi]
    if site_symbol in ('O','S') and frag_smi and frag_smi.startswith('*'):
        tail = frag_smi[1:]
        candidate = f"*{site_symbol}{tail}"
        if candidate in code_map:
            return code_map[candidate]
    return None

def _mw(m: Optional[Chem.Mol]) -> float:
    return float(Descr.CalcExactMolWt(m)) if m is not None else 0.0

def _row_mass_gap(row: Dict[str, Chem.Mol], mol: Chem.Mol) -> float:
    mw_mol = _mw(mol)
    mw_core = _mw(row.get('Core'))
    mw_R = sum(_mw(v) for k, v in row.items() if k.startswith('R') and v is not None)
    return abs(mw_mol - (mw_core + mw_R))

def _score_row(row: Dict[str, Chem.Mol], code_map: Dict[str,str], core_mol: Chem.Mol) -> tuple[int,int,float,int]:
    known = 0; total = 0; unknowns = 0
    for k, frag in row.items():
        if not k.startswith('R'):
            continue
        total += 1
        if frag is None:
            continue
        frag_smi = normalize_rgroup_smiles(frag)
        site_sym = _site_atom_symbol(core_mol, k) if core_mol else None
        code = _map_with_site(frag_smi, site_sym, code_map) if frag_smi else None
        if code is not None:
            known += 1
        else:
            unknowns += 1
    return (known, total, 0.0, unknowns)

def decompose_with_cores(
    mol: Chem.Mol,
    core_entries: List[tuple[str, Chem.Mol, str]],
    code_map: Dict[str,str],
    mass_gap_tol: float = 0.5
):
    params = RGD.RGroupDecompositionParameters()
    params.removeHydrogensPostMatch = True
    params.alignment = RGD.RGroupCoreAlignment.MCS

    best = (None, None, None, (-1,-1,1e9,1e9))
    for core_smi, core, origin in core_entries:
        if core is None:
            continue
        rgd = RGD.RGroupDecomposition(core, params)
        rgd.Add(mol); rgd.Process()
        rows = rgd.GetRGroupsAsRows()
        if not rows:
            continue
        row = rows[0]
        known, total, _, unknowns = _score_row(row, code_map, core)
        mgap = _row_mass_gap(row, mol)
        if mgap > mass_gap_tol:
            continue
        score = (known, total, mgap, unknowns)

        bk, bt, bmg, bu = best[3]
        replace = False
        if (known, total) > (bk, bt):
            replace = True
        elif (known, total) == (bk, bt):
            if mgap < bmg - 1e-6:
                replace = True
            elif abs(mgap - bmg) <= 1e-6 and unknowns < bu:
                replace = True
        if replace:
            best = (row, core_smi, origin, score)
    return best

def decompose_for_monomer(
    mol: Chem.Mol,
    monomer_name: str,
    monomers_as_is: Dict[str, str],
    code_map: Dict[str, str],
    alt_cores: Optional[Dict[str, List[str]]] = None,
    use_peptidic_variant: bool = True,
    mass_gap_tol: float = 0.5
):
    asis = monomers_as_is.get(monomer_name)
    if not asis:
        return {"row": None, "core_used": None, "core_origin": None, "score": None}

    core_entries: List[tuple[str, Chem.Mol, str]] = [(asis, to_core(asis), 'as-is')]
    if use_peptidic_variant:
        pep = to_peptidic_scaffold(asis)
        core_entries.append((pep, to_core(pep), 'peptidic'))

    if alt_cores and monomer_name in alt_cores:
        for i, alt in enumerate(alt_cores[monomer_name], start=1):
            core_entries.append((alt, to_core(alt), f'alt#{i}'))

    row, core_smi, origin, score = decompose_with_cores(
        mol=mol, core_entries=core_entries, code_map=code_map, mass_gap_tol=mass_gap_tol
    )
    return {"row": row, "core_used": core_smi, "core_origin": origin, "score": score}
