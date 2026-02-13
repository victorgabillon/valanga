"""Tests for the dynamics protocol exports."""

from valanga import Dynamics, ReversibleDynamics, Transition


def test_dynamics_symbols_are_exported():
    """Top-level exports should include dynamics symbols."""
    assert Dynamics is not None
    assert ReversibleDynamics is not None
    assert Transition is not None


def test_transition_defaults():
    """Transition should provide expected default values."""
    transition = Transition(next_state="state")

    assert transition.next_state == "state"
    assert transition.modifications is None
    assert transition.is_over is False
    assert transition.over_event is None
    assert dict(transition.info) == {}


def test_dynamics_protocol_exposes_name_mapping_methods():
    """Dynamics protocols should include both mapping directions."""
    assert hasattr(Dynamics, "action_name")
    assert hasattr(Dynamics, "action_from_name")
    assert hasattr(ReversibleDynamics, "action_name")
    assert hasattr(ReversibleDynamics, "action_from_name")
