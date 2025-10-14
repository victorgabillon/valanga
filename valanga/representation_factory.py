"""
Factory class for creating state representations.
"""

from dataclasses import dataclass
from typing import Protocol

from .game import State, StateModifications
from .represention_for_evaluation import ContentRepresentation


class CreateFromState[T: ContentRepresentation](Protocol):
    """
    Protocol for creating a state representation from a state.
    """

    def __call__(self, state: State) -> T: ...


class CreateFromStateAndModifications[T: ContentRepresentation](Protocol):
    """
    Protocol for creating a state representation from a state and modifications.
    """

    def __call__(
        self,
        state: State,
        state_modifications: StateModifications,
        previous_state_representation: T,
    ) -> T: ...


@dataclass
class RepresentationFactory[T: ContentRepresentation = ContentRepresentation]:
    """
    Factory class for creating state representations.
    """

    create_from_state: CreateFromState[T]
    create_from_state_and_modifications: CreateFromStateAndModifications[T]

    def create_from_transition(
        self,
        state: State,
        previous_state_representation: T | None,
        modifications: StateModifications | None,
    ) -> T:
        """
        Create a Generic T_StateRepresentation object from a transition.

        Args:
            state (State): The current state of the game.
            previous_state_representation (Representation364 | None): The representation of the previous state. None if this is the root node.
            modifications (StateModifications | None): The modifications from the parent state to the current state. None if this is the root node.

        Returns:
            T_StateRepresentation: The created (Generic) Representation object

        This version is supposed to be faster as it only modifies the previous state
        representation with the last modification
        """
        if previous_state_representation is None:  # this is the root_node
            representation = self.create_from_state(state=state)
        else:
            if modifications is None:
                representation = self.create_from_state(state=state)
            else:
                representation = self.create_from_state_and_modifications(
                    state=state,
                    state_modifications=modifications,
                    previous_state_representation=previous_state_representation,
                )

        return representation
