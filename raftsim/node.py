"""The Raft node state machine: election, replication, membership, snapshots.

Implemented in the golden patch. The constructor signature below is
stable: the cluster harness and the graded tests build nodes through it.

- Election over the virtual clock: followers time out, candidates
  request votes, at most one leader per term (Election Safety).
- AppendEntries replication with Log Matching, Leader Completeness and
  State Machine Safety; an old-term entry commits only via a
  current-term commitment, never by counting old-term replicas.
- Single-node membership change with joint-consensus transitions and
  snapshotting that truncates only the covered log prefix.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .types import Role


class RaftNode:
    """One Raft server. All timing comes from ``clock``; all randomness
    from ``rng`` (seeded); all I/O goes through ``transport``/``store``."""

    def __init__(
        self,
        node_id: str,
        peers: List[str],
        clock,
        transport,
        store,
        rng,
    ) -> None:
        self.node_id = node_id
        self.peers = list(peers)
        self.clock = clock
        self.transport = transport
        self.store = store
        self.rng = rng
        self.role = Role.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None

    # -- protocol entry points (golden patch) -----------------------------
    def start(self) -> None:
        """Take office as a follower: schedule the first election timer."""
        raise NotImplementedError

    def on_message(self, message) -> None:
        """Dispatch one delivered RPC."""
        raise NotImplementedError

    def client_write(self, command: Dict[str, Any]) -> bool:
        """Replicate a client command. True when this node is the leader."""
        raise NotImplementedError
