from typing import  Annotated
from enum import Enum

type Color = Annotated[bool, "True for white, False for black"]

WHITE: Color = True
BLACK: Color = False

class Colors(Enum):
    WHITE = WHITE
    BLACK = BLACK