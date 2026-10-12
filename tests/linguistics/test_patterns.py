import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from core.linguistics.prosody.meters import Weight
from core.linguistics.prosody.ganas import to_ganas, from_ganas
from core.linguistics.prosody.patterns import MeterEntry, match_pada, match_verse

L = Weight.L
G = Weight.G


class TestPatternMatching(unittest.TestCase):

    def setUp(self):
        toml_path = Path(__file__).resolve().parents[2] / "core" / "linguistics" / "data" / "chhandas_meters.toml"
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
        self.db = {m["name"]: MeterEntry.from_dict(m) for m in data["meters"]}

    def test_match_pada_wildcards(self):
        # Pattern: XXXXLGGX
        pattern = "XXXXLGGX"
        valid_pada = [G, G, G, G, L, G, G, G]
        self.assertTrue(match_pada(valid_pada, pattern))

        # Fails on wrong weight at index 5 (expected G, got L)
        invalid_cadence = [G, G, G, G, L, L, G, G]
        self.assertFalse(match_pada(invalid_cadence, pattern))

        # Fails on length mismatch
        self.assertFalse(match_pada([G, G, G], pattern))

    def test_match_verse_anustubh_positive(self):
        # BG 1.1:
        # Pāda 1: dharma-kṣetre kuru-kṣetre (GGGG LGGG) -> matches XXXXLGGX
        # Pāda 2: samavetā yuyutsavaḥ       (LLGG LGLG) -> matches XXXXLGLX
        # Pāda 3: māmakāḥ pāṇḍavāścaiva     (GLGG LGGG) -> matches XXXXLGGX
        # Pāda 4: kimakurvata sañjaya       (LLGL LGLG) -> matches XXXXLGLX
        bg_1_1 = [
            [G, G, G, G, L, G, G, G],
            [L, L, G, G, L, G, L, G],
            [G, L, G, G, L, G, G, G],
            [L, L, G, L, L, G, L, G],
        ]
        anustubh = self.db["Anuṣṭubh"]
        self.assertTrue(match_verse(bg_1_1, anustubh))

    def test_match_verse_anustubh_cadence_negative(self):
        # Pāda 2 given wrong cadence (LGG instead of LGL)
        bad_bg = [
            [G, G, G, G, L, G, G, G],
            [L, L, G, G, L, G, G, G],
            [G, L, G, G, L, G, G, G],
            [L, L, G, L, L, G, L, G],
        ]
        anustubh = self.db["Anuṣṭubh"]
        self.assertFalse(match_verse(bad_bg, anustubh))

    def test_match_verse_dispatches_fixed_vs_pattern(self):
        totaka = self.db["Toṭaka"]
        self.assertEqual(totaka.meter_type, "fixed")
        totaka_verse = [[L, L, G] * 4] * 4
        self.assertTrue(match_verse(totaka_verse, totaka))

        anustubh = self.db["Anuṣṭubh"]
        self.assertEqual(anustubh.meter_type, "pattern")

    def test_roundtrip_pattern_render_ganas(self):
        # [G, G, G] (ma) + [G, L, G] (ra) + [G] (ga) + [G] (ga) -> ma-ra-ga-ga
        sample_odd_pada = [G, G, G, G, L, G, G, G]
        decomp = to_ganas(sample_odd_pada)
        self.assertEqual(decomp, "ma-ra-ga-ga")
        self.assertEqual(from_ganas(decomp), sample_odd_pada)


if __name__ == "__main__":
    unittest.main()