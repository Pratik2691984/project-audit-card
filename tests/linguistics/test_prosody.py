import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from core.linguistics.prosody.syllables import syllabify
from core.linguistics.prosody.meters import Weight, scan_line, match_meter
from core.linguistics.prosody.ganas import to_ganas, from_ganas

L = Weight.L
G = Weight.G


class TestPingalaProsody(unittest.TestCase):

    def test_scan_known_sloka(self):
        pada = "dharmakṣetre kurukṣetre"
        sylls = syllabify(pada)
        self.assertEqual(len(sylls), 8)
        weights = scan_line(pada, end_is_guru=True)
        expected = [G, G, G, G, L, G, G, G]
        self.assertEqual(weights, expected)

    def test_match_totaka(self):
        toml_path = Path(__file__).resolve().parents[2] / "core" / "linguistics" / "data" / "chhandas_meters.toml"
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
        
        # Load fixed meters into dict for simple matching
        fixed_meters = {
            m["name"]: m["pattern"] for m in data["meters"] if m.get("type", "fixed") == "fixed"
        }

        totaka_pattern = [
            L, L, G,
            L, L, G,
            L, L, G,
            L, L, G,
        ]
        matches = match_meter(totaka_pattern, fixed_meters)
        self.assertIn("Toṭaka", matches)

    def test_last_syllable_rules(self):
        phrase = "kavi"
        weights_padanta = scan_line(phrase, end_is_guru=True)
        self.assertEqual(weights_padanta[-1], G)
        weights_strict = scan_line(phrase, end_is_guru=False)
        self.assertEqual(weights_strict[-1], L)

    def test_totaka_decomposes_to_sa_sa_sa_sa(self):
        weights = [L, L, G, L, L, G, L, L, G, L, L, G]
        self.assertEqual(to_ganas(weights), "sa-sa-sa-sa")

    def test_anustubh_pada_decomposes_with_trailing_singles(self):
        weights = [G, L, G, L, L, G, L]
        self.assertEqual(to_ganas(weights), "ra-sa-la")

    def test_concatenated_parsing(self):
        self.assertEqual(from_ganas("sasasasa"), [L, L, G, L, L, G, L, L, G, L, L, G])
        self.assertEqual(from_ganas("rasala"), [G, L, G, L, L, G, L])

    def test_roundtrip_against_table(self):
        toml_path = Path(__file__).resolve().parents[2] / "core" / "linguistics" / "data" / "chhandas_meters.toml"
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        for m in data["meters"]:
            if m.get("type", "fixed") == "fixed":
                pattern_str = m["pattern"]
                weights = [Weight[ch] for ch in pattern_str]
                decomp = to_ganas(weights)
                reconstructed = from_ganas(decomp)
                self.assertEqual(
                    reconstructed,
                    weights,
                    f"Round-trip failed for meter '{m['name']}' ({pattern_str} -> {decomp})"
                )


if __name__ == "__main__":
    unittest.main()