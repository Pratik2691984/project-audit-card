"""
sandhi.py - Pāṇinian Sandhi Engine
Covers:
  - Ac-Sandhi (6.1.101, 6.1.109, 6.1.88, 6.1.87, 6.1.78, 6.1.77, 8.3.19)
  - 6.1.84 ekaḥ pūrvaparayoḥ (adhikāra single substitution provenance)
  - Hal-Sandhi (8.4.40 stoḥ ścunā ścuḥ, 8.4.41 ṣṭunā ṣṭuḥ)
  - Visarga-Sandhi (8.2.66 sasajuṣo ruḥ, 6.1.113 ato ror aplutād aplute,
                    6.1.114 haśi ca, 8.3.17 bhobhagoaghopūrvasya yo'śi)
"""

from typing import Optional, Tuple, List
from core.linguistics.ast.nodes import (
    SutraRef,
    SutraType,
    DerivationTree,
    ADHIKARA_EKAH_PURVAPARAYOH,
)

# Sūtra Constants
SUTRA_6_1_77 = SutraRef("6.1.77", "iko yaṇaci", SutraType.VIDHI)
SUTRA_6_1_78 = SutraRef("6.1.78", "eco'yavāyāvaḥ", SutraType.VIDHI)
SUTRA_6_1_84 = ADHIKARA_EKAH_PURVAPARAYOH
SUTRA_6_1_87 = SutraRef("6.1.87", "ād guṇaḥ", SutraType.VIDHI)
SUTRA_6_1_88 = SutraRef("6.1.88", "vṛddhir eci", SutraType.VIDHI)
SUTRA_6_1_101 = SutraRef("6.1.101", "akaḥ savarṇe dīrghaḥ", SutraType.VIDHI)
SUTRA_6_1_109 = SutraRef("6.1.109", "eṅaḥ padāntād ati", SutraType.VIDHI)
SUTRA_6_1_113 = SutraRef("6.1.113", "ato ror aplutād aplute", SutraType.VIDHI)
SUTRA_6_1_114 = SutraRef("6.1.114", "haśi ca", SutraType.VIDHI)
SUTRA_8_2_66 = SutraRef("8.2.66", "sasajuṣo ruḥ", SutraType.VIDHI)
SUTRA_8_3_17 = SutraRef("8.3.17", "bhobhagoaghopūrvasya yo'śi", SutraType.VIDHI)
SUTRA_8_3_19 = SutraRef("8.3.19", "lopaḥ śākalyasya", SutraType.VIDHI)
SUTRA_8_4_40 = SutraRef("8.4.40", "stoḥ ścunā ścuḥ", SutraType.VIDHI)
SUTRA_8_4_41 = SutraRef("8.4.41", "ṣṭunā ṣṭuḥ", SutraType.VIDHI)
SUTRA_1_1_51 = SutraRef("1.1.51", "uraṇ raparaḥ", SutraType.PARIBHASA)

# Phoneme mappings
IK_YAN_MAP = {"i": "y", "ī": "y", "u": "v", "ū": "v", "ṛ": "r", "ṝ": "r", "ḷ": "l"}
GUNA_MAP = {"i": "e", "ī": "e", "u": "o", "ū": "o", "ṛ": "ar", "ṝ": "ar", "ḷ": "al"}
VRDDHI_MAP = {"e": "ai", "ai": "ai", "o": "au", "au": "au"}
EC_AYAV_MAP = {"e": "ay", "o": "av", "ai": "āy", "au": "āv"}

AK_SAVARNA_MAP = {
    "a": {"a", "ā"}, "ā": {"a", "ā"},
    "i": {"i", "ī"}, "ī": {"i", "ī"},
    "u": {"u", "ū"}, "ū": {"u", "ū"},
    "ṛ": {"ṛ", "ṝ", "ḷ"}, "ṝ": {"ṛ", "ṝ", "ḷ"}, "ḷ": {"ṛ", "ṝ", "ḷ"}
}
SAVARNA_DIRGHA_OUT = {
    "a": "ā", "ā": "ā", "i": "ī", "ī": "ī", "u": "ū", "ū": "ū",
    "ṛ": "ṝ", "ṝ": "ṝ", "ḷ": "ṝ"
}

