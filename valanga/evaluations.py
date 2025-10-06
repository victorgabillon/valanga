from dataclasses import dataclass
from .over_event import OverEvent

from typing import Hashable, Annotated

type ActionKey = Annotated[Hashable, "A label or identifier for an action"]



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
class FloatyBoardEvaluation:
    """
    The class to defines what is an evaluation of a board.
    By convention is it always evaluated from the view point of the white side.
    """

    # The evaluation value for the white side when the outcome is not certain. Typically, a float.
    # todo can we remove the None option?
    value_white: float | None


BoardEvaluation = FloatyBoardEvaluation | ForcedOutcome
