"""
tests/linguistics/test_sivasutras.py
Unit tests for the Śivasūtra Pratyāhāra expansion engine.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.linguistics.ast.sivasutras import Sivasutras, expand_pratyahara


class TestSivasutras(unittest.TestCase):

    def setUp(self):
        self.engine = Sivasutras()

    def test_expand_ac_all_vowels(self):
        """
        'ac' pratyāhāra spanning sūtras 1 to 4:
        a-i-u-ṇ, ṛ-ḷ-k, e-o-ṅ, ai-au-c -> 9 vowels
        """
        ac = self.engine.expand("ac")
        expected = ["a", "i", "u", "ṛ", "ḷ", "e", "o", "ai", "au"]
        self.assertEqual(ac, expected)

    def test_expand_ik_vocalic_subset(self):
        """
        'ik' pratyāhāra starting from 'i' up to it-marker 'k' (sūtras 1-2):
        i, u, ṛ, ḷ
        """
        ik = self.engine.expand("ik")
        expected = ["i", "u", "ṛ", "ḷ"]
        self.assertEqual(ik, expected)

    def test_expand_yan_semivowels(self):
        """
        'yaṇ' pratyāhāra: y, v, r, l (target of iko yaṇaci)
        Spans sūtras 5 (ha-ya-va-ra-ṭ) and 6 (la-ṇ).
        """
        yan = self.engine.expand("yaṇ")
        expected = ["y", "v", "r", "l"]
        self.assertEqual(yan, expected)

    def test_expand_hal_consonants(self):
        """
        'hal' pratyāhāra: all consonants from 'h' in sūtra 5 to final 'l' in sūtra 14.
        """
        hal = self.engine.expand("hal")
        self.assertEqual(hal[0], "h")
        self.assertEqual(hal[-1], "l")
        # 34 consonants in traditional counting
        self.assertEqual(len(hal), 34)
        # Verify no vowels are present in 'hal'
        self.assertNotIn("a", hal)
        self.assertNotIn("i", hal)

    def test_expand_al_all_phonemes(self):
        """
        'al' pratyāhāra: the universe of all sounds (ac + hal).
        """
        al = self.engine.expand("al")
        self.assertEqual(len(al), 9 + 34)  # 43 elements

    def test_invalid_it_marker_raises(self):
        with self.assertRaises(ValueError):
            self.engine.expand("ap")  # 'p' is not an it marker (it is 'y' in ka-pa-y)

    def test_invalid_start_phoneme_raises(self):
        with self.assertRaises(ValueError):
            self.engine.expand("zc")  # 'z' does not exist in Śivasūtras


if __name__ == "__main__":
    unittest.main()