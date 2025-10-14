"""Common types and utilities shared by multiple libraries."""

from .evaluations import BoardEvaluation, FloatyBoardEvaluation, ForcedOutcome
from .game import BLACK, WHITE, Color, ColorIndex, HasTurn
from .over_event import OverEvent
from .represention_for_evaluation import ContentRepresentation

__all__ = [
    "ForcedOutcome",
    "FloatyBoardEvaluation",
    "BoardEvaluation",
    "OverEvent",
    "Color",
    "WHITE",
    "BLACK",
    "ColorIndex",
    "HasTurn",
    "ContentRepresentation",
]
