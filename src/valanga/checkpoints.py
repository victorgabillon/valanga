"""Protocols for checkpoint-oriented state reconstruction.

Checkpoint reconstruction is a persistence concern, so it lives outside
``Dynamics``, which remains focused on transition semantics. Some domains can
reconstruct states directly from reversible tags, while others need structured
or otherwise domain-specific payloads.
"""

from collections.abc import Hashable
from typing import Protocol, TypeVar

StateT = TypeVar("StateT")
TagT = TypeVar("TagT", bound=Hashable)

__all__ = ["StateCheckpointCodec", "StateFromTagResolver"]


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


class StateFromTagResolver[StateT, TagT](Protocol):
    """Reconstruct states from reversible tags in domains where that is enough.

    This helper protocol is intentionally narrower than
    ``StateCheckpointCodec`` and does not imply that every domain can use
    ``State.tag`` as its checkpoint payload.
    """

    def state_from_tag(self, tag: TagT) -> StateT:
        """Reconstruct a state from a reversible tag."""
        ...
