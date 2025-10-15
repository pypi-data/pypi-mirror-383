from __future__ import annotations
from typing import Optional
import pandas as pd
from .scaffold_normalize import normalize_scaffold_chiral

def find_duplicate_monomers_chiral_df(
    df: pd.DataFrame,
    scaffold_col: str = "scaffold_smiles",
    id_col: str = "id",
    symbol_col: str = "symbol",
    author_col: Optional[str] = "author",
    relabel_R: bool = True,
) -> pd.DataFrame:
    """Find duplicates preserving stereochemistry (D/L distinct)."""
    df = df.copy()
    df["scaffold_canonical_iso"] = df[scaffold_col].apply(
        lambda s: normalize_scaffold_chiral(s, relabel_R=relabel_R)
    )
    dup = (
        df.groupby("scaffold_canonical_iso")
          .filter(lambda g: (len(g) > 1) and (g[symbol_col].nunique() > 1))
          .sort_values(["scaffold_canonical_iso", symbol_col], kind="stable")
    )
    cols = [id_col, symbol_col, scaffold_col, "scaffold_canonical_iso"]
    if author_col and (author_col in df.columns):
        cols.append(author_col)
    return dup[cols]
