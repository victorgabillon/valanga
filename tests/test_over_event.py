"""Tests for valanga.over_event module."""

from enum import Enum, auto

import pytest

import valanga
from valanga import Outcome, OverEvent
from valanga.game import Color, SoloRole


class DummyTermination(Enum):
    """Small enum used to test termination semantics."""

    CHECKMATE = auto()
    GOAL_REACHED = auto()
    DEAD_END = auto()
    STEP_LIMIT = auto()


class TeamRole(Enum):
    """Example non-Color role type used for generic winner semantics."""

    ATTACKER = "attacker"
    DEFENDER = "defender"


def test_role_based_win_uses_outcome_termination_and_winner():
    """A role-based win should use the canonical outcome model directly."""
    event = OverEvent(
        outcome=Outcome.WIN,
        termination=DummyTermination.CHECKMATE,
        winner=Color.BLACK,
    )

    assert event.outcome is Outcome.WIN
    assert event.termination is DummyTermination.CHECKMATE
    assert event.winner is Color.BLACK
    assert event.is_over() is True
    assert event.is_win() is True
    assert event.is_success() is True
    assert event.is_win_for(Color.BLACK) is True
    assert event.is_loss_for(Color.WHITE) is True


def test_single_player_win_does_not_require_a_winner():
    """A single-player success should not need role metadata."""
    event = OverEvent(
        outcome=Outcome.WIN,
        termination=DummyTermination.GOAL_REACHED,
    )

    assert event.outcome is Outcome.WIN
    assert event.termination is DummyTermination.GOAL_REACHED
    assert event.winner is None
    assert event.is_over() is True
    assert event.is_success() is True
    assert event.is_win_for(SoloRole.SOLO) is False


def test_single_player_loss_is_role_free():
    """A single-player failure should be represented without a fake winner."""
    event = OverEvent(
        outcome=Outcome.LOSS,
        termination=DummyTermination.DEAD_END,
    )

    assert event.outcome is Outcome.LOSS
    assert event.termination is DummyTermination.DEAD_END
    assert event.winner is None
    assert event.is_over() is True
    assert event.is_loss() is True
    assert event.is_failure() is True
    assert event.is_loss_for(SoloRole.SOLO) is False


def test_unknown_outcome_is_not_over():
    """Outcome.UNKNOWN should represent the absence of a terminal result."""
    event = OverEvent(outcome=Outcome.UNKNOWN)

    assert event.is_over() is False
    assert event.is_win() is False
    assert event.is_loss() is False
    assert event.is_draw() is False


@pytest.mark.parametrize(
    "outcome, winner",
    [
        (Outcome.DRAW, Color.WHITE),
        (Outcome.LOSS, Color.BLACK),
        (Outcome.UNKNOWN, TeamRole.ATTACKER),
    ],
)
def test_non_win_outcomes_reject_winner_metadata(outcome, winner):
    """Only win outcomes may carry winner metadata."""
    with pytest.raises(AssertionError):
        OverEvent(outcome=outcome, winner=winner)


def test_generic_role_helpers_work_with_non_color_roles():
    """The final model should work with any hashable role identity."""
    event = OverEvent(
        outcome=Outcome.WIN,
        termination=DummyTermination.CHECKMATE,
        winner=TeamRole.ATTACKER,
    )

    assert event.is_win_for(TeamRole.ATTACKER) is True
    assert event.is_loss_for(TeamRole.DEFENDER) is True
    assert event.is_loss_for(TeamRole.ATTACKER) is False


def test_test_method_rejects_invalid_mutated_state():
    """The explicit validation helper should catch broken mutated states."""
    event = OverEvent(outcome=Outcome.WIN, winner=Color.WHITE)
    event.outcome = Outcome.DRAW

    with pytest.raises(AssertionError):
        event.test()


def test_bool_raises():
    """Truthiness checks should remain invalid."""
    event = OverEvent(outcome=Outcome.UNKNOWN)

    with pytest.raises(ValueError):
        bool(event)


def test_package_exports_only_include_the_final_over_event_surface():
    """Top-level exports should expose the final API only."""
    assert valanga.Outcome is Outcome
    assert valanga.OverEvent is OverEvent
    assert {"Outcome", "OverEvent"}.issubset(set(valanga.__all__))
