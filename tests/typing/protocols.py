"""Static public-API contracts checked by both mypy and Pyright."""

from collections.abc import Hashable
from dataclasses import dataclass

from valanga import (
    BranchKeyGeneratorP,
    Color,
    Dynamics,
    HasTurn,
    ReversibleDynamics,
    Transition,
    TurnState,
)
from valanga.game import State
from valanga.policy import BranchSelector
from valanga.represention_for_evaluation import ContentRepresentation


@dataclass(frozen=True)
class Position:
    """A minimal concrete implementation of State."""

    tag: int

    def is_game_over(self) -> bool:
        """Return whether this position is terminal."""
        return self.tag == 0

    def pprint(self) -> str:
        """Render the position."""
        return str(self.tag)


def key_covariance(keys: BranchKeyGeneratorP[str]) -> BranchKeyGeneratorP[Hashable]:
    """A string key generator can be used by a generic hashable-key consumer."""
    return keys


def role_covariance(state: HasTurn[Color]) -> HasTurn[Hashable]:
    """Concrete acting roles can be read through the generic role interface."""
    return state


def turn_state_covariance(state: TurnState[Color]) -> TurnState[Hashable]:
    """The combined state/turn protocol retains the same covariance."""
    return state


def selector_contravariance(
    selector: BranchSelector[State],
) -> BranchSelector[Position]:
    """A selector accepting any State also accepts a concrete Position."""
    return selector


def representation_variance(
    representation: ContentRepresentation[State, str],
) -> ContentRepresentation[Position, object]:
    """State inputs are contravariant and evaluator outputs are covariant."""
    return representation


def representation_defaults(
    representation: ContentRepresentation[State, object],
) -> ContentRepresentation:
    """An unspecialized representation uses precise State/object defaults."""
    return representation


def transition_state_relationship(
    dynamics: Dynamics[Position], state: Position
) -> Transition[Position]:
    """Dynamics returns the same concrete state type that it accepts."""
    return dynamics.step(state, "action")


def undo_relationship(dynamics: ReversibleDynamics[Position, int]) -> Position:
    """An undo token returned by push is accepted by the same adapter's pop."""
    token = dynamics.push("action")
    dynamics.pop(token)
    return dynamics.state
