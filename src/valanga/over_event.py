"""Module for handling terminal outcome events."""

from collections.abc import Hashable
from dataclasses import dataclass
from enum import Enum, StrEnum, auto

from .game import Color


class WinnerNotProperlyDefinedError(ValueError):
    """Winner is not properly defined."""


class OverNotProperlyDefinedError(ValueError):
    """Over is not properly defined."""


class OverEventInvariantError(ValueError):
    """OverEvent reached an invalid state."""


class Outcome(Enum):
    """Result semantics for a terminal event.

    `Outcome` answers what the result is, independently from why the game or
    episode stopped. It is the preferred result model for Valanga.
    """

    WIN = auto()
    LOSS = auto()
    DRAW = auto()
    UNKNOWN = auto()


class HowOver(Enum):
    """Legacy high-level result classification.

    This compatibility enum predates :class:`Outcome` and cannot represent
    :attr:`Outcome.LOSS`.

    It is kept in this first migration step so existing callers can continue
    to use the historical color-based API while newer code moves to
    :class:`Outcome`.
    """

    WIN = 1
    DRAW = 2
    DO_NOT_KNOW_OVER = 3


class Winner(Enum):
    """Legacy color-based winner compatibility enum.

    This enum is preserved for compatibility with existing two-player callers.
    Newer code should prefer the optional `winner` identity carried directly by
    :class:`OverEvent`.
    """

    WHITE = Color.WHITE
    BLACK = Color.BLACK
    NO_KNOWN_WINNER = None

    def is_none(self) -> bool:
        """Check if the winner is unknown."""
        return self is Winner.NO_KNOWN_WINNER

    def is_white(self) -> bool:
        """Check if the winner is white."""
        return self is Winner.WHITE

    def is_black(self) -> bool:
        """Check if the winner is black."""
        return self is Winner.BLACK


class OverTags(StrEnum):
    """Legacy tags for color-based game-over storage."""

    TAG_WIN_WHITE = "Win-Wh"
    TAG_WIN_BLACK = "Win-Bl"
    TAG_DRAW = "Draw"
    TAG_DO_NOT_KNOW = "?"


def _normalize_winner_identity(
    winner: Hashable | Winner | None,
) -> Hashable | None:
    """Normalize a winner identity into the role/object carried by the event."""
    if winner is None or winner is Winner.NO_KNOWN_WINNER:
        return None
    if winner is Winner.WHITE:
        return Color.WHITE
    if winner is Winner.BLACK:
        return Color.BLACK
    return winner


def _winner_identity_from_legacy(who_is_winner: Winner) -> Color | None:
    """Translate the legacy winner enum into a winner identity."""
    assert isinstance(who_is_winner, Winner)
    if who_is_winner is Winner.WHITE:
        return Color.WHITE
    if who_is_winner is Winner.BLACK:
        return Color.BLACK
    return None


def _legacy_winner_from_identity(winner: Hashable | None) -> Winner:
    """Translate a winner identity into the legacy color-only enum."""
    if winner is Color.WHITE:
        return Winner.WHITE
    if winner is Color.BLACK:
        return Winner.BLACK
    return Winner.NO_KNOWN_WINNER


def _outcome_from_legacy(how_over: HowOver) -> Outcome:
    """Translate the legacy outcome enum into the new outcome model."""
    assert isinstance(how_over, HowOver)
    if how_over is HowOver.WIN:
        return Outcome.WIN
    if how_over is HowOver.DRAW:
        return Outcome.DRAW
    return Outcome.UNKNOWN


def _legacy_how_over_from_outcome(outcome: Outcome) -> HowOver:
    """Translate the new outcome model into the legacy enum.

    This translation is intentionally lossy: the legacy enum has no dedicated
    representation for :attr:`Outcome.LOSS`, so both `LOSS` and `UNKNOWN`
    degrade to :attr:`HowOver.DO_NOT_KNOW_OVER`.
    """
    if outcome is Outcome.WIN:
        return HowOver.WIN
    if outcome is Outcome.DRAW:
        return HowOver.DRAW
    if outcome in {Outcome.LOSS, Outcome.UNKNOWN}:
        return HowOver.DO_NOT_KNOW_OVER
    raise OverNotProperlyDefinedError


