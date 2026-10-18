# ss027-raft-consensus-sim

Deterministic, single-process simulation of the Raft consensus protocol
in stdlib-only Python, graded by an exhaustive seeded-schedule invariant
sweep. See `build/` in the task tree for the task contract; this repo is
the scaffold the solver starts from.

## Layout

- `raftsim/` -- the simulation library (`types`, `transport`, `storage`,
  `node`, `cluster`).
- `tools/raftcheck` -- shell entrypoint for the schedule-replay CLI.
- `tools/raftcheck.py` -- the explorer core (seeded schedules plus the
  four executable safety invariants).
- `tests/` -- scaffold smoke tests plus the graded suite (installed at
  grade time).

## Reproduce

```sh
pip install -r requirements-lock.txt
pytest tests/ -q            # from the repo root
tools/raftcheck --help
tools/raftcheck --seed 0 --count 1500
```

Every run is deterministic in its seed: no network, no wall clock.
