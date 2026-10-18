"""raftsim -- deterministic, single-process Raft consensus simulation.

The library models the Raft protocol (leader election, log replication,
persistence, membership change and snapshotting) on top of a virtual clock
and an in-process message transport, so every execution is fully
reproducible from its seed: no network, no wall-clock time, no live
randomness.

Modules:

- :mod:`raftsim.types` -- shared value types and protocol constants.
- :mod:`raftsim.transport` -- :class:`VirtualClock` and :class:`Transport`.
- :mod:`raftsim.storage` -- durable log (WAL) and snapshot persistence.
- :mod:`raftsim.node` -- the Raft node state machine.
- :mod:`raftsim.cluster` -- multi-node cluster harness used by the tests.
"""

__version__ = "0.1.0"
