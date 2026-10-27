"""Runtime contracts used by Python 3.14 annotation consumers."""

from annotationlib import Format, get_annotations
from dataclasses import fields
from typing import get_args, get_origin, get_protocol_members, get_type_hints

import pytest

from valanga import (
    SOLO,
    BranchKeyGeneratorP,
    HasTurn,
    Outcome,
    OverEvent,
    SoloRole,
    StateCheckpointCodec,
    Transition,
    TurnState,
)
from valanga.evaluations import Certainty, Value
from valanga.game import StatePlusHistory, TurnStatePlusHistory
from valanga.policy import BranchSelector
from valanga.represention_for_evaluation import ContentRepresentation


def test_native_protocol_parameters_and_role_defaults() -> None:
    """Native parameters preserve hashable bounds, role defaults and relationships."""
    assert BranchKeyGeneratorP.__type_params__[0].__bound__ is not None
    assert HasTurn.__type_params__[0].has_default()
    assert TurnState.__type_params__[0].has_default()
    assert get_origin(TurnState[SoloRole]) is TurnState
    assert get_args(TurnState[SoloRole]) == (SoloRole,)
    assert get_type_hints(HasTurn.turn.fget)["return"] is HasTurn.__type_params__[0]
    assert (
        get_type_hints(BranchSelector.recommend)["state"]
        is BranchSelector.__type_params__[0]
    )
    assert {"tag", "turn", "is_game_over", "pprint"} <= get_protocol_members(TurnState)
    assert get_protocol_members(StateCheckpointCodec) == {
        "dump_state_ref",
        "load_state_ref",
    }
    assert get_protocol_members(ContentRepresentation) == {"get_evaluator_input"}


def test_dataclass_annotations_and_factory_isolation() -> None:
    """Dataclass types remain resolvable and mutable defaults stay independent."""
    assert get_type_hints(Value)["score"] is float
    assert get_type_hints(OverEvent)["outcome"] is Outcome
    assert get_type_hints(Transition)["next_state"] is Transition.__type_params__[0]
    info = next(f for f in fields(Transition) if f.name == "info")
    assert info.default_factory() == {}
    assert info.doc == "Additional domain-specific transition metadata."
    first = Transition(next_state="first")
    second = Transition(next_state="second")
    assert first.info == second.info == {}
    assert first.info is not second.info
    for history_type in (StatePlusHistory, TurnStatePlusHistory):
        kwargs = {"current_state_tag": "root"}
        if history_type is TurnStatePlusHistory:
            kwargs["turn"] = SOLO
        left = history_type(**kwargs)
        right = history_type(**kwargs)
        assert left.historical_actions is not right.historical_actions
        assert left.historical_states is not right.historical_states


def test_deferred_recursive_state_annotations() -> None:
    """Unquoted forward references resolve after a local state is defined."""

    def successor(state: RecursiveState) -> RecursiveState | None:
        return state.next_state

    class RecursiveState:
        next_state: RecursiveState | None = None

    assert successor.__annotations__["state"] is RecursiveState
    assert get_type_hints(successor)["return"] == RecursiveState | None
    assert get_annotations(successor, format=Format.STRING)["state"] == "RecursiveState"
    assert successor(RecursiveState()) is None


def test_terminal_values_keep_existing_semantics() -> None:
    """Evaluation data and terminal events retain their equality and truthiness rules."""
    event = OverEvent[SoloRole](outcome=Outcome.WIN, winner=SOLO)
    value = Value(score=1.0, certainty=Certainty.TERMINAL, over_event=event)
    assert value == Value(score=1.0, certainty=Certainty.TERMINAL, over_event=event)
    assert event.is_success()
    with pytest.raises(ValueError):
        bool(event)
