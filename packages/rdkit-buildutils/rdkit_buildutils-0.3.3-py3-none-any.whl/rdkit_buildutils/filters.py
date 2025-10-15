from __future__ import annotations
from typing import Iterable, Tuple
from rdkit import Chem

_AA_BACKBONE = Chem.MolFromSmarts("[N;!a]-[CH0,CH1,CH2]-C(=O)")

def is_aminoacid_like_scaffold(scaffold_with_R: str,
                               peptidic_variant: str | None,
                               r_to_atommap) -> bool:
    if not scaffold_with_R: return False
    try:
        asis=Chem.MolFromSmiles(r_to_atommap(scaffold_with_R))
        if asis and asis.HasSubstructMatch(_AA_BACKBONE): return True
    except Exception: pass
    if peptidic_variant:
        try:
            pep=Chem.MolFromSmiles(r_to_atommap(peptidic_variant))
            if pep and pep.HasSubstructMatch(_AA_BACKBONE): return True
        except Exception: pass
    return False

_AA_CORE_QUERY = Chem.MolFromSmarts("[NX2,NX3]-[CX4H0,H1,H2]-[CX3](=O)-[O,S,N]")

def keep_targets_with_single_aa_core(targets: Iterable[Tuple[str, Chem.Mol]]):
    for tid, m in targets:
        try:
            matches=m.GetSubstructMatches(_AA_CORE_QUERY, useChirality=False, uniquify=True)
            alpha=set(mt[1] for mt in matches)
            if len(alpha)==1:
                yield (tid, m)
        except Exception:
            continue
