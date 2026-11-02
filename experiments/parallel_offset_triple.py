"""One selected three-visit meeting on the 11/6 outward offset leg.

Circumcenters certify a selected event in three rational circle parameters.
A separate four-variable enclosure classifies the viewer's entire room
throughout its offset controls: exactly one triple and no touch. This is
not an event census elsewhere on the curve. See parallel_offset.md.
"""

import argparse
from fractions import Fraction as Q
from itertools import permutations
import json
from math import atan, pi, tan
from pathlib import Path

from blend_cusps import Interval as I, require
from normal_front import dot
from parallel_offset_events import compact_interval, isolate_contact
from phase_unfolding import inverse, sqrt_interval
from rhythm_tangencies import cross, evaluate

HINT = (0.220212726246662, 0.9677364681604113, 5.8762440009048085)


def solve(A, b):
    determinant = cross(*A)
    return ((b[0] * A[1][1] - A[0][1] * b[1]) / determinant,
            (A[0][0] * b[1] - b[0] * A[1][0]) / determinant)


def equations(quarters, parameters):
    points, velocities, accelerations = [
        [evaluate(q, s, Q(0), order) for q, s in zip(quarters, parameters)]
        for order in range(3)
    ]
    A = [tuple(2 * (x - y) for x, y in zip(points[k], points[0])) for k in (1, 2)]
    b = [dot(points[k], points[k]) - dot(points[0], points[0]) for k in (1, 2)]
    center = solve(A, b)
    center_derivatives = []
    for j in range(3):
        db = [2 * ((dot(points[k], velocities[k]) if j == k else 0)
                   - (dot(points[0], velocities[0]) if j == 0 else 0)) for k in (1, 2)]
        dA = [tuple(2 * ((velocities[k][i] if j == k else 0)
                        - (velocities[0][i] if j == 0 else 0)) for i in range(2)) for k in (1, 2)]
        center_derivatives.append(solve(A, [x - dot(row, center) for x, row in zip(db, dA)]))
    radii = [tuple(x - y for x, y in zip(point, center)) for point in points]
    F = [dot(r, v) for r, v in zip(radii, velocities)]
    J = [[((dot(velocities[i], velocities[i]) + dot(radii[i], accelerations[i])) if i == j else 0)
          - dot(center_derivatives[j], velocities[i]) for j in range(3)] for i in range(3)]
    factors = [I.wrap(2) / (1 + s * s) for s in parameters]
    J = [[entry * factors[j] for j, entry in enumerate(row)] for row in J]
    return F, J, center, radii, velocities


def offset_equations(quarters, parameters, offset):
    """Equal shifted points and the four-variable circle-chart Jacobian."""
    points, normals, velocities = [], [], []
    for quarter, s in zip(quarters, parameters):
        p = evaluate(quarter, s, Q(0))
        v = evaluate(quarter, s, Q(0), 1)
        a = evaluate(quarter, s, Q(0), 2)

        def square(x):
            low = Q(0) if x.low <= 0 <= x.high else min(x.low ** 2, x.high ** 2)
            return I(low, max(x.low ** 2, x.high ** 2))

        speed = sqrt_interval(sum((square(x) for x in v), I.wrap(0)))
        normal = (-v[1] / speed, v[0] / speed)
        curvature = cross(v, a) / (speed * speed * speed)
        factor = I.wrap(2) / (1 + s * s)
        points.append(tuple(x - offset * n for x, n in zip(p, normal)))
        normals.append(normal)
        velocities.append(tuple((1 + offset * curvature) * x * factor for x in v))
    F, J = [], []
    for other in (1, 2):
        for axis in range(2):
            F.append(points[0][axis] - points[other][axis])
            J.append([velocities[0][axis],
                      -velocities[1][axis] if other == 1 else I.wrap(0),
                      -velocities[2][axis] if other == 2 else I.wrap(0),
                      normals[other][axis] - normals[0][axis]])
    return F, J


