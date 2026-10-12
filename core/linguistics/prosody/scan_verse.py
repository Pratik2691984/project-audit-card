"""
core/linguistics/prosody/scan_verse.py
Top-level verse segmentation, end-to-end scansion, and meter identification.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from core.linguistics.prosody.syllables import syllabify
from core.linguistics.prosody.meters import Weight, scan_line
from core.linguistics.prosody.ganas import to_ganas
from core.linguistics.prosody.patterns import MeterEntry, match_verse, match_pada


@dataclass(frozen=True)
class MatchResult:
    name: str
    confidence: str
    per_pada_ganas: List[str]


def split_padas(text: str) -> List[str]:
    normalized = text.replace("॥", "||").replace("।", "|")
    raw_segments = re.split(r"(?:\|\||\||\r?\n)+", normalized)
    padas = [re.sub(r"\s+", " ", seg).strip() for seg in raw_segments if seg.strip()]

    if len(padas) == 2:
        s1 = syllabify(padas[0])
        s2 = syllabify(padas[1])
        if len(s1) == 16 and len(s2) == 16:
            words_1 = padas[0].split(" ")
            words_2 = padas[1].split(" ")

            def bisect_line(words: List[str]) -> Tuple[str, str]:
                acc = []
                for i, w in enumerate(words):
                    acc.append(w)
                    if len(syllabify(" ".join(acc))) == 8:
                        return " ".join(acc), " ".join(words[i + 1:])
                mid = len(words) // 2
                return " ".join(words[:mid]), " ".join(words[mid:])

            p1, p2 = bisect_line(words_1)
            p3, p4 = bisect_line(words_2)
            return [p1, p2, p3, p4]

    return padas


def load_default_meters() -> List[MeterEntry]:
    toml_path = Path(__file__).resolve().parents[1] / "data" / "chhandas_meters.toml"
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    return [MeterEntry.from_dict(m) for m in data.get("meters", [])]


def scan_and_identify(
    verse_text: str,
    meters: Optional[List[MeterEntry]] = None,
    end_is_guru: bool = True,
) -> List[MatchResult]:
    if meters is None:
        meters = load_default_meters()

    padas = split_padas(verse_text)
    num_padas = len(padas)
    if num_padas not in (1, 2, 4):
        return []

    verse_weights: List[List[Weight]] = [
        scan_line(p, end_is_guru=end_is_guru) for p in padas
    ]
    per_pada_ganas = [to_ganas(w) for w in verse_weights]

    matches: List[MatchResult] = []

    for entry in meters:
        is_match = False

        if num_padas == 4:
            is_match = match_verse(verse_weights, entry)
        elif num_padas == 1 and entry.meter_type == "fixed":
            is_match = match_pada(verse_weights[0], entry.pada_patterns[0][0])
        elif num_padas == 2:
            is_match = (
                any(match_pada(verse_weights[0], pat) for pat in entry.pada_patterns[0])
                and any(match_pada(verse_weights[1], pat) for pat in entry.pada_patterns[1])
            )

        if is_match:
            matches.append(
                MatchResult(
                    name=entry.name,
                    confidence="exact" if entry.meter_type == "fixed" else "pattern",
                    per_pada_ganas=per_pada_ganas,
                )
            )

    return sorted(matches, key=lambda m: (m.confidence == "exact", m.name), reverse=True)