AC_ALL = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "o", "ai", "au"}
EC_ALL = {"e", "o", "ai", "au"}
ENG_ALL = {"e", "o"}
HASH_VOICED_CONS = {
    "h", "y", "v", "r", "l",
    "ñ", "m", "ṅ", "ṇ", "n",
    "jh", "bh", "gh", "ḍh", "dh",
    "j", "b", "g", "ḍ", "d"
}
AS_ALL = AC_ALL | HASH_VOICED_CONS

# Hal-Sandhi: Ścutva & Ṣṭutva Maps (s, t, th, d, dh, n)
STU_PHONEMES = ("th", "dh", "s", "t", "d", "n")  # ordered multi-char first
SCU_REPLACE = {"s": "ś", "t": "c", "th": "ch", "d": "j", "dh": "jh", "n": "ñ"}
SCU_TRIGGER = {"ś", "c", "ch", "j", "jh", "ñ"}

SHTU_REPLACE = {"s": "ṣ", "t": "ṭ", "th": "ṭh", "d": "ḍ", "dh": "ḍh", "n": "ṇ"}
SHTU_TRIGGER = {"ṣ", "ṭ", "ṭh", "ḍ", "ḍh", "ṇ"}


def extract_final_vowel(s: str) -> Tuple[str, str]:
    if len(s) >= 2 and s[-2:] in ("ai", "au"):
        return s[:-2], s[-2:]
    return s[:-1], s[-1]


# ---------------------------------------------------------------------------
# Ac-Sandhi (Governed by 6.1.84 ekaḥ pūrvaparayoḥ where applicable)
# ---------------------------------------------------------------------------

def apply_akah_savarne_dirghah(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in AK_SAVARNA_MAP and c2 in AK_SAVARNA_MAP[c1]:
        res_vowel = SAVARNA_DIRGHA_OUT[c1]
        out = stem + res_vowel + right[1:]
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_101,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=SUTRA_6_1_84,
                is_ekadesha=True,
            )
        return out, SUTRA_6_1_101
    return None


def apply_enah_padantad_ati(left: str, right: str, is_padanta: bool = True, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right or not is_padanta:
        return None
    _, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in ENG_ALL and c2 == "a":
        out = left + "'" + right[1:]
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_109,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=SUTRA_6_1_84,
                is_ekadesha=True,
            )
        return out, SUTRA_6_1_109
    return None


def apply_vrddhir_eci(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[:2] if len(right) >= 2 and right[:2] in ("ai", "au") else right[0]
    if c1 in ("a", "ā") and c2 in EC_ALL:
        res_vowel = VRDDHI_MAP[c2]
        out = stem + res_vowel + right[len(c2):]
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_88,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=SUTRA_6_1_84,
                is_ekadesha=True,
            )
        return out, SUTRA_6_1_88
    return None


def apply_ad_gunah(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in ("a", "ā") and c2 in GUNA_MAP:
        res_sub = GUNA_MAP[c2]
        out = stem + res_sub + right[1:]
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_87,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=SUTRA_6_1_84,
                is_ekadesha=True,
            )
        return out, SUTRA_6_1_87
    return None


def apply_ecoyavayavah(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in EC_AYAV_MAP and c2 in AC_ALL:
        sub = EC_AYAV_MAP[c1]
        out = stem + sub + right
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_78,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=None,
                is_ekadesha=False,
            )
        return out, SUTRA_6_1_78
    return None


