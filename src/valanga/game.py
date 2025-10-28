"""
Common types and utilities representing game objects shared by multiple libraries.
"""

from enum import Enum
from typing import Annotated, Hashable, Iterator, Protocol, Self

type StateTag = Annotated[Hashable, "A label or identifier for a state in a game"]

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


class State(Protocol):
    """Protocol for a content object that has a tag."""

    @property
    def tag(self) -> StateTag:
        """Returns the tag of the content.

        Returns:
            StateTag: The tag of the content.
        """
        ...

    @property
    def branch_keys(self) -> BranchKeyGeneratorP[BranchKey]:
        """Returns the branch keys associated with the content.

        Returns:
            BranchKeyGeneratorP: The branch keys associated with the content.
        """
        ...

    def branch_name_from_key(self, key: BranchKey) -> str:
        """Returns the branch name corresponding to the given branch key.

        Args:
            key (BranchKey): The branch key.

        Returns:
            str: The branch name corresponding to the given branch key.
        """
        ...

    def is_game_over(self) -> bool:
        """Checks if the game represented by the content is over.

        Returns:
            bool: True if the game is over, False otherwise.
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
