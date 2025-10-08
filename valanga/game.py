from typing import  Annotated, Protocol
from enum import Enum

type Color = Annotated[bool, "True for white, False for black"]

WHITE: Color = True
BLACK: Color = False

class Colors(Enum):
    WHITE = WHITE
    BLACK = BLACK


class HasTurn(Protocol):
    """Protocol for a content object that has a tag."""

    @property
    def turn(self) -> Colors:
        """Returns the tag of the content.

        Returns:
            ContentTag: The tag of the content.
        """
        ...