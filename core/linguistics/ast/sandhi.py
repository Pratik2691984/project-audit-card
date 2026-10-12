"""
sandhi.py - Pāṇinian Ac-Sandhi (Vowel Sandhi) Transformation Engine
Implements rule dispatch with strict apavāda precedence and Tripādī optionality:
  1. 6.1.101 akaḥ savarṇe dīrghaḥ (homogeneous vowel lengthening)
  2. 6.1.109 eṅaḥ padāntād ati (pūrvarūpa sandhi with avagraha for padānta e/o + short a)
  3. 6.1.88  vṛddhir eci (vṛddhi substitution for a/ā + ec)
  4. 6.1.87  ād guṇaḥ (guṇa substitution with 1.1.51 uraṇ raparaḥ for a/ā + ac)
  5. 6.1.78  eco'yavāyāvaḥ (ec substitution: e->ay, o->av, ai->āy, au->āv before ac)
  6. 8.3.19  lopaḥ śākalyasya (optional elision of padānta y/v preceded by a/ā before aś)
  7. 6.1.77  iko yaṇaci (semi-vowel substitution for ik + ac)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Set, List


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
SUTRA_6_1_78 = SutraRef("6.1.78", "eco'yavāyāvaḥ", SutraType.VIDHI)
SUTRA_6_1_87 = SutraRef("6.1.87", "ād guṇaḥ", SutraType.VIDHI)
SUTRA_6_1_88 = SutraRef("6.1.88", "vṛddhir eci", SutraType.VIDHI)
SUTRA_6_1_101 = SutraRef("6.1.101", "akaḥ savarṇe dīrghaḥ", SutraType.VIDHI)
SUTRA_6_1_109 = SutraRef("6.1.109", "eṅaḥ padāntād ati", SutraType.VIDHI)
SUTRA_8_3_19 = SutraRef("8.3.19", "lopaḥ śākalyasya", SutraType.VIDHI)
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
    "ṛ": "ar",  # 1.1.51 uraṇ raparaḥ
    "ṝ": "ar",
    "ḷ": "al",
}

VRDDHI_MAP = {
    "e": "ai",
    "ai": "ai",
    "o": "au",
    "au": "au",
}

EC_AYAV_MAP = {
    "e": "ay",
    "o": "av",
    "ai": "āy",
    "au": "āv",
}

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
ENG_ALL = {"e", "o"}
# aś pratyāhāra (all vowels + voiced consonants)
AS_ALL = AC_ALL | {
    "h", "y", "v", "r", "l",
    "ñ", "m", "ṅ", "ṇ", "n",
    "jh", "bh",
    "gh", "ḍh", "dh",
    "j", "b", "g", "ḍ", "d"
}


def extract_final_vowel(s: str) -> Tuple[str, str]:
    """Extracts base stem and trailing vocalic phoneme (handling 'ai'/'au')."""
    if len(s) >= 2 and s[-2:] in ("ai", "au"):
        return s[:-2], s[-2:]
    return s[:-1], s[-1]


def apply_akah_savarne_dirghah(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.101: akaḥ savarṇe dīrghaḥ"""
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in AK_SAVARNA_MAP and c2 in AK_SAVARNA_MAP[c1]:
        res_vowel = SAVARNA_DIRGHA_OUT[c1]
        out = stem + res_vowel + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_101, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_101
    return None


