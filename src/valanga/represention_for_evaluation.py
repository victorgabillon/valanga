"""Contains the definition of the ContentRepresentation protocol for content representations used in evaluations."""

from typing import Protocol

from valanga.evaluator_types import EvaluatorInput

from .game import State


class ContentRepresentation[
    StateT_contra: State = State,
    EvalIn_co: EvaluatorInput = EvaluatorInput,
](Protocol):
    """Define the interface for a content representation.

    It is a function returning the proper input for evaluation by the content evaluator.
    """

    def get_evaluator_input(self, state: StateT_contra) -> EvalIn_co:
        """Return the evaluator input tensor for the content.

        Content representations have generally a compressed view and complementary view
        of state info so to avoid redundancy and have all the necessary info we also
        give the state as input.

        Args:
            state: The current state of the game.

        Returns:
            The evaluator input tensor.

        """
        ...
