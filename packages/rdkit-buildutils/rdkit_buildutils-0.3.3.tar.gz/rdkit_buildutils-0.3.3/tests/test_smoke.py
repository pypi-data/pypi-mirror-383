import rdkit_buildutils as r

def test_smoke_import():
    assert hasattr(r, "__version__")
    assert "build_molecule_final" in r.__all__
    assert "make_scaffold_variants" in r.__all__
    assert "standardize_for_matching" in r.__all__

def test_altcores_import_and_empty_validate():
    from rdkit_buildutils.rgroup.altcores import load_alt_cores_yaml, validate_alt_cores, get_alt_core_provider
    assert validate_alt_cores({}) == []
    assert callable(get_alt_core_provider({}, merge_mode="override"))
