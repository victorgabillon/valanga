"""Tests for the generalized role/turn model."""

from dataclasses import dataclass

import valanga
from valanga import Color, HasTurn, SOLO, SoloRole, TurnState
from valanga.game import TurnStatePlusHistory


@dataclass(frozen=True)
class ChessLikeState:
    """Simple two-player turn state used to exercise Color roles."""

    tag: str
    turn: Color

    def is_game_over(self) -> bool:
        """Return whether the state is terminal."""
        return False

    def pprint(self) -> str:
        """Return a compact debug representation."""
        return f"{self.tag}:{self.turn.name}"


@dataclass(frozen=True)
class SoloPuzzleState:
    """Simple single-player turn state using the dedicated solo role."""

    tag: str
    turn: SoloRole

    def is_game_over(self) -> bool:
        """Return whether the state is terminal."""
        return False

    def pprint(self) -> str:
        """Return a compact debug representation."""
        return f"{self.tag}:{self.turn.name}"


def acting_color(state: HasTurn[Color]) -> Color:
    """Return the acting color from a color-based turn state."""
    return state.turn


def acting_solo_role(state: HasTurn[SoloRole]) -> SoloRole:
    """Return the acting solo role from a single-player turn state."""
    return state.turn


def tagged_color_state(state: TurnState[Color]) -> tuple[str, Color]:
    """Return the tag and current acting color from a two-player turn state."""
    return state.tag, state.turn


def tagged_solo_state(state: TurnState[SoloRole]) -> tuple[str, SoloRole]:
    """Return the tag and current acting role from a single-player turn state."""
    return state.tag, state.turn


def test_color_turn_state_is_natural():
    """Color should remain a natural concrete role type."""
    state = ChessLikeState(tag="midgame", turn=Color.BLACK)

    assert acting_color(state) is Color.BLACK
    assert tagged_color_state(state) == ("midgame", Color.BLACK)

    history = TurnStatePlusHistory(current_state_tag=state.tag, turn=Color.WHITE)
    assert history.turn is Color.WHITE


def test_solo_role_turn_state_works_without_fake_color():
    """Single-player turn states should use SoloRole rather than fake Color."""
    state = SoloPuzzleState(tag="puzzle", turn=SoloRole.SOLO)

    assert acting_solo_role(state) is SoloRole.SOLO
    assert tagged_solo_state(state) == ("puzzle", SoloRole.SOLO)

    history = TurnStatePlusHistory(current_state_tag=state.tag, turn=SOLO)
    assert history.turn is SoloRole.SOLO


def test_package_exports_include_new_role_symbols():
    """Top-level exports should include the final role-model surface."""
    assert valanga.Color is Color
    assert valanga.SoloRole is SoloRole
    assert valanga.SOLO is SoloRole.SOLO
    assert valanga.HasTurn is HasTurn
    assert valanga.TurnState is TurnState
