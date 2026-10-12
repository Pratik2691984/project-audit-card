"""
core/linguistics/prosody/ganas.py
Piṅgala gaṇa decomposition and reconstruction.
"""
from __future__ import annotations
import re
from typing import List, Tuple, Dict
from core.linguistics.prosody.meters import Weight

L = Weight.L
G = Weight.G

GANA_MAP: Dict[Tuple[Weight, Weight, Weight], str] = {
    (G, G, G): "ma",
    (L, G, G): "ya",
    (G, L, G): "ra",
    (L, L, G): "sa",
    (G, G, L): "ta",
    (L, G, L): "ja",
    (G, L, L): "bha",
    (L, L, L): "na",
}

GANA_INV_MAP: Dict[str, Tuple[Weight, Weight, Weight]] = {
    name: pattern for pattern, name in GANA_MAP.items()
}

SINGLE_MAP: Dict[Weight, str] = {
    L: "la",
    G: "ga",
}

SINGLE_INV_MAP: Dict[str, Weight] = {
    "la": L,
    "ga": G,
    "l": L,
    "g": G,
}


def to_ganas(weights: List[Weight], separator: str = "-") -> str:
    """
    Decomposes a list of weights into classical Piṅgala gaṇa notation.
    """
    parts: List[str] = []
    i = 0
    n = len(weights)
    while i + 3 <= n:
        triad = (weights[i], weights[i + 1], weights[i + 2])
        parts.append(GANA_MAP[triad])
        i += 3
    for w in weights[i:]:
        parts.append(SINGLE_MAP[w])
    return separator.join(parts)


def from_ganas(gana_str: str) -> List[Weight]:
    """
    Parses a gaṇa notation string (hyphenated or concatenated) into Weight enums.
    """
    clean = gana_str.strip().lower()
    if "-" in clean or " " in clean:
        tokens = [tok for tok in re.split(r"[- \t]+", clean) if tok]
    else:
        tokens = re.findall(r"(bha|[myrstjnl]a|la|ga|[lg])", clean)

    weights: List[Weight] = []
    for tok in tokens:
        if tok in GANA_INV_MAP:
            weights.extend(GANA_INV_MAP[tok])
        elif tok in SINGLE_INV_MAP:
            weights.append(SINGLE_INV_MAP[tok])
        else:
            raise ValueError(f"Unrecognized gaṇa token: '{tok}' in '{gana_str}'")
    return weights