from rdkit import Chem
from rdkit_buildutils.core import build_molecule_final

def test_build_molecule_final_simple():
    base = "[*:1]NCC(=O)[*:2]"
    mol = build_molecule_final(base, r1="C", r2="OC")
    assert mol is not None
    pat = Chem.MolFromSmarts("N-C-C(=O)-O")
    assert mol.HasSubstructMatch(pat)
