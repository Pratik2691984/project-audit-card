"""
core/linguistics/prosody/syllables.py
IAST syllabification into akṣara units with proper coda/onset division.
"""
from __future__ import annotations
import re
from typing import List

VOWELS_LONG = {"ā", "ī", "ū", "ṝ", "e", "ai", "o", "au"}
VOWELS_SHORT = {"a", "i", "u", "ṛ", "ḷ"}
ALL_VOWELS = VOWELS_LONG | VOWELS_SHORT

MODIFIERS = {"ṃ", "ḥ"}

# Ordered longest-first for greedy matching
CONSONANTS = [
    "kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh",
    "k", "g", "ṅ", "c", "j", "ñ", "ṭ", "ḍ", "ṇ", "t", "d", "n",
    "p", "b", "m", "y", "r", "l", "v", "ś", "ṣ", "s", "h"
]

_VOWEL_RE = "|".join(re.escape(v) for v in sorted(ALL_VOWELS, key=len, reverse=True))
_CONS_RE = "|".join(re.escape(c) for c in CONSONANTS)
_MOD_RE = "|".join(re.escape(m) for m in MODIFIERS)

_TOKEN_PATTERN = re.compile(f"({_CONS_RE}|{_VOWEL_RE}|{_MOD_RE})", re.IGNORECASE)


def tokenize(text: str) -> List[str]:
    """Tokenizes IAST string into individual phonemes."""
    return _TOKEN_PATTERN.findall(text.lower().strip())


def syllabify(text: str) -> List[str]:
    """
    Partitions IAST text into phonological syllables (akṣaras).
    When an intervocalic consonant cluster C1...Ck occurs (k >= 2):
      C1 attaches as coda to the preceding syllable, making it heavy.
      C2...Ck attach as onset to the subsequent syllable.
    Single intervocalic consonant C1 attaches as onset to the subsequent syllable.
    """
    tokens = tokenize(text)
    if not tokens:
        return []

    # Identify vowel indices (syllable nuclei)
    nuclei_indices = []
    for i, tok in enumerate(tokens):
        if tok in ALL_VOWELS:
            nuclei_indices.append(i)

    if not nuclei_indices:
        return []

    syllable_slices = []
    num_nuclei = len(nuclei_indices)

    for idx, v_idx in enumerate(nuclei_indices):
        # Start of onset for this syllable
        if idx == 0:
            start = 0
        else:
            prev_v = nuclei_indices[idx - 1]
            inter_consonants = v_idx - prev_v - 1
            # Check if previous vowel had a modifier (ṃ/ḥ)
            has_mod = (prev_v + 1 < len(tokens) and tokens[prev_v + 1] in MODIFIERS)
            offset = 1 if has_mod else 0
            
            cluster_len = v_idx - (prev_v + 1 + offset)
            if cluster_len >= 2:
                # First consonant stays with previous syllable as coda
                start = prev_v + 1 + offset + 1
            else:
                start = prev_v + 1 + offset

        # End of this syllable (includes vowel, optional modifier, and optional coda)
        if idx == num_nuclei - 1:
            end = len(tokens)
        else:
            next_v = nuclei_indices[idx + 1]
            has_mod = (v_idx + 1 < len(tokens) and tokens[v_idx + 1] in MODIFIERS)
            offset = 1 if has_mod else 0
            cluster_len = next_v - (v_idx + 1 + offset)
            if cluster_len >= 2:
                # Include the first consonant of the cluster as coda
                end = v_idx + 1 + offset + 1
            else:
                end = v_idx + 1 + offset

        syllable_slices.append("".join(tokens[start:end]))

    return syllable_slices