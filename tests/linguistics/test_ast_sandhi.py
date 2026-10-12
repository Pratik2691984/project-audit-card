import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.linguistics.ast.nodes import DerivationTree, SutraType
from core.linguistics.ast.sandhi import (
    apply_iko_yanaci,
    apply_guna,
    apply_vrddhi,
    SUTRA_6_1_77,
    SUTRA_6_1_87,
    SUTRA_6_1_88,
)


class TestAstSandhi(unittest.TestCase):

    def test_iko_yanaci_i_to_y(self):
        result, tree = apply_iko_yanaci("iti", "api")
        self.assertEqual(result, "ityapi")
        self.assertEqual(tree.current_state, "ityapi")
        self.assertEqual(len(tree.steps), 1)

        step = tree.steps[0]
        self.assertEqual(step.rule_applied.sutra.number, "6.1.77")
        self.assertEqual(step.rule_applied.sutra.name, "iko yaṇaci")
        self.assertEqual(step.rule_applied.sutra.sutra_type, SutraType.VIDHI)
        self.assertEqual(step.rule_applied.input_slice, "i+a")
        self.assertEqual(step.rule_applied.output_slice, "ya")

    def test_iko_yanaci_u_to_v(self):
        result, tree = apply_iko_yanaci("madhu", "ari")
        self.assertEqual(result, "madhvari")
        self.assertEqual(tree.current_state, "madhvari")

        step = tree.steps[0]
        self.assertEqual(step.rule_applied.input_slice, "u+a")
        self.assertEqual(step.rule_applied.output_slice, "va")

    def test_iko_yanaci_r_to_r(self):
        result, tree = apply_iko_yanaci("dhātṛ", "aṃśa")
        self.assertEqual(result, "dhātraṃśa")

        step = tree.steps[0]
        self.assertEqual(step.rule_applied.input_slice, "ṛ+a")
        self.assertEqual(step.rule_applied.output_slice, "ra")

    def test_iko_yanaci_no_trigger_consonant(self):
        result, tree = apply_iko_yanaci("iti", "gacchati")
        self.assertEqual(result, "itigacchati")
        self.assertEqual(len(tree.steps), 0)

    def test_ad_gunah_a_plus_i(self):
        # deva + indra -> devendra
        result, tree = apply_guna("deva", "indra")
        self.assertEqual(result, "devendra")
        self.assertEqual(len(tree.steps), 1)
        step = tree.steps[0]
        self.assertEqual(step.rule_applied.sutra.number, "6.1.87")
        self.assertEqual(step.rule_applied.input_slice, "a+i")
        self.assertEqual(step.rule_applied.output_slice, "e")

    def test_ad_gunah_a_plus_u(self):
        # sūrya + udaya -> sūryodaya
        result, tree = apply_guna("sūrya", "udaya")
        self.assertEqual(result, "sūryodaya")
        self.assertEqual(tree.steps[0].rule_applied.output_slice, "o")

    def test_ad_gunah_rapara(self):
        # mahā + ṛṣi -> maharṣi (via 1.1.51 uraṇ raparaḥ)
        result, tree = apply_guna("mahā", "ṛṣi")
        self.assertEqual(result, "maharṣi")
        self.assertEqual(tree.steps[0].rule_applied.output_slice, "ar")

    def test_vrddhir_eci_a_plus_e(self):
        # kṛṣṇa + ekatvam -> kṛṣṇaikatvam
        result, tree = apply_vrddhi("kṛṣṇa", "ekatvam")
        self.assertEqual(result, "kṛṣṇaikatvam")
        self.assertEqual(len(tree.steps), 1)
        step = tree.steps[0]
        self.assertEqual(step.rule_applied.sutra.number, "6.1.88")
        self.assertEqual(step.rule_applied.input_slice, "a+e")
        self.assertEqual(step.rule_applied.output_slice, "ai")

    def test_vrddhir_eci_a_plus_o(self):
        # gaṅgā + oghaḥ -> gaṅgaughaḥ
        result, tree = apply_vrddhi("gaṅgā", "oghaḥ")
        self.assertEqual(result, "gaṅgaughaḥ")
        self.assertEqual(tree.steps[0].rule_applied.output_slice, "au")


if __name__ == "__main__":
    unittest.main()