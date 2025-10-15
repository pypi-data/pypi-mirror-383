from __future__ import annotations
from typing import Optional, List, Tuple
from rdkit import Chem
import re

def canonical_ranks(mol: Chem.Mol) -> List[int]:
    """Return canonical atom ranks with robust fallbacks across RDKit builds."""
    if hasattr(Chem, "CanonicalRankAtoms"):
        return list(Chem.CanonicalRankAtoms(mol))
    from rdkit.Chem.rdmolops import CanonicalizeMol
    m2 = Chem.Mol(mol)
    CanonicalizeMol(m2)
    if m2.HasProp("_smilesAtomOutputOrder"):
        order = m2.GetProp("_smilesAtomOutputOrder")
        order_idx = [int(x) for x in order.split(",")] if order else []
        if order_idx:
            inv_rank = [0] * m2.GetNumAtoms()
            for rank_pos, atom_idx in enumerate(order_idx):
                inv_rank[atom_idx] = rank_pos
            return inv_rank
    ranks = [(a.GetSymbol(), a.GetDegree(), a.GetIdx()) for a in mol.GetAtoms()]
    order = sorted(range(len(ranks)), key=lambda i: ranks[i])
    inv_rank = [0]*len(ranks)
    for pos, idx in enumerate(order):
        inv_rank[idx] = pos
    return inv_rank

def r_to_atommap(smiles_r: str) -> Optional[Chem.Mol]:
    """Convert [R1],[R2],... -> RDKit [*:1],[*:2],... and return Mol."""
    if not isinstance(smiles_r, str) or not smiles_r.strip():
        return None
    s = re.sub(r'\[R(\d+)\]', r'[*:\1]', smiles_r)
    return Chem.MolFromSmiles(s)

def relabel_dummies_canonically(mol: Chem.Mol) -> Chem.Mol:
    """Deterministic renumbering of dummy atoms [*:k] -> [*:1..m]."""
    m = Chem.Mol(mol)
    ranks = canonical_ranks(m)
    rw = Chem.RWMol(m)
    dummies: List[Tuple[int,int,int]] = []
    for a in rw.GetAtoms():
        if a.GetAtomicNum() == 0:
            dummies.append((a.GetIdx(), ranks[a.GetIdx()], a.GetDegree()))
    dummies.sort(key=lambda t: (t[1], t[2], t[0]))
    for new_num, (idx, _, _) in enumerate(dummies, start=1):
        rw.GetAtomWithIdx(idx).SetAtomMapNum(new_num)
    return rw.GetMol()

def normalize_scaffold_chiral(smiles_with_R: str, relabel_R: bool = True) -> Optional[str]:
    """Normalize scaffold preserving stereochemistry (D/L distinction)."""
    mol = r_to_atommap(smiles_with_R)
    if mol is None:
        return None
    if relabel_R:
        mol = relabel_dummies_canonically(mol)
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
