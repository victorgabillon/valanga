"""Terminal outcome types and helpers."""

from collections.abc import Hashable
from dataclasses import dataclass
from enum import Enum, auto


class OverEventInvariantError(ValueError):
    """OverEvent has no truthiness semantics."""


class Outcome(Enum):
    """Result semantics for a terminal event.

    `outcome` answers what the result is, independently from why the game or
    episode stopped.
    """

    WIN = auto()
    LOSS = auto()
    DRAW = auto()
    UNKNOWN = auto()


@dataclass(slots=True)
class OverEvent:
    """Describe a terminal result.

    Attributes:
        outcome: The result semantics.
        termination: Why the game or episode stopped.
        winner: Optional role metadata for role-based wins.

    Notes:
        `turn` belongs to the state model.
        `outcome` describes what the result is.
        `termination` describes why play ended.
        `winner` is optional metadata and is only meaningful for role-based
        wins.
    """

    outcome: Outcome
    termination: Enum | None = None
    winner: Hashable | None = None

    def __post_init__(self) -> None:
        """Validate the event state."""
        assert isinstance(self.outcome, Outcome)
        assert self.winner is None or isinstance(self.winner, Hashable)

        if self.outcome is Outcome.WIN:
            return

        assert self.winner is None

    def __bool__(self) -> None:
        """Disallow truthiness checks on terminal events."""
        raise OverEventInvariantError

    def is_over(self) -> bool:
        """Return whether the event is terminal."""
        return self.outcome is not Outcome.UNKNOWN

    def is_win(self) -> bool:
        """Return whether the result is a win."""
        return self.outcome is Outcome.WIN

    def is_loss(self) -> bool:
        """Return whether the result is a loss."""
        return self.outcome is Outcome.LOSS

    def is_draw(self) -> bool:
        """Return whether the result is a draw."""
        return self.outcome is Outcome.DRAW

    def is_success(self) -> bool:
        """Return whether the terminal result is a success."""
        return self.is_win()

    def is_failure(self) -> bool:
        """Return whether the terminal result is a failure."""
        return self.is_loss()

    def is_win_for(self, role: Hashable) -> bool:
        """Return whether a specific role is the winner."""
        return self.is_win() and self.winner == role

    def is_loss_for(self, role: Hashable) -> bool:
        """Return whether a specific role lost to a known winner.

        For role-free failures, use :meth:`is_failure`.
        """
        return self.is_win() and self.winner is not None and self.winner != role

    def print_info(self) -> None:
        """Print information about the event."""
        print(
            "over_event:",
            "outcome:",
            self.outcome,
            "termination:",
            self.termination,
            "winner:",
            self.winner,
        )

    def test(self) -> None:
        """Re-run the invariant checks."""
        self.__post_init__()
