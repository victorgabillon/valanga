"""Common types and utilities shared by multiple libraries."""

from .evaluations import BoardEvaluation, FloatyBoardEvaluation, ForcedOutcome
from .game import BLACK, WHITE, Color, ColorIndex, HasTurn, State, StateModifications
from .over_event import OverEvent
from .represention_for_evaluation import ContentRepresentation
from .representation_factory import RepresentationFactory

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
    "RepresentationFactory",
    "State",
    "StateModifications",
]