def viewer_window(record):
    """Exactly one triple and no touch inside the viewer's entire fixed room.

    First exclude all but three monotone slots from the full room and M
    interval. Then narrow every possible four-variable zero from the FULL
    slot product by an exact mean-value enclosure. The last enclosure has
    a contraction derivative. This proves uniqueness throughout the room,
    not just in the tiny existence box. No numerical root search is used.
    """
    quarters = record["quarters"]
    centers = list(map(Q, record["center"]))
    offset = I(*map(Q, record["offset"]))
    width = Q(3, 20)
    window = {**record,
              "offset": compact_interval(offset + I(-width, width)),
              "point": [compact_interval(I(*map(Q, b)) + I(-1, 1)) for b in record["point"]]}
    isolation = isolate_contact(window, 6)
    slots = isolation["slots"]
    require(all(Q(s["low"]) == c - Q(1, 1000) and Q(s["high"]) == c + Q(1, 1000)
                for c, s in zip(centers, slots)), "The full viewer slots changed.")
    origin = centers + [offset.midpoint()]
    offset_window = I(*map(Q, window["offset"]))
    domains = [I(Q(s["low"]) - c, Q(s["high"]) - c) for s, c in zip(slots, centers)]
    domains.append(offset_window - origin[3])
    F0, J0 = offset_equations(quarters, tuple(I.wrap(c) for c in centers), I.wrap(origin[3]))
    R = inverse([[entry.midpoint() for entry in row] for row in J0])
    # Any exact rational preconditioner works; outward dyadics keep its
    # entries compact. This rounding is not an interval inverse assertion.
    R = [[I(*map(Q, compact_interval(I.wrap(x)))).midpoint() for x in row] for row in R]
    residual = [-sum(R[i][k] * F0[k] for k in range(4)) for i in range(4)]
    rounds = 0
    while True:
        # The mean-value segment runs from the FIXED origin to each possible
        # zero. A narrowed box can cease to contain that origin, so evaluate
        # derivatives on their convex hull, not just on the narrowed box.
        hull = [I(min(Q(0), d.low), max(Q(0), d.high)) for d in domains]
        parameters = tuple(I(c + d.low, c + d.high) for c, d in zip(centers, hull[:3]))
        _, J = offset_equations(quarters, parameters, origin[3] + hull[3])
        E = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
        norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in E)
        if norm < Q(1, 1000):
            break
        require(rounds < 16, "The complete viewer product did not narrow to a contraction.")
        image = [residual[i] + sum(E[i][j] * domains[j] for j in range(4)) for i in range(4)]
        narrowed = [I(max(x.low, y.low), min(x.high, y.high)) for x, y in zip(domains, image)]
        require(all(x.low <= x.high for x in narrowed), "The known event was lost while narrowing.")
        domains = [I(*map(Q, compact_interval(x))) for x in narrowed]
        rounds += 1
    # Compare the new shifted-point Jacobian against rational differences.
    epsilon = Q(1, 10**8)
    for axis in range(4):
        plus, minus = origin[:], origin[:]
        plus[axis] += epsilon
        minus[axis] -= epsilon
        fp = offset_equations(quarters, tuple(I.wrap(c) for c in plus[:3]), I.wrap(plus[3]))[0]
        fm = offset_equations(quarters, tuple(I.wrap(c) for c in minus[:3]), I.wrap(minus[3]))[0]
        for row in range(4):
            error = (fp[row] - fm[row]) / (2 * epsilon) - J0[row][axis]
            require(-Q(1, 10**4) < error.low <= error.high < Q(1, 10**4),
                    "The shifted-point Jacobian disagrees with exact differences.")
    # Prove all three tangent pairs stay transverse in the WHOLE slots.
    velocities = []
    for quarter, slot in zip(quarters, slots):
        low, high = Q(slot["low"]), Q(slot["high"])
        cuts = [low + (high - low) * k / 8 for k in range(9)]
        velocities.append([evaluate(quarter, I(a, b), Q(0), 1) for a, b in zip(cuts, cuts[1:])])
    comparisons, signs = 0, []
    for i in range(3):
        for j in range(i):
            sign = cross(velocities[i][0], velocities[j][0]).sign()
            for a in velocities[i]:
                for b in velocities[j]:
                    require(cross(a, b).sign() == sign, "A viewer tangent pair may become parallel.")
                    comparisons += 1
            signs.append(sign)
    result = {"offset": window["offset"], "room": window["point"],
              "isolation": isolation, "narrowing_rounds": rounds,
              "unique_root_box": [compact_interval(c + d) for c, d in zip(origin, domains)],
              "final_norm_upper": compact_interval(I.wrap(norm))[1],
              "tangent_pair_comparisons": comparisons, "tangent_pair_signs": signs,
              "jacobian_difference_comparisons": 16}
    print(f"Viewer room: {isolation['excluded_arcs']} uniform arc exclusions, {rounds} mean-value narrowing rounds, exactly one triple and no touch throughout the controls.", flush=True)
    print(f"  Sixteen shifted-point Jacobian controls and {comparisons} uniform tangent-pair comparisons passed.", flush=True)
    return result


