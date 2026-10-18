"""Durable log (WAL) and snapshot persistence.

Implemented in the golden patch. The contract below is what the node
state machine, the cluster harness and the graded tests program against:

- :class:`DurableLog` appends every mutation to a per-node write-ahead
  log and replays it on restart, so ``current_term``, ``voted_for`` and
  the full entry log survive simulated crashes.
- :class:`SnapshotStore` atomically persists snapshots (last included
  index/term plus the serialized state machine) and truncates only the
  log prefix the snapshot covers on install.
"""

from __future__ import annotations


class DurableLog:
    """Write-ahead log for one node's persistent Raft state."""

    def __init__(self, path: str) -> None:
        self.path = path

    @classmethod
    def load(cls, path: str) -> "DurableLog":
        raise NotImplementedError


class SnapshotStore:
    """Atomic snapshot persistence for one node."""

    def __init__(self, path: str) -> None:
        self.path = path

    @classmethod
    def load(cls, path: str) -> "SnapshotStore":
        raise NotImplementedError
