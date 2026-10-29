"""Verify the complete event census of the 11/6 -> 11/8 blend.

Run: python3 experiments/rhythm_route.py --jobs 2
     python3 experiments/rhythm_route.py --write --jobs 2
Standard library only. The default repeats fresh rational proofs on the
archived partition, together with all six continuous event-window proofs.
--write rediscovers a partition; unsuccessful searches never update the
archive. See rhythm_route.md for the proof, controls, and scope.
"""

import argparse
import io
import itertools
import json
import time
from fractions import Fraction as Q
from functools import lru_cache
from contextlib import redirect_stdout
from concurrent.futures import ProcessPoolExecutor, as_completed
from rhythm_passages import (
    Family,
    RhythmBlend,
    WINDOWS,
    overlap,
    contains,
    HERE,
    HINTS as TRIPLES,
    certify_window,
)
from rhythm_tangencies import HINTS
from blend_cusps import require, Interval as I
from phase_unfolding import inverse
from rhythm_touch_windows import certify as certify_contact_window

ARCHIVE = HERE / "rhythm_route.json"


class ShiftedCurve(RhythmBlend):
    """The same orbit, with t replaced by t+2 atan(shift).

    The rational tangent-addition map changes the chart seam without
    changing the curve, weight affinity, or any analytic derivative bound.
    """

    def __init__(self, weight, shift=Q(0), partition=1024):
        super().__init__(weight, partition)
        self.shift = shift

    @lru_cache(maxsize=16384)
    def evaluate(self, q, s):
        c = self.shift
        u = (s + c) / (1 - c * s)
        p, v, raw = RhythmBlend.evaluate(self, q, u)
        factor = (1 + u * u) / (1 + s * s)
        return p, tuple(x * factor for x in v), raw

    def numerical(self, q, s):
        c = float(self.shift)
        u = (s + c) / (1 - c * s)
        p, v = RhythmBlend.numerical(self, q, u)
        return p, v * (1 + u * u) / (1 + s * s)


