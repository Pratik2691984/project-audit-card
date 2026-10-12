"""
core/linguistics/ast/sivasutras.py
Implementation of the 14 Māheśvara / Śivasūtras and dynamic Pratyāhāra resolution
per Aṣṭādhyāyī 1.1.71 (ādirantyena sahetā).
"""
from __future__ import annotations
from typing import List, Tuple, Set

SIVASUTRA_DATA: List[Tuple[List[str], str]] = [
    (["a", "i", "u"], "ṇ"),
    (["ṛ", "ḷ"], "k"),
    (["e", "o"], "ṅ"),
    (["ai", "au"], "c"),
    (["h", "y", "v", "r"], "ṭ"),
    (["l"], "ṇ"),
    (["ñ", "m", "ṅ", "ṇ", "n"], "m"),
    (["jh", "bh"], "ñ"),
    (["gh", "ḍh", "dh"], "ṣ"),
    (["j", "b", "g", "ḍ", "d"], "ś"),
    (["kh", "ph", "ch", "ṭh", "th", "c", "ṭ", "t"], "v"),
    (["k", "p"], "y"),
    (["ś", "ṣ", "s"], "r"),
    (["h"], "l"),
]


class Sivasutras:
    def __init__(self, data: List[Tuple[List[str], str]] = SIVASUTRA_DATA):
        self._sutras = data
        self._it_markers: Set[str] = {it for _, it in self._sutras}

        self._phoneme_stream: List[str] = []
        self._it_positions: List[Tuple[str, int]] = []

        curr_pos = 0
        for phonemes, it in self._sutras:
            for ph in phonemes:
                self._phoneme_stream.append(ph)
                curr_pos += 1
            self._it_positions.append((it, curr_pos))

    @property
    def it_markers(self) -> Set[str]:
        return set(self._it_markers)

    def expand(self, pratyahara: str, target_sutra_hint: int | None = None) -> List[str]:
        clean = pratyahara.strip().lower()
        if len(clean) < 2:
            raise ValueError(f"Pratyāhāra must be at least 2 characters: '{pratyahara}'")

        it = clean[-1]
        start_ph = clean[:-1]

        if it not in self._it_markers:
            raise ValueError(f"'{it}' is not a valid Śivasūtra it-marker")

        # Normalize enunciation vowel 'a' on consonant names (e.g. 'ha' -> 'h', 'ya' -> 'y')
        # while preserving true vowel 'a'
        lookup_ph = start_ph
        if lookup_ph not in self._phoneme_stream and lookup_ph.endswith("a") and len(lookup_ph) > 1:
            lookup_ph = lookup_ph[:-1]

        start_indices = [
            idx for idx, ph in enumerate(self._phoneme_stream) if ph == lookup_ph
        ]
        if not start_indices:
            raise ValueError(f"Starting phoneme '{start_ph}' not found in Śivasūtras")

        end_cutoffs = [pos for marker, pos in self._it_positions if marker == it]

        chosen_start = None
        chosen_end = None

        if target_sutra_hint is not None:
            chosen_end = [pos for marker, pos in self._it_positions[:target_sutra_hint] if marker == it][-1]
            chosen_start = [idx for idx in start_indices if idx < chosen_end][0]
        else:
            # Pair start phoneme with the earliest matching it-marker that follows it
            for s_idx in start_indices:
                valid_ends = [e for e in end_cutoffs if e > s_idx]
                if valid_ends:
                    chosen_start = s_idx
                    chosen_end = valid_ends[0]
                    break

        if chosen_start is None or chosen_end is None:
            raise ValueError(f"Could not resolve valid span for pratyāhāra '{pratyahara}'")

        return self._phoneme_stream[chosen_start:chosen_end]


_DEFAULT_ENGINE = Sivasutras()


def expand_pratyahara(pratyahara: str) -> List[str]:
    return _DEFAULT_ENGINE.expand(pratyahara)