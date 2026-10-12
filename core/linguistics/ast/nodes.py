"""
nodes.py - AST nodes, provenance references, and derivation tree structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any


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
    metadata: dict = field(default_factory=dict)


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
        **metadata: Any,
    ) -> None:
        step = DerivationStep(
            rule_applied=rule_applied,
            left_operand=left_operand,
            right_operand=right_operand,
            output=output,
            governing_adhikara=governing_adhikara,
            is_ekadesha=is_ekadesha,
            metadata=metadata,
        )
        self.steps.append(step)

    @property
    def final_output(self) -> str:
        return self.steps[-1].output if self.steps else f"{self.root_left}{self.root_right}"