"""Tests for valanga.over_event module."""

from enum import Enum, auto

import pytest

import valanga
from valanga.game import Color
from valanga.over_event import HowOver, Outcome, OverEvent, OverTags, Winner


class DummyTermination(Enum):
    """Small enum used to test termination semantics."""

    CHECKMATE = auto()
    GOAL_REACHED = auto()
    DEAD_END = auto()
    STEP_LIMIT = auto()


@pytest.mark.parametrize(
    "who, expected",
    [
        (Winner.WHITE, OverTags.TAG_WIN_WHITE),
        (Winner.BLACK, OverTags.TAG_WIN_BLACK),
    ],
)
def test_get_over_tag_win_outcomes(who, expected):
    """Legacy color-based wins should keep their tags and helpers."""
    event = OverEvent(how_over=HowOver.WIN, who_is_winner=who)

    assert event.get_over_tag() == expected
    assert event.outcome is Outcome.WIN
    assert event.is_over() is True
    assert event.is_win() is True
    assert event.is_draw() is False


@pytest.mark.parametrize("winner", [Winner.WHITE, Winner.BLACK])
def test_is_winner_matches_color(winner):
    """The compatibility winner helper should still match colors."""
    event = OverEvent(how_over=HowOver.WIN, who_is_winner=winner)

    assert event.is_winner(Color.WHITE) is (winner == Winner.WHITE)
    assert event.is_winner(Color.BLACK) is (winner == Winner.BLACK)
    assert event.is_win_for(Color.WHITE) is (winner == Winner.WHITE)
    assert event.is_loss_for(Color.BLACK) is (winner == Winner.WHITE)


@pytest.mark.parametrize(
    "how_over, winner, expected",
    [
        (HowOver.DRAW, Winner.NO_KNOWN_WINNER, OverTags.TAG_DRAW),
        (HowOver.DO_NOT_KNOW_OVER, Winner.NO_KNOWN_WINNER, OverTags.TAG_DO_NOT_KNOW),
    ],
)
def test_get_over_tag_draw_and_unknown(how_over, winner, expected):
    """Legacy draw and unknown outcomes should remain supported."""
    event = OverEvent(how_over=how_over, who_is_winner=winner)

    assert event.get_over_tag() == expected
    assert event.is_over() is (how_over == HowOver.DRAW)
    assert event.is_win() is False
    assert event.is_draw() is (how_over == HowOver.DRAW)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"how_over": HowOver.DRAW, "who_is_winner": Winner.WHITE},
        {"outcome": Outcome.DRAW, "winner": Color.WHITE},
        {"outcome": Outcome.LOSS, "winner": Color.BLACK},
    ],
)
def test_post_init_validates_incompatible_winner_configurations(kwargs):
    """Only win outcomes may carry a winner identity."""
    with pytest.raises(AssertionError):
        OverEvent(**kwargs)


@pytest.mark.parametrize("player", [Color.WHITE, Color.BLACK])
def test_is_winner_requires_role_based_win(player):
    """Compatibility winner checks should stay false for non-win outcomes."""
    event = OverEvent(how_over=HowOver.DRAW, who_is_winner=Winner.NO_KNOWN_WINNER)

    assert event.is_winner(player) is False


def test_single_player_win_supports_outcome_without_fake_winner():
    """A single-player success should not require a color winner."""
    event = OverEvent(
        outcome=Outcome.WIN,
        termination=DummyTermination.GOAL_REACHED,
    )

    assert event.outcome is Outcome.WIN
    assert event.termination is DummyTermination.GOAL_REACHED
    assert event.winner is None
    assert event.how_over is HowOver.WIN
    assert event.who_is_winner is Winner.NO_KNOWN_WINNER
    assert event.is_over() is True
    assert event.is_success() is True
    assert event.is_failure() is False
    assert event.get_over_tag() is OverTags.TAG_DO_NOT_KNOW


def test_single_player_loss_is_terminal_and_outcome_centered():
    """A single-player failure should be representable without a winner."""
    event = OverEvent(
        outcome=Outcome.LOSS,
        termination=DummyTermination.DEAD_END,
    )

    assert event.outcome is Outcome.LOSS
    assert event.termination is DummyTermination.DEAD_END
    assert event.winner is None
    assert event.how_over is HowOver.DO_NOT_KNOW_OVER
    assert event.who_is_winner is Winner.NO_KNOWN_WINNER
    assert event.is_over() is True
    assert event.is_failure() is True
    assert event.is_success() is False
    assert event.is_loss_for(Color.WHITE) is False
    assert event.get_over_tag() is OverTags.TAG_DO_NOT_KNOW


def test_termination_is_orthogonal_to_outcome():
    """Termination cause and result semantics should coexist independently."""
    event = OverEvent(
        outcome=Outcome.DRAW,
        termination=DummyTermination.STEP_LIMIT,
    )

    assert event.outcome is Outcome.DRAW
    assert event.termination is DummyTermination.STEP_LIMIT
    assert event.is_draw() is True
    assert event.get_over_tag() is OverTags.TAG_DRAW


def test_legacy_construction_populates_new_outcome_fields():
    """Legacy construction should fill the new fields consistently."""
    event = OverEvent(
        how_over=HowOver.WIN,
        who_is_winner=Winner.WHITE,
        termination=DummyTermination.CHECKMATE,
    )

    assert event.outcome is Outcome.WIN
    assert event.winner is Color.WHITE
    assert event.termination is DummyTermination.CHECKMATE
    assert event.is_win_for(Color.WHITE) is True
    assert event.is_loss_for(Color.BLACK) is True


def test_becomes_over_supports_new_api():
    """The mutating helper should support the new outcome-centered API."""
    event = OverEvent()

    event.becomes_over(
        outcome=Outcome.WIN,
        termination=DummyTermination.GOAL_REACHED,
    )

    assert event.outcome is Outcome.WIN
    assert event.termination is DummyTermination.GOAL_REACHED
    assert event.winner is None


def test_get_over_tag_raises_for_invalid_outcome_type():
    """Mutating the event into an invalid state should still be detectable."""
    event = OverEvent(how_over=HowOver.WIN, who_is_winner=Winner.WHITE)
    event.outcome = None

    with pytest.raises(ValueError):
        event.get_over_tag()


def test_test_method_for_valid_events():
    """The consistency helper should accept valid role-based and role-free wins."""
    OverEvent(how_over=HowOver.WIN, who_is_winner=Winner.WHITE).test()
    OverEvent(outcome=Outcome.WIN, termination=DummyTermination.GOAL_REACHED).test()
    OverEvent(outcome=Outcome.DRAW, termination=DummyTermination.STEP_LIMIT).test()


def test_test_method_rejects_invalid_draw_winner_configuration():
    """The consistency helper should reject non-win outcomes with winners."""
    event = OverEvent(outcome=Outcome.WIN, winner=Color.WHITE)
    event.outcome = Outcome.DRAW

    with pytest.raises(AssertionError):
        event.test()


def test_bool_raises():
    """Truthiness checks should still raise."""
    event = OverEvent()

    with pytest.raises(ValueError):
        bool(event)


def test_package_exports_include_new_and_legacy_over_event_types():
    """The package root should expose the updated over-event surface."""
    assert valanga.Outcome is Outcome
    assert valanga.HowOver is HowOver
    assert valanga.Winner is Winner
    assert valanga.OverTags is OverTags