def apply_lopah_sakalyasya(left_transformed: str, right: str, is_padanta: bool = True, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left_transformed or not right or not is_padanta or len(left_transformed) < 2:
        return None
    last_semi = left_transformed[-1]
    prev_vowel = left_transformed[-2]
    first_follow = right[0]
    if last_semi in ("y", "v") and prev_vowel in ("a", "ā") and first_follow in AS_ALL:
        out = left_transformed[:-1] + " " + right
        if tree:
            tree.record_step(
                rule_applied=SUTRA_8_3_19,
                left_operand=left_transformed,
                right_operand=right,
                output=out,
                governing_adhikara=None,
                is_ekadesha=False,
            )
        return out, SUTRA_8_3_19
    return None


def apply_iko_yanaci(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    if not left or not right:
        return None
    stem, c1 = extract_final_vowel(left)
    c2 = right[0]
    if c1 in IK_YAN_MAP and c2 in AC_ALL:
        res_semi = IK_YAN_MAP[c1]
        out = stem + res_semi + right
        if tree:
            tree.record_step(
                rule_applied=SUTRA_6_1_77,
                left_operand=left,
                right_operand=right,
                output=out,
                governing_adhikara=None,
                is_ekadesha=False,
            )
        return out, SUTRA_6_1_77
    return None


def apply_vowel_sandhi_variants(left: str, right: str, is_padanta: bool = True, tree: Optional[DerivationTree] = None) -> List[str]:
    if not left or not right:
        return [left + right]
    first_right = right[0]
    if first_right not in AC_ALL:
        return [left + right]

    dirgha_res = apply_akah_savarne_dirghah(left, right, tree=tree)
    if dirgha_res:
        return [dirgha_res[0]]

    stem, last_vowel = extract_final_vowel(left)

    if is_padanta and last_vowel in ENG_ALL and first_right == "a":
        purva_res = apply_enah_padantad_ati(left, right, is_padanta=is_padanta, tree=tree)
        if purva_res:
            return [purva_res[0]]

    if last_vowel in ("a", "ā"):
        right_vowel = right[:2] if len(right) >= 2 and right[:2] in ("ai", "au") else right[0]
        if right_vowel in EC_ALL:
            vrddhi_res = apply_vrddhir_eci(left, right, tree=tree)
            if vrddhi_res:
                return [vrddhi_res[0]]
        else:
            guna_res = apply_ad_gunah(left, right, tree=tree)
            if guna_res:
                return guna_res[0]

    if last_vowel in EC_ALL:
        sub = EC_AYAV_MAP[last_vowel]
        prakriya_left = stem + sub
        general_out = prakriya_left + right
        if is_padanta:
            lopa_res = apply_lopah_sakalyasya(prakriya_left, right, is_padanta=True, tree=tree)
            if lopa_res:
                return [lopa_res[0], general_out]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_78, left_operand=left, right_operand=right, output=general_out)
        return [general_out]

    if last_vowel in IK_YAN_MAP:
        yan_res = apply_iko_yanaci(left, right, tree=tree)
        if yan_res:
            return [yan_res[0]]

    return [left + right]


def apply_vowel_sandhi(left: str, right: str, is_padanta: bool = True, tree: Optional[DerivationTree] = None) -> str:
    variants = apply_vowel_sandhi_variants(left, right, is_padanta=is_padanta, tree=tree)
    return variants[0]


# ---------------------------------------------------------------------------
# Hal-Sandhi: 8.4.40 Ścutva & 8.4.41 Ṣṭutva
# ---------------------------------------------------------------------------

def apply_stoh_scuna_scuh(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    """8.4.40: stoḥ ścunā ścuḥ (s/tu replaced by ś/cu when in contact with ś/cu)."""
    if not left or not right:
        return None

    # Check forward contact: left ends in 'stu' and right starts with 'ścu'
    for ph in STU_PHONEMES:
        if left.endswith(ph):
            # check trigger on right
            first_right = right[:2] if len(right) >= 2 and right[:2] in ("ch", "jh") else right[0]
            if first_right in SCU_TRIGGER:
                stem = left[:-len(ph)]
                rep = SCU_REPLACE[ph]
                out = stem + rep + right
                if tree:
                    tree.record_step(rule_applied=SUTRA_8_4_40, left_operand=left, right_operand=right, output=out)
                return out, SUTRA_8_4_40

    # Check backward contact: left ends in 'ścu' and right starts with 'stu'
    for trigger in ("ch", "jh", "ś", "c", "j", "ñ"):
        if left.endswith(trigger):
            for ph in STU_PHONEMES:
                if right.startswith(ph):
                    rep = SCU_REPLACE[ph]
                    out = left + rep + right[len(ph):]
                    if tree:
                        tree.record_step(rule_applied=SUTRA_8_4_40, left_operand=left, right_operand=right, output=out)
                    return out, SUTRA_8_4_40
    return None


def apply_stuna_stuh(left: str, right: str, tree: Optional[DerivationTree] = None) -> Optional[Tuple[str, SutraRef]]:
    """8.4.41: ṣṭunā ṣṭuḥ (s/tu replaced by ṣ/ṭu when in contact with ṣ/ṭu)."""
    if not left or not right:
        return None

    # Forward contact
    for ph in STU_PHONEMES:
        if left.endswith(ph):
            first_right = right[:2] if len(right) >= 2 and right[:2] in ("ṭh", "ḍh") else right[0]
            if first_right in SHTU_TRIGGER:
                stem = left[:-len(ph)]
                rep = SHTU_REPLACE[ph]
                out = stem + rep + right
                if tree:
                    tree.record_step(rule_applied=SUTRA_8_4_41, left_operand=left, right_operand=right, output=out)
                return out, SUTRA_8_4_41

    # Backward contact
    for trigger in ("ṭh", "ḍh", "ṣ", "ṭ", "ḍ", "ṇ"):
        if left.endswith(trigger):
            for ph in STU_PHONEMES:
                if right.startswith(ph):
                    rep = SHTU_REPLACE[ph]
                    out = left + rep + right[len(ph):]
                    if tree:
                        tree.record_step(rule_applied=SUTRA_8_4_41, left_operand=left, right_operand=right, output=out)
                    return out, SUTRA_8_4_41
    return None


def apply_hal_sandhi(left: str, right: str, tree: Optional[DerivationTree] = None) -> str:
    """Consonant sandhi dispatcher."""
    res_scu = apply_stoh_scuna_scuh(left, right, tree=tree)
    if res_scu:
        return res_scu[0]

    res_shtu = apply_stuna_stuh(left, right, tree=tree)
    if res_shtu:
        return res_shtu[0]

    return left + right


# ---------------------------------------------------------------------------
# Visarga-Sandhi: 8.2.66, 6.1.113, 6.1.114, 8.3.17
# ---------------------------------------------------------------------------

def apply_visarga_sandhi(left: str, right: str, is_padanta: bool = True, tree: Optional[DerivationTree] = None) -> str:
    """
    Visarga derivation pipeline:
      1. 8.2.66 sasajuṣo ruḥ: terminal -s or -ḥ turns into 'r' (ru) at word-boundary.
      2. 6.1.113 ato ror aplutād aplute: a + ru + a -> a + u + a -> o'
      3. 6.1.114 haśi ca: a + ru + haś -> a + u + haś -> o + haś
      4. 8.3.17 bhobhagoaghopūrvasya yo'śi: (bho/bhago/agho/ā) + ru + aś -> y-lopa
    """
    if not left or not right:
        return left + right

    # Normalize final s or visarga ḥ to padānta 'ru' via 8.2.66
    if not (left.endswith("ḥ") or left.endswith("s")):
        return left + right

    # Base stem prior to terminal visarga/s
    stem = left[:-1]
    if tree:
        tree.record_step(
            rule_applied=SUTRA_8_2_66,
            left_operand=left,
            right_operand=right,
            output=stem + "r " + right,
            metadata={"intermediate": "ru"}
        )

    first_right = right[0]

    # Rule 6.1.113: ato ror aplutād aplute (short a + ru + short a -> o')
    if stem.endswith("a") and not stem.endswith("ā") and first_right == "a":
        base = stem[:-1] + "o"
        out = base + "'" + right[1:]
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_113, left_operand=stem + "r", right_operand=right, output=out)
        return out

    # Rule 6.1.114: haśi ca (short a + ru + voiced consonant haś -> o + consonant)
    if stem.endswith("a") and not stem.endswith("ā") and first_right in HASH_VOICED_CONS:
        base = stem[:-1] + "o"
        out = base + " " + right
        if tree:
            tree.record_step(rule_applied=SUTRA_6_1_114, left_operand=stem + "r", right_operand=right, output=out)
        return out

    # Rule 8.3.17: bhobhagoaghopūrvasya yo'śi (bho/bhago/agho or ā + ru + aś -> y -> lopa)
    if (stem in ("bho", "bhago", "agho") or stem.endswith("ā")) and first_right in AS_ALL:
        out = stem + " " + right
        if tree:
            tree.record_step(rule_applied=SUTRA_8_3_17, left_operand=stem + "r", right_operand=right, output=out)
        return out

    # Default fallback: ru remains as 'r' before vowels
    if first_right in AC_ALL:
        out = stem + "r" + right
        return out

    return left + " " + right


# Aliases for package re-exports
apply_guna = apply_ad_gunah
apply_vrddhi = apply_vrddhir_eci
apply_yan = apply_iko_yanaci
apply_dirgha = apply_akah_savarne_dirghah
apply_purvarupa = apply_enah_padantad_ati
apply_ayavayavah = apply_ecoyavayavah
apply_sakalyalopa = apply_lopah_sakalyasya
apply_scutva = apply_stoh_scuna_scuh
apply_shtutva = apply_stuna_stuh