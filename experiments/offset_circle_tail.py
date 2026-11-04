"""Exclude every endpoint offset triple for M >= 270,000.

An expanded conormal-front cover supplies a complete list of possible
three-arc products. Homogeneous circle equations and circumradius bounds
close products that expanded boxes alone cannot exclude. Exact rational
arithmetic only; no hints or archived roots. See parallel_offset.md.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

from blend_cusps import Interval as I, require
from normal_front import dot
from normal_front_census import ACCELERATION, FrontCensus, disjoint
from offset_tail import ExpandedFront

EPSILON = Q(1, 100)
THRESHOLD = 2700 / EPSILON


def compact(interval):
    denominator = 2 ** 80
    result = I(Q((interval.low * denominator) // 1, denominator),
               Q(-((-interval.high * denominator) // 1), denominator))
    require(result.low <= interval.low <= interval.high <= result.high,
            "Dyadic rounding narrowed a circle-jet enclosure.")
    return result


def determinant(rows):
    a, b, c = rows
    return ((a[0] * b[1] - a[1] * b[0]) * c[2]
            + (a[1] * b[2] - a[2] * b[1]) * c[0]
            + (a[2] * b[0] - a[0] * b[2]) * c[1])


def strict(interval):
    return interval.low > 0 or interval.high < 0


def circle_exclusion(data, threshold):
    """Exclude all circles tangent to three complete point/velocity boxes.

    A common center P makes each tangent row (v_x,v_y,q.v) and chord
    row (2dq_x,2dq_y,d|q|²) orthogonal to (P_x,P_y,-1). Every 3x3 minor
    must vanish. Nonzero minors need no division, including at collinear
    point triples. A nonsingular chord matrix also bounds the one circle
    through the three points, without assuming tangency.
    """
    require(type(threshold) is Q and threshold > 0, "Use a positive rational tail threshold.")
    require(len(data) == 3, "A circle product needs three visits.")
    tangent = [[*v, dot(p, v)] for p, v in data]
    if strict(determinant(tangent)):
        return "normal_concurrency"
    points = [p for p, _ in data]
    chords = [[2 * (points[j][k] - points[0][k]) for k in (0, 1)]
              + [dot(points[j], points[j]) - dot(points[0], points[0])]
              for j in (1, 2)]
    a, b = chords
    denominator = a[0] * b[1] - a[1] * b[0]
    if strict(denominator):
        X = (a[2] * b[1] - b[2] * a[1]) / denominator
        Y = (a[0] * b[2] - b[0] * a[2]) / denominator
        radius = (points[0][0] - X, points[0][1] - Y)
        if dot(radius, radius).high < threshold * threshold:
            return "radius_bound"
    for row in tangent:
        if strict(determinant([*chords, row])):
            return "circle_minor"
    for chord in chords:
        for first, second in combinations(tangent, 2):
            if strict(determinant([chord, first, second])):
                return "mixed_minor"
    return None


class CircleTail(ExpandedFront):
    def bounds(self, domain):
        box = FrontCensus.bounds(self, domain)
        return tuple(x + I(-e, e) for x, e in zip(box, (EPSILON, EPSILON, 900 * EPSILON)))

    @lru_cache(maxsize=32768)
    def jets(self, domain):
        quarter, low, high = domain
        require(type(quarter) is int and 0 <= quarter < 4
                and type(low) is Q and type(high) is Q and 0 <= low < high <= 1,
                "Use a nonempty rational circle-chart interval.")
        middle, radius_t = (low + high) / 2, high - low
        position, _, raw = self.evaluator.evaluate(quarter, middle)
        velocity = (-Q(raw[1], raw[2]), Q(raw[0], raw[2]))
        remainder = ACCELERATION * radius_t * radius_t / 2
        points = [I.wrap(p) + v * I(-radius_t, radius_t) + I(-remainder, remainder)
                  for p, v in zip(position, velocity)]
        velocities = [I(v - ACCELERATION * radius_t, v + ACCELERATION * radius_t) for v in velocity]
        return tuple(map(compact, points)), tuple(map(compact, velocities))


def prove(inner, max_depth=36):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(type(max_depth) is int and max_depth >= 0, "Use a nonnegative depth limit.")
    started, stats = monotonic(), Counter()
    cover = CircleTail(inner, max_depth=max_depth)
    try:
        grid, pairs = cover.candidates()
        adjacency = defaultdict(set)
        for first, second in pairs:
            adjacency[first].add(second)
        candidates = [(grid[a], grid[b], grid[c]) for a in sorted(adjacency)
                      for b in sorted(adjacency[a]) for c in sorted(adjacency[a] & adjacency[b])]
        print(f"11/{inner}: {len(pairs)} expanded pairs, {len(candidates)} complete triple products.", flush=True)
        pending = [(domains, 0) for domains in candidates]
        while pending:
            domains, depth = pending.pop()
            stats["max_depth"] = max(stats["max_depth"], depth)
            boxes = [cover.bounds(d) for d in domains]
            if any(any(disjoint(a, b) for a, b in zip(boxes[i], boxes[j]))
                   for i in range(3) for j in range(i)):
                stats["front_exclusion"] += 1
                continue
            reason = circle_exclusion([cover.jets(d) for d in domains], THRESHOLD)
            if reason:
                stats[reason] += 1
                continue
            require(depth < max_depth, "An unresolved circle product rejects the tail proof.")
            stats["bisections"] += 1
            axis = max(range(3), key=lambda i: domains[i][2] - domains[i][1])
            quarter, low, high = domains[axis]
            middle = (low + high) / 2
            for a, b in ((low, middle), (middle, high)):
                child = list(domains)
                child[axis] = (quarter, a, b)
                pending.append((tuple(child), depth + 1))
        leaves = sum(stats[k] for k in ("front_exclusion", "radius_bound", "normal_concurrency",
                                       "circle_minor", "mixed_minor"))
        require(leaves == len(candidates) + stats["bisections"], "The complete binary cover lost a leaf.")
        print(f"11/{inner}: no triple at any M >= {int(THRESHOLD)}; {dict(stats)}; "
              f"{monotonic() - started:.2f}s.", flush=True)
        return {"inner": inner, "pairs": len(pairs), "triple_products": len(candidates), "cover": dict(stats)}
    finally:
        CircleTail.jets.cache_clear()
        FrontCensus.bounds.cache_clear()
        cover.evaluator.evaluate.cache_clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", type=int, choices=(6, 8))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    require(not args.write or args.inner is None, "The saved theorem requires both endpoints.")
    require(THRESHOLD == 270000 and ACCELERATION == 245 + 16940 + 65 * 64,
            "The stated tail or acceleration bound changed.")
    started = monotonic()
    endpoints = [prove(inner) for inner in ((args.inner,) if args.inner is not None else (6, 8))]
    if args.write:
        record = {"scope": "Complete endpoint exclusion of every triple or higher meeting for all M>=270000. No finite-interval event count or middle-family threshold.",
                  "threshold": str(THRESHOLD), "front_expansion": str(EPSILON), "endpoints": endpoints}
        (Path(__file__).resolve().parent / "offset_circle_tail.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Elapsed {monotonic() - started:.2f}s.")


if __name__ == "__main__":
    main()
