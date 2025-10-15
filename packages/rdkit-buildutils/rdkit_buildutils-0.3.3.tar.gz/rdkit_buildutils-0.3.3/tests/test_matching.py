from rdkit import Chem
from rdkit_buildutils.datatypes import MonomerScaffold
from rdkit_buildutils.matching import prepare_targets, find_monomer_matches
from rdkit_buildutils.helm import helm_to_query_mol

def test_prepare_and_match_minimal():
    helm = "[R1]NCC(=O)[R2]"
    q = helm_to_query_mol(helm)
    sc = MonomerScaffold(symbol="X", scaffold_str=helm, query_mol=q, r_labels_present=[1,2])
    t = Chem.MolFromSmiles("CC(C)(C)OC(=O)NCC(=O)OC")
    prepared = prepare_targets([("t1", t)], standardize=True)
    rows = find_monomer_matches([sc], prepared, peptidic_queries=None, keep_all_variants=False)
    assert len(rows) >= 1
    row = rows[0]
    assert row.target_id == "t1"
    assert row.monomer_symbol == "X"
    assert row.variant_score >= 80
