"""
core/linguistics/prosody/patterns.py
Pattern-based meter matching with wildcard (X) support and multi-pāda dispatch.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from core.linguistics.prosody.meters import Weight

L = Weight.L
G = Weight.G


@dataclass(frozen=True)
class MeterEntry:
    name: str
    meter_type: str
    pada_patterns: List[List[str]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MeterEntry:
        m_type = data.get("type", "fixed")
        name = data["name"]

        if m_type == "fixed":
            single_pat = data["pattern"]
            pada_patterns = [[single_pat]] * 4
        elif m_type == "pattern":
            raw_padas = data.get("pada_patterns", [])
            pada_patterns = [
                p if isinstance(p, list) else [p] for p in raw_padas
            ]
        else:
            raise ValueError(f"Unknown meter type: {m_type}")

        return cls(name=name, meter_type=m_type, pada_patterns=pada_patterns)


def match_pada(weights: List[Weight], pattern: str) -> bool:
    """
    Matches a single pāda weight vector against a pattern string.
    Supported symbols: 'L', 'G', 'X'.
    """
    clean_pat = pattern.strip().upper()
    if len(weights) != len(clean_pat):
        return False

    for w, p in zip(weights, clean_pat):
        if p == "X":
            continue
        if p == "L" and w != L:
            return False
        if p == "G" and w != G:
            return False
        if p not in ("L", "G", "X"):
            raise ValueError(f"Invalid character in meter pattern: '{p}'")

    return True


def match_verse(
    verse_weights: List[List[Weight]],
    meter: MeterEntry,
) -> bool:
    """
    Verifies that a multi-pāda verse matches all pāda patterns of a meter entry.
    """
    if len(verse_weights) != len(meter.pada_patterns):
        return False

    return all(
        any(match_pada(pada, pat) for pat in pattern_set)
        for pada, pattern_set in zip(verse_weights, meter.pada_patterns)
    )