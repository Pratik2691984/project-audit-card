"""
engine.py - Pāṇinian Prakriyā (Derivation) Engine
Declarative vikaraṇa and morphosyntactic rule dispatcher covering:
  - Class 1 (Bhvādi): śap (3.1.68) -> a, allows guṇa (7.3.84)
  - Class 2 (Adādi): śap (3.1.68) -> luk (2.4.72), consonant sandhi (8.4.55)
  - Class 3 (Juhotyādi): śap -> ślu (2.4.75), dvitva (6.1.10), abhyāsa (6.1.4, 7.4.59, 7.4.62, 8.4.54)
  - Class 4 (Divādi): śyan (3.1.69) -> ya, 1.1.5 kniti ca blocks guṇa
  - Class 6 (Tudādi): śa (3.1.77) -> a, 1.2.4 apit + 1.1.5 blocks guṇa
  - Class 7 (Rudhādi): śnam (3.1.78) mit-infix (1.1.47), 8.4.1 ṇatva, 6.4.111 al-lopa, 8.2.40 + 8.4.53
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

# Sūtra Canonical Definitions
SUTRA_1_1_5 = SutraRef("1.1.5", "kṅiti ca", SutraType.NIYAMA)
SUTRA_1_1_47 = SutraRef("1.1.47", "midaco'ntyāt paraḥ", SutraType.PARIBHASA)
SUTRA_1_2_4 = SutraRef("1.2.4", "sārvadhātukam apit", SutraType.ATIDESHA)
SUTRA_1_3_1 = SutraRef("1.3.1", "bhūvādayo dhātavaḥ", SutraType.SAMJNA)
SUTRA_1_3_3 = SutraRef("1.3.3", "halantyam", SutraType.SAMJNA)
SUTRA_1_3_8 = SutraRef("1.3.8", "laśakvataddhite", SutraType.SAMJNA)
SUTRA_1_3_9 = SutraRef("1.3.9", "tasya lopaḥ", SutraType.VIDHI)
SUTRA_2_4_72 = SutraRef("2.4.72", "adiprabhṛtibhyaḥ śapaḥ", SutraType.VIDHI)
SUTRA_2_4_75 = SutraRef("2.4.75", "juhotyādibhyaḥ śluḥ", SutraType.VIDHI)
SUTRA_3_1_68 = SutraRef("3.1.68", "kartari śap", SutraType.VIDHI)
SUTRA_3_1_69 = SutraRef("3.1.69", "divādibhyaḥ śyan", SutraType.VIDHI)
SUTRA_3_1_77 = SutraRef("3.1.77", "tudādibhyaḥ śaḥ", SutraType.VIDHI)
SUTRA_3_1_78 = SutraRef("3.1.78", "rudhādibhyaḥ śnam", SutraType.VIDHI)
SUTRA_3_2_123 = SutraRef("3.2.123", "vartamāne laṭ", SutraType.VIDHI)
SUTRA_3_4_78 = SutraRef("3.4.78", "tiptasjhi...", SutraType.VIDHI)
SUTRA_6_1_4 = SutraRef("6.1.4", "pūrvo'bhyāsaḥ", SutraType.SAMJNA)
SUTRA_6_1_10 = SutraRef("6.1.10", "ślau", SutraType.VIDHI)
SUTRA_6_1_77 = SutraRef("6.1.77", "iko yaṇaci", SutraType.VIDHI)
SUTRA_6_1_78 = SutraRef("6.1.78", "eco'yavāyāvaḥ", SutraType.VIDHI)
SUTRA_6_1_97 = SutraRef("6.1.97", "ato guṇe", SutraType.VIDHI)
SUTRA_6_4_111 = SutraRef("6.4.111", "śnasorallopaḥ", SutraType.VIDHI)
SUTRA_7_1_3 = SutraRef("7.1.3", "jho'ntaḥ", SutraType.VIDHI)
SUTRA_7_1_4 = SutraRef("7.1.4", "adabhyastāt", SutraType.VIDHI)
SUTRA_7_3_84 = SutraRef("7.3.84", "sārvadhātukārdhadhātukayoḥ", SutraType.VIDHI)
SUTRA_7_3_86 = SutraRef("7.3.86", "pugantalaghūpadhasya ca", SutraType.VIDHI)
SUTRA_7_3_101 = SutraRef("7.3.101", "ato dīrgho yañi", SutraType.VIDHI)
SUTRA_7_4_59 = SutraRef("7.4.59", "hrasvaḥ", SutraType.VIDHI)
SUTRA_7_4_62 = SutraRef("7.4.62", "kuhoścuḥ", SutraType.VIDHI)
SUTRA_8_2_40 = SutraRef("8.2.40", "jhaṣastathordho'dhaḥ", SutraType.VIDHI)
SUTRA_8_2_66 = SutraRef("8.2.66", "sasajuṣo ruḥ", SutraType.VIDHI)
SUTRA_8_3_15 = SutraRef("8.3.15", "kharavasānayor visarjanīyaḥ", SutraType.VIDHI)
SUTRA_8_4_1 = SutraRef("8.4.1", "raṣābhyāṃ no ṇaḥ samānapade", SutraType.VIDHI)
SUTRA_8_4_53 = SutraRef("8.4.53", "jhalāṁ jaś jhaśi", SutraType.VIDHI)
SUTRA_8_4_54 = SutraRef("8.4.54", "abhyāse carca", SutraType.VIDHI)
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

YAN_PRATYAHARA = set(expand_pratyahara("yañ"))

KUHO_SCU_MAP = {"k": "c", "kh": "ch", "g": "j", "gh": "jh", "h": "jh"}
CARCA_MAP = {
    "kh": "k", "gh": "g",
    "ch": "c", "jh": "j",
    "ṭh": "ṭ", "ḍh": "ḍ",
    "th": "t", "dh": "d",
    "ph": "p", "bh": "b",
}


@dataclass(frozen=True)
class VikaranaSpec:
    raw_pratyaya: str
    shuddha: str
    vidhi_sutra: SutraRef
    is_elided: bool = False
    elision_type: Optional[str] = None
    elision_sutra: Optional[SutraRef] = None
    blocks_guna: bool = False
    guna_block_sutra: Optional[SutraRef] = None
    is_mit_infix: bool = False


VIKARANA_TABLE: Dict[Gana, VikaranaSpec] = {
    Gana.BHVADI: VikaranaSpec(
        raw_pratyaya="śap",
        shuddha="a",
        vidhi_sutra=SUTRA_3_1_68,
        blocks_guna=False,
    ),
    Gana.ADADI: VikaranaSpec(
        raw_pratyaya="śap",
        shuddha="",
        vidhi_sutra=SUTRA_3_1_68,
        is_elided=True,
        elision_type="luk",
        elision_sutra=SUTRA_2_4_72,
        blocks_guna=True,
        guna_block_sutra=SUTRA_1_1_5,
    ),
    Gana.JUHOTYADI: VikaranaSpec(
        raw_pratyaya="śap",
        shuddha="",
        vidhi_sutra=SUTRA_3_1_68,
        is_elided=True,
        elision_type="ślu",
        elision_sutra=SUTRA_2_4_75,
        blocks_guna=False,
    ),
    Gana.DIVADI: VikaranaSpec(
        raw_pratyaya="śyan",
        shuddha="ya",
        vidhi_sutra=SUTRA_3_1_69,
        blocks_guna=True,
        guna_block_sutra=SUTRA_1_1_5,
    ),
    Gana.TUDADI: VikaranaSpec(
        raw_pratyaya="śa",
        shuddha="a",
        vidhi_sutra=SUTRA_3_1_77,
        blocks_guna=True,
        guna_block_sutra=SUTRA_1_2_4,
    ),
    Gana.RUDHADI: VikaranaSpec(
        raw_pratyaya="śnam",
        shuddha="na",
        vidhi_sutra=SUTRA_3_1_78,
        blocks_guna=True,
        guna_block_sutra=SUTRA_1_2_4,
        is_mit_infix=True,
    ),
}


def apply_it_lopa(pratyaya: str) -> str:
    """Strips canonical it-markers (p, n, m, ś), preserving inflectional consonants."""
    res = pratyaya
    if res.endswith("p") or res.endswith("n") or res.endswith("m"):
        res = res[:-1]
    if res.startswith("ś"):
        res = res[1:]
    return res


def terminal_visarga_avasana(pada: str) -> str:
    """Converts terminal padānta -s to -ḥ in avasāna."""
    if pada.endswith("s"):
        return pada[:-1] + "ḥ"
    return pada


def insert_mit_infix(dhatu: str, infix: str, tree: DerivationTree) -> str:
    """1.1.47 midaco'ntyāt paraḥ: mit augment attaches after the last vowel."""
    vowels = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au"}
    last_vowel = -1
    for i, ch in enumerate(dhatu):
        if ch in vowels:
            last_vowel = i
    if last_vowel == -1:
        infixed = dhatu + infix
    else:
        infixed = dhatu[:last_vowel + 1] + infix + dhatu[last_vowel + 1:]
    tree.record_step(
        rule_applied=SUTRA_1_1_47,
        left_operand=dhatu,
        right_operand=infix,
        output=infixed,
        metadata={"stage": "mit_ac_antyat_parah"},
    )
    return infixed


