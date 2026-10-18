"""Multi-node cluster harness: topology, faults and schedule stepping.

The scaffold owns the shared machinery -- the virtual clock, the
transport, the seeded RNGs and the node registry -- so smoke tests can
build clusters. The golden patch adds the protocol orchestration used
by the graded suite: deterministic stepping, partitions, restarts,
client writes, membership change and the executable invariant checkers.
"""

from __future__ import annotations

import os
import random
import tempfile
import zlib
from typing import Dict, List, Optional

from .node import RaftNode
from .storage import DurableLog
from .transport import Transport, VirtualClock


class Cluster:
    """A named set of nodes sharing one clock and one transport."""

    def __init__(
        self,
        node_ids: List[str],
        seed: int = 0,
        storage_dir: Optional[str] = None,
    ) -> None:
        self.node_ids = list(node_ids)
        self.seed = seed
        self.storage_dir = storage_dir or tempfile.mkdtemp(prefix="raftsim-")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.clock = VirtualClock()
        self.transport = Transport(self.clock)
        self.rng = random.Random(seed)
        self.nodes: Dict[str, RaftNode] = {}
        for node_id in self.node_ids:
            self.nodes[node_id] = self._build_node(node_id)

    def _node_rng(self, node_id: str) -> random.Random:
        # zlib.crc32, not hash(): str.__hash__ is salted per process and
        # would make seeded runs irreproducible across processes.
        stream = zlib.crc32(f"{self.seed}/{node_id}".encode("utf-8"))
        return random.Random((self.seed * 7919 + stream) & 0xFFFFFFFF)

    def _store_for(self, node_id: str) -> DurableLog:
        return DurableLog(os.path.join(self.storage_dir, f"node-{node_id}.wal"))

    def _build_node(self, node_id: str) -> RaftNode:
        peers = [other for other in self.node_ids if other != node_id]
        return RaftNode(
            node_id,
            peers,
            self.clock,
            self.transport,
            self._store_for(node_id),
            self._node_rng(node_id),
        )
