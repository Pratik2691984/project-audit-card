"""
nodes.py - AST nodes, provenance references, and derivation tree structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict


class SutraType(Enum):
    SAMJNA = "saṃjñā"
    PARIBHASA = "paribhāṣā"
    VIDHI = "vidhi"
    NIYAMA = "niyama"
    ADHIKARA = "adhikāra"
    ATIDESHA = "atideśa"


class PrakriyaStage(str, Enum):
    DHATU_SAMJNA = "dhātu_saṃjñā"
    LAKARA_VIDHI = "lakāra_vidhi"
    TIN_ADESHA = "tiṅ_ādeśa"
    IT_LOPA_TIN = "it_lopa_tiṅ"
    VIKARANA_VIDHI = "vikaraṇa_vidhi"
    IT_LOPA_VIKARANA = "it_lopa_vikaraṇa"
    LUK_ELISION = "luk_elision"
    SLU_ELISION = "ślu_elision"
    DVITVA = "dvitva"
    ABHYASA_SAMJNA = "abhyāsa_saṃjñā"
    ABHYASA_KARYA = "abhyāsa_kārya"
    ABHYASE_CARCA = "abhyāse_carca"
    ANGA_GUNA = "aṅga_guṇa"
    VIKARANA_GUNA = "vikaraṇa_guṇa"
    PRATYAYA_GUNA = "pratyaya_guṇa"
    LAGHUPADHA_GUNA = "laghūpadha_guṇa"
    GUNA_PRATISHEDHA = "guṇa_pratiṣedha"
    APIT_AGUNA = "apit_aguṇa"
    MIT_AC_ANTYAT_PARAH = "mit_ac_antyat_parah"
    SNASOR_ALLOPAH = "śnasor_allopaḥ"
    SNA_IITVA = "śnā_īttva"
    RASABHYAM_NO_NAH = "raṣabhyam_no_nah"
    JHASAS_TATHOR_DHAH = "jhaṣas_tathor_dhaḥ"
    JHALAM_JAS_JHASI = "jhalāṁ_jaś_jhaśi"
    KHARI_CA_CARITVA = "khari_ca_caritva"
    HAL_SANDHI = "hal_sandhi"
    AC_SANDHI = "ac_sandhi"
    ECO_YAVAYAVAH = "eco_yavāyāvaḥ"
    ATO_GUNE = "ato_guṇe"
    ATO_DIRGHO_YANI = "ato_dīrgho_yañi"
    JHO_ANTAH = "jho_antaḥ"
    ADABHYASTAT = "adabhyastāt"
    AVASANE_VISARGAH = "avasāne_visargaḥ"
    PADANIRVRITTI = "padanirvṛtti"


@dataclass(frozen=True)
class SutraRef:
    number: str
    name: str
    sutra_type: SutraType


# 6.1.84 Adhikāra Reference
ADHIKARA_EKAH_PURVAPARAYOH = SutraRef(
    number="6.1.84",
    name="ekaḥ pūrvaparayoḥ",
    sutra_type=SutraType.ADHIKARA,
)


@dataclass
class DerivationStep:
    rule_applied: SutraRef
    left_operand: str
    right_operand: str
    output: str
    governing_adhikara: Optional[SutraRef] = None
    is_ekadesha: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


# Alias required by __init__.py and external consumers
SutraApplication = DerivationStep


@dataclass
class DerivationTree:
    root_left: str
    root_right: str
    steps: List[DerivationStep] = field(default_factory=list)

    def record_step(
        self,
        rule_applied: SutraRef,
        left_operand: str,
        right_operand: str,
        output: str,
        governing_adhikara: Optional[SutraRef] = None,
        is_ekadesha: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        **extra_metadata: Any,
    ) -> None:
        merged_metadata: Dict[str, Any] = {}
        if metadata:
            merged_metadata.update(metadata)
        if extra_metadata:
            merged_metadata.update(extra_metadata)

        step = DerivationStep(
            rule_applied=rule_applied,
            left_operand=left_operand,
            right_operand=right_operand,
            output=output,
            governing_adhikara=governing_adhikara,
            is_ekadesha=is_ekadesha,
            metadata=merged_metadata,
        )
        self.steps.append(step)

    @property
    def final_output(self) -> str:
        return self.steps[-1].output if self.steps else f"{self.root_left}{self.root_right}"