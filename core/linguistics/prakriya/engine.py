"""
engine.py - Pāṇinian Prakriyā (Derivation) Engine
Executes step-by-step morphosyntactic derivation trees for tiṅanta forms across gaṇas:
  - Bhvādi (Class 1): 3.1.68 śap retention, 7.3.84 guṇa, 6.1.78 eco'yavāyāvaḥ
  - Adādi (Class 2): 2.4.72 śap luk-elision, 8.4.55 khari ca caritva
  - Juhotyādi (Class 3): 2.4.75 ślu-elision, 6.1.10 dvitva, abhyāsa-kārya (8.4.54/8.4.55),
                         7.1.4 adabhyastāt, 1.2.4 sārvadhātukam apit
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
    apply_hal_sandhi,
    apply_iko_yanaci,
)
from core.linguistics.ast.sivasutras import expand_pratyahara

# Canonical Sūtras
SUTRA_1_1_4 = SutraRef("1.1.4", "pūrvo'bhyāsaḥ", SutraType.SAMJNA)
SUTRA_1_2_4 = SutraRef("1.2.4", "sārvadhātukam apit", SutraType.ATIDESHA)
SUTRA_1_3_1 = SutraRef("1.3.1", "bhūvādayo dhātavaḥ", SutraType.SAMJNA)
SUTRA_1_3_3 = SutraRef("1.3.3", "halantyam", SutraType.SAMJNA)
SUTRA_1_3_8 = SutraRef("1.3.8", "laśakvataddhite", SutraType.SAMJNA)
SUTRA_1_3_9 = SutraRef("1.3.9", "tasya lopaḥ", SutraType.VIDHI)
SUTRA_2_4_72 = SutraRef("2.4.72", "adiprabhṛtibhyaḥ śapaḥ", SutraType.VIDHI)
SUTRA_2_4_75 = SutraRef("2.4.75", "juhotyādibhyaḥ śluḥ", SutraType.VIDHI)
SUTRA_3_1_68 = SutraRef("3.1.68", "kartari śap", SutraType.VIDHI)
SUTRA_3_2_123 = SutraRef("3.2.123", "vartamāne laṭ", SutraType.VIDHI)
SUTRA_3_4_78 = SutraRef("3.4.78", "tiptasjhi...", SutraType.VIDHI)
SUTRA_6_1_10 = SutraRef("6.1.10", "ślau", SutraType.VIDHI)
SUTRA_6_1_77 = SutraRef("6.1.77", "iko yaṇaci", SutraType.VIDHI)
SUTRA_6_1_78 = SutraRef("6.1.78", "eco'yavāyāvaḥ", SutraType.VIDHI)
SUTRA_6_1_97 = SutraRef("6.1.97", "ato guṇe", SutraType.VIDHI)
SUTRA_7_1_3 = SutraRef("7.1.3", "jho'ntaḥ", SutraType.VIDHI)
SUTRA_7_1_4 = SutraRef("7.1.4", "adabhyastāt", SutraType.VIDHI)
SUTRA_7_3_84 = SutraRef("7.3.84", "sārvadhātukārdhadhātukayoḥ", SutraType.VIDHI)
SUTRA_7_3_101 = SutraRef("7.3.101", "ato dīrgho yañi", SutraType.VIDHI)
SUTRA_7_4_59 = SutraRef("7.4.59", "hrasvaḥ", SutraType.VIDHI)
SUTRA_8_2_66 = SutraRef("8.2.66", "sasajuṣo ruḥ", SutraType.VIDHI)
SUTRA_8_3_15 = SutraRef("8.3.15", "kharavasānayor visarjanīyaḥ", SutraType.VIDHI)
SUTRA_8_4_54 = SutraRef("8.4.54", "kuhoścuḥ", SutraType.VIDHI)
SUTRA_8_4_55_CARCA = SutraRef("8.4.55", "abhyāse carca", SutraType.VIDHI)
SUTRA_VARNAMELANA = SutraRef("varṇa-melana", "saṃyoga / padanirvṛtti", SutraType.VIDHI)


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

# Expand yañ pratyāhāra
YAN_PRATYAHARA = set(expand_pratyahara("yañ"))

# Abhyāse kavarga -> cavarga & h -> jh (8.4.54 kuhoścuḥ)
KUHO_SCU_MAP = {
    "k": "c", "kh": "ch", "g": "j", "gh": "jh",
    "h": "jh"
}

# Abhyāse carca: de-aspiration (8.4.55 abhyāse carca)
# 2nd/4th stops un-aspirate to 1st/3rd stops
CARCA_MAP = {
    "kh": "k", "gh": "g",
    "ch": "c", "jh": "j",
    "ṭh": "ṭ", "ḍh": "ḍ",
    "th": "t", "dh": "d",
    "ph": "p", "bh": "b",
}


def apply_it_lopa(pratyaya: str) -> str:
    """Strips canonical it markers per 1.3.3 and 1.3.8."""
    res = pratyaya
    if res.endswith("p"):
        res = res[:-1]
    if res.startswith("ś"):
        res = res[1:]
    return res


def terminal_visarga_avasana(pada: str) -> str:
    """Converts terminal padānta -s to -ḥ in avasāna."""
    if pada.endswith("s"):
        return pada[:-1] + "ḥ"
    return pada


def transform_abhyasa(dhatu: str, tree: DerivationTree) -> str:
    """
    Applies classical abhyāsa-kārya to the reduplicated prefix:
      1. 7.4.59 hrasvaḥ: shortens vowels
      2. 8.4.54 kuhoścuḥ: replaces velars and 'h' with palatals
      3. 8.4.55 abhyāse carca: de-aspirates
    """
    abhyasa = dhatu

    # 1. 7.4.59 hrasvaḥ
    long_to_short = {"ā": "a", "ī": "i", "ū": "u", "ṝ": "ṛ"}
    for l_v, s_v in long_to_short.items():
        if abhyasa.endswith(l_v):
            abhyasa = abhyasa[:-len(l_v)] + s_v
            tree.record_step(
                rule_applied=SUTRA_7_4_59,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāsa_hrasva"}
            )
            break

    # 2. 8.4.54 kuhoścuḥ (h -> jh, k -> c, etc.)
    for k_ph, c_ph in KUHO_SCU_MAP.items():
        if abhyasa.startswith(k_ph):
            abhyasa = c_ph + abhyasa[len(k_ph):]
            tree.record_step(
                rule_applied=SUTRA_8_4_54,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāsa_kuhos_cuh"}
            )
            break

    # 3. 8.4.55 abhyāse carca (jh -> j, etc.)
    for asp, unasp in CARCA_MAP.items():
        if abhyasa.startswith(asp):
            abhyasa = unasp + abhyasa[len(asp):]
            tree.record_step(
                rule_applied=SUTRA_8_4_55_CARCA,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāse_carca"}
            )
            break

    return abhyasa


def derive_lat_kartari(
    dhatu_upadesha: str,
    gana: Gana = Gana.BHVADI,
    purusha: int = 3,
    vacana: int = 1,
) -> DerivationTree:
    """
    Derives present indicative (laṭ parasmaipada) forms across Gaṇas:
      - Bhvādi (bhū -> bhavati)
      - Adādi (ad -> atti)
      - Juhotyādi (hu -> juhoti, juhutaḥ, juhvati)
    """
    raw_tin = PARASMAIPADA_MAP[(purusha, vacana)]
    tree = DerivationTree(root_left=dhatu_upadesha, root_right=raw_tin)

    # 1. 1.3.1 Dhātusaṃjñā
    tree.record_step(
        rule_applied=SUTRA_1_3_1,
        left_operand=dhatu_upadesha,
        right_operand="",
        output=dhatu_upadesha,
        metadata={"stage": "dhātu_saṃjñā"},
    )

    # 2. 3.2.123 Lakāra vidhi
    tree.record_step(
        rule_applied=SUTRA_3_2_123,
        left_operand=dhatu_upadesha,
        right_operand="laṭ",
        output=f"{dhatu_upadesha} + laṭ",
        metadata={"stage": "lakāra_vidhi"},
    )

    # 3. 3.4.78 Tiṅ-ādeśa
    tree.record_step(
        rule_applied=SUTRA_3_4_78,
        left_operand=dhatu_upadesha,
        right_operand=raw_tin,
        output=f"{dhatu_upadesha} + {raw_tin}",
        metadata={"stage": "tiṅ_ādeśa"},
    )

    # 4. Tiṅ It-lopa or special affix dispatch
    is_pit = raw_tin.endswith("p")

    # 7.1.4 adabhyastāt: jhi -> ati after abhyasta roots (Class 3)
    if gana == Gana.JUHOTYADI and raw_tin == "jhi":
        tin_shuddha = "ati"
        tree.record_step(
            rule_applied=SUTRA_7_1_4,
            left_operand="jhi",
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "adabhyastāt"}
        )
    elif raw_tin == "jhi":
        # 7.1.3 jho'ntaḥ: jhi -> anti for non-reduplicated roots
        tin_shuddha = "anti"
        tree.record_step(
            rule_applied=SUTRA_7_1_3,
            left_operand="jhi",
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "jho_antaḥ"},
        )
    else:
        tin_shuddha = apply_it_lopa(raw_tin)
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand=raw_tin,
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "it_lopa_tiṅ"},
        )

    # 5. 3.1.68 Vikaraṇa introduction (kartari śap)
    tree.record_step(
        rule_applied=SUTRA_3_1_68,
        left_operand=dhatu_upadesha,
        right_operand="śap",
        output=f"{dhatu_upadesha} + śap + {tin_shuddha}",
        metadata={"stage": "vikaraṇa"},
    )

    # ----------------------------------------------------
    # Branch A: Adādi Gaṇa (2.4.72 luk śapaḥ)
    # ----------------------------------------------------
    if gana == Gana.ADADI:
        tree.record_step(
            rule_applied=SUTRA_2_4_72,
            left_operand=dhatu_upadesha,
            right_operand="śap",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "luk_elision"},
        )

        if tin_shuddha.startswith("a"):
            final_form = f"{dhatu_upadesha}{tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_VARNAMELANA,
                left_operand=dhatu_upadesha,
                right_operand=tin_shuddha,
                output=final_form,
                metadata={"stage": "padanirvṛtti"},
            )
        else:
            sandhi_res = apply_hal_sandhi(dhatu_upadesha, tin_shuddha, tree=tree)
            final_form = sandhi_res

        if final_form.endswith("s"):
            visarga_form = terminal_visarga_avasana(final_form)
            tree.record_step(
                rule_applied=SUTRA_8_3_15,
                left_operand=final_form,
                right_operand="",
                output=visarga_form,
                metadata={"stage": "avasāne_visargaḥ"},
            )
            final_form = visarga_form

        return tree

    # ----------------------------------------------------
    # Branch B: Juhotyādi Gaṇa (2.4.75 ślu + 6.1.10 dvitva)
    # ----------------------------------------------------
    if gana == Gana.JUHOTYADI:
        # Step 6: 2.4.75 juhotyādibhyaḥ śluḥ
        tree.record_step(
            rule_applied=SUTRA_2_4_75,
            left_operand=dhatu_upadesha,
            right_operand="śap",
            output=f"{dhatu_upadesha} + ∅ + {tin_shuddha}",
            metadata={"stage": "ślu_elision"}
        )

        # Step 7: 6.1.10 ślau (dvitva)
        dvitva_pair = f"{dhatu_upadesha} + {dhatu_upadesha}"
        tree.record_step(
            rule_applied=SUTRA_6_1_10,
            left_operand=dhatu_upadesha,
            right_operand="",
            output=f"{dvitva_pair} + {tin_shuddha}",
            metadata={"stage": "dvitva"}
        )

        # Step 8: Abhyāsa designation (1.1.4) & Abhyāsa-kārya
        tree.record_step(
            rule_applied=SUTRA_1_1_4,
            left_operand=dhatu_upadesha,
            right_operand="",
            output=f"abhyāsa({dhatu_upadesha}) + {dhatu_upadesha}",
            metadata={"stage": "abhyāsa_saṃjñā"}
        )
        abhyasa = transform_abhyasa(dhatu_upadesha, tree)

        # Base reduplicated stem: e.g., 'ju' + 'hu' -> 'juhu'
        stem_anga = f"{abhyasa}{dhatu_upadesha}"

        # Step 9: Aṅga-kārya conditioned on sārvadhātuka weight
        if is_pit:
            # Strong affix: 7.3.84 sārvadhātukārdhadhātukayoḥ (hu -> ho)
            if dhatu_upadesha.endswith("u"):
                dhatu_guna = dhatu_upadesha[:-1] + "o"
            else:
                dhatu_guna = dhatu_upadesha
            
            anga_modified = f"{abhyasa}{dhatu_guna}"
            tree.record_step(
                rule_applied=SUTRA_7_3_84,
                left_operand=stem_anga,
                right_operand=tin_shuddha,
                output=f"{anga_modified} + {tin_shuddha}",
                metadata={"stage": "aṅga_guṇa"}
            )
            final_form = f"{anga_modified}{tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_VARNAMELANA,
                left_operand=anga_modified,
                right_operand=tin_shuddha,
                output=final_form,
                metadata={"stage": "padanirvṛtti"}
            )
        else:
            # Weak affix: 1.2.4 sārvadhātukam apit (ṅit-vat blocks guṇa)
            tree.record_step(
                rule_applied=SUTRA_1_2_4,
                left_operand=stem_anga,
                right_operand=tin_shuddha,
                output=f"{stem_anga} + {tin_shuddha}",
                metadata={"stage": "apit_ṅitvat_aguṇa"}
            )

            if tin_shuddha.startswith("a"):
                # Junction before vowel: 6.1.77 iko yaṇaci (juhu + ati -> juhvati)
                yan_out, _ = apply_iko_yanaci(stem_anga, tin_shuddha)
                final_form = yan_out
                tree.record_step(
                    rule_applied=SUTRA_6_1_77,
                    left_operand=stem_anga,
                    right_operand=tin_shuddha,
                    output=final_form,
                    metadata={"stage": "iko_yaṇaci"}
                )
            else:
                final_form = f"{stem_anga}{tin_shuddha}"
                tree.record_step(
                    rule_applied=SUTRA_VARNAMELANA,
                    left_operand=stem_anga,
                    right_operand=tin_shuddha,
                    output=final_form,
                    metadata={"stage": "padanirvṛtti"}
                )

        # Step 10: Padānta visarga
        if final_form.endswith("s"):
            visarga_form = terminal_visarga_avasana(final_form)
            tree.record_step(
                rule_applied=SUTRA_8_3_15,
                left_operand=final_form,
                right_operand="",
                output=visarga_form,
                metadata={"stage": "avasāne_visargaḥ"}
            )
            final_form = visarga_form

        return tree

    # ----------------------------------------------------
    # Branch C: Bhvādi Gaṇa (śap retains 'a')
    # ----------------------------------------------------
    if gana == Gana.BHVADI:
        vikarana = "a"
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand="śap",
            right_operand="",
            output=f"{dhatu_upadesha} + {vikarana} + {tin_shuddha}",
            metadata={"stage": "it_lopa_vikaraṇa"},
        )

        dhatu_guna = dhatu_upadesha
        if dhatu_upadesha == "bhū":
            dhatu_guna = "bho"
            tree.record_step(
                rule_applied=SUTRA_7_3_84,
                left_operand=dhatu_upadesha,
                right_operand=vikarana,
                output=f"{dhatu_guna} + {vikarana} + {tin_shuddha}",
                metadata={"stage": "aṅga_guṇa"},
            )

            sandhi_res, _ = apply_ecoyavayavah(dhatu_guna, vikarana)
            base_anga = sandhi_res
            tree.record_step(
                rule_applied=SUTRA_6_1_78,
                left_operand=dhatu_guna,
                right_operand=vikarana,
                output=f"{base_anga} + {tin_shuddha}",
                metadata={"stage": "eco_yavāyāvaḥ"},
            )
        else:
            base_anga = f"{dhatu_upadesha}{vikarana}"

        if tin_shuddha == "anti":
            merged = base_anga[:-1] + tin_shuddha
            tree.record_step(
                rule_applied=SUTRA_6_1_97,
                left_operand=base_anga,
                right_operand=tin_shuddha,
                output=merged,
                metadata={"stage": "ato_guṇe"},
            )
            final_form = merged

        elif tin_shuddha[0] in YAN_PRATYAHARA:
            lengthened_anga = base_anga[:-1] + "ā"
            final_form = f"{lengthened_anga}{tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_7_3_101,
                left_operand=base_anga,
                right_operand=tin_shuddha,
                output=final_form,
                metadata={"stage": "ato_dīrgho_yañi"},
            )

        else:
            final_form = f"{base_anga}{tin_shuddha}"
            tree.record_step(
                rule_applied=SUTRA_VARNAMELANA,
                left_operand=base_anga,
                right_operand=tin_shuddha,
                output=final_form,
                metadata={"stage": "padanirvṛtti"},
            )

        if final_form.endswith("s"):
            visarga_form = terminal_visarga_avasana(final_form)
            tree.record_step(
                rule_applied=SUTRA_8_3_15,
                left_operand=final_form,
                right_operand="",
                output=visarga_form,
                metadata={"stage": "avasāne_visargaḥ"},
            )
            final_form = visarga_form

    return tree