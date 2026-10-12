"""
core/linguistics/prosody/meters.py
Piṅgala scansion: Laghu (L) and Guru (G) weight calculation and pattern matching.
"""
from __future__ import annotations
import enum
from typing import List, Dict
from core.linguistics.prosody.syllables import (
    syllabify, tokenize, VOWELS_LONG, ALL_VOWELS, MODIFIERS, CONSONANTS
)


class Weight(enum.Enum):
    L = "L"  # Laghu (light, 1 mātrā)
    G = "G"  # Guru (heavy, 2 mātrās)

    def __str__(self) -> str:
        return self.value


def scan_line(text: str, end_is_guru: bool = True) -> List[Weight]:
    """
    Computes the Laghu/Guru weight vector for a given IAST pāda or verse.
    """
    sylls = syllabify(text)
    if not sylls:
        return []

    weights: List[Weight] = []
    num_sylls = len(sylls)

    for idx, syl in enumerate(sylls):
        # Rule 4: Pādānta rule
        if idx == num_sylls - 1 and end_is_guru:
            weights.append(Weight.G)
            continue

        toks = tokenize(syl)
        
        # Rule 1: Long vowel / diphthong
        has_long_vowel = any(t in VOWELS_LONG for t in toks)
        if has_long_vowel:
            weights.append(Weight.G)
            continue

        # Rule 2: Anusvāra / Visarga modifier
        has_modifier = any(t in MODIFIERS for t in toks)
        if has_modifier:
            weights.append(Weight.G)
            continue

        # Rule 3: Coda consonant (saṃyoga) - consonant appears after the vowel in this syllable
        v_idx = -1
        for i, t in enumerate(toks):
            if t in ALL_VOWELS:
                v_idx = i
                break
        
        has_coda_consonant = any(toks[i] in CONSONANTS for i in range(v_idx + 1, len(toks)))
        if has_coda_consonant:
            weights.append(Weight.G)
            continue

        weights.append(Weight.L)

    return weights


def match_meter(weights: List[Weight], meter_db: Dict[str, str]) -> List[str]:
    """
    Matches an observed weight vector against known meter definitions.
    """
    observed = "".join(str(w) for w in weights)
    matches = []
    for name, pattern in meter_db.items():
        if pattern == observed:
            matches.append(name)
    return matches