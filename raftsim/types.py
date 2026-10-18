"""Shared value types and protocol constants for the Raft simulation.

All timing is expressed in virtual-clock ticks. Tunables below are the
page-stated contract between the library, the ``raftcheck`` explorer and
the graded tests: do not change their values without updating every
consumer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# Election timeout range (ticks). Every follower draws a fresh uniform
# timeout from [ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX] on every
# reset, using only its seeded RNG. Fixed or wall-clock timeouts are
# not permitted: simultaneously timing-out followers split the vote and
# livelock the cluster.
ELECTION_TIMEOUT_MIN = 15
ELECTION_TIMEOUT_MAX = 30

# Leader heartbeat period (ticks). Strictly smaller than
# ELECTION_TIMEOUT_MIN so a live leader suppresses elections.
HEARTBEAT_INTERVAL = 5

# Snapshotting threshold. A node compacts its log once the number of
# retained (post-snapshot) log entries reaches SNAPSHOT_THRESHOLD.
SNAPSHOT_THRESHOLD = 64

# Default schedule-explorer budget: seeds [0, SWEEP_SEED_COUNT) are the
# graded sweep. The explorer accepts other ranges via --seed/--count.
SWEEP_SEED_COUNT = 1500


class Role:
    """Node roles. Plain strings so traces and fixtures stay readable."""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


# RPC kinds carried by Message.kind.
REQUEST_VOTE = "request_vote"
REQUEST_VOTE_RESPONSE = "request_vote_response"
APPEND_ENTRIES = "append_entries"
APPEND_ENTRIES_RESPONSE = "append_entries_response"
INSTALL_SNAPSHOT = "install_snapshot"
INSTALL_SNAPSHOT_RESPONSE = "install_snapshot_response"


@dataclass
class LogEntry:
    """One replicated log record. Indices are 1-based; index 0 is the
    virtual slot occupied by the latest snapshot point."""

    index: int
    term: int
    command: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"index": self.index, "term": self.term, "command": self.command}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        return cls(
            index=int(data["index"]),
            term=int(data["term"]),
            command=dict(data["command"]),
        )


@dataclass
class Message:
    """One RPC request or response between two nodes."""

    kind: str
    frm: str
    to: str
    term: int
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "from": self.frm,
            "to": self.to,
            "term": self.term,
            "payload": self.payload,
        }


@dataclass
class Envelope:
    """A message queued in the transport with its delivery stamp."""

    deliver_at: int
    seq: int
    message: Message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deliver_at": self.deliver_at,
            "seq": self.seq,
            "message": self.message.to_dict(),
        }


def initial_configuration(node_ids: List[str]) -> Dict[str, Any]:
    """The single-server equivalent of the initial cluster config."""
    members = sorted(node_ids)
    return {"old": list(members), "new": list(members)}
