"""Virtual clock and in-process message transport.

Both are deterministic: time advances only through :meth:`VirtualClock.advance`
and messages are delivered in ``(deliver_at, seq)`` order. Nothing here reads
the wall clock or draws live randomness.
"""

from __future__ import annotations

import heapq
import itertools
from typing import Callable, Dict, List, Optional, Set, Tuple

from .types import Envelope, Message


class VirtualClock:
    """A discrete tick counter with a timer heap.

    Callbacks scheduled with :meth:`schedule` fire when the clock reaches
    their tick, in ``(fire_at, seq)`` order. A callback may schedule new
    timers; those fire on later ticks only, never re-entrantly.
    """

    def __init__(self) -> None:
        self.now = 0
        self._heap: List[Tuple[int, int, int, Callable[[], None]]] = []
        self._ids = itertools.count(1)
        self._cancelled: Set[int] = set()

    def schedule(
        self, delay_ticks: int, callback: Callable[[], None], owner: Optional[str] = None
    ) -> int:
        """Schedule ``callback`` ``delay_ticks`` ticks from now. Returns a
        timer id suitable for :meth:`cancel`. Non-positive delays fire on
        the next :meth:`advance` call."""
        timer_id = next(self._ids)
        fire_at = self.now + max(0, int(delay_ticks))
        heapq.heappush(self._heap, (fire_at, timer_id, timer_id, callback))
        return timer_id

    def cancel(self, timer_id: int) -> None:
        """Cancel a pending timer. Unknown or already-fired ids are ignored."""
        self._cancelled.add(timer_id)

    def pending_count(self, owner: Optional[str] = None) -> int:
        return sum(
            1
            for _, tid, _, _ in self._heap
            if tid not in self._cancelled
        )

    def advance(self, steps: int = 1) -> None:
        """Advance the clock by ``steps`` ticks, firing due timers."""
        for _ in range(max(0, int(steps))):
            self.now += 1
            while self._heap and self._heap[0][0] <= self.now:
                _, timer_id, _, callback = heapq.heappop(self._heap)
                if timer_id in self._cancelled:
                    self._cancelled.discard(timer_id)
                    continue
                callback()


class Transport:
    """Deterministic message queue between nodes.

    :meth:`send` stamps a message for delivery ``delay`` ticks later;
    :meth:`pump` returns every message whose tick has arrived, in
    ``(deliver_at, seq)`` order. A partitioned link HOLDS its messages
    (they stay queued until healed); a blackholed link DROPS them.
    """

    def __init__(self, clock: VirtualClock) -> None:
        self.clock = clock
        self._heap: List[Tuple[int, int, Envelope]] = []
        self._seq = itertools.count()
        self._partitions: Set[frozenset] = set()
        self._blackholes: Set[Tuple[str, str]] = set()

    # -- fault injection -------------------------------------------------
    def partition(self, first: str, second: str) -> None:
        """Hold messages in both directions between two nodes."""
        self._partitions.add(frozenset((first, second)))

    def heal(self, first: str, second: str) -> None:
        self._partitions.discard(frozenset((first, second)))

    def set_blackhole(self, frm: str, to: str, on: bool = True) -> None:
        """Drop (or stop dropping) messages from ``frm`` to ``to``."""
        if on:
            self._blackholes.add((frm, to))
        else:
            self._blackholes.discard((frm, to))

    def partitioned(self, first: str, second: str) -> bool:
        return frozenset((first, second)) in self._partitions

    # -- data path --------------------------------------------------------
    def send(self, message: Message, delay: int = 1) -> Envelope:
        envelope = Envelope(
            deliver_at=self.clock.now + max(0, int(delay)),
            seq=next(self._seq),
            message=message,
        )
        heapq.heappush(self._heap, (envelope.deliver_at, envelope.seq, envelope))
        return envelope

    def pending_count(self) -> int:
        return len(self._heap)

    def pump(self) -> List[Message]:
        """Deliver every due message. Returns them in delivery order."""
        due: List[Message] = []
        held: List[Tuple[int, int, Envelope]] = []
        while self._heap and self._heap[0][0] <= self.clock.now:
            _, _, envelope = heapq.heappop(self._heap)
            message = envelope.message
            if (message.frm, message.to) in self._blackholes:
                continue
            if self.partitioned(message.frm, message.to):
                held.append((envelope.deliver_at, envelope.seq, envelope))
                continue
            due.append(message)
        for item in held:
            heapq.heappush(self._heap, item)
        return due

    def drop_all(self, frm: Optional[str] = None, to: Optional[str] = None) -> int:
        """Discard queued messages matching the filter. Returns the count."""
        kept: List[Tuple[int, int, Envelope]] = []
        dropped = 0
        while self._heap:
            deliver_at, seq, envelope = heapq.heappop(self._heap)
            message = envelope.message
            if (frm is None or message.frm == frm) and (
                to is None or message.to == to
            ):
                dropped += 1
                continue
            kept.append((deliver_at, seq, envelope))
        for item in kept:
            heapq.heappush(self._heap, item)
        return dropped
