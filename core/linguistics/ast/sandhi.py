"""
core/linguistics/ast/sandhi.py
Foundational Pāṇinian Sandhi transformations utilizing Śivasūtra pratyāhāras.
"""
from __future__ import annotations
from typing import Optional, Tuple
from core.linguistics.ast.sivasutras import expand_pratyahara
from core.linguistics.ast.nodes import (
    SutraRef, SutraType, SutraApplication, DerivationTree
)

SUTRA_6_1_77 = SutraRef(
    number="6.1.77",
    name="iko yaṇaci",
    sutra_type=SutraType.VIDHI,
)

SUTRA_6_1_87 = SutraRef(
    number="6.1.87",
    name="ād guṇaḥ",
    sutra_type=SutraType.VIDHI,
)

SUTRA_6_1_88 = SutraRef(
    number="6.1.88",
    name="vṛddhir eci",
    sutra_type=SutraType.VIDHI,
)

# 1.1.50 sthāne 'ntaratamaḥ: maps ik vowels to homorganic yaṇ semivowels
IK_YAN_MAP = {
    "i": "y", "ī": "y",
    "u": "v", "ū": "v",
    "ṛ": "r", "ṝ": "r",
    "ḷ": "l",
}

# 6.1.87 ād guṇaḥ (combined with 1.1.51 uraṇ raparaḥ for ṛ/ḷ)
GUNA_MAP = {
    "i": "e", "ī": "e",
    "u": "o", "ū": "o",
    "ṛ": "ar", "ṝ": "ar",
    "ḷ": "al",
}

# 6.1.88 vṛddhir eci
VRDDHI_ECI_MAP = {
    "e": "ai",
    "ai": "ai",
    "o": "au",
    "au": "au",
}

A_VOWELS = {"a", "ā"}


def apply_iko_yanaci(left: str, right: str, tree: Optional[DerivationTree] = None) -> Tuple[str, DerivationTree]:
    """
    Applies Aṣṭādhyāyī 6.1.77: iko yaṇaci.
    Replaces a terminal ik vowel of `left` with its corresponding yaṇ semivowel
    when followed by an initial ac vowel of `right`.
    """
    if tree is None:
        tree = DerivationTree(initial_input=f"{left}+{right}")

    if not left or not right:
        return f"{left}{right}", tree

    last_left = left[-1]
    first_right = right[0]

    ac_vowels = set(expand_pratyahara("ac")) | {"ā", "ī", "ū", "ṝ"}

    if last_left in IK_YAN_MAP and first_right in ac_vowels:
        yan_replacement = IK_YAN_MAP[last_left]
        new_state = f"{left[:-1]}{yan_replacement}{right}"

        application = SutraApplication(
            sutra=SUTRA_6_1_77,
            index=len(left) - 1,
            input_slice=f"{last_left}+{first_right}",
            output_slice=f"{yan_replacement}{first_right}",
            metadata={"source_vowel": last_left, "follower": first_right},
        )
        tree.add_step(application, new_state)
        return new_state, tree

    return f"{left}{right}", tree


def apply_guna(left: str, right: str, tree: Optional[DerivationTree] = None) -> Tuple[str, DerivationTree]:
    """
    Applies Aṣṭādhyāyī 6.1.87: ād guṇaḥ.
    Replaces pre-boundary a/ā and post-boundary ik vowel with their corresponding
    guṇa single substitute (ekādeśa).
    """
    if tree is None:
        tree = DerivationTree(initial_input=f"{left}+{right}")

    if not left or not right:
        return f"{left}{right}", tree

    last_left = left[-1]
    first_right = right[0]

    if last_left in A_VOWELS and first_right in GUNA_MAP:
        replacement = GUNA_MAP[first_right]
        new_state = f"{left[:-1]}{replacement}{right[1:]}"

        application = SutraApplication(
            sutra=SUTRA_6_1_87,
            index=len(left) - 1,
            input_slice=f"{last_left}+{first_right}",
            output_slice=replacement,
            metadata={"left_vowel": last_left, "right_vowel": first_right},
        )
        tree.add_step(application, new_state)
        return new_state, tree

    return f"{left}{right}", tree


def apply_vrddhi(left: str, right: str, tree: Optional[DerivationTree] = None) -> Tuple[str, DerivationTree]:
    """
    Applies Aṣṭādhyāyī 6.1.88: vṛddhir eci.
    Replaces pre-boundary a/ā and post-boundary ec diphthong (e, o, ai, au)
    with their corresponding vṛddhi single substitute (ekādeśa).
    """
    if tree is None:
        tree = DerivationTree(initial_input=f"{left}+{right}")

    if not left or not right:
        return f"{left}{right}", tree

    last_left = left[-1]
    first_right = right[0]

    ec_diphthongs = set(expand_pratyahara("ec"))  # ['e', 'o', 'ai', 'au']

    if last_left in A_VOWELS and first_right in ec_diphthongs and first_right in VRDDHI_ECI_MAP:
        replacement = VRDDHI_ECI_MAP[first_right]
        new_state = f"{left[:-1]}{replacement}{right[1:]}"

        application = SutraApplication(
            sutra=SUTRA_6_1_88,
            index=len(left) - 1,
            input_slice=f"{last_left}+{first_right}",
            output_slice=replacement,
            metadata={"left_vowel": last_left, "right_vowel": first_right},
        )
        tree.add_step(application, new_state)
        return new_state, tree

    return f"{left}{right}", tree