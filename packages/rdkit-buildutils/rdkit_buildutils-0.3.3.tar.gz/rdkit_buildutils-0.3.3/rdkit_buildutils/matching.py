from __future__ import annotations
from typing import List, Dict, Iterable, Tuple
from rdkit import Chem
from .datatypes import MonomerScaffold, MatchRecord
from .query_variants import make_scaffold_variants
from .standardize import standardize_for_matching

_SCORE = {
    "strict":100,"nostereo":95,"kekule":90,
    "dropR":85,"nostereo_dropR":80,
    "peptidic":120,"peptidic_nostereo":115,"peptidic_dropR":110,
}
_CHIRAL = {
    "strict":True,"nostereo":False,"kekule":True,
    "dropR":True,"nostereo_dropR":False,
    "peptidic":True,"peptidic_nostereo":False,"peptidic_dropR":True,
}

def _to_smiles(m: Chem.Mol) -> str:
    return Chem.MolToSmiles(m, isomericSmiles=True)

def prepare_targets(targets: Iterable[Tuple[str, Chem.Mol]], standardize: bool = True) -> Dict[str, Tuple[Chem.Mol,str]]:
    out={}
    for tid, m in targets:
        if m is None: continue
        try:
            mm=standardize_for_matching(m) if standardize else m
            out[str(tid)]=(mm, _to_smiles(mm))
        except Exception:
            continue
    return out

def find_monomer_matches(scaffolds: List[MonomerScaffold],
                         prepared_targets: Dict[str, Tuple[Chem.Mol,str]],
                         peptidic_queries: Dict[str, Chem.Mol] | None = None,
                         keep_all_variants: bool = False) -> List[MatchRecord]:
    rows: List[MatchRecord]=[]
    for sc in scaffolds:
        base_q=sc.query_mol
        pep_q=None
        if peptidic_queries is not None:
            pep_q=peptidic_queries.get(sc.symbol or "", None)
        variants=make_scaffold_variants(base_q, peptidic_query=pep_q, include_dropR=True)
        variants.sort(key=lambda t: -_SCORE.get(t[0],0))
        for tid,(tmol, smi) in prepared_targets.items():
            best=None; best_tag=None; best_score=-1; best_count=0
            for tag,qmol in variants:
                try:
                    hits=tmol.GetSubstructMatches(qmol, useChirality=_CHIRAL.get(tag,True), uniquify=True)
                except Exception:
                    hits=()
                if hits:
                    if keep_all_variants:
                        rows.append(MatchRecord(tid, sc.symbol, tag, _SCORE.get(tag,0), len(hits), smi))
                    s=_SCORE.get(tag,0)
                    if s>best_score:
                        best_score=s; best_tag=tag; best_count=len(hits); best=True
                    if not keep_all_variants:
                        break
            if (not keep_all_variants) and best:
                rows.append(MatchRecord(tid, sc.symbol, best_tag or "strict", best_score, best_count, smi))
    return rows
