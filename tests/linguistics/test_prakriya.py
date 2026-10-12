"""
test_prakriya.py - Test suite for Pāṇinian morphological derivation trees.
"""

import unittest
from core.linguistics.prakriya.engine import derive_lat_kartari, Gana


class TestPrakriyaEngine(unittest.TestCase):
    def test_derive_bhu_lat_prathama_ekavacana(self):
        # bhū + laṭ (3, 1) -> bhavati
        tree = derive_lat_kartari("bhū", gana=Gana.BHVADI, purusha=3, vacana=1)
        self.assertEqual(tree.final_output, "bhavati")
        
        # Verify rule progression in DerivationTree
        sutra_sequence = [step.rule_applied.number for step in tree.steps]
        expected_sequence = [
            "1.3.1",    # bhūvādayo dhātavaḥ
            "3.2.123",  # vartamāne laṭ
            "3.4.78",   # tiptasjhi...
            "1.3.9",    # tasya lopaḥ (tip -> ti)
            "3.1.68",   # kartari śap
            "1.3.9",    # tasya lopaḥ (śap -> a)
            "7.3.84",   # sārvadhātukārdhadhātukayoḥ (bhū -> bho)
            "6.1.78",   # eco'yavāyāvaḥ (bho + a -> bhava + ti)
        ]
        self.assertEqual(sutra_sequence, expected_sequence)


if __name__ == "__main__":
    unittest.main()