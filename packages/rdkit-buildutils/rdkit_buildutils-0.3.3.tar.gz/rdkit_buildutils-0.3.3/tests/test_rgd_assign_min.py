from rdkit import Chem
from rdkit_buildutils.rgroup_core import to_core
from rdkit_buildutils.rgd_assign import (
    best_rgd_row_with_scoring,
    build_code_map,
    normalize_rgroup_smiles_anchor,
    site_atom_symbol,
    map_with_site,
)

def test_assign_rgroups_minimal_with_primitives():
    monomer_scaffold = "[R1]NCC(=O)[R2]"
    target = Chem.MolFromSmiles("CC(C)(C)OC(=O)NCC(=O)OC")

    rgroups = [
        {"code": "BOC", "smiles": "-C(=O)OC(C)(C)C"},
        {"code": "OME", "smiles": "-OC"},
    ]
    import pandas as pd
    code_map = build_code_map(pd.DataFrame(rgroups))

    core_entries = []
    core_mol = to_core(monomer_scaffold)
    assert core_mol is not None
    core_entries.append((monomer_scaffold, core_mol, "as-is"))

    row, core_used, origin, score = best_rgd_row_with_scoring(core_entries, target, code_map)

    assert row is not None
    assert core_used is not None
    assert score is not None

    core_mol_used = to_core(core_used)
    found_codes = set()
    for i in (1, 2, 3, 4, 5):
        label = f"R{i}"
        frag = row.get(label)
        if frag is None:
            continue
        frag_smi = normalize_rgroup_smiles_anchor(frag)
        if not frag_smi:
            continue
        site = site_atom_symbol(core_mol_used, label) if core_mol_used is not None else None
        code = map_with_site(frag_smi, site, code_map)
        if code:
            found_codes.add(code)

    assert ("BOC" in found_codes) or ("OME" in found_codes)
