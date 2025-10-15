# rdkit_buildutils/__init__.py — OCX31 (0.3.3)
__all__ = [
    # core (placeholder -> atom map, build)
    "convert_r_to_atom_map", "build_molecule_final",
    # standardize
    "standardize_for_matching",
    # matching / query variants
    "prepare_targets", "find_monomer_matches", "make_scaffold_variants",
    # rgroup core
    "to_core",
    # rgd primitives (nuove API ufficiali)
    "best_rgd_row_with_scoring", "build_code_map",
    "normalize_rgroup_smiles_anchor", "site_atom_symbol",
    "map_with_site", "to_anchored_smiles", "to_peptidic_scaffold",
]

__version__ = "0.3.3"

# re-exports
from .core import convert_r_to_atom_map, build_molecule_final
from .standardize import standardize_for_matching
from .matching import prepare_targets, find_monomer_matches
from .query_variants import make_scaffold_variants
from .rgroup_core import to_core
from .rgd_assign import (
    best_rgd_row_with_scoring,
    build_code_map,
    normalize_rgroup_smiles_anchor,
    site_atom_symbol,
    map_with_site,
    to_anchored_smiles,
    to_peptidic_scaffold,
)

# Nota: gli helper ALT cores sono nel sotto-modulo:
#   from rdkit_buildutils.rgroup.altcores import load_alt_cores_yaml, validate_alt_cores, get_alt_core_provider
# e NON vengono importati al top-level per chiarezza dell'API.
