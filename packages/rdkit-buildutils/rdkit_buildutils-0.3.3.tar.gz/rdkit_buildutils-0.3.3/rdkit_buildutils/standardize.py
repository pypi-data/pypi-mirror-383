from __future__ import annotations
from rdkit import Chem

def standardize_for_matching(m: Chem.Mol | None) -> Chem.Mol | None:
    """
    Disconnect metals, keep largest organic fragment, normalize, re-ionize, neutralize.
    If input is None, return None.
    """
    if m is None:
        return None
    try:
        from rdkit.Chem.MolStandardize import rdMolStandardize as S
        lfc = S.LargestFragmentChooser(preferOrganic=True)
        md = S.MetalDisconnector()
        norm = S.Normalizer()
        reion = S.Reionizer()
        unch = S.Uncharger()
        m2 = Chem.Mol(m)
        m2 = md.Disconnect(m2)
        m2 = lfc.choose(m2)
        m2 = norm.normalize(m2)
        m2 = reion.reionize(m2)
        m2 = unch.uncharge(m2)
        Chem.SanitizeMol(m2)
        return m2
    except Exception:
        try:
            frags = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
            if frags:
                frags.sort(key=lambda x: x.GetNumAtoms(), reverse=True)
                return frags[0]
        except Exception:
            pass
        return m