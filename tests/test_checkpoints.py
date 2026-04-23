"""Tests for checkpoint protocol exports and usage."""

from dataclasses import dataclass
from typing import cast

import valanga
from valanga import (
    CheckpointStateSummary,
    IncrementalStateCheckpointCodec,
    StateCheckpointCodec,
    StateCheckpointSummaryCodec,
    StateFromTagResolver,
)
from valanga.checkpoints import (
    CheckpointStateSummary as ModuleCheckpointStateSummary,
    IncrementalStateCheckpointCodec as ModuleIncrementalStateCheckpointCodec,
    StateCheckpointCodec as ModuleStateCheckpointCodec,
    StateCheckpointSummaryCodec as ModuleStateCheckpointSummaryCodec,
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


class FakeStateSummaryCodec(StateCheckpointSummaryCodec[FakeState]):
    """Summary codec that exposes cheap checkpoint metadata."""

    def dump_state_summary(self, state: FakeState) -> CheckpointStateSummary:
        """Return a tiny summary for the state."""
        return CheckpointStateSummary(tag=(state.x, state.y), is_terminal=False)


class FakeIncrementalCodec(
    IncrementalStateCheckpointCodec[FakeState, dict[str, object], int, str]
):
    """Incremental codec using whole-state anchors and integer deltas."""

    def dump_anchor_ref(self, state: FakeState) -> dict[str, object]:
        """Store an anchor as a whole-state structured payload."""
        return {"x": state.x, "y": state.y}

    def load_anchor_ref(self, payload: dict[str, object]) -> FakeState:
        """Restore an anchor payload."""
        return FakeState(x=cast(int, payload["x"]), y=cast(str, payload["y"]))

    def dump_delta_from_parent(
        self,
        *,
        parent_state: FakeState,
        child_state: FakeState,
        branch_from_parent: str | None = None,
    ) -> int:
        """Encode only the integer delta between parent and child."""
        del branch_from_parent
        assert parent_state.y == child_state.y
        return child_state.x - parent_state.x

    def load_child_from_delta(
        self,
        *,
        parent_state: FakeState,
        delta_ref: int,
    ) -> FakeState:
        """Apply the integer delta to the parent state."""
        return FakeState(x=parent_state.x + delta_ref, y=parent_state.y)


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


def rebuild_child[StateT, AnchorRefT, DeltaRefT, BranchRefT](
    codec: IncrementalStateCheckpointCodec[StateT, AnchorRefT, DeltaRefT, BranchRefT],
    *,
    parent_state: StateT,
    child_state: StateT,
) -> StateT:
    """Rebuild a child through the incremental checkpoint protocol."""
    delta_ref = codec.dump_delta_from_parent(
        parent_state=parent_state,
        child_state=child_state,
    )
    return codec.load_child_from_delta(parent_state=parent_state, delta_ref=delta_ref)


def test_checkpoint_symbols_are_exported() -> None:
    """Checkpoint protocols should be available from public import paths."""
    assert CheckpointStateSummary is ModuleCheckpointStateSummary
    assert IncrementalStateCheckpointCodec is ModuleIncrementalStateCheckpointCodec
    assert StateCheckpointCodec is ModuleStateCheckpointCodec
    assert StateCheckpointSummaryCodec is ModuleStateCheckpointSummaryCodec
    assert StateFromTagResolver is ModuleStateFromTagResolver
    assert {
        "CheckpointStateSummary",
        "IncrementalStateCheckpointCodec",
        "StateCheckpointCodec",
        "StateCheckpointSummaryCodec",
        "StateFromTagResolver",
    }.issubset(set(valanga.__all__))


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


def test_checkpoint_state_summary_defaults_are_optional() -> None:
    """Checkpoint summaries should allow partial metadata."""
    assert CheckpointStateSummary() == CheckpointStateSummary(
        tag=None, is_terminal=None
    )


def test_checkpoint_state_summary_codec_produces_small_metadata() -> None:
    """Summary codecs should expose cheap checkpoint-time metadata."""
    summary = FakeStateSummaryCodec().dump_state_summary(FakeState(x=5, y="east"))

    assert summary == CheckpointStateSummary(tag=(5, "east"), is_terminal=False)


def test_incremental_checkpoint_codec_reconstructs_child_from_parent_delta() -> None:
    """Incremental codecs should support parent-plus-delta reconstruction."""
    codec = FakeIncrementalCodec()
    parent_state = FakeState(x=10, y="lane")
    child_state = FakeState(x=14, y="lane")

    assert (
        rebuild_child(
            codec,
            parent_state=parent_state,
            child_state=child_state,
        )
        == child_state
    )


def test_incremental_checkpoint_codec_restores_anchor_snapshots() -> None:
    """Incremental codecs should also support self-contained anchor snapshots."""
    codec = FakeIncrementalCodec()
    state = FakeState(x=9, y="west")

    assert codec.load_anchor_ref(codec.dump_anchor_ref(state)) == state


def test_state_from_tag_resolver_reconstructs_reversible_tags() -> None:
    """Tag-based reconstruction remains an optional narrower helper."""
    resolver = TagResolver()

    assert resolver.state_from_tag(11) == TagState(tag=11)
