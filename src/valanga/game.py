"""
Common types and utilities representing game objects shared by multiple libraries.
"""

from enum import Enum
from typing import Annotated, Hashable, Iterator, Protocol, Self

type State = Annotated[object, "State of the game (evaluable)"]

type StateModifications = Annotated[
    object, "Modifications to the state between to time steps of the game"
]  # used for time and memory optimisation


type BranchKey = Annotated[Hashable, "A label or identifier for a branch in a tree"]


class BranchKeyGeneratorP[T_co: BranchKey = BranchKey](Protocol):
    """Protocol for a branch key generator that yields branch keys."""

    all_generated_keys: list[T_co] | None

    # whether to sort the branch keys by their respective uci for easy comparison of various implementations
    sort_branch_keys: bool = False

    def __iter__(self) -> Iterator[T_co]:
        """Returns an iterator over the branch keys."""
        ...

    def __next__(self) -> T_co:
        """Returns the next branch key."""
        ...

    def more_than_one(self) -> bool:
        """Checks if there is more than one branch available.

        Returns:
            bool: True if there is more than one branch, False otherwise.
        """
        ...

    def get_all(self) -> list[T_co]:
        """Returns a list of all branch keys."""
        ...

    def copy_with_reset(self) -> Self:
        """Creates a copy of the legal move generator with an optional reset of generated moves.

        Returns:
            Self: A new instance of the legal move generator with the specified generated moves.
        """
        ...


type ColorIndex = Annotated[int, "1 for white, 0 for black"]

WHITE: ColorIndex = 1
BLACK: ColorIndex = 0


class Color(int, Enum):
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
        ...
