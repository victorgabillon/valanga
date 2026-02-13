"""Protocols and data structures for game dynamics."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

from .game import BranchKey, BranchKeyGeneratorP, State as StateP, StateModifications
from .over_event import OverEvent

StateT = TypeVar("StateT", bound=StateP)


@dataclass(frozen=True)
class Transition[StateT]:
    """Result of applying an action to a state.

    Notes:
        ``modifications`` is an optional compatibility field for diff-based engines.
        Reversible engines may instead use their own ``UndoT`` token via
        ``ReversibleDynamics``.
    """

    next_state: StateT
    modifications: StateModifications | None = None
    is_over: bool = False
    over_event: OverEvent | None = None
    info: Mapping[str, Any] = field(default_factory=dict)


class Dynamics[StateT](Protocol):
    """Stateless game dynamics API."""

    def legal_actions(self, state: StateT) -> BranchKeyGeneratorP[BranchKey]:
        """Return legal actions for ``state`` as a lazy/resettable branch generator."""
        ...

    def step(self, state: StateT, action: BranchKey) -> Transition[StateT]:
        """Apply ``action`` to ``state`` and return a transition."""
        ...

    def action_name(self, state: StateT, action: BranchKey) -> str:
        """Return a human-readable action name."""
        ...

    def action_from_name(self, state: StateT, name: str) -> BranchKey:
        """Parse a human-readable action name into an action key."""
        ...
