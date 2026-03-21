"""Progress-message helpers.

`PlayerProgressMessage` is a Color-specific helper for two-player progress
reporting. It is not part of the core generic role model.
"""

from dataclasses import dataclass

from .game import Color


@dataclass
class PlayerProgressMessage:
    """Represents per-player progress information for Color-based callers."""

    progress_percent: int | None
    player_color: Color
