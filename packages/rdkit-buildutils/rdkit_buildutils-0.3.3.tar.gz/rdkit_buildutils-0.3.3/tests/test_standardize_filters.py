from rdkit import Chem
from rdkit_buildutils.standardize import standardize_for_matching

def test_standardize_for_matching_smoke():
    m = Chem.MolFromSmiles("C[NH3+].[Cl-]")
    out = standardize_for_matching(m)
    assert out is not None
    smi = Chem.MolToSmiles(out, isomericSmiles=True)
    assert '.' not in smi or 'Cl' not in smi
