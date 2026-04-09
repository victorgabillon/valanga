"""Tests for checkpoint protocol exports and usage."""

from dataclasses import dataclass
from typing import cast

import valanga
from valanga import StateCheckpointCodec, StateFromTagResolver
from valanga.checkpoints import (
    StateCheckpointCodec as ModuleStateCheckpointCodec,
)
from valanga.checkpoints import StateFromTagResolver as ModuleStateFromTagResolver


@dataclass(frozen=True)
class FakeState:
    """Toy state used to exercise structured checkpoint payloads."""

    x: int
    y: str


class FakeStateCodec(StateCheckpointCodec[FakeState]):
    """Checkpoint codec that stores a small structured payload."""

    def dump_state_ref(self, state: FakeState) -> object:
        """Return a reversible structured payload."""
        return {"x": state.x, "y": state.y}

    def load_state_ref(self, payload: object) -> FakeState:
        """Reconstruct the state from its structured payload."""
        data = cast(dict[str, object], payload)
        return FakeState(x=cast(int, data["x"]), y=cast(str, data["y"]))


@dataclass(frozen=True)
class TagState:
    """Toy state whose tag fully identifies the state."""

    tag: int


class TagResolver(StateFromTagResolver[TagState, int]):
    """Resolver for domains where a reversible tag is enough."""

    def state_from_tag(self, tag: int) -> TagState:
        """Reconstruct the state directly from its reversible tag."""
        return TagState(tag=tag)


def round_trip[StateT](
    codec: StateCheckpointCodec[StateT],
    state: StateT,
) -> StateT:
    """Round-trip a state through a generic checkpoint codec."""
    return codec.load_state_ref(codec.dump_state_ref(state))


def test_checkpoint_symbols_are_exported() -> None:
    """Checkpoint protocols should be available from public import paths."""
    assert StateCheckpointCodec is ModuleStateCheckpointCodec
    assert StateFromTagResolver is ModuleStateFromTagResolver
    assert {"StateCheckpointCodec", "StateFromTagResolver"}.issubset(
        set(valanga.__all__)
    )


def test_structured_checkpoint_payload_round_trip() -> None:
    """Structured checkpoint payloads should reconstruct the original state."""
    codec = FakeStateCodec()
    state = FakeState(x=3, y="north")

    payload = codec.dump_state_ref(state)

    assert payload == {"x": 3, "y": "north"}
    assert codec.load_state_ref(payload) == state


def test_checkpoint_codec_is_usable_in_generic_code() -> None:
    """Generic helper code should be able to use the checkpoint codec protocol."""
    codec = FakeStateCodec()
    state = FakeState(x=7, y="south")

    assert round_trip(codec, state) == state


def test_state_from_tag_resolver_reconstructs_reversible_tags() -> None:
    """Tag-based reconstruction remains an optional narrower helper."""
    resolver = TagResolver()

    assert resolver.state_from_tag(11) == TagState(tag=11)
