"""
Evaluation-related classes and types.
"""

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Annotated

from .over_event import OverEvent

type ActionKey = Annotated[Hashable, "A label or identifier for an action"]
type EvaluatorInput = Annotated[
    object, "The input type for the evaluator, typically a tensor or array"
]


@dataclass
class ForcedOutcome:
    """
    The class
    """

    # The forced outcome with optimal play by both sides.
    outcome: OverEvent

    # the line
    line: list[ActionKey]


@dataclass
class FloatyStateEvaluation:
    """
    The class to defines what is an evaluation of a board.
    By convention is it always evaluated from the view point of the white side.
    """

    # The evaluation value for the white side when the outcome is not certain. Typically, a float.
    # todo can we remove the None option?
    value_white: float | None


StateEvaluation = FloatyStateEvaluation | ForcedOutcome
