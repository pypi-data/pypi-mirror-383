from rdkit import Chem
from rdkit_buildutils.query_variants import make_scaffold_variants

def test_make_scaffold_variants_basic():
    q = Chem.MolFromSmiles("[*:1]NCC(=O)[*:2]")
    vs = make_scaffold_variants(q, peptidic_query=None, include_dropR=True)
    tags = [t for t,_ in vs]
    for tag in ("strict", "nostereo", "dropR"):
        assert tag in tags