class ShiftedFamily(Family):
    """Regular product charts and a complete orbit cover on one weight slab."""

    def __init__(self, low, high, shift=Q(0), budget=None):
        super().__init__(low, high)
        self.shift = shift
        self.started = time.process_time()
        self.budget = budget
        self.curve = ShiftedCurve(self.middle, shift)
        self.ends = [ShiftedCurve(Q(a), shift) for a in (0, 1)]

    def charts(self):
        solver = ShiftedCurve(self.low, self.shift)
        try:
            with redirect_stdout(io.StringIO()):
                solver.run()
                solver.refine()
            hints = []
            for A, B, _ in solver.refined:
                x, y = [float((D[1] + D[2]) / 2) for D in (A, B)]
                for _ in range(12):
                    p, v = self.curve.numerical(A[0], x)
                    q, w = self.curve.numerical(B[0], y)
                    f = p - q
                    a, b, c, d = v.real, -w.real, v.imag, -w.imag
                    det = a * d - b * c
                    x -= (d * f.real - b * f.imag) / det
                    y -= (-c * f.real + a * f.imag) / det
                hints.append(
                    (
                        (A[0], Q(round(x * 10**12), 10**12)),
                        (B[0], Q(round(y * 10**12), 10**12)),
                    )
                )
        finally:
            solver.evaluate.cache_clear()
            RhythmBlend.evaluate.cache_clear()
        charts = []
        for (qa, x), (qb, y) in hints:
            for denominator in (
                100000000,
                50000000,
                20000000,
                10000000,
                5000000,
                2000000,
                1000000,
                500000,
                200000,
                100000,
                50000,
                20000,
                10000,
                5000,
                2000,
                1000,
                500,
            ):
                r = Q(1, denominator)
                A, B = (qa, x - r, x + r), (qb, y - r, y + r)
                if (
                    min(A[1], B[1]) > 0
                    and max(A[2], B[2]) < 1
                    and self.contract(A, B) == "root"
                ):
                    wider = ((qa, x - 2 * r, x + 2 * r), (qb, y - 2 * r, y + 2 * r))
                    if (
                        min(wider[0][1], wider[1][1]) > 0
                        and max(wider[0][2], wider[1][2]) < 1
                        and self.contract(*wider) == "root"
                    ):
                        A, B = wider
                    charts.append((A, B))
                    break
            else:
                raise ValueError("root chart")
        require(
            all(
                not (overlap(A, C) and overlap(B, D))
                for j, (A, B) in enumerate(charts)
                for C, D in charts[:j]
            ),
            "product overlap",
        )
        require(
            all(A < B and not overlap(A, B) for A, B in charts),
            "A crossing chart meets its own diagonal",
        )
        self.root_charts = charts
        self.no_triples()
        return charts

    def check_work(self):
        if self.budget is not None:
            require(
                time.process_time() - self.started < self.budget, "search work budget"
            )

    def triple_empty(self, slots, weight, depth=0):
        """Exclude three equal positions by a rational interval Newton image.

        For any zero x in the box, x-center lies in the image below by the
        mean value theorem. One disjoint coordinate excludes every zero;
        no contraction-norm assumption is needed for this exclusion test.
        An inconclusive test subdivides and must exclude BOTH children.
        """
        self.check_work()
        mids = [(D[1] + D[2]) / 2 for D in slots] + [weight.midpoint()]
        radii = [(D[2] - D[1]) / 2 for D in slots] + [(weight.high - weight.low) / 2]
        curve = ShiftedCurve(mids[3], self.shift)
        pts = []
        vs = []
        ds = []
        for D, m, r in zip(slots, mids, radii):
            p, v, _ = curve.evaluate(D[0], m)
            pts.append(p)
            error = 89990 * r + 1820 * radii[3]
            vs.append([I(x - error, x + error) for x in v])
            ds.append(
                [I(x - 1820 * r, x + 1820 * r) for x in self.weight_derivative(D[0], m)]
            )
        F = [pts[0][axis] - pts[j][axis] for j in (1, 2) for axis in (0, 1)]
        J = []
        for j in (1, 2):
            for axis in (0, 1):
                row = [I.wrap(0)] * 4
                row[0] = vs[0][axis]
                row[j] = -vs[j][axis]
                row[3] = ds[0][axis] - ds[j][axis]
                J.append(row)
        R = inverse([[x.midpoint() for x in row] for row in J])
        defect = [
            [Q(i == j) - sum(R[i][k] * J[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)
        ]
        offsets = [
            -sum(R[i][k] * F[k] for k in range(4))
            + sum(defect[i][j] * I(-radii[j], radii[j]) for j in range(4))
            for i in range(4)
        ]
        if any(x.low > r or x.high < -r for x, r in zip(offsets, radii)):
            self.stats["triple_exclusion"] += 1
            return
        require(depth < 20, "triple exclusion depth")
        k = max(range(4), key=lambda j: radii[j])
        if k == 3:
            m = weight.midpoint()
            for half in (I(weight.low, m), I(m, weight.high)):
                self.triple_empty(slots, half, depth + 1)
        else:
            q, low, high = slots[k]
            m = (low + high) / 2
            for half in ((q, low, m), (q, m, high)):
                new = list(slots)
                new[k] = half
                self.triple_empty(new, weight, depth + 1)

    def no_triples(self):
        """Enumerate every possible assignment of three crossing charts.

        Three visits give three distinct crossing charts in a connected
        component of visit-slot overlaps. Components of size <3 cannot
        contain a triple. Larger components are rejected for subdivision.
        All six assignments of a three-chart component to pairs 01/02/12
        are tested, using intersections of their corresponding visit slots.
        """
        charts = self.root_charts
        adj = {j: set() for j in range(len(charts))}
        for j, pair in enumerate(charts):
            for k, other in enumerate(charts[:j]):
                if any(overlap(A, B) for A in pair for B in other):
                    adj[j].add(k)
                    adj[k].add(j)
        seen = set()
        for j in adj:
            if j in seen:
                continue
            group = set()
            pending = [j]
            while pending:
                k = pending.pop()
                if k not in group:
                    group.add(k)
                    pending.extend(adj[k] - group)
            seen.update(group)
            if len(group) < 3:
                continue
            require(len(group) == 3, "large possible triple group")
            for c, d, e in itertools.permutations(group):
                slots = []
                for A, B in (
                    (charts[c][0], charts[d][0]),
                    (charts[c][1], charts[e][0]),
                    (charts[d][1], charts[e][1]),
                ):
                    if not overlap(A, B):
                        break
                    slots.append((A[0], max(A[1], B[1]), min(A[2], B[2])))
                if len(slots) == 3:
                    self.triple_empty(slots, I(self.low, self.high))

    def exclude(self, A, B, depth=0):
        self.check_work()
        if any(contains(C, A) and contains(D, B) for C, D in self.root_charts):
            self.stats["inside_root_chart"] += 1
            return
        a, b = self.bounds(A), self.bounds(B)
        if a[1] < b[0] or b[1] < a[0] or a[3] < b[2] or b[3] < a[2]:
            self.stats["spatial_exclusion"] += 1
            return
        if self.contract(A, B) == "empty":
            self.stats["contraction_exclusion"] += 1
            return
        require(depth < 48, "crossing exclusion depth")
        if A[2] - A[1] < B[2] - B[1]:
            A, B = B, A
        q, low, high = A
        mid = (low + high) / 2
        for half in ((q, low, mid), (q, mid, high)):
            first, second = sorted((half, B))
            self.exclude(first, second, depth + 1)

    def clear(self):
        super().clear()
        RhythmBlend.evaluate.cache_clear()


def leaf(low, high):
    errors = []
    for shift in (Q(0), Q(1, 3)):
        f = ShiftedFamily(low, high, shift, budget=4)
        try:
            with redirect_stdout(io.StringIO()):
                f.charts()
                f.cover()
            return {
                "low": str(low),
                "high": str(high),
                "shift": str(shift),
                "crossings": len(f.root_charts),
                "stats": dict(f.stats),
            }
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            errors.append(str(e))
        finally:
            f.clear()
    raise ValueError(" | ".join(errors))


def cover(job):
    low, high = map(Q, job)
    start = time.monotonic()
    results = []
    failures = 0

    def visit(a, b):
        nonlocal failures
        try:
            result = leaf(a, b)
            results.append(result)
            if len(results) % 20 == 0:
                print(
                    "PROGRESS",
                    str(low),
                    str(high),
                    "at",
                    float(b),
                    "leaves",
                    len(results),
                    "seconds",
                    round(time.monotonic() - start, 1),
                    flush=True,
                )
        except ValueError as e:
            failures += 1
            require(b - a > Q(1, 10**8), f"Unresolved box {a} .. {b}: {e}")
            m = (a + b) / 2
            visit(a, m)
            visit(m, b)

    visit(low, high)
    print(
        "Discovered",
        str(low),
        str(high),
        "with",
        len(results),
        "regular windows in",
        round(time.monotonic() - start, 1),
        "seconds.",
        flush=True,
    )
    return results


def jobs():
    events = sorted(
        [tuple(w) for w in WINDOWS]
        + [(Q(str(h[2])) - Q(1, 100000), Q(str(h[2])) + Q(1, 100000)) for h in HINTS]
    )
    gaps = []
    previous = Q(0)
    for a, b in events:
        gaps.append((previous, a))
        previous = b
    gaps.append((previous, Q(1)))
    result = []
    for a, b in gaps:
        n = max(1, int((b - a) * 20) + 1)
        result.extend(
            (str(a + (b - a) * Q(j, n)), str(a + (b - a) * Q(j + 1, n)))
            for j in range(n)
        )
    return result


def event_windows():
    return sorted(
        list(WINDOWS)
        + [(Q(str(h[2])) - Q(1, 100000), Q(str(h[2])) + Q(1, 100000)) for h in HINTS]
    )


def audit_partition(rows):
    """Exact closed-interval tiling, without relying on decimal tolerances."""
    require(bool(rows), "The regular-window archive is empty.")
    slabs = []
    for row in rows:
        require(
            all(type(row[k]) is str for k in ("low", "high", "shift")),
            "Archive bounds and shifts must be exact rational strings.",
        )
        low, high, shift = [Q(row[k]) for k in ("low", "high", "shift")]
        require(
            0 <= low < high <= 1 and shift in (0, Q(1, 3)), "Invalid archived chart."
        )
        middle = (low + high) / 2
        stage = sum(middle > Q(str(h[2])) for h in HINTS)
        require(
            row["crossings"] == (40 if stage % 2 == 0 else 36),
            "The archived crossing count disagrees with the route stages.",
        )
        slabs.append((low, high))
    slabs += event_windows()
    cursor = Q(0)
    for low, high in sorted(slabs):
        require(
            low == cursor, "The archived partition has a gap or overlapping interiors."
        )
        cursor = high
    require(cursor == 1, "The partition does not reach the end of the route.")


def verify_regular(row):
    family = ShiftedFamily(Q(row["low"]), Q(row["high"]), Q(row["shift"]))
    try:
        with redirect_stdout(io.StringIO()):
            family.charts()
            family.cover()
        require(
            len(family.root_charts) == row["crossings"],
            "A fresh crossing count changed.",
        )
        return dict(family.stats)
    finally:
        family.clear()


def verify_task(task):
    kind, data = task
    if kind == "regular":
        return verify_regular(data)
    with redirect_stdout(io.StringIO()):
        if kind == "triple":
            certify_window(data)
        else:
            require(kind == "contact", "Unknown proof task.")
            certify_contact_window(data)
    return {}


def check_evaluation():
    """Independent rational complex powers check both shifted chart jets."""
    count = 0

    def mul(p, q):
        return p[0] * q[0] - p[1] * q[1], p[0] * q[1] + p[1] * q[0]

    for c in (Q(0), Q(1, 3)):
        rotation = ((1 - c * c) / (1 + c * c), 2 * c / (1 + c * c))
        for weight in (Q(0), Q(1, 3), Q(1)):
            curve = ShiftedCurve(weight, c)
            try:
                for quarter in range(4):
                    for s in (Q(0), Q(1, 7), Q(2, 3), Q(1)):
                        w = mul(
                            rotation, ((1 - s * s) / (1 + s * s), 2 * s / (1 + s * s))
                        )
                        for _ in range(quarter):
                            w = -w[1], w[0]
                        powers = [(Q(1), Q(0))]
                        for _ in range(11):
                            powers.append(mul(powers[-1], w))
                        P, V = [Q(0), Q(0)], [Q(0), Q(0)]
                        for k, r in curve.terms:
                            x, y = powers[abs(k)]
                            if k < 0:
                                y = -y
                            P[0] += r * x
                            P[1] += r * y
                            V[0] -= r * k * y
                            V[1] += r * k * x
                        p, v, raw = curve.evaluate(quarter, s)
                        require(
                            p == tuple(P)
                            and v == tuple(x * 2 / (1 + s * s) for x in V),
                            "The shifted rational position or s-velocity differs.",
                        )
                        require(
                            (-Q(raw[1], raw[2]), Q(raw[0], raw[2])) == tuple(V),
                            "The shifted raw t-velocity differs.",
                        )
                        count += 6
            finally:
                curve.evaluate.cache_clear()
                RhythmBlend.evaluate.cache_clear()
    print(f"{count} exact shifted-evaluator component comparisons passed.")


def check_controls(rows):
    # Existence is proved independently, before asking an exclusion routine
    # to try the same box. Reporting it empty would be a serious failure.
    known = Family(*WINDOWS[0])
    try:
        proof = known.triple(TRIPLES[0])
        box = proof["small"]["box"]
        slots = [(q, X.low, X.high) for (q, _), X in zip(proof["parameters"], box[:3])]
        family = ShiftedFamily(*WINDOWS[0], budget=Q(1))
        try:
            try:
                family.triple_empty(slots, box[3])
            except ValueError:
                pass
            else:
                raise ValueError(
                    "A certified existing triple was incorrectly excluded."
                )
        finally:
            family.clear()
    finally:
        known.clear()
    for bad in ([], rows[:-1], rows + [rows[0]]):
        try:
            audit_partition(bad)
        except ValueError:
            pass
        else:
            raise ValueError(
                "An incomplete or overlapping route partition was accepted."
            )
    print(
        "A known existing triple was not excluded; empty, incomplete, and overlapping partitions rejected."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jobs", type=int, default=2, help="Number of independent proof processes."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Rediscover and replace the complete archive.",
    )
    args = parser.parse_args()
    require(args.jobs > 0, "Use a positive process count.")
    start = time.monotonic()
    check_evaluation()
    if args.write:
        rows = []
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for result in pool.map(cover, jobs()):
                rows.extend(result)
        rows.sort(key=lambda row: Q(row["low"]))
    else:
        archive = json.loads(ARCHIVE.read_text())
        require(
            archive["schema"] == "aldebaran-rhythm-route-v1",
            "Unknown route archive schema.",
        )
        require(
            archive["event_windows"] == [[str(a), str(b)] for a, b in event_windows()],
            "The archived event windows changed.",
        )
        rows = archive["regular_windows"]
    audit_partition(rows)
    check_controls(rows)
    tasks = (
        [("regular", row) for row in rows]
        + [("triple", i) for i in range(2)]
        + [("contact", i) for i in range(4)]
    )
    totals = {}
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        pending = [pool.submit(verify_task, task) for task in tasks]
        for n, future in enumerate(as_completed(pending), 1):
            for name, count in future.result().items():
                totals[name] = totals.get(name, 0) + count
            if n % 20 == 0 or n == len(tasks):
                print(
                    f"Fresh proof tasks {n}/{len(tasks)}; {time.monotonic()-start:.1f}s elapsed.",
                    flush=True,
                )
    if args.write:
        record = {
            "schema": "aldebaran-rhythm-route-v1",
            "event_windows": [[str(a), str(b)] for a, b in event_windows()],
            "regular_windows": rows,
        }
        temporary = ARCHIVE.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(record, indent=2) + "\n")
        temporary.replace(ARCHIVE)
    print(f"{len(rows)} regular slabs plus six event windows cover [0,1] exactly.")
    print(
        f"Four ordinary triple passages and eight ordinary tangencies; no other curve event."
    )
    print(
        f"Every slab has a fresh 4096-arc cover. Aggregate regular-slab exclusions: {totals}"
    )
    print(
        f"Complete route certified in {time.monotonic()-start:.2f}s. Archived counts were not trusted."
    )


if __name__ == "__main__":
    main()
