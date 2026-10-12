"""
test_prakriya.py - Test suite for Pāṇinian morphological derivation trees.
"""

import unittest
from core.linguistics.prakriya.engine import derive_lat_kartari, Gana


class TestPrakriyaEngine(unittest.TestCase):
    def test_bhu_lat_all_nine_cells(self):
        """
        Verify all 9 cells of the Parasmaipada present active matrix for bhū:
          Prathama:  bhavati,  bhavataḥ,  bhavanti
          Madhyama:  bhavasi,  bhavathaḥ, bhavatha
          Uttama:    bhavāmi,  bhavāvaḥ,  bhavāmaḥ
        """
        expected_matrix = {
            # Prathama puruṣa (3rd person)
            (3, 1): "bhavati",
            (3, 2): "bhavataḥ",
            (3, 3): "bhavanti",
            # Madhyama puruṣa (2nd person)
            (2, 1): "bhavasi",
            (2, 2): "bhavathaḥ",
            (2, 3): "bhavatha",
            # Uttama puruṣa (1st person)
            (1, 1): "bhavāmi",
            (1, 2): "bhavāvaḥ",
            (1, 3): "bhavāmaḥ",
        }

        for (purusha, vacana), expected_form in expected_matrix.items():
            with self.subTest(purusha=purusha, vacana=vacana):
                tree = derive_lat_kartari("bhū", gana=Gana.BHVADI, purusha=purusha, vacana=vacana)
                self.assertEqual(
                    tree.final_output,
                    expected_form,
                    f"Mismatch at purusha={purusha}, vacana={vacana}"
                )

    def test_jhonta_and_ato_gune_provenance(self):
        """Verify 7.1.3 (jho'ntaḥ) and 6.1.97 (ato guṇe) in bhavanti derivation."""
        tree = derive_lat_kartari("bhū", purusha=3, vacana=3)
        self.assertEqual(tree.final_output, "bhavanti")
        applied_sutras = [step.rule_applied.number for step in tree.steps]
        self.assertIn("7.1.3", applied_sutras)
        self.assertIn("6.1.97", applied_sutras)

    def test_ato_dirgho_yani_provenance(self):
        """Verify 7.3.101 (ato dīrgho yañi) in bhavāmi, bhavāvaḥ, bhavāmaḥ."""
        for vacana in (1, 2, 3):
            tree = derive_lat_kartari("bhū", purusha=1, vacana=vacana)
            applied_sutras = [step.rule_applied.number for step in tree.steps]
            self.assertIn("7.3.101", applied_sutras)

    def test_ad_lat_adadi_cells(self):
        """
        Verify Adādi (Class 2) luk-elision of śap (2.4.72) and khari ca (8.4.55):
          3sg: ad + ti   -> at + ti  -> atti
          3du: ad + tas  -> at + tas -> attaḥ
          3pl: ad + anti -> adanti
        """
        # 3sg: atti
        tree_3sg = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "atti")
        applied_3sg = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("2.4.72", applied_3sg)
        self.assertIn("8.4.55", applied_3sg)

        # 3du: attaḥ
        tree_3du = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=2)
        self.assertEqual(tree_3du.final_output, "attaḥ")
        applied_3du = [step.rule_applied.number for step in tree_3du.steps]
        self.assertIn("2.4.72", applied_3du)
        self.assertIn("8.4.55", applied_3du)
        self.assertIn("8.3.15", applied_3du)

        # 3pl: adanti
        tree_3pl = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=3)
        self.assertEqual(tree_3pl.final_output, "adanti")
        applied_3pl = [step.rule_applied.number for step in tree_3pl.steps]
        self.assertIn("2.4.72", applied_3pl)

    def test_hu_lat_juhotyadi_cells(self):
        """
        Verify Juhotyādi (Class 3) reduplication (6.1.10) and abhyāsa-kārya:
          3sg: hu + tip -> juhu + ti -> juhoti (7.3.84 guṇa on pit)
          3du: hu + tas -> juhu + tas -> juhutaḥ (1.2.4 apit blocks guṇa, 8.3.15 visarga)
          3pl: hu + jhi -> juhu + ati -> juhvati (7.1.4 adabhyastāt + 6.1.77 yaṇ)
        """
        # 3sg: juhoti
        tree_3sg = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "juhoti")
        applied_3sg = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("2.4.75", applied_3sg)  # ślu
        self.assertIn("6.1.10", applied_3sg)  # dvitva
        self.assertIn("8.4.54", applied_3sg)  # kuhoścuḥ
        self.assertIn("8.4.55", applied_3sg)  # abhyāse carca
        self.assertIn("7.3.84", applied_3sg)  # sārvadhātukārdhadhātukayoḥ guṇa

        # 3du: juhutaḥ
        tree_3du = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=2)
        self.assertEqual(tree_3du.final_output, "juhutaḥ")
        applied_3du = [step.rule_applied.number for step in tree_3du.steps]
        self.assertIn("1.2.4", applied_3du)   # sārvadhātukam apit
        self.assertIn("8.3.15", applied_3du)  # visarjanīyaḥ
        self.assertNotIn("7.3.84", applied_3du)  # guṇa must NOT fire

        # 3pl: juhvati
        tree_3pl = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=3)
        self.assertEqual(tree_3pl.final_output, "juhvati")
        applied_3pl = [step.rule_applied.number for step in tree_3pl.steps]
        self.assertIn("7.1.4", applied_3pl)   # adabhyastāt
        self.assertIn("6.1.77", applied_3pl)  # iko yaṇaci


if __name__ == "__main__":
    unittest.main()