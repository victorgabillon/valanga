"""Protocols for checkpoint-oriented state reconstruction.

Checkpoint reconstruction is a persistence concern, so it lives outside
``Dynamics``, which remains focused on transition semantics. Some domains can
reconstruct states directly from reversible tags, while others need structured
or otherwise domain-specific payloads.
"""

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Protocol, TypeVar

from .game import BranchKey, StateTag

StateT = TypeVar("StateT")
TagT = TypeVar("TagT", bound=Hashable)
AnchorRefT = TypeVar("AnchorRefT")
DeltaRefT = TypeVar("DeltaRefT")

__all__ = [
    "CheckpointStateSummary",
    "IncrementalStateCheckpointCodec",
    "StateCheckpointCodec",
    "StateCheckpointSummaryCodec",
    "StateFromTagResolver",
]


@dataclass(frozen=True, slots=True)
class CheckpointStateSummary:
    """Small optional metadata about a state at checkpoint time.

    This structure is intentionally tiny. Higher-level systems can persist it
    beside a whole-state reference, an anchor reference, or a parent/delta
    record so they can inspect common state facts without materializing the
    full state again.

    All fields are optional because some domains cannot provide every summary
    value cheaply or at all.
    """

    tag: StateTag | None = None
    is_terminal: bool | None = None


class StateCheckpointCodec[StateT](Protocol):
    """Dump and load state references for checkpoint persistence.

    Implementations may use a reversible tag, a structured payload, or another
    small domain-specific reference. This remains separate from ``Dynamics``
    because persistence is optional and ``State.tag`` is not universally
    sufficient to reconstruct a concrete state.
    """

    def dump_state_ref(self, state: StateT) -> object:
        """Return a checkpoint reference payload for ``state``."""
        ...

    def load_state_ref(self, payload: object) -> StateT:
        """Reconstruct a state from a checkpoint reference payload."""
        ...


class StateCheckpointSummaryCodec[StateT](Protocol):
    """Optional companion protocol for producing cheap checkpoint summaries.

    This protocol is intentionally separate from ``StateCheckpointCodec`` and
    ``IncrementalStateCheckpointCodec`` because summary support is useful but
    not universal. Implementations can expose a small summary while a concrete
    state is already available at checkpoint time, and higher-level systems can
    later store or reuse that summary without forcing full state restoration.
    """

    def dump_state_summary(self, state: StateT) -> CheckpointStateSummary:
        """Return a small optional summary for ``state``."""
        ...


class IncrementalStateCheckpointCodec[StateT, AnchorRefT, DeltaRefT](Protocol):
    """Checkpoint codec for parent/delta reconstruction with periodic anchors.

    This protocol extends the checkpoint surface beyond whole-state round trips.
    It supports:

    - explicit anchor snapshots that can reconstruct a state on their own
    - parent-to-child deltas for incremental reconstruction
    - optional branch context when a domain can use it to encode a delta

    Higher-level systems such as Anemone can decide when to record anchors,
    when to store deltas, and how to manage lazy state handles. Valanga keeps
    this protocol focused on the domain-facing reconstruction operations only.
    """

    def dump_anchor_ref(self, state: StateT) -> AnchorRefT:
        """Return an anchor payload that can reconstruct ``state`` directly."""
        ...

    def load_anchor_ref(self, payload: AnchorRefT) -> StateT:
        """Reconstruct a state from an anchor payload."""
        ...

    def dump_delta_from_parent(
        self,
        *,
        parent_state: StateT,
        child_state: StateT,
        branch_from_parent: BranchKey | None = None,
    ) -> DeltaRefT:
        """Return a delta payload that reconstructs ``child_state`` from ``parent_state``.

        ``branch_from_parent`` is optional domain context for codecs that can
        derive a more compact or clearer delta when the parent-to-child branch
        identity is known.
        """

        ...

    def load_child_from_delta(
        self,
        *,
        parent_state: StateT,
        delta_ref: DeltaRefT,
    ) -> StateT:
        """Reconstruct a child state from ``parent_state`` and ``delta_ref``."""
        ...


class StateFromTagResolver[StateT, TagT](Protocol):
    """Reconstruct states from reversible tags in domains where that is enough.

    This helper protocol is intentionally narrower than
    ``StateCheckpointCodec`` and does not imply that every domain can use
    ``State.tag`` as its checkpoint payload.
    """

    def state_from_tag(self, tag: TagT) -> StateT:
        """Reconstruct a state from a reversible tag."""
        ...
