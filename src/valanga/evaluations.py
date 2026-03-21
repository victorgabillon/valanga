"""Evaluation-related classes and types."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from valanga.evaluator_types import EvaluatorInput

from .game import BranchKey, State
from .over_event import OverEvent
from .represention_for_evaluation import ContentRepresentation


class EvalItem[StateT: State](Protocol):
    """Define the protocol for an evaluation item.

    An evaluation item is something that has a state and optionally a representation of that state.
    """

    @property
    def state(self) -> StateT:
        """The state associated with this evaluation item."""
        ...

    @property
    def state_representation(
        self,
    ) -> ContentRepresentation[StateT, EvaluatorInput] | None:
        """The representation of the state associated with this evaluation item, if available."""
        ...


class Certainty(Enum):
    """Certainty levels associated with an evaluation score."""

    ESTIMATE = auto()
    TERMINAL = auto()
    FORCED = auto()


@dataclass(frozen=True, slots=True)
class Value:
    """Score plus certainty and optional terminal outcome metadata.

    When present, `over_event` is described by its `outcome`, `termination`,
    and optional `winner` fields.
    """

    score: float
    certainty: Certainty
    over_event: OverEvent | None = None
    line: list[BranchKey] | None = None
