import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.linguistics.ast.sivasutras import Sivasutras, expand_pratyahara


class TestSivasutras(unittest.TestCase):

    def setUp(self):
        self.engine = Sivasutras()

    def test_expand_ac_all_vowels(self):
        ac = self.engine.expand("ac")
        expected = ["a", "i", "u", "ṛ", "ḷ", "e", "o", "ai", "au"]
        self.assertEqual(ac, expected)

    def test_expand_ik_vocalic_subset(self):
        ik = self.engine.expand("ik")
        expected = ["i", "u", "ṛ", "ḷ"]
        self.assertEqual(ik, expected)

    def test_expand_yan_semivowels(self):
        yan = self.engine.expand("yaṇ")
        expected = ["y", "v", "r", "l"]
        self.assertEqual(yan, expected)

    def test_expand_hal_consonants(self):
        hal = self.engine.expand("hal")
        self.assertEqual(hal[0], "h")
        # Terminal consonant of Sūtra 14 (ha-l) is 'h', as 'l' is the it-marker boundary
        self.assertEqual(hal[-1], "h")
        self.assertEqual(len(hal), 34)
        self.assertNotIn("a", hal)
        self.assertNotIn("i", hal)
        # Sūtra 6 contains vocalic/approximant 'l', but boundary marker 'l' is excluded
        self.assertIn("l", hal)

    def test_expand_al_all_phonemes(self):
        al = self.engine.expand("al")
        # 9 vowels (ac) + 34 consonants (hal) = 43 phonemes
        self.assertEqual(len(al), 43)
        self.assertEqual(al[0], "a")
        self.assertEqual(al[-1], "h")

    def test_invalid_it_marker_raises(self):
        with self.assertRaises(ValueError):
            self.engine.expand("ap")

    def test_invalid_start_phoneme_raises(self):
        with self.assertRaises(ValueError):
            self.engine.expand("zc")


if __name__ == "__main__":
    unittest.main()