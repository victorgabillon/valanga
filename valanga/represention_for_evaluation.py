"""
Contains the definition of the ContentRepresentation protocol for content representations used in evaluations.
"""

from typing import Protocol

from .evaluations import EvaluatorInput
from .game import Color


class ContentRepresentation(Protocol):
    """
    Protocol defining the interface for a content representation.
    It is a function returning the proper input for evaluation by the content evaluator.
    """

    def get_evaluator_input(self, color_to_play: Color) -> EvaluatorInput:
        """
        Returns the evaluator input tensor for the given color to play.

        Args:
            color_to_play: The color to play, either chess.WHITE or chess.BLACK.

        Returns:
            The evaluator input tensor.
        """
