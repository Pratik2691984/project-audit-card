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
    SUTRA_6_1_77,
    SUTRA_6_1_87,
    SUTRA_6_1_88,
    SUTRA_6_1_101,
)


class TestAstSandhi(unittest.TestCase):
    # --- 6.1.77: Iko Yaṇaci Tests ---
    def test_iko_yanaci_i_to_y(self):
        # iti + api -> ityapi
        res, sutra = apply_iko_yanaci("iti", "api")
        self.assertEqual(res, "ityapi")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_u_to_v(self):
        # madhu + ari -> madhvari
        res, sutra = apply_iko_yanaci("madhu", "ari")
        self.assertEqual(res, "madhvari")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_r_to_r(self):
        # dhātṛ + aṃśa -> dhātraṃśa
        res, sutra = apply_iko_yanaci("dhātṛ", "aṃśa")
        self.assertEqual(res, "dhātraṃśa")
        self.assertEqual(sutra.number, "6.1.77")

    def test_iko_yanaci_no_trigger_consonant(self):
        # iti + gacchati -> None (no ac follower)
        res = apply_iko_yanaci("iti", "gacchati")
        self.assertIsNone(res)

    # --- 6.1.87: Ād Guṇaḥ Tests ---
    def test_ad_gunah_a_plus_i(self):
        # rāma + iva -> rāmeva
        res, sutra = apply_ad_gunah("rāma", "iva")
        self.assertEqual(res, "rāmeva")
        self.assertEqual(sutra.number, "6.1.87")

    def test_ad_gunah_a_plus_u(self):
        # rāma + uṣas -> rāmoṣas
        res, sutra = apply_ad_gunah("rāma", "uṣas")
        self.assertEqual(res, "rāmoṣas")
        self.assertEqual(sutra.number, "6.1.87")

    def test_ad_gunah_rapara(self):
        # mahā + ṛṣi -> maharṣi (1.1.51 uran raparah)
        res, sutra = apply_ad_gunah("mahā", "ṛṣi")
        self.assertEqual(res, "maharṣi")
        self.assertEqual(sutra.number, "6.1.87")

    # --- 6.1.88: Vṛddhir Eci Tests ---
    def test_vrddhir_eci_a_plus_e(self):
        # na + eti -> naiti
        res, sutra = apply_vrddhir_eci("na", "eti")
        self.assertEqual(res, "naiti")
        self.assertEqual(sutra.number, "6.1.88")

    def test_vrddhir_eci_a_plus_o(self):
        # jala + ogha -> jalaugha
        res, sutra = apply_vrddhir_eci("jala", "ogha")
        self.assertEqual(res, "jalaugha")
        self.assertEqual(sutra.number, "6.1.88")

    # --- 6.1.101: Akaḥ Savarṇe Dīrghaḥ Tests ---
    def test_dirgha_a_plus_a(self):
        # daitya + ari -> daityāri
        res = apply_vowel_sandhi("daitya", "ari")
        self.assertEqual(res, "daityāri")

    def test_dirgha_a_plus_aa(self):
        # vidyā + ālaya -> vidyālaya
        res = apply_vowel_sandhi("vidyā", "ālaya")
        self.assertEqual(res, "vidyālaya")

    def test_dirgha_i_plus_i(self):
        # kavi + indra -> kavīndra
        res = apply_vowel_sandhi("kavi", "indra")
        self.assertEqual(res, "kavīndra")

    def test_dirgha_i_plus_ii(self):
        # giri + īśa -> girīśa
        res = apply_vowel_sandhi("giri", "īśa")
        self.assertEqual(res, "girīśa")

    def test_dirgha_u_plus_u(self):
        # bhānu + udaya -> bhānūdaya
        res = apply_vowel_sandhi("bhānu", "udaya")
        self.assertEqual(res, "bhānūdaya")

    def test_dirgha_r_plus_r(self):
        # hotṛ + ṛkāra -> hotṝkāra
        res = apply_vowel_sandhi("hotṛ", "ṛkāra")
        self.assertEqual(res, "hotṝkāra")

    def test_dirgha_r_plus_l_varttika(self):
        # hotṛ + ḷkāra -> hotṝkāra (ṛ and ḷ are savarṇa per vārttika)
        res = apply_vowel_sandhi("hotṛ", "ḷkāra")
        self.assertEqual(res, "hotṝkāra")

    # --- Precedence & Dispatcher Tests ---
    def test_precedence_dirgha_over_yan(self):
        # prati + iti -> pratīti (MUST NOT produce pratyiti via 6.1.77)
        res = apply_vowel_sandhi("prati", "iti")
        self.assertEqual(res, "pratīti")

    def test_precedence_dirgha_over_guna(self):
        # rāma + aśva -> rāmāśva (MUST NOT produce rāmaśva via 6.1.87)
        res = apply_vowel_sandhi("rāma", "aśva")
        self.assertEqual(res, "rāmāśva")

    def test_precedence_vrddhi_over_guna(self):
        # kṛṣṇa + ekatvam -> kṛṣṇaikatvam (MUST NOT produce kṛṣṇekatvam)
        res = apply_vowel_sandhi("kṛṣṇa", "ekatvam")
        self.assertEqual(res, "kṛṣṇaikatvam")


if __name__ == "__main__":
    unittest.main()