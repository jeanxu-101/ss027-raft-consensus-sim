"""Scaffold smoke tests: harness machinery that exists before the protocol.

These four tests guard the deterministic substrate (virtual clock,
transport, envelopes, cluster construction) the golden patch builds on.
They pass on the scaffold and must keep passing after the solution.
"""

from raftsim.cluster import Cluster
from raftsim.transport import Transport, VirtualClock
from raftsim.types import Envelope, Message


def test_virtual_clock_advances_deterministically():
    first = VirtualClock()
    second = VirtualClock()
    fired = []
    first.schedule(5, lambda: fired.append(("a", first.now)))
    second.schedule(5, lambda: fired.append(("b", second.now)))
    first.advance(10)
    second.advance(4)
    second.advance(6)
    assert [name for name, _ in fired] == ["a", "b"]
    assert [tick for _, tick in fired] == [5, 5]
    assert (first.now, second.now) == (10, 10)


def test_transport_queues_and_delivers_in_order():
    clock = VirtualClock()
    transport = Transport(clock)
    transport.send(Message("ping", "n1", "n2", 1), delay=3)
    transport.send(Message("ping", "n1", "n2", 1), delay=1)
    transport.send(Message("ping", "n2", "n1", 1), delay=2)
    assert transport.pump() == []
    clock.advance(1)
    first = transport.pump()
    assert [m.to for m in first] == ["n2"]
    clock.advance(2)
    rest = transport.pump()
    assert [(m.frm, m.to) for m in rest] == [("n2", "n1"), ("n1", "n2")]
    assert transport.pending_count() == 0


def test_envelope_shape_is_stable():
    message = Message("append_entries", "n1", "n2", 4, {"prev_index": 7})
    envelope = Envelope(deliver_at=12, seq=3, message=message)
    wire = envelope.to_dict()
    assert wire == {
        "deliver_at": 12,
        "seq": 3,
        "message": {
            "kind": "append_entries",
            "from": "n1",
            "to": "n2",
            "term": 4,
            "payload": {"prev_index": 7},
        },
    }


def test_cluster_builds_named_nodes():
    cluster = Cluster(["n1", "n2", "n3"], seed=11)
    assert sorted(cluster.nodes) == ["n1", "n2", "n3"]
    for node_id, node in cluster.nodes.items():
        assert node.node_id == node_id
        assert sorted(node.peers) == sorted(
            other for other in ("n1", "n2", "n3") if other != node_id
        )
