"""Optional reversible game dynamics protocol."""

from typing import Protocol, TypeVar

from .game import BranchKey, BranchKeyGeneratorP
from .game import State as StateP

StateT = TypeVar("StateT", bound=StateP)
UndoT = TypeVar("UndoT")


class ReversibleDynamics[StateT, UndoT](Protocol):
    """Stateful dynamics API supporting push/pop operations."""

    @property
    def state(self) -> StateT:
        """Return current mutable state."""
        ...

    def legal_actions(self) -> BranchKeyGeneratorP[BranchKey]:
        """Return legal actions from current state."""
        ...

    def push(self, action: BranchKey) -> UndoT:
        """Apply ``action`` and return undo information."""
        ...

    def pop(self, undo: UndoT) -> None:
        """Undo the most recent push using ``undo``."""
        ...

    def action_name(self, action: BranchKey) -> str:
        """Return a human-readable action name."""
        ...

    def action_from_name(self, name: str) -> BranchKey:
        """Parse a human-readable action name into an action key."""
        ...
