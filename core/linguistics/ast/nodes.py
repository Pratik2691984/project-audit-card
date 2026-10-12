"""
core/linguistics/ast/nodes.py
Data structures for Pāṇinian derivation trees and rule execution traces.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict


class SutraType(str, Enum):
    SAMJNA = "saṃjñā"            # Name / definition (e.g. 1.1.1 vṛddhirādaic)
    PARIBHASA = "paribhāṣā"      # Meta-rule / rule of interpretation
    VIDHI = "vidhi"              # Operational / generative rule
    NIYAMA = "niyama"            # Restriction rule
    ATIDESA = "atideśa"          # Extension / analogy rule
    ADHIKARA = "adhikāra"        # Governing heading rule


@dataclass(frozen=True)
class SutraRef:
    number: str                  # e.g., "6.1.77"
    name: str                    # e.g., "iko yaṇaci"
    sutra_type: SutraType        # Operational category


@dataclass(frozen=True)
class SutraApplication:
    sutra: SutraRef
    index: int                   # Left boundary index in the string
    input_slice: str             # Pre-transformation phoneme sequence
    output_slice: str            # Replaced phoneme sequence
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DerivationStep:
    step_number: int
    rule_applied: Optional[SutraApplication]
    state: str                   # Current derived phoneme string


@dataclass
class DerivationTree:
    initial_input: str
    steps: List[DerivationStep] = field(default_factory=list)

    @property
    def current_state(self) -> str:
        if not self.steps:
            return self.initial_input
        return self.steps[-1].state

    def add_step(self, application: SutraApplication, new_state: str) -> None:
        next_idx = len(self.steps) + 1
        self.steps.append(
            DerivationStep(
                step_number=next_idx,
                rule_applied=application,
                state=new_state,
            )
        )