def retroflex_n_after_r(pada: str, tree: DerivationTree) -> str:
    """8.4.1 raṣābhyāṃ no ṇaḥ samānapade: n after r/ṣ in same pada -> ṇ."""
    r_idx = max(pada.rfind("r"), pada.rfind("ṣ"))
    if r_idx == -1:
        return pada
    for i in range(r_idx + 1, len(pada)):
        if pada[i] == "n":
            result = pada[:i] + "ṇ" + pada[i + 1:]
            tree.record_step(
                rule_applied=SUTRA_8_4_1,
                left_operand=pada,
                right_operand="",
                output=result,
                metadata={"stage": "raṣabhyam_no_nah"},
            )
            return result
    return pada


def transform_abhyasa(dhatu: str, tree: DerivationTree) -> str:
    abhyasa = dhatu
    long_to_short = {"ā": "a", "ī": "i", "ū": "u", "ṝ": "ṛ"}
    for l_v, s_v in long_to_short.items():
        if abhyasa.endswith(l_v):
            abhyasa = abhyasa[:-len(l_v)] + s_v
            tree.record_step(
                rule_applied=SUTRA_7_4_59,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāsa_hrasva"},
            )
            break

    for k_ph, c_ph in KUHO_SCU_MAP.items():
        if abhyasa.startswith(k_ph):
            abhyasa = c_ph + abhyasa[len(k_ph):]
            tree.record_step(
                rule_applied=SUTRA_7_4_62,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāsa_kuhos_cuh"},
            )
            break

    for asp, unasp in CARCA_MAP.items():
        if abhyasa.startswith(asp):
            abhyasa = unasp + abhyasa[len(asp):]
            tree.record_step(
                rule_applied=SUTRA_8_4_54,
                left_operand=dhatu,
                right_operand="",
                output=abhyasa,
                metadata={"stage": "abhyāse_carca"},
            )
            break

    return abhyasa


