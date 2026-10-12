"""
engine.py - Pāṇinian Prakriyā (Derivation) Engine
Executes step-by-step morphosyntactic derivation trees for tiṅanta forms.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict

from core.linguistics.ast.nodes import (
    SutraRef,
    SutraType,
    DerivationTree,
)
from core.linguistics.ast.sandhi import (
    apply_ad_gunah,
    apply_ecoyavayavah,
)

# Canonical Sūtras for Lakāra and Tiṅ-derivation
SUTRA_1_3_1 = SutraRef("1.3.1", "bhūvādayo dhātavaḥ", SutraType.SAMJNA)
SUTRA_1_3_3 = SutraRef("1.3.3", "halantyam", SutraType.SAMJNA)
SUTRA_1_3_8 = SutraRef("1.3.8", "laśakvataddhite", SutraType.SAMJNA)
SUTRA_1_3_9 = SutraRef("1.3.9", "tasya lopaḥ", SutraType.VIDHI)
SUTRA_3_1_68 = SutraRef("3.1.68", "kartari śap", SutraType.VIDHI)
SUTRA_3_2_123 = SutraRef("3.2.123", "vartamāne laṭ", SutraType.VIDHI)
SUTRA_3_4_78 = SutraRef("3.4.78", "tiptasjhi...", SutraType.VIDHI)
SUTRA_3_4_113 = SutraRef("3.4.113", "tiṅśit sārvadhātukam", SutraType.SAMJNA)
SUTRA_7_3_84 = SutraRef("7.3.84", "sārvadhātukārdhadhātukayoḥ", SutraType.VIDHI)


class Prayoga(Enum):
    KARTARI = "kartari"
    KARMANI = "karmaṇi"
    BHAVE = "bhāve"


class Gana(Enum):
    BHVADI = 1
    ADADI = 2
    JUHOTYADI = 3
    DIVADI = 4
    SVADI = 5
    TUDADI = 6
    RUDHADI = 7
    TANADI = 8
    KRYADI = 9
    CURADI = 10


# Canonical mapping for 3.4.78 Parasmaipada
PARASMAIPADA_MAP = {
    (3, 1): "tip",
    (3, 2): "tas",
    (3, 3): "jhi",
    (2, 1): "sip",
    (2, 2): "thas",
    (2, 3): "tha",
    (1, 1): "mip",
    (1, 2): "vas",
    (1, 3): "mas",
}


def apply_it_lopa(pratyaya: str, is_vaddi: bool = False) -> str:
    """Strips canonical it markers per 1.3.3 (halantyam) and 1.3.8 (laśakvataddhite)."""
    res = pratyaya
    # Halantyam p-kāra lopa (e.g., tip -> ti, śap -> śa)
    if res.endswith("p"):
        res = res[:-1]
    # Laśakvataddhite ś-kāra lopa (e.g., śa -> a)
    if res.startswith("ś"):
        res = res[1:]
    return res


def derive_lat_kartari(
    dhatu_upadesha: str,
    gana: Gana = Gana.BHVADI,
    purusha: int = 3,
    vacana: int = 1,
) -> DerivationTree:
    """
    Derives present indicative (laṭ parasmaipada) forms for Bhvādi dhātus.
    Example: bhū -> bhavati
    """
    tree = DerivationTree(root_left=dhatu_upadesha, root_right="laṭ")

    # Step 1: 1.3.1 Declare Dhātusaṃjñā
    tree.record_step(
        rule_applied=SUTRA_1_3_1,
        left_operand=dhatu_upadesha,
        right_operand="",
        output=dhatu_upadesha,
        metadata={"stage": "dhātu_saṃjñā"}
    )

    # Step 2: 3.2.123 Introduce laṭ pratyaya
    dhatu_stage = f"{dhatu_upadesha} + laṭ"
    tree.record_step(
        rule_applied=SUTRA_3_2_123,
        left_operand=dhatu_upadesha,
        right_operand="laṭ",
        output=dhatu_stage,
        metadata={"stage": "lakāra_vidhi"}
    )

    # Step 3: 3.4.78 Replace laṭ with specific Tiṅ pratyaya
    raw_tin = PARASMAIPADA_MAP.get((purusha, vacana), "tip")
    dhatu_stage = f"{dhatu_upadesha} + {raw_tin}"
    tree.record_step(
        rule_applied=SUTRA_3_4_78,
        left_operand=dhatu_upadesha,
        right_operand=raw_tin,
        output=dhatu_stage,
        metadata={"stage": "tiṅ_ādeśa"}
    )

    # Step 4: 1.3.3 / 1.3.9 It-lopa on Tiṅ
    tin_shuddha = apply_it_lopa(raw_tin)
    dhatu_stage = f"{dhatu_upadesha} + {tin_shuddha}"
    tree.record_step(
        rule_applied=SUTRA_1_3_9,
        left_operand=dhatu_upadesha,
        right_operand=tin_shuddha,
        output=dhatu_stage,
        metadata={"stage": "it_lopa_tiṅ"}
    )

    # Step 5: 3.1.68 Introduce Vikaraṇa (śap for Bhvādi)
    if gana == Gana.BHVADI:
        dhatu_stage = f"{dhatu_upadesha} + śap + {tin_shuddha}"
        tree.record_step(
            rule_applied=SUTRA_3_1_68,
            left_operand=dhatu_upadesha,
            right_operand="śap",
            output=dhatu_stage,
            metadata={"stage": "vikaraṇa"}
        )

        # Step 6: It-lopa on śap (ś -> 1.3.8, p -> 1.3.3, remaining -> 'a')
        vikarana_shuddha = apply_it_lopa("śap")
        dhatu_stage = f"{dhatu_upadesha} + {vikarana_shuddha} + {tin_shuddha}"
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand=dhatu_upadesha,
            right_operand=vikarana_shuddha,
            output=dhatu_stage,
            metadata={"stage": "it_lopa_vikaraṇa"}
        )

        # Step 7: 7.3.84 Guṇa on ik-ending dhātu before sārvadhātuka (śap)
        # bhū -> bho
        if dhatu_upadesha == "bhū":
            dhatu_guna = "bho"
            dhatu_stage = f"{dhatu_guna} + {vikarana_shuddha} + {tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_7_3_84,
                left_operand=dhatu_upadesha,
                right_operand=vikarana_shuddha,
                output=dhatu_stage,
                metadata={"stage": "aṅga_guṇa"}
            )

            # Step 8: 6.1.78 eco'yavāyāvaḥ (bho + a -> bhav + a)
            sandhi_res, sutra = apply_ecoyavayavah(dhatu_guna, vikarana_shuddha)
            final_form = f"{sandhi_res}{tin_shuddha}"
            tree.record_step(
                rule_applied=sutra,
                left_operand=dhatu_guna,
                right_operand=vikarana_shuddha,
                output=final_form,
                metadata={"stage": "ac_sandhi_pada"}
            )

    return tree