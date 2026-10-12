"""
test_ast_sandhi.py - Complete Pāṇinian Sandhi Test Suite
"""

import unittest
from core.linguistics.ast.nodes import DerivationTree, ADHIKARA_EKAH_PURVAPARAYOH
from core.linguistics.ast.sandhi import (
    apply_vowel_sandhi,
    apply_vowel_sandhi_variants,
    apply_iko_yanaci,
    apply_ad_gunah,
    apply_vrddhir_eci,
    apply_akah_savarne_dirghah,
    apply_ecoyavayavah,
    apply_enah_padantad_ati,
    apply_lopah_sakalyasya,
    apply_stoh_scuna_scuh,
    apply_stuna_stuh,
    apply_hal_sandhi,
    apply_visarga_sandhi,
    SUTRA_6_1_77,
    SUTRA_6_1_78,
    SUTRA_6_1_87,
    SUTRA_6_1_88,
    SUTRA_6_1_101,
    SUTRA_6_1_109,
    SUTRA_8_3_19,
    SUTRA_8_4_40,
    SUTRA_8_4_41,
    SUTRA_6_1_113,
    SUTRA_6_1_114,
    SUTRA_8_3_17,
)


class TestAstSandhi(unittest.TestCase):
    # --- 6.1.84: Ekaḥ Pūrvaparayoḥ Adhikāra Provenance Tests ---
    def test_adhikara_6_1_84_provenance_in_guna(self):
        tree = DerivationTree("rāma", "iva")
        res, sutra = apply_ad_gunah("rāma", "iva", tree=tree)
        self.assertEqual(res, "rāmeva")
        self.assertEqual(len(tree.steps), 1)
        step = tree.steps[0]
        self.assertEqual(step.governing_adhikara, ADHIKARA_EKAH_PURVAPARAYOH)
        self.assertTrue(step.is_ekadesha)

    def test_adhikara_6_1_84_provenance_in_dirgha(self):
        tree = DerivationTree("kavi", "indra")
        res, sutra = apply_akah_savarne_dirghah("kavi", "indra", tree=tree)
        self.assertEqual(res, "kavīndra")
        step = tree.steps[0]
        self.assertEqual(step.governing_adhikara, ADHIKARA_EKAH_PURVAPARAYOH)
        self.assertTrue(step.is_ekadesha)

    def test_adhikara_6_1_84_absent_in_yan(self):
        # Iko yaṇaci is an ādeśa for 'ik' only, NOT an ekādeśa across pūrvapara
        tree = DerivationTree("iti", "api")
        res, sutra = apply_iko_yanaci("iti", "api", tree=tree)
        self.assertEqual(res, "ityapi")
        step = tree.steps[0]
        self.assertIsNone(step.governing_adhikara)
        self.assertFalse(step.is_ekadesha)

    # --- 8.4.40 & 8.4.41: Hal-Sandhi Tests ---
    def test_stoh_scuna_scuh_forward(self):
        # sat + cit -> saccit
        res, sutra = apply_stoh_scuna_scuh("sat", "cit")
        self.assertEqual(res, "saccit")
        self.assertEqual(sutra.number, "8.4.40")

    def test_stoh_scuna_scuh_s_to_sh(self):
        # rāmas + cinoti -> rāmaścinoti
        res, sutra = apply_stoh_scuna_scuh("rāmas", "cinoti")
        self.assertEqual(res, "rāmaścinoti")

    def test_stoh_scuna_scuh_d_to_j(self):
        # sad + jana -> sajjana
        res, sutra = apply_stoh_scuna_scuh("sad", "jana")
        self.assertEqual(res, "sajjana")

    def test_stuna_stuh_forward(self):
        # rāmas + ṣaṣṭha -> rāmaṣṣaṣṭha
        res, sutra = apply_stuna_stuh("rāmas", "ṣaṣṭha")
        self.assertEqual(res, "rāmaṣṣaṣṭha")
        self.assertEqual(sutra.number, "8.4.41")

    def test_stuna_stuh_t_to_th(self):
        # tat + ṭīkā -> taṭṭīkā
        res, sutra = apply_stuna_stuh("tat", "ṭīkā")
        self.assertEqual(res, "taṭṭīkā")

    # --- Visarga-Sandhi: 8.2.66, 6.1.113, 6.1.114, 8.3.17 Tests ---
    def test_visarga_ato_ror_aplutad_aplute(self):
        # rāmaḥ + ayam -> rāmo'yam (6.1.113)
        res = apply_visarga_sandhi("rāmaḥ", "ayam")
        self.assertEqual(res, "rāmo'yam")

    def test_visarga_hasi_ca(self):
        # rāmaḥ + gacchati -> rāmo gacchati (6.1.114 before voiced cons 'g')
        res = apply_visarga_sandhi("rāmaḥ", "gacchati")
        self.assertEqual(res, "rāmo gacchati")

    def test_visarga_bho_bhago_agho(self):
        # bhoḥ + acyuta -> bho acyuta (8.3.17 y-lopa)
        res = apply_visarga_sandhi("bhoḥ", "acyuta")
        self.assertEqual(res, "bho acyuta")

    def test_visarga_aa_purva_lopa(self):
        # devāḥ + gacchanti -> devā gacchanti (8.3.17 after ā before aś)
        res = apply_visarga_sandhi("devāḥ", "gacchanti")
        self.assertEqual(res, "devā gacchanti")

    # --- 6.1.77: Iko Yaṇaci Tests ---
    def test_iko_yanaci_i_to_y(self):
        res, sutra = apply_iko_yanaci("iti", "api")
        self.assertEqual(res, "ityapi")

    def test_iko_yanaci_u_to_v(self):
        res, sutra = apply_iko_yanaci("madhu", "ari")
        self.assertEqual(res, "madhvari")

    def test_iko_yanaci_r_to_r(self):
        res, sutra = apply_iko_yanaci("dhātṛ", "aṃśa")
        self.assertEqual(res, "dhātraṃśa")

    def test_iko_yanaci_no_trigger_consonant(self):
        res = apply_iko_yanaci("iti", "gacchati")
        self.assertIsNone(res)

    # --- 6.1.87: Ād Guṇaḥ Tests ---
    def test_ad_gunah_a_plus_i(self):
        res, sutra = apply_ad_gunah("rāma", "iva")
        self.assertEqual(res, "rāmeva")

    def test_ad_gunah_a_plus_u(self):
        res, sutra = apply_ad_gunah("rāma", "uṣas")
        self.assertEqual(res, "rāmoṣas")

    def test_ad_gunah_rapara(self):
        res, sutra = apply_ad_gunah("mahā", "ṛṣi")
        self.assertEqual(res, "maharṣi")

    # --- 6.1.88: Vṛddhir Eci Tests ---
    def test_vrddhir_eci_a_plus_e(self):
        res, sutra = apply_vrddhir_eci("na", "eti")
        self.assertEqual(res, "naiti")

    def test_vrddhir_eci_a_plus_o(self):
        res, sutra = apply_vrddhir_eci("jala", "ogha")
        self.assertEqual(res, "jalaugha")

    # --- 6.1.101: Akaḥ Savarṇe Dīrghaḥ Tests ---
    def test_dirgha_a_plus_a(self):
        res = apply_vowel_sandhi("daitya", "ari")
        self.assertEqual(res, "daityāri")

    def test_dirgha_a_plus_aa(self):
        res = apply_vowel_sandhi("vidyā", "ālaya")
        self.assertEqual(res, "vidyālaya")

    def test_dirgha_i_plus_i(self):
        res = apply_vowel_sandhi("kavi", "indra")
        self.assertEqual(res, "kavīndra")

    def test_dirgha_i_plus_ii(self):
        res = apply_vowel_sandhi("giri", "īśa")
        self.assertEqual(res, "girīśa")

    def test_dirgha_u_plus_u(self):
        res = apply_vowel_sandhi("bhānu", "udaya")
        self.assertEqual(res, "bhānūdaya")

    def test_dirgha_r_plus_r(self):
        res = apply_vowel_sandhi("hotṛ", "ṛkāra")
        self.assertEqual(res, "hotṝkāra")

    def test_dirgha_r_plus_l_varttika(self):
        res = apply_vowel_sandhi("hotṛ", "ḷkāra")
        self.assertEqual(res, "hotṝkāra")

    # --- 6.1.78: Eco'yavāyāvaḥ Tests ---
    def test_ecoyavayavah_e_to_ay(self):
        res, sutra = apply_ecoyavayavah("hare", "e")
        self.assertEqual(res, "haraye")

    def test_ecoyavayavah_o_to_av(self):
        res, sutra = apply_ecoyavayavah("bho", "anam")
        self.assertEqual(res, "bhavanam")

    def test_ecoyavayavah_ai_to_aay(self):
        res, sutra = apply_ecoyavayavah("nai", "aka")
        self.assertEqual(res, "nāyaka")

    def test_ecoyavayavah_au_to_aav(self):
        res, sutra = apply_ecoyavayavah("pau", "aka")
        self.assertEqual(res, "pāvaka")

    # --- 6.1.109: Eṅaḥ Padāntād Ati (Pūrvarūpa) Tests ---
    def test_enah_padantad_ati_e(self):
        res, sutra = apply_enah_padantad_ati("hare", "atra", is_padanta=True)
        self.assertEqual(res, "hare'tra")

    def test_enah_padantad_ati_o(self):
        res, sutra = apply_enah_padantad_ati("prabho", "atra", is_padanta=True)
        self.assertEqual(res, "prabho'tra")

    def test_enah_padantad_ati_rejected_when_not_padanta(self):
        res = apply_enah_padantad_ati("bho", "anam", is_padanta=False)
        self.assertIsNone(res)

    def test_enah_padantad_ati_rejected_when_long_a(self):
        res = apply_enah_padantad_ati("te", "āgatāḥ", is_padanta=True)
        self.assertIsNone(res)

    # --- 8.3.19: Lopaḥ Śākalyasya Tests ---
    def test_lopah_sakalyasya_y_elision(self):
        res, sutra = apply_lopah_sakalyasya("vanay", "āste", is_padanta=True)
        self.assertEqual(res, "vana āste")

    def test_lopah_sakalyasya_v_elision(self):
        res, sutra = apply_lopah_sakalyasya("ubhāv", "atra", is_padanta=True)
        self.assertEqual(res, "ubhā atra")

    def test_lopah_sakalyasya_dual_variants(self):
        variants = apply_vowel_sandhi_variants("vane", "āste", is_padanta=True)
        self.assertIn("vana āste", variants)
        self.assertIn("vanayāste", variants)

    def test_lopah_sakalyasya_asiddhatva_no_secondary_sandhi(self):
        res = apply_vowel_sandhi("vane", "āste", is_padanta=True)
        self.assertEqual(res, "vana āste")
        self.assertNotEqual(res, "vanāste")

    # --- Precedence & Dispatcher Tests ---
    def test_precedence_purvarupa_over_ecoyavayavah(self):
        res = apply_vowel_sandhi("hare", "atra", is_padanta=True)
        self.assertEqual(res, "hare'tra")

    def test_fallback_ecoyavayavah_when_not_padanta(self):
        res = apply_vowel_sandhi("hare", "atra", is_padanta=False)
        self.assertEqual(res, "harayatra")

    def test_precedence_dirgha_over_yan(self):
        res = apply_vowel_sandhi("prati", "iti")
        self.assertEqual(res, "pratīti")

    def test_precedence_dirgha_over_guna(self):
        res = apply_vowel_sandhi("rāma", "aśva")
        self.assertEqual(res, "rāmāśva")

    def test_precedence_vrddhi_over_guna(self):
        res = apply_vowel_sandhi("kṛṣṇa", "ekatvam")
        self.assertEqual(res, "kṛṣṇaikatvam")


if __name__ == "__main__":
    unittest.main()