def apply_enah_padantad_ati(left: str, right: str, is_padanta: bool = True, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.109: eṅaḥ padāntād ati"""
    if not left or not right or not is_padanta:
        return None
    _, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in ENG_ALL and c2 == "a":
        out = left + "'" + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_109, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_109
    return None


def apply_ecoyavayavah(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.78: eco'yavāyāvaḥ"""
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in EC_AYAV_MAP and c2 in AC_ALL:
        sub = EC_AYAV_MAP[c1]
        out = stem + sub + right
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_78, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_78
    return None


def apply_lopah_sakalyasya(left_transformed: str, right: str, is_padanta: bool = True, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """
    8.3.19: lopaḥ śākalyasya
    Optionally drops padānta y or v if preceded by a/ā and followed by a sound from 'aś'.
    Note: Asiddhatva prevents further vowel sandhi between the resulting hiatus.
    """
    if not left_transformed or not right or not is_padanta:
        return None

    if len(left_transformed) < 2:
        return None

    last_semi = left_transformed[-1]
    prev_vowel = left_transformed[-2]
    first_follow = right[0]

    if last_semi in ("y", "v") and prev_vowel in ("a", "ā") and first_follow in AS_ALL:
        # Elide trailing y or v, preserving word boundary space
        out = left_transformed[:-1] + " " + right
        if tree:
            tree.record_step(rule_applied=SUTRA_8_3_19, left_operand=left_transformed, right_operand=right, output=out)
        return out, SUTRA_8_3_19
    return None


def apply_vrddhir_eci(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.88: vṛddhir eci"""
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[:2] if len(right) >= 2 and right[:2] in ("ai", "au") else right[0]
    if c1 in ("a", "ā") and c2 in EC_ALL:
        res_vowel = VRDDHI_MAP[c2]
        slice_len = len(c2)
        out = stem + res_vowel + right[slice_len:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_88, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_88
    return None


def apply_ad_gunah(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.87: ād guṇaḥ (with 1.1.51 uraṇ raparaḥ)"""
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in ("a", "ā") and c2 in GUNA_MAP:
        res_sub = GUNA_MAP[c2]
        out = stem + res_sub + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_87, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_87
    return None


def apply_iko_yanaci(left: str, right: str, tree=None) -> Optional[Tuple[str, SutraRef]]:
    """6.1.77: iko yaṇaci"""
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in IK_YAN_MAP and c2 in AC_ALL:
        res_semi = IK_YAN_MAP[c1]
        out = stem + res_semi + right
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_77, left_operand=left, right_operand=right, output=out)
        return out, SUTRA_6_1_77
    return None


def apply_vowel_sandhi_variants(left: str, right: str, is_padanta: bool = True, tree=None) -> List[str]:
    """
    Returns all valid phonological derivations, including optional 8.3.19 variants.
    """
    if not left or not right:
        return [left + right]

    first_right = right[0]
    if first_right not in AC_ALL:
        return [left + right]

    # 1. 6.1.101 akaḥ savarṇe dīrghaḥ
    dirgha_res = apply_akah_savarne_dirghah(left, right, tree=tree)
    if dirgha_res:
        return [dirgha_res[0]]

    stem, last_vowel = extract_final_vowel(left)

    # 2. 6.1.109 eṅaḥ padāntād ati
    if is_padanta and last_vowel in ENG_ALL and first_right == "a":
        purva_res = apply_enah_padantad_ati(left, right, is_padanta=is_padanta, tree=tree)
        if purva_res:
            return [purva_res[0]]

    # 3 & 4. a/ā branches: 6.1.88 or 6.1.87
    if last_vowel in ("a", "ā"):
        right_vowel = right[:2] if len(right) >= 2 and right[:2] in ("ai", "au") else right[0]
        if right_vowel in EC_ALL:
            vrddhi_res = apply_vrddhir_eci(left, right, tree=tree)
            if vrddhi_res:
                return [vrddhi_res[0]]
        else:
            guna_res = apply_ad_gunah(left, right, tree=tree)
            if guna_res:
                return [guna_res[0]]

    # 5. 6.1.78 eco'yavāyāvaḥ (+ optional 8.3.19 lopaḥ śākalyasya)
    if last_vowel in EC_ALL:
        sub = EC_AYAV_MAP[last_vowel]
        prakriya_left = stem + sub
        general_out = prakriya_left + right

        if is_padanta:
            lopa_res = apply_lopah_sakalyasya(prakriya_left, right, is_padanta=True, tree=tree)
            if lopa_res:
                # Returns [Śākalya elision variant, Pāṇinian joined variant]
                return [lopa_res[0], general_out]

        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_78, left_operand=left, right_operand=right, output=general_out)
        return [general_out]

    # 6. 6.1.77 iko yaṇaci
    if last_vowel in IK_YAN_MAP:
        yan_res = apply_iko_yanaci(left, right, tree=tree)
        if yan_res:
            return [yan_res[0]]

    return [left + right]


def apply_vowel_sandhi(left: str, right: str, is_padanta: bool = True, tree=None) -> str:
    """Standard deterministic dispatcher returning the primary phonological output."""
    variants = apply_vowel_sandhi_variants(left, right, is_padanta=is_padanta, tree=tree)
    # When lopaḥ śākalyasya fires, variant[0] is Śākalya lopa (vana āste); variant[1] is vanayāste
    return variants[0]


# Aliases for package re-exports
apply_guna = apply_ad_gunah
apply_vrddhi = apply_vrddhir_eci
apply_yan = apply_iko_yanaci
apply_dirgha = apply_akah_savarne_dirghah
apply_purvarupa = apply_enah_padantad_ati
apply_ayavayavah = apply_ecoyavayavah
apply_sakalyalopa = apply_lopah_sakalyasya