"""
Core utilities for RDKit molecule construction with placeholder substitution.
"""
from rdkit import Chem
import re

def convert_r_to_atom_map(smiles_r: str) -> str:
    """Convert [R1],[R2],... to RDKit [*:1],[*:2],... format."""
    return re.sub(r'\[R(\d+)\]', r'[*:\1]', smiles_r)

def build_molecule_final(base_smiles: str, **substituents) -> Chem.Mol | None:
    """Replace [*:n] placeholders in base_smiles with substituents (r1='CC', r2='O', ...)."""
    mol = Chem.MolFromSmiles(base_smiles)
    if not mol:
        return None
    current = Chem.RWMol(mol)

    def _maps(m):
        return {a.GetAtomMapNum(): a for a in m.GetAtoms() if a.GetAtomMapNum() != 0}

    placeholders = sorted(_maps(current).keys())
    if not placeholders:
        return current.GetMol()

    for num in placeholders:
        key = f"r{num}"
        if key not in substituents:
            return None
        subsmi = substituents[key]
        ph_atom = _maps(current)[num]
        ph_idx = ph_atom.GetIdx()
        nbrs = ph_atom.GetNeighbors()
        if len(nbrs) != 1:
            return None
        nbr_idx = nbrs[0].GetIdx()

        if not subsmi:
            current.RemoveAtom(ph_idx)
        else:
            frag = Chem.MolFromSmiles(subsmi)
            if not frag:
                return None
            combined = Chem.CombineMols(current.GetMol(), frag)
            rw = Chem.RWMol(combined)
            attach_idx = rw.GetNumAtoms() - frag.GetNumAtoms()
            rw.AddBond(nbr_idx, attach_idx, Chem.BondType.SINGLE)
            rw.RemoveAtom(ph_idx)
            current = rw

    out = current.GetMol()
    Chem.SanitizeMol(out)
    for a in out.GetAtoms():
        a.SetAtomMapNum(0)
    return out
