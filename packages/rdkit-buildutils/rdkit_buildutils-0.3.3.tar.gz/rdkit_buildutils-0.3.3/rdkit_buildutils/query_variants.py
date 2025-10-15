from __future__ import annotations
from typing import List, Tuple
from rdkit import Chem

def _remove_stereo(m: Chem.Mol) -> Chem.Mol:
    m2=Chem.Mol(m); Chem.RemoveStereochemistry(m2); return m2

def _kekulize_safe(m: Chem.Mol) -> Chem.Mol | None:
    m2=Chem.Mol(m)
    try: Chem.Kekulize(m2, clearAromaticFlags=True)
    except Exception: return None
    return m2

def _drop_all_dummies(m: Chem.Mol) -> Chem.Mol:
    rw=Chem.RWMol(m)
    for idx in sorted([a.GetIdx() for a in rw.GetAtoms() if a.GetAtomicNum()==0], reverse=True):
        rw.RemoveAtom(idx)
    out=rw.GetMol(); Chem.SanitizeMol(out); return out

def make_scaffold_variants(base_query: Chem.Mol,
                           peptidic_query: Chem.Mol | None = None,
                           include_dropR: bool = True) -> List[Tuple[str, Chem.Mol]]:
    out: List[Tuple[str,Chem.Mol]]=[]
    if base_query is None or base_query.GetNumAtoms()==0: return out
    out.append(("strict", Chem.Mol(base_query)))
    out.append(("nostereo", _remove_stereo(base_query)))
    k=_kekulize_safe(base_query);  k and out.append(("kekule", k))
    if include_dropR:
        out.append(("dropR", _drop_all_dummies(base_query)))
        out.append(("nostereo_dropR", _drop_all_dummies(_remove_stereo(base_query))))
    if peptidic_query is not None:
        out.append(("peptidic", peptidic_query))
        out.append(("peptidic_nostereo", _remove_stereo(peptidic_query)))
        if include_dropR:
            out.append(("peptidic_dropR", _drop_all_dummies(peptidic_query)))
    # dedup
    uniq=[]; seen=set()
    for tag,q in out:
        try: key=(tag, Chem.MolToSmiles(q, canonical=True))
        except Exception: continue
        if key in seen: continue
        uniq.append((tag,q)); seen.add(key)
    return uniq
