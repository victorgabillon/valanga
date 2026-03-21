# valanga

![Python 3.13](https://img.shields.io/badge/python-3.13-blue?logo=python)
[![Tests](https://github.com/victorgabillon/valanga/actions/workflows/ci.yaml/badge.svg?label=tests)](https://github.com/victorgabillon/valanga/actions/workflows/ci.yaml)
[![License: GPL v3](https://img.shields.io/github/license/victorgabillon/valanga)](LICENSE)

Shared Python types and lightweight utilities for describing turn-based games and their evaluations. The package exposes protocols for representing states, outcomes, and state representations that other libraries can build on.

## Key concepts
- **Game primitives**: `State`, `HasTurn[RoleT]`, and `TurnState[RoleT]` model states and acting roles. `Color` remains the natural role type for black/white games, while `SoloRole` supports single-player sequential games without fake color semantics. 【F:src/valanga/game.py†L1-L189】
- **Evaluations**: `Value` carries a score, certainty level, and optional terminal `OverEvent` metadata. 【F:src/valanga/evaluations.py†L31-L47】
- **Game termination**: `OverEvent` stores `outcome`, `termination`, and optional `winner` metadata. 【F:src/valanga/over_event.py†L1-L99】
- **State representations**: `ContentRepresentation` defines how to turn a `State` into evaluator input, and `RepresentationFactory` builds or updates those representations from states and modifications. 【F:src/valanga/represention_for_evaluation.py†L9-L22】【F:src/valanga/representation_factory.py†L7-L55】
- **Progress reporting**: `PlayerProgressMessage` is a Color-specific helper for per-player progress reporting. It is not part of the core generic role model. 【F:src/valanga/progress_messsage.py†L1-L13】

## Installation
```bash
pip install .
```
The project targets Python 3.13 and has no required runtime dependencies.

## Quick start
Below is a minimal example that records both a two-player terminal result and a single-player terminal result:
```python
from enum import Enum, auto

from valanga import Color, Outcome, OverEvent


class ChessTermination(Enum):
    CHECKMATE = auto()


class PuzzleTermination(Enum):
    GOAL_REACHED = auto()


# Two-player result: white wins by checkmate.
checkmate = OverEvent(
    outcome=Outcome.WIN,
    termination=ChessTermination.CHECKMATE,
    winner=Color.WHITE,
)

# Single-player result: the puzzle objective was reached.
puzzle_clear = OverEvent(
    outcome=Outcome.WIN,
    termination=PuzzleTermination.GOAL_REACHED,
)

print(checkmate.is_win_for(Color.WHITE))  # -> True
print(puzzle_clear.is_success())  # -> True
```

To wire in a custom state representation, supply callables to `RepresentationFactory` that know how to build representations from a `State` and its modifications.

## Development
Install the development dependencies and run the test suite:
```bash
pip install -e '.[dev]'
pytest
```