def derive_lat_kartari(
    dhatu_upadesha: str,
    gana: Gana = Gana.BHVADI,
    purusha: int = 3,
    vacana: int = 1,
) -> DerivationTree:
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

    is_pit = raw_tin.endswith("p")

    # 4. Affix resolution
    if gana == Gana.JUHOTYADI and raw_tin == "jhi":
        tin_shuddha = "ati"
        tree.record_step(
            rule_applied=SUTRA_7_1_4,
            left_operand="jhi",
            right_operand="",
            output=f"{dhatu_upadesha} + {tin_shuddha}",
            metadata={"stage": "adabhyastāt"},
        )
    elif raw_tin == "jhi":
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

    # 5. Declarative Vikaraṇa Dispatch
    spec = VIKARANA_TABLE[gana]
    tree.record_step(
        rule_applied=spec.vidhi_sutra,
        left_operand=dhatu_upadesha,
        right_operand=spec.raw_pratyaya,
        output=f"{dhatu_upadesha} + {spec.raw_pratyaya} + {tin_shuddha}",
        metadata={"stage": "vikaraṇa_vidhi"},
    )

    # Handle Elision (Classes 2 & 3)
    if spec.is_elided:
        tree.record_step(
            rule_applied=spec.elision_sutra,
            left_operand=dhatu_upadesha,
            right_operand=spec.raw_pratyaya,
            output=f"{dhatu_upadesha} + ∅ + {tin_shuddha}",
            metadata={"stage": f"{spec.elision_type}_elision"},
        )

        if gana == Gana.ADADI:
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

        if gana == Gana.JUHOTYADI:
            tree.record_step(
                rule_applied=SUTRA_6_1_10,
                left_operand=dhatu_upadesha,
                right_operand="",
                output=f"{dhatu_upadesha} + {dhatu_upadesha} + {tin_shuddha}",
                metadata={"stage": "dvitva"},
            )
            tree.record_step(
                rule_applied=SUTRA_6_1_4,
                left_operand=dhatu_upadesha,
                right_operand="",
                output=f"abhyāsa({dhatu_upadesha}) + {dhatu_upadesha}",
                metadata={"stage": "abhyāsa_saṃjñā"},
            )
            abhyasa = transform_abhyasa(dhatu_upadesha, tree)
            stem_anga = f"{abhyasa}{dhatu_upadesha}"

            if is_pit:
                dhatu_guna = dhatu_upadesha[:-1] + "o" if dhatu_upadesha.endswith("u") else dhatu_upadesha
                anga_modified = f"{abhyasa}{dhatu_guna}"
                tree.record_step(
                    rule_applied=SUTRA_7_3_84,
                    left_operand=stem_anga,
                    right_operand=tin_shuddha,
                    output=f"{anga_modified} + {tin_shuddha}",
                    metadata={"stage": "aṅga_guṇa"},
                )
                final_form = f"{anga_modified}{tin_shuddha}"
                tree.record_step(
                    rule_applied=SUTRA_VARNAMELANA,
                    left_operand=anga_modified,
                    right_operand=tin_shuddha,
                    output=final_form,
                    metadata={"stage": "padanirvṛtti"},
                )
            else:
                tree.record_step(
                    rule_applied=SUTRA_1_2_4,
                    left_operand=stem_anga,
                    right_operand=tin_shuddha,
                    output=f"{stem_anga} + {tin_shuddha}",
                    metadata={"stage": "apit_ṅitvat_aguṇa"},
                )
                if tin_shuddha.startswith("a"):
                    yan_out, _ = apply_iko_yanaci(stem_anga, tin_shuddha)
                    final_form = yan_out
                    tree.record_step(
                        rule_applied=SUTRA_6_1_77,
                        left_operand=stem_anga,
                        right_operand=tin_shuddha,
                        output=final_form,
                        metadata={"stage": "iko_yaṇaci"},
                    )
                else:
                    final_form = f"{stem_anga}{tin_shuddha}"
                    tree.record_step(
                        rule_applied=SUTRA_VARNAMELANA,
                        left_operand=stem_anga,
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

    # ----------------------------------------------------
    # Branch D: Rudhādi Gaṇa (Class 7) Mit-Infix
    # ----------------------------------------------------
    if gana == Gana.RUDHADI:
        vikarana = spec.shuddha  # "na"
        tree.record_step(
            rule_applied=SUTRA_1_3_9,
            left_operand="śnam",
            right_operand="",
            output=f"{dhatu_upadesha} + {vikarana} + {tin_shuddha}",
            metadata={"stage": "it_lopa_vikaraṇa"},
        )

        if is_pit:
            base = insert_mit_infix(dhatu_upadesha, vikarana, tree)
            base = retroflex_n_after_r(base, tree)
        else:
            infix_elided = "n"
            tree.record_step(
                rule_applied=SUTRA_6_4_111,
                left_operand=vikarana,
                right_operand=tin_shuddha,
                output=infix_elided,
                metadata={"stage": "śnasor_allopaḥ"},
            )
            base = insert_mit_infix(dhatu_upadesha, infix_elided, tree)

        # Consonant contact: dh + t -> ddh (8.2.40 + 8.4.53)
        if base.endswith("dh") and tin_shuddha.startswith("t"):
            tin_dha = "dh" + tin_shuddha[1:]
            tree.record_step(
                rule_applied=SUTRA_8_2_40,
                left_operand=base,
                right_operand=tin_shuddha,
                output=f"{base} + {tin_dha}",
                metadata={"stage": "jhaṣas_tathor_dhaḥ"},
            )
            base_d = base[:-2] + "d"  # replace trailing 'dh' with 'd'
            final_form = base_d + tin_dha
            tree.record_step(
                rule_applied=SUTRA_8_4_53,
                left_operand=f"{base} + {tin_dha}",
                right_operand="",
                output=final_form,
                metadata={"stage": "jhalāṁ_jaś_jhaśi"},
            )
        else:
            final_form = base + tin_shuddha
            tree.record_step(
                rule_applied=SUTRA_VARNAMELANA,
                left_operand=base,
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

    # 6. Overt Suffix Stripping (Classes 1, 4, 6)
    vikarana = spec.shuddha
    tree.record_step(
        rule_applied=SUTRA_1_3_9,
        left_operand=spec.raw_pratyaya,
        right_operand="",
        output=f"{dhatu_upadesha} + {vikarana} + {tin_shuddha}",
        metadata={"stage": "it_lopa_vikaraṇa"},
    )

    # 7. Guṇa Application or Blocking
    if spec.blocks_guna:
        tree.record_step(
            rule_applied=spec.guna_block_sutra,
            left_operand=dhatu_upadesha,
            right_operand=vikarana,
            output=f"{dhatu_upadesha} + {vikarana}",
            metadata={"stage": "guṇa_pratiṣedha"},
        )
        base_anga = f"{dhatu_upadesha}{vikarana}"
    else:
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

    # 8. Stem + Affix Junction
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
    elif tin_shuddha[0] in YAN_PRATYAHARA and base_anga.endswith("a"):
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

    # 9. Terminal Visarga
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