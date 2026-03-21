"""Progress-message helpers.

`PlayerProgressMessage` remains a Color-oriented helper for existing
two-player integrations. The preferred generalized acting-role model now lives
in :mod:`valanga.game`.
"""

from dataclasses import dataclass

from .game import Color


@dataclass
class PlayerProgressMessage:
    """Represents per-player progress information for Color-based callers."""

    progress_percent: int | None
    player_color: Color
