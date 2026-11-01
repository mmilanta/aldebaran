"""One selected three-visit meeting on the 11/6 outward offset leg.

This is a selected local certificate with a whole-orbit fourth-branch
exclusion, not an event census. Circumcenters reduce the search to three
rational circle parameters. See the closing 2026-11-01 journal note.
"""

from fractions import Fraction as Q
from itertools import permutations
from math import pi, tan

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


def main():
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
    isolation = isolate_contact({"quarters": list(quarters), "center": list(map(str, center)),
                                 "radius": str(radius), "offset": compact_interval(distance),
                                 "point": [compact_interval(x) for x in location]}, 6)
    print("Nine exact Jacobian difference comparisons passed.")
    print("One unique positive-offset three-visit circle in a chart cube of radius 1e-13; contraction norm < 1e-5.")
    print("10.17121 < M < 10.17123; meeting point in (143.9662,143.9664) x (91.0882,91.0884).")
    print(f"The four-variable unfolding determinant is nonzero; {isolation['excluded_arcs']} rational arcs exclude every fourth branch.")
    print("This is one selected ordinary triple passage, not a complete offset-event census.")


if __name__ == "__main__":
    main()
