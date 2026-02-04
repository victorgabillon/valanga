"""Docstring for tests.test_representation_factory."""

from collections import Counter

from valanga.representation_factory import RepresentationFactory


class DummyRepresentation:
    """A dummy representation class for testing purposes."""

    pass


def test_create_from_transition_root_uses_full_creator():
    """At the root, create_from_state should be used even if modifications are None."""
    calls = Counter()

    def create_from_state(state):
        """Mock create_from_state function."""
        calls["create_from_state"] += 1
        return ("state", state)

    factory = RepresentationFactory(
        create_from_state=create_from_state, create_from_state_and_modifications=None
    )

    result = factory.create_from_transition(
        state="root", previous_state_representation=None, modifications=None
    )

    assert result == ("state", "root")
    assert calls["create_from_state"] == 1


def test_create_from_transition_no_modifications_falls_back_to_state():
    """If no modifications are provided, create_from_state should be used."""
    calls = Counter()

    def create_from_state(state):
        calls["create_from_state"] += 1
        return ("state", state)

    factory = RepresentationFactory(
        create_from_state=create_from_state, create_from_state_and_modifications=None
    )

    result = factory.create_from_transition(
        state="child",
        previous_state_representation=DummyRepresentation(),
        modifications=None,
    )

    assert result == ("state", "child")
    assert calls["create_from_state"] == 1


def test_create_from_transition_with_modifications():
    """If modifications are provided, create_from_state_and_modifications should be used."""
    calls = Counter()

    def create_from_state_and_modifications(
        state, state_modifications, previous_state_representation
    ):
        """Mock create_from_state_and_modifications function."""
        calls["create_from_state_and_modifications"] += 1
        return (state, state_modifications, previous_state_representation)

    factory = RepresentationFactory(
        create_from_state=lambda state: ("unused", state),
        create_from_state_and_modifications=create_from_state_and_modifications,
    )

    previous = DummyRepresentation()
    result = factory.create_from_transition(
        state="child", previous_state_representation=previous, modifications="delta"
    )

    assert result == ("child", "delta", previous)
    assert calls["create_from_state_and_modifications"] == 1
