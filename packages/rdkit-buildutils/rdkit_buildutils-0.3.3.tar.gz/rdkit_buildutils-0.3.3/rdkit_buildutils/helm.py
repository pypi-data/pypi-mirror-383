from __future__ import annotations
from rdkit import Chem
from .core import convert_r_to_atom_map

def helm_to_query_mol(helm_smiles: str) -> Chem.Mol | None:
    if not helm_smiles: return None
    return Chem.MolFromSmiles(convert_r_to_atom_map(helm_smiles))
