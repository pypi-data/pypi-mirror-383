from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from rdkit import Chem

@dataclass(frozen=True)
class MonomerScaffold:
    symbol: Optional[str]
    scaffold_str: str
    query_mol: Chem.Mol
    r_labels_present: List[int]

@dataclass(frozen=True)
class MatchRecord:
    target_id: str
    monomer_symbol: Optional[str]
    variant_tag: str
    variant_score: int
    match_count: int
    structure_smiles: str

@dataclass(frozen=True)
class RAssignment:
    target_id: str
    monomer_symbol: Optional[str]
    r_codes: Dict[str, Optional[str]]
    core_used: Optional[str]
    score: Optional[Tuple[int,int,float,int]]
