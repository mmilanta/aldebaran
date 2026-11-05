"""Independent controls for the complete outward-circle cover.

These controls exercise the arithmetic, singular cases, Fourier jets,
analytic Jacobian, real archived events, reflection, and rejected incomplete
covers. They do not replace the fresh whole-domain proof.
"""

from fractions import Fraction as Q
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random

from blend_cusps import Interval as I, require
from offset_leg_census import (SCALE, candidates, clear_caches, contract, cover, cross,
                               determinant, dot, equations, exact_jets, integer,
                               integer_jets, jets, minus, minor_exclusion, near,
                               pair_exclusion, plus, prove, reflect, scale, times)
from parallel_offset_triple import equations as independent_equations
from rhythm_tangencies import evaluate

CHECKS = 0
HERE = Path(__file__).resolve().parent


def check(condition, message):
    global CHECKS
    require(condition, message)
    CHECKS += 1


def rejects(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError:
        check(True, "Rejected invalid input.")
    else:
        raise ValueError("An invalid input or incomplete cover was accepted.")


def data(points, velocities):
    return [tuple(tuple((Q(x) * SCALE, Q(x) * SCALE) for x in row) for row in (p, v))
            for p, v in zip(points, velocities)]


def exact_determinant(rows):
    return sum((-1) ** sum(order[i] > order[j] for i in range(3) for j in range(i + 1, 3))
               * rows[0][order[0]] * rows[1][order[1]] * rows[2][order[2]]
               for order in permutations(range(3)))


def main():
    rng = Random(20261105)
    # Derive the scalar pair equation independently from the actual lifted
    # lines. Translation and arbitrary nonzero velocity scales are included.
    for _ in range(500):
        p, q, v, w = [tuple(Q(rng.randrange(-20, 21), rng.randrange(1, 8)) for _ in range(2))
                       for _ in range(4)]
        scalar_dot = lambda a, b: sum(x * y for x, y in zip(a, b))
        scalar_cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
        base = lambda a: (*a, scalar_dot(a, a))
        direction = lambda a, b: (b[1], -b[0], 2 * scalar_cross(a, b))
        h = tuple(y - x for x, y in zip(p, q))
        delta = scalar_cross(v, w)
        F = scalar_dot(h, h) * delta - 2 * scalar_dot(v, h) * scalar_cross(h, w)
        lifted = exact_determinant([direction(p, v), direction(q, w),
                                    tuple(y - x for x, y in zip(base(p), base(q)))])
        check(lifted == F, "The chord formula disagrees with lifted-line coplanarity.")
        if delta:
            Lp, Lq = -scalar_dot(h, w) / delta, -scalar_dot(h, v) / delta
            first = tuple(x + Lp * d for x, d in zip(p, direction(p, v)))
            second = tuple(x + Lq * d for x, d in zip(q, direction(q, w)))
            check(first == second, "The two normal-line parameters disagree on their center.")
            Cp = scalar_dot(p, p) + 2 * Lp * scalar_cross(p, v)
            Cq = scalar_dot(q, q) + 2 * Lq * scalar_cross(q, w)
            check(Cq - Cp == F / delta, "The circle constants disagree with the scalar pair residual.")
    for _ in range(12):
        matrix = [[(x := rng.randrange(-10, 11), x + rng.randrange(1, 4)) for _ in range(3)] for _ in range(3)]
        bound = determinant(matrix)
        for choices in product((0, 1), repeat=9):
            rows = [[matrix[i][j][choices[3 * i + j]] for j in range(3)] for i in range(3)]
            actual = exact_determinant(rows)
            check(bound[0] <= actual <= bound[1], "An integer determinant lost a box vertex.")
    for _ in range(200):
        a, b = [(x := rng.randrange(-30, 31), x + rng.randrange(0, 10)) for _ in range(2)]
        for x, y in product(a, b):
            for bound, actual in ((plus(a, b), x + y), (minus(a, b), x - y), (times(a, b), x * y)):
                check(bound[0] <= actual <= bound[1], "An integer interval operation lost an endpoint.")
        for n in (-7, 0, 5):
            bound = scale(a, n)
            check(all(bound[0] <= x * n <= bound[1] for x in a), "Signed scaling lost a bound.")
    for low, high in ((Q(-1, 3), Q(2, 7)), (Q(0), Q(0)), (Q(-7), Q(-7)),
                      (Q(-1, 2 ** 60), Q(1, 2 ** 60))):
        bound = integer(I(low, high))
        check(bound[0] <= low * SCALE <= high * SCALE <= bound[1], "Integer rounding narrowed a box.")

    parameters = (Q(-2, 3), Q(0), Q(1, 2), Q(3))
    normals = [((1 - s * s) / (1 + s * s), 2 * s / (1 + s * s)) for s in parameters]
    center, radius = (Q(2), Q(-3)), Q(5)
    points = [tuple(c + radius * n for c, n in zip(center, normal)) for normal in normals]
    velocities = [(n[1], -n[0]) for n in normals]
    true_circle = data(points, velocities)
    for a, b in combinations(true_circle, 2):
        check(pair_exclusion(a, b) is None, "A real outward tangent circle lost a pair.")
    for triple in combinations(true_circle, 3):
        check(minor_exclusion(triple) is None, "A real outward tangent circle lost a triple.")
    inward = data(points[:2], [tuple(-x for x in v) for v in velocities[:2]])
    check(pair_exclusion(*inward) == "inward", "An inward pair was retained.")
    skew = data([(0, 0), (1, 2)], [(-1, 0), (0, -1)])
    check(pair_exclusion(*skew) == "skew", "Skew lifted circle lines were retained.")
    # Pairwise coplanarity is not three-line concurrency. These three
    # lifted tangents to a parabola lie in one plane but do not concur.
    collinear = data([(0, 0), (1, 0), (2, 0)], [(0, 1)] * 3)
    check(all(pair_exclusion(a, b) is None for a, b in combinations(collinear, 2)),
          "The parallel-lines obstruction should survive the pair filter.")
    check(minor_exclusion(collinear) == "chord_minor", "Pairwise-compatible nonconcurrent lines were accepted.")
    infinity = data([(0, 0), (1, 0), (2, 0)], [(1, 0)] * 3)
    check(minor_exclusion(infinity) is None, "A limiting common line must stay unresolved.")
    repeated = data([(0, 0), (0, 0), (1, 0)], [(1, 0), (0, 1), (0, 1)])
    check(minor_exclusion(repeated) == "mixed_minor", "A repeated-point obstruction was missed.")

    for inner in (6, 8):
        weight = Q(inner - 6, 2)
        for quarter in range(4):
            for s in map(Q, (0, Q(1, 17), Q(1, 3), Q(4, 5), 1)):
                expected = exact_jets(quarter, s, inner)
                for order in range(3):
                    actual = evaluate(quarter, s, weight, order)
                    for a, b in zip(actual, expected[order]):
                        check(a.low == a.high == b, "The integer Fourier evaluator disagrees with the independent one.")
            for low, high in ((Q(0), Q(1, 128)), (Q(1, 8), Q(1, 4)), (Q(127, 128), Q(1))):
                bounds = jets((quarter, low, high), inner)
                for k in range(9):
                    s = low + (high - low) * k / 8
                    for order in range(3):
                        for actual, box in zip(evaluate(quarter, s, weight, order), bounds[order]):
                            check(box.low <= actual.low == actual.high <= box.high,
                                  "A Taylor jet missed an independent exact Fourier value.")
        archived = json.loads((HERE / "offset_positive.json").read_text())
        endpoint = next(e for e in archived["endpoints"] if e["inner"] == inner)
        for event in endpoint["fourfolds"]:
            domains = tuple((q, *map(Q, box)) for q, box in zip(event["quarters"], event["root_box"]))
            actual = [integer_jets(d, inner) for d in domains]
            for a, b in combinations(actual, 2):
                check(pair_exclusion(a, b) is None, "The pair filter lost a certified orbital circle.")
            for indices in combinations(range(4), 3):
                ds = tuple(domains[i] for i in indices)
                check(minor_exclusion([actual[i] for i in indices]) is None,
                      "The minor filter lost a certified orbital circle.")
                check(contract(ds, inner)[0] == "root", "A certified orbital triple subset did not contract.")
        # A separately implemented circumcenter Jacobian and central
        # differences audit both the value and derivative enclosures.
        event = endpoint["fourfolds"][0]
        qs = event["quarters"][:3]
        centers = [sum(map(Q, box)) / 2 for box in event["root_box"][:3]]
        ds = tuple((q, s, s) for q, s in zip(qs, centers))
        F, J, *_ = equations(ds, inner)
        other_F, other_J, *_ = independent_equations(qs, tuple(I.wrap(s) for s in centers), inner)
        for actual, box in zip(other_F, F):
            check(box.low <= actual.low == actual.high <= box.high, "Independent circle residual left its enclosure.")
        for row, boxes in zip(other_J, J):
            for actual, box in zip(row, boxes):
                check(box.low <= actual.low == actual.high <= box.high, "Independent circle Jacobian left its enclosure.")
        epsilon = Q(1, 10 ** 9)
        for axis in range(3):
            plus_ds, minus_ds = list(ds), list(ds)
            q, s, _ = ds[axis]
            plus_ds[axis], minus_ds[axis] = (q, s + epsilon, s + epsilon), (q, s - epsilon, s - epsilon)
            fp, fm = equations(tuple(plus_ds), inner)[0], equations(tuple(minus_ds), inner)[0]
            for row in range(3):
                error = (fp[row] - fm[row]) / (2 * epsilon) - J[row][axis]
                check(-Q(1, 100) < error.low <= error.high < Q(1, 100),
                      "A central difference disagrees with the circle Jacobian.")
        reflected = reflect(ds)
        check(reflect(reflected) == ds, "Rational chart reflection is not an involution.")
        check(near(0, 512) and near(1, 512) and not near(128, 512), "The short-arc turn filter changed.")
        clear_caches()
    rejects(exact_jets, 4, Q(1, 3), 6)
    rejects(exact_jets, 0, .5, 6)
    rejects(exact_jets, 0, Q(1, 3), True)
    rejects(jets, (0, Q(3, 4), Q(1, 4)), 6)
    rejects(candidates, True)
    rejects(candidates, 7)
    rejects(candidates, 6, 0)
    rejects(cover, 6, max_depth=-1)
    rejects(cover, 6, partition=128, max_depth=0)
    rejects(cover, 8, partition=128, max_depth=0)
    rejects(prove, True)
    rejects(prove, 7)
    rejects(prove, 6, partition=0)
    rejects(prove, 6, partition=True)
    rejects(prove, 6, max_depth=-1)
    clear_caches()
    print(f"{CHECKS} independent integer-box, determinant-vertex, circle, singular-case, Fourier, "
          "Taylor, preserved orbital-event, contraction, Jacobian, reflection, and rejection controls passed.")


if __name__ == "__main__":
    main()
