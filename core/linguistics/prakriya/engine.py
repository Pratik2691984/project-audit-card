"""
engine.py - Pāṇinian Prakriyā (Derivation) Engine
Executes step-by-step morphosyntactic derivation trees for tiṅanta forms across all 9 cells.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Tuple

from core.linguistics.ast.nodes import (
    SutraRef,
    SutraType,
    DerivationTree,
)
from core.linguistics.ast.sandhi import (
    apply_ad_gunah,
    apply_ecoyavayavah,
)
from core.linguistics.ast.sivasutras import expand_pratyahara

# Sūtras
SUTRA_1_3_1 = SutraRef("1.3.1", "bhūvādayo dhātavaḥ", SutraType.SAMJNA)
SUTRA_1_3_3 = SutraRef("1.3.3", "halantyam", SutraType.SAMJNA)
SUTRA_1_3_8 = SutraRef("1.3.8", "laśakvataddhite", SutraType.SAMJNA)
SUTRA_1_3_9 = SutraRef("1.3.9", "tasya lopaḥ", SutraType.VIDHI)
SUTRA_3_1_68 = SutraRef("3.1.68", "kartari śap", SutraType.VIDHI)
SUTRA_3_2_123 = SutraRef("3.2.123", "vartamāne laṭ", SutraType.VIDHI)
SUTRA_3_4_78 = SutraRef("3.4.78", "tiptasjhi...", SutraType.VIDHI)
SUTRA_6_1_78 = SutraRef("6.1.78", "eco'yavāyāvaḥ", SutraType.VIDHI)
SUTRA_6_1_97 = SutraRef("6.1.97", "ato guṇe", SutraType.VIDHI)
SUTRA_7_1_3 = SutraRef("7.1.3", "jho'ntaḥ", SutraType.VIDHI)
SUTRA_7_3_84 = SutraRef("7.3.84", "sārvadhātukārdhadhātukayoḥ", SutraType.VIDHI)
SUTRA_7_3_101 = SutraRef("7.3.101", "ato dīrgho yañi", SutraType.VIDHI)
SUTRA_8_2_66 = SutraRef("8.2.66", "sasajuṣo ruḥ", SutraType.VIDHI)
SUTRA_8_3_15 = SutraRef("8.3.15", "kharavasānayor visarjanīyaḥ", SutraType.VIDHI)


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

# Expand yañ pratyāhāra: y, v, r, l, ñ, m, ṅ, ṇ, n, jh, bh
YAN_PRATYAHARA = set(expand_pratyahara("yañ"))


def apply_it_lopa(pratyaya: str) -> str:
    """Strips canonical it markers per 1.3.3 and 1.3.8."""
    res = pratyaya
    if res.endswith("p"):
        res = res[:-1]
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
    Derives present indicative (laṭ parasmaipada) forms across all 9 cells.
    """
    raw_tin = PARASMAIPADA_MAP[(purusha, vacana)]
    tree = DerivationTree(root_left=dhatu_upadesha, root_right=raw_tin)

    # 1. 1.3.1 Dhātusaṃjñā
    tree.record_step(
        rule_applied=SUTRA_1_3_1,
        left_operand=dhatu_upadesha,
        right_operand="",
        output=dhatu_upadesha,
        metadata={"stage": "dhātu_saṃjñā"}
    )

    # 2. 3.2.123 Lakāra vidhi
    tree.record_step(
        rule_applied=SUTRA_3_2_123,
        left_operand=dhatu_upadesha,
        right_operand="laṭ",
        output=f"{dhatu_upadesha} + laṭ",
        metadata={"stage": "lakāra_vidhi"}
    )

    # 3. 3.4.78 Tiṅ-ādeśa
    tree.record_step(
        rule_applied=SUTRA_3_4_78,
        left_operand=dhatu_upadesha,
        right_operand=raw_tin,
        output=f"{dhatu_upadesha} + {raw_tin}",
        metadata={"stage": "tiṅ_ādeśa"}
    )

    # 4. Handle jhi -> anti (7.1.3 jho'ntaḥ) vs standard it-lopa (1.3.9)
    if raw_tin == "jhi":
        tin_shuddha = "anti"
        tree.record_step(
            rule_applied=SUTRA_7_1_3,
            left_operand="jhi",
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "jho_antaḥ"}
        )
    else:
        tin_shuddha = apply_it_lopa(raw_tin)
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand=raw_tin,
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "it_lopa_tiṅ"}
        )

    # 5. 3.1.68 Vikaraṇa (kartari śap for Bhvādi)
    if gana == Gana.BHVADI:
        tree.record_step(
            rule_applied=SUTRA_3_1_68,
            left_operand=dhatu_upadesha,
            right_operand="śap",
            output=f"{dhatu_upadesha} + śap + {tin_shuddha}",
            metadata={"stage": "vikaraṇa"}
        )

        # 6. It-lopa on śap (śap -> a)
        vikarana = "a"
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand="śap",
            right_operand="",
            output=f"{dhatu_upadesha} + {vikarana} + {tin_shuddha}",
            metadata={"stage": "it_lopa_vikaraṇa"}
        )

        # 7. 7.3.84 Guṇa on ik-ending dhātu before sārvadhātuka (bhū -> bho)
        dhatu_guna = dhatu_upadesha
        if dhatu_upadesha == "bhū":
            dhatu_guna = "bho"
            tree.record_step(
                rule_applied=SUTRA_7_3_84,
                left_operand=dhatu_upadesha,
                right_operand=vikarana,
                output=f"{dhatu_guna} + {vikarana} + {tin_shuddha}",
                metadata={"stage": "aṅga_guṇa"}
            )

            # 8. 6.1.78 eco'yavāyāvaḥ (bho + a -> bhava)
            sandhi_res, _ = apply_ecoyavayavah(dhatu_guna, vikarana)
            base_anga = sandhi_res  # "bhava"
            tree.record_step(
                rule_applied=SUTRA_6_1_78,
                left_operand=dhatu_guna,
                right_operand=vikarana,
                output=f"{base_anga} + {tin_shuddha}",
                metadata={"stage": "eco_yavāyāvaḥ"}
            )
        else:
            base_anga = f"{dhatu_upadesha}{vikarana}"

        # 9. Aṅga adjustments before specific terminations
        # Case A: 6.1.97 ato guṇe for anti (bhava + anti -> bhavanti)
        if tin_shuddha == "anti":
            merged = base_anga[:-1] + tin_shuddha
            tree.record_step(
                rule_applied=SUTRA_6_1_97,
                left_operand=base_anga,
                right_operand=tin_shuddha,
                output=merged,
                metadata={"stage": "ato_guṇe"}
            )
            final_form = merged

        # Case B: 7.3.101 ato dīrgho yañi (bhava -> bhavā before mi, vas, mas)
        elif tin_shuddha[0] in YAN_PRATYAHARA:
            lengthened_anga = base_anga[:-1] + "ā"
            final_form = f"{lengthened_anga}{tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_7_3_101,
                left_operand=base_anga,
                right_operand=tin_shuddha,
                output=final_form,
                metadata={"stage": "ato_dīrgho_yañi"}
            )

        else:
            final_form = f"{base_anga}{tin_shuddha}"

        # 10. Padānta visarga (8.2.66 sasajuṣo ruḥ -> 8.3.15 kharavasānayoḥ)
        if final_form.endswith("s"):
            visarga_form = final_form[:-1] + "ḥ"
            tree.record_step(
                rule_applied=SUTRA_8_3_15,
                left_operand=final_form,
                right_operand="",
                output=visarga_form,
                metadata={"stage": "avasāne_visargaḥ"}
            )
            final_form = visarga_form

    return tree