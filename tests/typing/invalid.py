"""Deliberately invalid uses that both checkers must reject at marked lines."""

from collections.abc import Hashable

from valanga import (
    BranchKeyGeneratorP,
    Color,
    Dynamics,
    HasTurn,
    ReversibleDynamics,
    Transition,
)
from valanga.checkpoints import StateFromTagResolver
from valanga.game import State
from valanga.policy import BranchSelector
from valanga.represention_for_evaluation import ContentRepresentation

from .protocols import Position


bad_keys: BranchKeyGeneratorP[list[int]]  # expect-error
bad_roles: HasTurn[list[int]]  # expect-error
bad_dynamics: Dynamics[object]  # expect-error
bad_resolver: StateFromTagResolver[Position, list[int]]  # expect-error


def reversed_role(state: HasTurn[Hashable]) -> HasTurn[Color]:
    return state  # expect-error


def reversed_selector(selector: BranchSelector[Position]) -> BranchSelector[State]:
    return selector  # expect-error


def reversed_representation(
    representation: ContentRepresentation[Position, object],
) -> ContentRepresentation[State, str]:
    return representation  # expect-error


def wrong_state(dynamics: Dynamics[Position], state: Position) -> Transition[str]:
    return dynamics.step(state, "action")  # expect-error


def wrong_undo(dynamics: ReversibleDynamics[Position, int]) -> None:
    dynamics.pop("not an integer undo token")  # expect-error
