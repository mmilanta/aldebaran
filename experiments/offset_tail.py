"""Exclude all endpoint offset triples at M >= 2,700,000,000.

Expand the L1 conormal front by epsilon=1e-6 in scaled coordinates.
Every offset triple in that tail would give three expanded front boxes
with a common point. A complete rational product cover excludes them.
The short-arc exclusion uses positive curvature and less than pi tangent
turn, uniformly for all outward offsets. See parallel_offset.md.
Standard library only; no archived roots or numerical hints are used.
"""

from collections import defaultdict
from fractions import Fraction as Q
from time import monotonic

from blend_cusps import Interval as I, require
from normal_front_census import (ACCELERATION, MIN_SPEED, FrontCensus,
                                 controls, disjoint)

EPSILON = Q(1, 10**6)
THRESHOLD = 2700 / EPSILON


class ExpandedFront(FrontCensus):
    def near(self, difference):
        # A strict open velocity half-plane excludes equal offset points.
        # 3 < pi; the older full-turn front exclusion would be too generous.
        return 2 * ACCELERATION * (difference + 1) < 3 * MIN_SPEED * self.K

    def bounds(self, domain):
        box = super().bounds(domain)
        return tuple(x + I(-e, e) for x, e in zip(box, (EPSILON, EPSILON, 900 * EPSILON)))


def prove(inner):
    started = monotonic()
    cover = ExpandedFront(inner)
    try:
        grid, pairs = cover.candidates()
        adjacency = defaultdict(set)
        for first, second in pairs:
            adjacency[first].add(second)
        candidates = []
        for first in sorted(adjacency):
            for second in sorted(adjacency[first]):
                for third in sorted(adjacency[first] & adjacency[second]):
                    candidates.append((grid[first], grid[second], grid[third]))
        pending = [(domains, 0) for domains in candidates]
        leaves = max_depth = 0
        while pending:
            domains, depth = pending.pop()
            max_depth = max(depth, max_depth)
            boxes = [cover.bounds(d) for d in domains]
            if any(any(disjoint(a, b) for a, b in zip(boxes[i], boxes[j]))
                   for i in range(3) for j in range(i)):
                leaves += 1
                continue
            require(depth < 30, "An unresolved expanded triple product rejects the tail proof.")
            axis = max(range(3), key=lambda i: domains[i][2] - domains[i][1])
            quarter, low, high = domains[axis]
            middle = (low + high) / 2
            for a, b in ((low, middle), (middle, high)):
                child = list(domains)
                child[axis] = (quarter, a, b)
                pending.append((tuple(child), depth + 1))
        print(f"11/{inner}: {len(pairs)} expanded pair candidates, {len(candidates)} triple products; {leaves} exclusion leaves, depth {max_depth}, {monotonic() - started:.2f}s.", flush=True)
    finally:
        FrontCensus.bounds.cache_clear()
        cover.evaluator.evaluate.cache_clear()


if __name__ == "__main__":
    controls()
    require(THRESHOLD == 2_700_000_000, "The advertised tail threshold changed.")
    for inner in (6, 8):
        prove(inner)
    print("Both endpoint outward offsets have no triple or higher meeting for every M >= 2700000000. This is a coarse global tail exclusion, not a census below that bound.")