def certify():
    quarters = tuple(int(t / (pi / 2)) for t in HINT)
    center = tuple(Q(str(tan((t - q * pi / 2) / 2))) for q, t in zip(quarters, HINT))
    radius = Q(1, 10**13)
    box = tuple(I(s - radius, s + radius) for s in center)
    require(all(0 < s.low < s.high < 1 for s in box), "A box left its circle chart.")
    require(quarters[0] == quarters[1] and box[0].high < box[1].low and quarters[1] < quarters[2], "The selected visits are not separately ordered.")
    F, J0, _, _, _ = equations(quarters, tuple(I.wrap(s) for s in center))
    _, J, location, radii, velocities = equations(quarters, box)
    epsilon = Q(1, 10**9)
    for axis in range(3):
        plus, minus = list(center), list(center)
        plus[axis] += epsilon
        minus[axis] -= epsilon
        fp = equations(quarters, tuple(I.wrap(s) for s in plus))[0]
        fm = equations(quarters, tuple(I.wrap(s) for s in minus))[0]
        for row in range(3):
            require(abs((fp[row].low - fm[row].low) / (2 * epsilon) - J0[row][axis].low) < Q(1, 10**4), "The circumcenter Jacobian disagrees with exact differences.")
    R = inverse([[x.low for x in row] for row in J0])
    defect = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 10**5), "The circle box is not a strong contraction.")
    offsets = [-sum(R[i][k] * F[k] for k in range(3)) + sum(defect[i][j] * I(-radius, radius) for j in range(3)) for i in range(3)]
    require(all(-radius < x.low <= x.high < radius for x in offsets), "The circle map does not send its box inside itself.")
    for r, v in zip(radii, velocities):
        require(dot(r, (-v[1], v[0])).low > 0, "A radius points opposite its left normal.")
    for i in range(3):
        for j in range(i):
            cross(velocities[i], velocities[j]).sign()
    distance = sqrt_interval(dot(radii[0], radii[0]))
    require(Q("10.17121") < distance.low <= distance.high < Q("10.17123"), "The selected offset enclosure changed.")
    require(Q("143.9662") < location[0].low <= location[0].high < Q("143.9664"), "The selected x enclosure changed.")
    require(Q("91.0882") < location[1].low <= location[1].high < Q("91.0884"), "The selected y enclosure changed.")
    normals, shifted_velocities = [], []
    for q, s, v in zip(quarters, box, velocities):
        speed = sqrt_interval(dot(v, v))
        acceleration = evaluate(q, s, Q(0), 2)
        curvature = cross(v, acceleration) / (speed * speed * speed)
        require(curvature.low > 0, "The original curvature lost its positive sign.")
        normals.append((-v[1] / speed, v[0] / speed))
        shifted_velocities.append(tuple((1 + distance * curvature) * x for x in v))
    G = []
    for other in (1, 2):
        for axis in range(2):
            G.append([shifted_velocities[0][axis],
                      -shifted_velocities[1][axis] if other == 1 else I.wrap(0),
                      -shifted_velocities[2][axis] if other == 2 else I.wrap(0),
                      normals[other][axis] - normals[0][axis]])
    determinant = I.wrap(0)
    for permutation in permutations(range(4)):
        inversions = sum(permutation[i] > permutation[j] for i in range(4) for j in range(i + 1, 4))
        term = I.wrap((-1) ** inversions)
        for i, j in enumerate(permutation):
            term *= G[i][j]
        determinant += term
    determinant.sign()
    record = {"quarters": list(quarters), "center": list(map(str, center)),
              "radius": str(radius), "offset": compact_interval(distance),
              "point": [compact_interval(x) for x in location],
              "norm_upper": compact_interval(I.wrap(norm))[1],
              "unfolding_determinant": compact_interval(determinant)}
    isolation = isolate_contact(record, 6)
    record["isolation"] = isolation
    print("Nine exact Jacobian difference comparisons passed.")
    print("One unique positive-offset three-visit circle in a chart cube of radius 1e-13; contraction norm < 1e-5.")
    print("10.17121 < M < 10.17123; meeting point in (143.9662,143.9664) x (91.0882,91.0884).")
    print(f"The four-variable unfolding determinant is nonzero; {isolation['excluded_arcs']} rational arcs exclude every fourth branch.")
    print("This is one selected ordinary triple passage, not a complete offset-event census.")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="save the freshly proved selected event and rounded browser coordinates")
    args = parser.parse_args()
    record = certify()
    record["viewer_window"] = viewer_window(record)
    if args.write:
        here = Path(__file__).resolve().parent
        (here / "parallel_offset_triple.json").write_text(json.dumps({
            "description": "One selected ordinary positive-offset triple on 11/6, with a rational contraction, nonzero unfolding determinant, and whole-orbit fourth-branch exclusion. Not a census.",
            "inner": 6, "event": record,
        }, indent=2) + "\n")
        midpoint = lambda bounds: float(sum(map(Q, bounds)) / 2)
        data = {"times": [q * pi / 2 + 2 * atan(float(Q(s)))
                          for q, s in zip(record["quarters"], record["center"])],
                "offset": midpoint(record["offset"]),
                "point": [midpoint(bounds) for bounds in record["point"]]}
        (here / "parallel_offset_data.js").write_text(
            "'use strict';\n\n// Rounded illustration coordinates from python3 experiments/parallel_offset_triple.py --write.\n"
            + "// The rational event certificate is parallel_offset_triple.json; this is not a census.\n"
            + "const ParallelOffsetData = " + json.dumps(data, separators=(",", ":")) + ";\n"
            + "if (typeof module !== 'undefined' && module.exports) module.exports = ParallelOffsetData;\n")
        print("Wrote the selected-event certificate and rounded browser coordinates.")


if __name__ == "__main__":
    main()
