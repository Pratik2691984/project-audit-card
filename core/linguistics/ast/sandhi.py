"""
sandhi.py - Pāṇinian Ac-Sandhi (Vowel Sandhi) Transformation Engine
Implements rule dispatch with strict apavāda precedence:
  1. 6.1.101 akaḥ savarṇe dīrghaḥ (homogeneous vowel lengthening)
  2. 6.1.88  vṛddhir eci (vṛddhi substitution)
  3. 6.1.87  ād guṇaḥ (guṇa substitution with 1.1.51 uran raparaḥ)
  4. 6.1.77  iko yaṇaci (semi-vowel substitution)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Set


class SutraType(Enum):
    SAMJNA = "saṃjñā"
    PARIBHASA = "paribhāṣā"
    VIDHI = "vidhi"
    NIYAMA = "niyama"
    ADHIKARA = "adhikāra"
    ATIDESHA = "atideśa"


@dataclass(frozen=True)
class SutraRef:
    number: str
    name: str
    sutra_type: SutraType


# Sūtra References
SUTRA_6_1_77 = SutraRef("6.1.77", "iko yaṇaci", SutraType.VIDHI)
SUTRA_6_1_87 = SutraRef("6.1.87", "ād guṇaḥ", SutraType.VIDHI)
SUTRA_6_1_88 = SutraRef("6.1.88", "vṛddhir eci", SutraType.VIDHI)
SUTRA_6_1_101 = SutraRef("6.1.101", "akaḥ savarṇe dīrghaḥ", SutraType.VIDHI)
SUTRA_1_1_51 = SutraRef("1.1.51", "uraṇ raparaḥ", SutraType.PARIBHASA)


# Phoneme sets & mappings
IK_YAN_MAP = {
    "i": "y",
    "ī": "y",
    "u": "v",
    "ū": "v",
    "ṛ": "r",
    "ṝ": "r",
    "ḷ": "l",
}

GUNA_MAP = {
    "i": "e",
    "ī": "e",
    "u": "o",
    "ū": "o",
    "ṛ": "ar",  # 1.1.51 uran raparaḥ: a + r
    "ṝ": "ar",
    "ḷ": "al",
}

VRDDHI_MAP = {
    "e": "ai",
    "ai": "ai",
    "o": "au",
    "au": "au",
}

# Homogeneous sets per 6.1.101 + Kātyāyana Vārttika for ṛ-ḷ sāvarṇya
AK_SAVARNA_MAP = {
    "a": {"a", "ā"},
    "ā": {"a", "ā"},
    "i": {"i", "ī"},
    "ī": {"i", "ī"},
    "u": {"u", "ū"},
    "ū": {"u", "ū"},
    "ṛ": {"ṛ", "ṝ", "ḷ"},
    "ṝ": {"ṛ", "ṝ", "ḷ"},
    "ḷ": {"ṛ", "ṝ", "ḷ"},
}

SAVARNA_DIRGHA_OUT = {
    "a": "ā",
    "ā": "ā",
    "i": "ī",
    "ī": "ī",
    "u": "ū",
    "ū": "ū",
    "ṛ": "ṝ",
    "ṝ": "ṝ",
    "ḷ": "ṝ",
}

AC_ALL = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "o", "ai", "au"}
EC_ALL = {"e", "o", "ai", "au"}


def apply_akah_savarne_dirghah(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.101: akaḥ savarṇe dīrghaḥ"""
    if not left or not right:
        return None
    c1, c2 = left[-1], right[0]
    if c1 in AK_SAVARNA_MAP and c2 in AK_SAVARNA_MAP[c1]:
        res_vowel = SAVARNA_DIRGHA_OUT[c1]
        out = left[:-1] + res_vowel + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_101, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_101
    return None


def apply_vrddhir_eci(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.88: vṛddhir eci"""
    if not left or not right:
        return None
    c1, c2 = left[-1], right[0]
    if c1 in ("a", "ā") and c2 in EC_ALL:
        res_vowel = VRDDHI_MAP[c2]
        out = left[:-1] + res_vowel + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_88, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_88
    return None


def apply_ad_gunah(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.87: ād guṇaḥ (with 1.1.51 uraṇ raparaḥ)"""
    if not left or not right:
        return None
    c1, c2 = left[-1], right[0]
    if c1 in ("a", "ā") and c2 in GUNA_MAP:
        res_sub = GUNA_MAP[c2]
        out = left[:-1] + res_sub + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_87, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_87
    return None


def apply_iko_yanaci(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.77: iko yaṇaci"""
    if not left or not right:
        return None
    c1, c2 = left[-1], right[0]
    if c1 in IK_YAN_MAP and c2 in AC_ALL:
        res_semi = IK_YAN_MAP[c1]
        out = left[:-1] + res_semi + right
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_77, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_77
    return None


def apply_vowel_sandhi(left: str, right: str, tree=None) -> str:
    """
    Unified Ac-Sandhi Dispatcher with Pāṇinian apavāda precedence:
      1. Savarṇa Dīrgha (6.1.101) - exception to both yaṇ and guṇa
      2. Vṛddhir eci (6.1.88)     - exception to guṇa when followed by ec
      3. Ād guṇaḥ (6.1.87)        - general replacement for a/ā + ac
      4. Iko yaṇaci (6.1.77)      - replacement for ik + ac
    """
    if not left or not right:
        return left + right

    first_right = right[0]
    if first_right not in AC_ALL:
        return left + right

    # 1. 6.1.101 akaḥ savarṇe dīrghaḥ
    dirgha_res = apply_akah_savarne_dirghah(left, right, tree=tree)
    if dirgha_res:
        return dirgha_res[0]

    last_left = left[-1]

    # 2 & 3. a/ā branches: 6.1.88 or 6.1.87
    if last_left in ("a", "ā"):
        if first_right in EC_ALL:
            vrddhi_res = apply_vrddhir_eci(left, right, tree=tree)
            if vrddhi_res:
                return vrddhi_res[0]
        else:
            guna_res = apply_ad_gunah(left, right, tree=tree)
            if guna_res:
                return guna_res[0]

    # 4. 6.1.77 iko yaṇaci
    if last_left in IK_YAN_MAP:
        yan_res = apply_iko_yanaci(left, right, tree=tree)
        if yan_res:
            return yan_res[0]

    return left + right


# Aliases for package re-exports expected by core.linguistics.ast.__init__
apply_guna = apply_ad_gunah
apply_vrddhi = apply_vrddhir_eci
apply_yan = apply_iko_yanaci
apply_dirgha = apply_akah_savarne_dirghah