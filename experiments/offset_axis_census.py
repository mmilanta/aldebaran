"""All higher mirror-axis meetings on the two complete outward offset legs.

Seven eligible upper-half arcs per endpoint reduce the proof to 21 closed
rectangle covers. Integer Bernstein coefficients enclose a projective
circle map, including its poles. Rational contractions discover every root
without hints. The fixed-visit proof closes the parameter boundary.
Standard library only; see offset_axis_census.md. --write saves a fresh proof.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
import json
from math import comb, gcd, lcm
from functools import reduce
from pathlib import Path
from time import monotonic

from blend_cusps import (Interval as I, add, derivative, isolate_roots,
                        product, remainder, require, scale, value)
from normal_front import dot
from offset_fourfold import determinant
from offset_axis_visits import polynomials, prove as fixed_visits
from parallel_offset_events import compact_interval
from phase_unfolding import sqrt_interval
from positive_front_projection import decimal_enclosure
from rhythm_tangencies import cross

HERE = Path(__file__).resolve().parent


def bernstein(polys, low, high, degree=None):
    """Integer controls for a common positive multiple of all polynomials.

    On low+(high-low)*u, p=sum b_k binom(n,k)u^k(1-u)^(n-k).
    Return the integer rows and the exact positive multiplier p -> rows.
    A common multiplier preserves every projective coordinate ratio.
    """
    require(type(low) is Q and type(high) is Q and low < high,
            "Use a nonempty rational Bernstein interval.")
    require(len(polys) > 0 and all(len(p) > 0 for p in polys),
            "Supply nonempty polynomials.")
    require(all(type(x) in (int, Q) for p in polys for x in p),
            "Bernstein coefficients must be exact integers or fractions.")
    minimum = max(len(p) - 1 for p in polys)
    degree = minimum if degree is None else degree
    require(type(degree) is int and degree >= minimum,
            "The Bernstein degree cannot truncate a polynomial.")
    rows = []
    for p in polys:
        powers = [(high - low) ** j * sum(p[k] * comb(k, j) * low ** (k - j)
                   for k in range(j, len(p))) for j in range(len(p))]
        rows.append([sum(powers[j] * Q(comb(k, j), comb(degree, j))
                     for j in range(min(k, len(p) - 1) + 1))
                     for k in range(degree + 1)])
    denominator = lcm(*(x.denominator for row in rows for x in row))
    rows = tuple(tuple(int(x * denominator) for x in row) for row in rows)
    common = reduce(gcd, (x for row in rows for x in row)) or 1
    return (tuple(tuple(x // common for x in row) for row in rows),
            Q(denominator, common))


def midpoint(row):
    degree = len(row) - 1
    return Q(sum(a * comb(degree, k) for k, a in enumerate(row)), 2 ** degree)


def enclose(polys, low, high):
    rows, factor = bernstein(polys, low, high)
    return [I(Q(min(row), factor), Q(max(row), factor)) for row in rows]


class Arc:
    """A homogeneous Bernstein arc and its exact bisection children."""

    def __init__(self, low, high, rows, factor):
        require(type(low) is Q and type(high) is Q and low < high,
                "Use a nonempty rational arc.")
        require(len(rows) == 3 and len(rows[0]) > 1
                and all(len(row) == len(rows[0]) for row in rows)
                and all(type(x) is int for row in rows for x in row)
                and type(factor) is Q and factor > 0,
                "Use three equal-degree integer control rows and a positive factor.")
        self.low, self.high, self.rows, self.factor = low, high, rows, factor
        self.children = self.jet_data = None
        self.charts = {}
        for axis, row in enumerate(rows):
            if min(row) > 0 or max(row) < 0:
                self.charts[axis] = {}
                for other, numerator in enumerate(rows):
                    if other != axis:
                        ratios = [Q(a, b) for a, b in zip(numerator, row)]
                        self.charts[axis][other] = (min(ratios), max(ratios))

    @classmethod
    def make(cls, polys, low, high):
        return cls(low, high, *bernstein(polys, low, high))

    def split(self):
        if self.children is None:
            left, right = [], []
            degree = len(self.rows[0]) - 1
            for row in self.rows:
                a, b = [row[0] << degree], [row[-1] << degree]
                for level in range(1, degree + 1):
                    row = tuple(x + y for x, y in zip(row, row[1:]))
                    a.append(row[0] << (degree - level))
                    b.append(row[-1] << (degree - level))
                left.append(tuple(a))
                right.append(tuple(b[::-1]))
            middle = (self.low + self.high) / 2
            factor = self.factor * 2 ** degree
            self.children = (Arc(self.low, middle, tuple(left), factor),
                             Arc(middle, self.high, tuple(right), factor))
        return self.children

    def jet(self):
        if self.jet_data is None:
            degree = len(self.rows[0]) - 1
            derivatives = [tuple(Q(degree * (b - a), self.high - self.low)
                           for a, b in zip(row, row[1:])) for row in self.rows]
            self.jet_data = (
                [I(min(row), max(row)) for row in self.rows],
                [I(min(row), max(row)) for row in derivatives],
                [midpoint(row) for row in self.rows],
                [midpoint(row) for row in derivatives])
        return self.jet_data


def separated(first, second):
    """A common affine chart separates at least one coordinate ratio.

    A strictly signed denominator control row makes every ratio a convex
    combination of the corresponding control ratios, even for negative
    denominators. The three possible charts include the finite pole chart.
    """
    for axis in sorted(first.charts.keys() & second.charts.keys()):
        for other in first.charts[axis]:
            a, b = first.charts[axis][other], second.charts[axis][other]
            if a[1] < b[0] or b[1] < a[0]:
                return True
    return False


def contraction(first, second):
    """Mean-value enclosure for F=(A_c V_d-A_d V_c, D_c V_d-D_d V_c)."""
    p, dp, pc, dpc = first.jet()
    q, dq, qc, dqc = second.jet()
    F = [pc[i] * qc[2] - qc[i] * pc[2] for i in (0, 1)]
    J0 = [[dpc[i] * qc[2] - qc[i] * dpc[2],
           pc[i] * dqc[2] - dqc[i] * pc[2]] for i in (0, 1)]
    determinant = J0[0][0] * J0[1][1] - J0[0][1] * J0[1][0]
    if determinant == 0:
        return "unknown", None
    R = [[J0[1][1] / determinant, -J0[0][1] / determinant],
         [-J0[1][0] / determinant, J0[0][0] / determinant]]
    J = [[dp[i] * q[2] - q[i] * dp[2],
          p[i] * dq[2] - dq[i] * p[2]] for i in (0, 1)]
    E = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in (0, 1))
          for j in (0, 1)] for i in (0, 1)]
    radii = [(arc.high - arc.low) / 2 for arc in (first, second)]
    image = [-sum(R[i][k] * F[k] for k in (0, 1))
             + sum(E[i][j] * I(-radii[j], radii[j]) for j in (0, 1))
             for i in (0, 1)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in E)
    data = {"norm": norm, "image": image}
    if any(x.low > radius or x.high < -radius for x, radius in zip(image, radii)):
        return "empty", data
    if norm < 1 and all(-r < x.low <= x.high < r for x, r in zip(image, radii)):
        return "root", data
    return "unknown", data


def dyadic_outer(low, high, bits=128):
    denominator = 2 ** bits
    return (Q((low * denominator) // 1, denominator),
            Q(-((-high * denominator) // 1), denominator))


def refine(polys, pair):
    """Retain the already proved root while intersecting mean-value boxes."""
    original = pair
    for _ in range(24):
        status, data = contraction(*pair)
        require(status != "empty" and data is not None,
                "A proved root was lost during refinement.")
        boxes = []
        for arc, image in zip(pair, data["image"]):
            center = (arc.low + arc.high) / 2
            low, high = dyadic_outer(center + image.low, center + image.high)
            low, high = max(arc.low, low), min(arc.high, high)
            require(low < high, "The retained root box became empty.")
            boxes.append((low, high))
        pair = tuple(Arc.make(polys, *box) for box in boxes)
        if max(arc.high - arc.low for arc in pair) < Q(1, 10 ** 28):
            require(all(a.low <= b.low < b.high <= a.high
                        for a, b in zip(original, pair)),
                    "The refined root left its unique original box.")
            return pair
    raise ValueError("The root did not refine to the required precision.")


def eligible_arcs(Y, V, polys):
    roots = sorted((low, high, label) for label, p in (("Y", Y), ("V", V))
                   for low, high in isolate_roots(p, bits=40))
    require(all(a[1] < b[0] for a, b in zip(roots, roots[1:])),
            "The Y and V root brackets must be strictly disjoint.")
    require(all(value(Y, c) * value(V, c) > 0 for c in (Q(-1), Q(1))),
            "An eligible arc may meet a fixed-visit boundary.")
    # Coprimality handles every apparent v_x=0 axis visit and makes the
    # projective map nonzero even at a V pole (A=-Yw there).
    p, q = Y, V
    while q != (0,):
        p, q = q, remainder(p, q)
    require(len(p) == 1 and p[0] != 0, "Y and V have a common root.")
    edges = [(Q(-1), Q(-1), "edge"), *roots, (Q(1), Q(1), "edge")]
    arcs = []
    for first, second in zip(edges, edges[1:]):
        control = (first[1] + second[0]) / 2
        if value(Y, control) * value(V, control) < 0:
            arcs.append(Arc.make(polys, first[0], second[1]))
    require(len(arcs) == 7 and sum(label == "Y" for _, _, label in roots) == 4
            and sum(label == "V" for _, _, label in roots) == 10,
            "The complete eligible-arc inventory changed.")
    require(all(a.high < b.low for a, b in zip(arcs, arcs[1:])),
            "The eligible-component covers must be strictly disjoint.")
    return arcs, roots


def classify(inner, geometry, coarse, pair, norm):
    x, Y, V, w, A, D = geometry
    data = []
    for arc in pair:
        y, v, vertical, center = enclose((Y, V, w, A), arc.low, arc.high)
        c = I(arc.low, arc.high)
        sine = sqrt_interval(1 - c * c, bits=120)
        velocity = (-sine * v, vertical)
        length = -y / v
        require(length.low > 0, "A covered circle does not give an outward meeting.")
        speed = sqrt_interval(dot(velocity, velocity), bits=120)
        data.append((center / v, length * speed, velocity, speed))
    center, offset = [], []
    for axis, result in ((0, center), (1, offset)):
        low, high = max(d[axis].low for d in data), min(d[axis].high for d in data)
        require(low <= high, "The two visits disagree on their common circle.")
        result.extend((low, high))
    center, offset = I(*center), I(*offset)
    require(offset.low > 0, "The fourfold distance is not strictly positive.")
    # c<d means the d visit occurs first on the upper half of the orbit.
    velocities = [data[1][2], data[0][2]]
    velocities += [(-v[0], v[1]) for v in velocities[::-1]]
    speeds = [data[1][3], data[0][3], data[0][3], data[1][3]]
    normals = [(-v[1] / speed, v[0] / speed) for v, speed in zip(velocities, speeds)]
    for first, second in combinations(velocities, 2):
        cross(first, second).sign()
    triples = []
    shifts = (0, 1, 3, 7)
    for indices in combinations(range(4), 3):
        a, b, c = [normals[i] for i in indices]
        H = -(cross(a, b) + cross(b, c) + cross(c, a))
        denominator = determinant([[*normals[i], I.wrap(1)] for i in indices])
        denominator.sign()
        weight = determinant([[*normals[i], I.wrap(shifts[i])] for i in indices]) / denominator
        triples.append({"visits": list(indices), "strangeness_jump": H.sign(),
                        "normalized_unfolding": compact_interval(H),
                        "first_order_weight": compact_interval(weight)})
    order = sorted(range(4), key=lambda i: Q(triples[i]["first_order_weight"][0]))
    require(all(Q(triples[a]["first_order_weight"][1]) < Q(triples[b]["first_order_weight"][0])
                for a, b in zip(order, order[1:])),
            "The chosen normal shifts do not separate this fourfold's four triples.")
    positive = sum(t["strangeness_jump"] > 0 for t in triples)
    record = {"inner": inner, "coarse_box": [[str(a.low), str(a.high)] for a in coarse],
              "contraction_norm_upper": compact_interval(I.wrap(norm))[1],
              "cosine_box": [[str(a.low), str(a.high)] for a in pair],
              "offset": compact_interval(offset), "axis_center": compact_interval(center),
              "normal_shifts": list(shifts), "perturbed_order": order,
              "positive_triples": positive, "negative_triples": 4 - positive,
              "triples": triples}
    return record


def prove(inner, max_depth=48):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(type(max_depth) is int and max_depth >= 0, "Use a nonnegative depth limit.")
    started = monotonic()
    x, Y, V, w, A, _ = polynomials(inner)
    radius_origin2 = add(product(x, x), product((1, 0, -1), product(Y, Y)))
    D = add(product(radius_origin2, V), scale(product(x, A), -2))
    require(derivative(x) == V, "The monotone-center polynomial identity failed.")
    require(w == add(product((0, 1), Y), scale(product((1, 0, -1), derivative(Y)), -1)),
            "The vertical-velocity polynomial identity failed.")
    polys = (A, D, V)
    arcs, roots = eligible_arcs(Y, V, polys)
    stats, meetings = Counter(), []
    pending = [(a, b, 0) for a, b in combinations(arcs, 2)]
    while pending:
        first, second, depth = pending.pop()
        stats["max_depth"] = max(stats["max_depth"], depth)
        if separated(first, second):
            stats["projective_exclusions"] += 1
            continue
        if max(first.high - first.low, second.high - second.low) < Q(1, 1000):
            status, data = contraction(first, second)
            if status == "empty":
                stats["mean_value_exclusions"] += 1
                continue
            if status == "root":
                pair = refine(polys, (first, second))
                meetings.append(classify(inner, (x, Y, V, w, A, D),
                                         (first, second), pair, data["norm"]))
                stats["root_leaves"] += 1
                continue
        require(depth < max_depth, "An unresolved product rectangle rejects the census.")
        stats["bisections"] += 1
        if first.high - first.low >= second.high - second.low:
            pending.extend((child, second, depth + 1) for child in first.split())
        else:
            pending.extend((first, child, depth + 1) for child in second.split())
    meetings.sort(key=lambda event: Q(event["offset"][0]))
    require(all(Q(a["offset"][1]) < Q(b["offset"][0])
                for a, b in zip(meetings, meetings[1:])),
            "Two circle events may coincide; a higher meeting remains possible.")
    require(len(meetings) == (11 if inner == 6 else 9), "The complete axis count changed.")
    require(Q(meetings[-1]["offset"][1]) < (875 if inner == 6 else 253),
            "The advertised higher-axis tail bound failed.")
    positives = sum(e["positive_triples"] for e in meetings)
    negatives = sum(e["negative_triples"] for e in meetings)
    print(f"11/{inner}: all {len(meetings)} higher axis meetings are transverse fourfolds; "
          f"{positives} positive and {negatives} negative local triples.", flush=True)
    for event in meetings:
        offset = I(*map(Q, event["offset"]))
        print(f"  M in {decimal_enclosure(offset, 10)}: "
              f"{event['positive_triples']} positive, {event['negative_triples']} negative.", flush=True)
    print(f"  {dict(stats)}, {monotonic() - started:.2f}s.", flush=True)
    require(stats["projective_exclusions"] + stats["mean_value_exclusions"]
            + stats["root_leaves"] == 21 + stats["bisections"],
            "The closed binary cover lost a leaf.")
    return {"inner": inner, "eligible_arcs": [[str(a.low), str(a.high)] for a in arcs],
            "boundary_roots": [{"kind": kind, "box": [str(low), str(high)]}
                               for low, high, kind in roots],
            "cover": dict(stats), "events": meetings,
            "positive_triples": positives, "negative_triples": negatives}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", type=int, choices=(6, 8))
    parser.add_argument("--write", action="store_true", help="save a freshly repeated complete proof")
    args = parser.parse_args()
    require(not args.write or args.inner is None, "The saved complete record requires both endpoints.")
    started = monotonic()
    require(1540 - 765 == 775 and 1540 * 16940 - 1540 * 4405 - 765 * 16940
            - 765 * 4405 == 2974975 > 0, "The uniform speed or positive-curvature bound failed.")
    endpoints = []
    for inner in ((args.inner,) if args.inner is not None else (6, 8)):
        fixed_visits(inner)
        endpoints.append(prove(inner))
    result = {"scope": "Complete higher mirror-axis meeting census on the two unperturbed outward offset legs for every M>=0. Each meeting has exactly four transverse visits. Off-axis events are not classified.",
              "endpoints": endpoints}
    if args.write:
        (HERE / "offset_axis_census.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Fixed visits stay alone; no ordinary axis triple or axis meeting with six or more visits occurs. "
          "The complete off-axis census remains open.", flush=True)
    print(f"Elapsed {monotonic() - started:.2f}s.")


if __name__ == "__main__":
    main()
