from __future__ import annotations
from typing import Dict, List, Callable, Optional
from pathlib import Path

class ALTCoreConfigError(Exception):
    """Errori di configurazione del file ALT_CORES YAML."""

def load_alt_cores_yaml(path: str | Path) -> dict[str, list[str]]:
    try:
        import yaml
    except Exception as e:
        raise RuntimeError("Per usare load_alt_cores_yaml è richiesto 'pyyaml'.") from e
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"ALT_CORES YAML non trovato: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ALTCoreConfigError("Root YAML deve essere un mapping: {symbol: [smiles,...]}")
    out: Dict[str, List[str]] = {}
    for sym, lst in data.items():
        if not isinstance(sym, str):
            raise ALTCoreConfigError(f"Chiave non-stringa nel YAML: {sym!r}")
        if lst is None:
            out[sym] = []
            continue
        if isinstance(lst, str):
            lst = [lst]
        if not isinstance(lst, list) or not all(isinstance(x, str) for x in lst):
            raise ALTCoreConfigError(f"Valore per {sym!r} deve essere stringa o lista di stringhe.")
        seen, clean = set(), []
        for s in lst:
            s = s.strip()
            if not s or s in seen:
                continue
            seen.add(s); clean.append(s)
        out[sym] = clean
    return out

def validate_alt_cores(alt: dict[str, list[str]], *, check_rdkit: bool = True) -> list[str]:
    errors: List[str] = []
    if not check_rdkit:
        return errors
    try:
        from rdkit import Chem  # type: ignore
        from ..core import convert_r_to_atom_map
    except Exception:
        return errors
    for sym, lst in alt.items():
        for s in lst:
            try:
                s_conv = convert_r_to_atom_map(s)
                m = Chem.MolFromSmiles(s_conv) if s_conv else None
            except Exception:
                m = None
            if m is None:
                errors.append(f"{sym}: SMILES non parsabile (dopo [Rk]->[*:k]): {s}")
    return errors

def merge_alt_cores(base: Optional[dict[str, list[str]]], extra: Optional[dict[str, list[str]]], mode: str = "override") -> dict[str, list[str]]:
    base = {k: list(v) for k, v in (base or {}).items()}
    extra = extra or {}
    if mode not in {"override", "extend", "append", "prepend"}:
        raise ValueError("merge mode deve essere 'override', 'extend', 'append' o 'prepend'")
    if mode == "override":
        out = dict(base)
        out.update({k: list(v) for k, v in extra.items()})
        return out
    def _merge(a: list[str], b: list[str]) -> list[str]:
        seen, res = set(), []
        for s in a:
            if s not in seen:
                res.append(s); seen.add(s)
        for s in b:
            if s not in seen:
                res.append(s); seen.add(s)
        return res
    out: dict[str, list[str]] = {}
    keys = set(base) | set(extra)
    if mode in {"extend", "append"}:
        for k in keys:
            out[k] = _merge(base.get(k, []), extra.get(k, []))
    else:
        for k in keys:
            out[k] = _merge(extra.get(k, []), base.get(k, []))
    return out

def make_alt_core_provider_from_yaml_simple(path: str | Path) -> Callable[[str], list[str]]:
    cfg = load_alt_cores_yaml(path)
    def provider(symbol: str) -> list[str]:
        return list(cfg.get(symbol, []))
    return provider

def get_alt_core_provider(alt: dict[str, list[str]], *, merge_mode: str = "override") -> Callable[[str, list[str]], list[str]]:
    allowed = {"override", "append", "prepend"}
    if merge_mode not in allowed:
        raise ValueError(f"merge_mode must be one of {allowed}")
    def _provider(symbol: str, current: list[str]) -> list[str]:
        alt_list = alt.get(symbol, [])
        if not alt_list:
            return current
        if not current:
            return list(alt_list)
        if merge_mode == "override":
            return list(alt_list)
        elif merge_mode == "append":
            return current + [s for s in alt_list if s not in set(current)]
        else:
            return [s for s in alt_list if s not in set(current)] + current
    return _provider
