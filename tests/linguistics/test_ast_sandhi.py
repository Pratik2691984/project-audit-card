"""
test_ast_sandhi.py - Test suite for Pāṇinian Ac-Sandhi rules
"""

import unittest
from core.linguistics.ast.sandhi import (
    apply_vowel_sandhi,
    apply_iko_yanaci,
    apply_ad_gunah,
    apply_vrddhir_eci,
    apply_akah_savarne_dirghah,
    apply_ecoyavayavah,
    apply_enah_padantad_ati,
    SUTRA_6_1_77,
    SUTRA_6_1_78,
    SUTRA_6_1_87,
    SUTRA_6_1_88,
    SUTRA_6_1_101,
    SUTRA_6_1_109,
)


class TestAstSandhi(unittest.TestCase):
    # --- 6.1.77: Iko Yaṇaci Tests ---
    def test_iko_yanaci_i_to_y(self):
        res, sutra = apply_iko_yanaci("iti", "api")
        self.assertEqual(res, "ityapi")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_u_to_v(self):
        res, sutra = apply_iko_yanaci("madhu", "ari")
        self.assertEqual(res, "madhvari")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_r_to_r(self):
        res, sutra = apply_iko_yanaci("dhātṛ", "aṃśa")
        self.assertEqual(res, "dhātraṃśa")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_no_trigger_consonant(self):
        res = apply_iko_yanaci("iti", "gacchati")
        self.assertIsNone(res)

    # --- 6.1.87: Ād Guṇaḥ Tests ---
    def test_ad_gunah_a_plus_i(self):
        res, sutra = apply_ad_gunah("rāma", "iva")
        self.assertEqual(res, "rāmeva")
        self.assertEqual(sutra.number, "6.1.87")

    def test_ad_gunah_a_plus_u(self):
        res, sutra = apply_ad_gunah("rāma", "uṣas")
        self.assertEqual(res, "rāmoṣas")
        self.assertEqual(sutra.number, "6.1.87")

    def test_ad_gunah_rapara(self):
        res, sutra = apply_ad_gunah("mahā", "ṛṣi")
        self.assertEqual(res, "maharṣi")
        self.assertEqual(sutra.number, "6.1.87")

    # --- 6.1.88: Vṛddhir Eci Tests ---
    def test_vrddhir_eci_a_plus_e(self):
        res, sutra = apply_vrddhir_eci("na", "eti")
        self.assertEqual(res, "naiti")
        self.assertEqual(sutra.number, "6.1.88")

    def test_vrddhir_eci_a_plus_o(self):
        res, sutra = apply_vrddhir_eci("jala", "ogha")
        self.assertEqual(res, "jalaugha")
        self.assertEqual(sutra.number, "6.1.88")

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
        # hare + e -> haraye
        res, sutra = apply_ecoyavayavah("hare", "e")
        self.assertEqual(res, "haraye")
        self.assertEqual(sutra.number, "6.1.78")

    def test_ecoyavayavah_o_to_av(self):
        # bho + anam -> bhavanam
        res, sutra = apply_ecoyavayavah("bho", "anam")
        self.assertEqual(res, "bhavanam")
        self.assertEqual(sutra.number, "6.1.78")

    def test_ecoyavayavah_ai_to_aay(self):
        # nai + aka -> nāyaka
        res, sutra = apply_ecoyavayavah("nai", "aka")
        self.assertEqual(res, "nāyaka")
        self.assertEqual(sutra.number, "6.1.78")

    def test_ecoyavayavah_au_to_aav(self):
        # pau + aka -> pāvaka
        res, sutra = apply_ecoyavayavah("pau", "aka")
        self.assertEqual(res, "pāvaka")
        self.assertEqual(sutra.number, "6.1.78")

    # --- 6.1.109: Eṅaḥ Padāntād Ati (Pūrvarūpa) Tests ---
    def test_enah_padantad_ati_e(self):
        # hare + atra -> hare'tra
        res, sutra = apply_enah_padantad_ati("hare", "atra", is_padanta=True)
        self.assertEqual(res, "hare'tra")
        self.assertEqual(sutra.number, "6.1.109")

    def test_enah_padantad_ati_o(self):
        # prabho + atra -> prabho'tra
        res, sutra = apply_enah_padantad_ati("prabho", "atra", is_padanta=True)
        self.assertEqual(res, "prabho'tra")
        self.assertEqual(sutra.number, "6.1.109")

    def test_enah_padantad_ati_rejected_when_not_padanta(self):
        # Internal morpheme boundary should NOT trigger 6.1.109
        res = apply_enah_padantad_ati("bho", "anam", is_padanta=False)
        self.assertIsNone(res)

    def test_enah_padantad_ati_rejected_when_long_a(self):
        # te + āgatāḥ -> 6.1.109 requires short 'at' (a), not 'āt' (ā)
        res = apply_enah_padantad_ati("te", "āgatāḥ", is_padanta=True)
        self.assertIsNone(res)

    # --- Precedence & Dispatcher Tests ---
    def test_precedence_purvarupa_over_ecoyavayavah(self):
        # hare + atra (padānta) -> hare'tra (MUST NOT produce harayatra via 6.1.78)
        res = apply_vowel_sandhi("hare", "atra", is_padanta=True)
        self.assertEqual(res, "hare'tra")

    def test_fallback_ecoyavayavah_when_not_padanta(self):
        # When not padānta, e + a -> ay + a
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