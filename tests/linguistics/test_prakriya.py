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
            (3, 1): "bhavati",
            (3, 2): "bhavataḥ",
            (3, 3): "bhavanti",
            (2, 1): "bhavasi",
            (2, 2): "bhavathaḥ",
            (2, 3): "bhavatha",
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
                    f"Mismatch at purusha={purusha}, vacana={vacana}",
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
        """Verify Adādi (Class 2) luk-elision of śap (2.4.72) and khari ca (8.4.55)."""
        tree_3sg = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "atti")
        applied_3sg = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("2.4.72", applied_3sg)
        self.assertIn("8.4.55", applied_3sg)

        tree_3du = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=2)
        self.assertEqual(tree_3du.final_output, "attaḥ")
        applied_3du = [step.rule_applied.number for step in tree_3du.steps]
        self.assertIn("2.4.72", applied_3du)
        self.assertIn("8.4.55", applied_3du)
        self.assertIn("8.3.15", applied_3du)

        tree_3pl = derive_lat_kartari("ad", gana=Gana.ADADI, purusha=3, vacana=3)
        self.assertEqual(tree_3pl.final_output, "adanti")
        applied_3pl = [step.rule_applied.number for step in tree_3pl.steps]
        self.assertIn("2.4.72", applied_3pl)

    def test_hu_lat_juhotyadi_cells(self):
        """Verify Juhotyādi (Class 3) reduplication (6.1.10) and abhyāsa-kārya (6.1.4)."""
        tree_3sg = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "juhoti")
        applied_3sg = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("2.4.75", applied_3sg)
        self.assertIn("6.1.10", applied_3sg)
        self.assertIn("6.1.4", applied_3sg)
        self.assertIn("7.4.62", applied_3sg)
        self.assertIn("8.4.54", applied_3sg)
        self.assertIn("7.3.84", applied_3sg)

        tree_3du = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=2)
        self.assertEqual(tree_3du.final_output, "juhutaḥ")
        applied_3du = [step.rule_applied.number for step in tree_3du.steps]
        self.assertIn("1.2.4", applied_3du)
        self.assertIn("8.3.15", applied_3du)
        self.assertNotIn("7.3.84", applied_3du)

        tree_3pl = derive_lat_kartari("hu", gana=Gana.JUHOTYADI, purusha=3, vacana=3)
        self.assertEqual(tree_3pl.final_output, "juhvati")
        applied_3pl = [step.rule_applied.number for step in tree_3pl.steps]
        self.assertIn("7.1.4", applied_3pl)
        self.assertIn("6.1.77", applied_3pl)

    def test_nrt_divadi_cells(self):
        """Verify Divādi (Class 4) 3.1.69 śyan (ya) with 1.1.5 kniti ca blocking guṇa."""
        tree_3sg = derive_lat_kartari("nṛt", gana=Gana.DIVADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "nṛtyati")
        applied = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("3.1.69", applied)
        self.assertIn("1.1.5", applied)
        self.assertNotIn("7.3.84", applied)
        self.assertNotIn("7.3.86", applied)

    def test_tud_tudadi_cells(self):
        """Verify Tudādi (Class 6) 3.1.77 śa (a) with 1.2.4 apit blocking guṇa."""
        tree_3sg = derive_lat_kartari("tud", gana=Gana.TUDADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "tudati")
        applied = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("3.1.77", applied)
        self.assertIn("1.2.4", applied)
        self.assertNotIn("7.3.84", applied)
        self.assertNotIn("7.3.86", applied)

        tree_vis = derive_lat_kartari("viś", gana=Gana.TUDADI, purusha=3, vacana=1)
        self.assertEqual(tree_vis.final_output, "viśati")
        self.assertNotEqual(tree_vis.final_output, "veśati")

    def test_rudh_rudhadi_cells(self):
        """
        Verify Rudhādi (Class 7) mit-infix (1.1.47), ṇatva (8.4.1),
        jhaṣas tathor dho'dhaḥ (8.2.40), and jhalāṁ jaś jhaśi (8.4.53):
          3sg: rudh + tip -> ruṇaddhi
          3du: rudh + tas -> runddhaḥ (via 6.4.111 al-lopa)
        """
        tree_3sg = derive_lat_kartari("rudh", gana=Gana.RUDHADI, purusha=3, vacana=1)
        self.assertEqual(tree_3sg.final_output, "ruṇaddhi")
        applied_3sg = [step.rule_applied.number for step in tree_3sg.steps]
        self.assertIn("3.1.78", applied_3sg)
        self.assertIn("1.1.47", applied_3sg)
        self.assertIn("8.4.1", applied_3sg)
        self.assertIn("8.2.40", applied_3sg)
        self.assertIn("8.4.53", applied_3sg)

        tree_3du = derive_lat_kartari("rudh", gana=Gana.RUDHADI, purusha=3, vacana=2)
        self.assertEqual(tree_3du.final_output, "runddhaḥ")
        applied_3du = [step.rule_applied.number for step in tree_3du.steps]
        self.assertIn("6.4.111", applied_3du)
        self.assertIn("8.2.40", applied_3du)
        self.assertIn("8.4.53", applied_3du)
        self.assertIn("8.3.15", applied_3du)

    def test_svadi_tanadi_kryadi_cells(self):
        """
        Verify Classes 5, 8, and 9:
          Class 5 (Svādi):  su + śnu -> sunoti (3sg), sunutaḥ (3du)
          Class 8 (Tanādi): tan + u  -> tanoti (3sg), tanutaḥ (3du)
          Class 9 (Kryādi): krī + śnā -> krīṇāti (3sg), krīṇītaḥ (3du via 6.4.112)
        """
        # Svādi: sunoti, sunutaḥ
        tree_su_3sg = derive_lat_kartari("su", gana=Gana.SVADI, purusha=3, vacana=1)
        self.assertEqual(tree_su_3sg.final_output, "sunoti")
        self.assertIn("3.1.73", [s.rule_applied.number for s in tree_su_3sg.steps])
        self.assertIn("7.3.84", [s.rule_applied.number for s in tree_su_3sg.steps])

        tree_su_3du = derive_lat_kartari("su", gana=Gana.SVADI, purusha=3, vacana=2)
        self.assertEqual(tree_su_3du.final_output, "sunutaḥ")
        self.assertIn("1.2.4", [s.rule_applied.number for s in tree_su_3du.steps])
        self.assertIn("8.3.15", [s.rule_applied.number for s in tree_su_3du.steps])

        # Tanādi: tanoti, tanutaḥ
        tree_tan_3sg = derive_lat_kartari("tan", gana=Gana.TANADI, purusha=3, vacana=1)
        self.assertEqual(tree_tan_3sg.final_output, "tanoti")
        self.assertIn("3.1.79", [s.rule_applied.number for s in tree_tan_3sg.steps])
        self.assertIn("7.3.84", [s.rule_applied.number for s in tree_tan_3sg.steps])

        tree_tan_3du = derive_lat_kartari("tan", gana=Gana.TANADI, purusha=3, vacana=2)
        self.assertEqual(tree_tan_3du.final_output, "tanutaḥ")
        self.assertIn("1.2.4", [s.rule_applied.number for s in tree_tan_3du.steps])
        self.assertIn("8.3.15", [s.rule_applied.number for s in tree_tan_3du.steps])

        # Kryādi: krīṇāti, krīṇītaḥ
        tree_kri_3sg = derive_lat_kartari("krī", gana=Gana.KRYADI, purusha=3, vacana=1)
        self.assertEqual(tree_kri_3sg.final_output, "krīṇāti")
        self.assertIn("3.1.81", [s.rule_applied.number for s in tree_kri_3sg.steps])
        self.assertIn("8.4.1", [s.rule_applied.number for s in tree_kri_3sg.steps])

        tree_kri_3du = derive_lat_kartari("krī", gana=Gana.KRYADI, purusha=3, vacana=2)
        self.assertEqual(tree_kri_3du.final_output, "krīṇītaḥ")
        self.assertIn("6.4.112", [s.rule_applied.number for s in tree_kri_3du.steps])
        self.assertIn("8.3.15", [s.rule_applied.number for s in tree_kri_3du.steps])


if __name__ == "__main__":
    unittest.main()