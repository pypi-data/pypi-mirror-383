from __future__ import annotations
from typing import Optional, Tuple, Dict
from rdkit import Chem

def extract_rgroup_smiles(target: Chem.Mol, query: Chem.Mol, match: Tuple[int, ...], r_index: int) -> Optional[str]:
    q2t=dict(enumerate(match))
    q_dummy=None
    for a in query.GetAtoms():
        if a.GetAtomicNum()==0 and a.GetAtomMapNum()==r_index:
            q_dummy=a.GetIdx(); break
    if q_dummy is None: return None
    t_anchor=q2t[q_dummy]
    qnei=[n.GetIdx() for n in query.GetAtomWithIdx(q_dummy).GetNeighbors()]
    if len(qnei)!=1: return None
    t_core=q2t[qnei[0]]
    rw=Chem.RWMol(target)
    if rw.GetBondBetweenAtoms(t_anchor, t_core) is None: return None
    rw.RemoveBond(t_anchor, t_core); cut=rw.GetMol()
    frags=Chem.GetMolFrags(cut, asMols=False, sanitizeFrags=False)
    frag_idx=next((i for i,atoms in enumerate(frags) if t_anchor in atoms), None)
    if frag_idx is None: return None
    atom_ids=list(frags[frag_idx]); amap: Dict[int,int]={}
    sub=Chem.PathToSubmol(cut, atom_ids, atomMap=amap)
    sub_idx=amap.get(t_anchor);  # type: ignore
    if sub_idx is None: return None
    rw_sub=Chem.RWMol(sub)
    anchor=rw_sub.GetAtomWithIdx(sub_idx)
    neigh=[n.GetIdx() for n in anchor.GetNeighbors()]
    d=rw_sub.AddAtom(Chem.Atom(0))
    for ni in neigh:
        b=sub.GetBondBetweenAtoms(sub_idx, ni); bt=b.GetBondType() if b else Chem.BondType.SINGLE
        rw_sub.AddBond(d, ni, bt)
    rw_sub.RemoveAtom(sub_idx)
    out=rw_sub.GetMol(); Chem.SanitizeMol(out)
    return Chem.MolToSmiles(out, canonical=True, isomericSmiles=True)