def _legacy_over_tag_from_winner_identity(winner: Hashable | None) -> OverTags | None:
    """Project a canonical winner identity into the legacy color tag space."""
    if winner is Color.WHITE:
        return OverTags.TAG_WIN_WHITE
    if winner is Color.BLACK:
        return OverTags.TAG_WIN_BLACK
    return None


@dataclass(slots=True, init=False)
class OverEvent:
    """Describe a terminal result in a role-aware but winner-optional way.

    Attributes:
        outcome: Result semantics such as win/loss/draw/unknown.
        termination: Why the game or episode stopped.
        winner: Optional winner identity for role-based wins.

    Notes:
        `termination` describes *why* play ended.
        `outcome` describes *what* the result is.
        `winner` is optional metadata and is only meaningful when a role-based
        winner exists.

        `outcome`, `termination`, and `winner` are the canonical model.
        The legacy `how_over` and `who_is_winner` views are preserved as
        compatibility projections for existing color-based callers.
    """

    outcome: Outcome
    termination: Enum | None
    winner: Hashable | None

    def __init__(
        self,
        how_over: HowOver = HowOver.DO_NOT_KNOW_OVER,
        who_is_winner: Winner = Winner.NO_KNOWN_WINNER,
        termination: Enum | None = None,
        *,
        outcome: Outcome | None = None,
        winner: Hashable | Winner | None = None,
    ) -> None:
        """Create an over event from the new or legacy API.

        Prefer the canonical keyword arguments `outcome`, `termination`, and
        `winner`. The legacy `how_over` and `who_is_winner` inputs remain for
        compatibility during the migration.
        """
        resolved_outcome = outcome
        if resolved_outcome is None:
            resolved_outcome = _outcome_from_legacy(how_over)
        elif how_over is not HowOver.DO_NOT_KNOW_OVER:
            assert resolved_outcome is _outcome_from_legacy(how_over)

        resolved_winner = _winner_identity_from_legacy(who_is_winner)
        if winner is not None:
            normalized_winner = _normalize_winner_identity(winner)
            if who_is_winner is not Winner.NO_KNOWN_WINNER:
                assert normalized_winner == resolved_winner
            resolved_winner = normalized_winner

        self.outcome = resolved_outcome
        self.termination = termination
        self.winner = resolved_winner
        self._validate()

    def becomes_terminal(
        self,
        outcome: Outcome,
        termination: Enum | None = None,
        winner: Hashable | Winner | None = None,
    ) -> None:
        """Preferred mutating API using canonical outcome semantics."""
        self.outcome = outcome
        self.termination = termination
        self.winner = _normalize_winner_identity(winner)
        self._validate()

    @property
    def how_over(self) -> HowOver:
        """Compatibility view of the outcome for legacy callers.

        This view is lossy: `Outcome.LOSS` is exposed as
        :attr:`HowOver.DO_NOT_KNOW_OVER` because the legacy API cannot express a
        role-free loss outcome directly.
        """
        return _legacy_how_over_from_outcome(self.outcome)

    @how_over.setter
    def how_over(self, how_over: HowOver) -> None:
        self.outcome = _outcome_from_legacy(how_over)

    @property
    def who_is_winner(self) -> Winner:
        """Compatibility view of the winner for legacy color-based callers."""
        return _legacy_winner_from_identity(self.winner)

    @who_is_winner.setter
    def who_is_winner(self, who_is_winner: Winner) -> None:
        self.winner = _winner_identity_from_legacy(who_is_winner)

    def _validate(self) -> None:
        """Validate the current event state.

        This is the PR1 migration invariant: only win outcomes may carry a
        winner identity. The model may broaden in later role/multiplayer
        refactors.
        """
        assert isinstance(self.outcome, Outcome)
        assert self.winner is None or isinstance(self.winner, Hashable)

        if self.outcome is Outcome.WIN:
            return

        assert self.winner is None

    def becomes_over(
        self,
        how_over: HowOver = HowOver.DO_NOT_KNOW_OVER,
        termination: Enum | None = None,
        who_is_winner: Winner = Winner.NO_KNOWN_WINNER,
        *,
        outcome: Outcome | None = None,
        winner: Hashable | Winner | None = None,
    ) -> None:
        """Compatibility mutator for legacy and transitional callers.

        New code should prefer :meth:`becomes_terminal`, which works directly
        with the canonical `outcome`, `termination`, and `winner` model.
        """
        updated = type(self)(
            how_over=how_over,
            who_is_winner=who_is_winner,
            termination=termination,
            outcome=outcome,
            winner=winner,
        )
        self.becomes_terminal(
            outcome=updated.outcome,
            termination=updated.termination,
            winner=updated.winner,
        )

    def get_over_tag(self) -> OverTags:
        """Return the legacy storage tag for the current outcome.

        Color-based wins and draws preserve the historical tags.
        Outcome shapes that the legacy storage model cannot express degrade to
        :attr:`OverTags.TAG_DO_NOT_KNOW`.

        This is also intentionally lossy compatibility behavior rather than a
        statement that `LOSS` and `UNKNOWN` are semantically identical.
        """
        if not isinstance(self.outcome, Outcome):
            raise OverNotProperlyDefinedError

        if self.outcome is Outcome.WIN:
            legacy_tag = _legacy_over_tag_from_winner_identity(self.winner)
            if legacy_tag is not None:
                return legacy_tag
            return OverTags.TAG_DO_NOT_KNOW
        if self.outcome is Outcome.DRAW:
            return OverTags.TAG_DRAW
        if self.outcome in {Outcome.LOSS, Outcome.UNKNOWN}:
            return OverTags.TAG_DO_NOT_KNOW
        raise WinnerNotProperlyDefinedError

    def __bool__(self) -> None:
        """Raise to avoid accidental truthiness checks."""
        raise OverEventInvariantError

    def is_over(self) -> bool:
        """Check whether the result is terminal."""
        return isinstance(self.outcome, Outcome) and self.outcome is not Outcome.UNKNOWN

    def is_win(self) -> bool:
        """Check whether the result is a win."""
        return self.outcome is Outcome.WIN

    def is_loss(self) -> bool:
        """Check whether the result is a loss."""
        return self.outcome is Outcome.LOSS

    def is_draw(self) -> bool:
        """Check whether the result is a draw."""
        return self.outcome is Outcome.DRAW

    def is_success(self) -> bool:
        """Check whether the terminal result is a success."""
        return self.is_win()

    def is_failure(self) -> bool:
        """Check whether the terminal result is a failure."""
        return self.is_loss()

    def is_win_for(self, player: Hashable | Winner) -> bool:
        """Check whether a specific role/player is the winner."""
        return self.is_win() and self.winner == _normalize_winner_identity(player)

    def is_loss_for(self, player: Hashable | Winner) -> bool:
        """Check whether a specific role/player lost to a known winner.

        This helper is role-relative and only reports losses derived from a
        known winner identity. For role-free or single-player failure semantics,
        prefer :meth:`is_failure`.
        """
        player_identity = _normalize_winner_identity(player)
        return self.is_win() and self.winner is not None and self.winner != player_identity

    def is_winner(self, player: Color) -> bool:
        """Compatibility helper for legacy color-based games."""
        assert player in {Color.WHITE, Color.BLACK}
        return self.is_win_for(player)

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
            "legacy_how_over:",
            self.how_over,
            "legacy_who_is_winner:",
            self.who_is_winner,
        )

    def test(self) -> None:
        """Perform a consistency check on the event."""
        self._validate()
