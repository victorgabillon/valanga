"""
Common types and utilities representing game objects shared by multiple libraries.
"""

from enum import Enum
from typing import Annotated, Protocol

type State = Annotated[object, "State of the game (evaluable)"]

type StateModifications = Annotated[
    object, "Modifications to the state between to time steps of the game"
]  # used for time and memory optimisation

type ColorIndex = Annotated[int, "1 for white, 0 for black"]

WHITE: ColorIndex = 1
BLACK: ColorIndex = 0


class Color(Enum):
    """Represents the color of a player in a game."""

    WHITE = WHITE
    BLACK = BLACK


class HasTurn(Protocol):
    """Protocol for a content object that has a tag."""

    @property
    def turn(self) -> Color:
        """Returns the tag of the content.

        Returns:
            ContentTag: The tag of the content.
        """
