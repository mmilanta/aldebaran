"""Independent controls for homogeneous-circle exclusions and arc jets."""

from fractions import Fraction as Q
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random

from blend_cusps import Interval as I, require
from offset_circle_tail import CircleTail, circle_exclusion, compact, determinant, prove
from rhythm_tangencies import evaluate

CHECKS = 0


def check(condition, message):
    global CHECKS
    require(condition, message)
    CHECKS += 1


def exact_determinant(matrix):
    total = 0
    for order in permutations(range(3)):
        inversions = sum(order[i] > order[j] for i in range(3) for j in range(i + 1, 3))
        total += (-1) ** inversions * matrix[0][order[0]] * matrix[1][order[1]] * matrix[2][order[2]]
    return total


def data(points, velocities):
    return [(tuple(map(I.wrap, p)), tuple(map(I.wrap, v))) for p, v in zip(points, velocities)]


def rejects(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError:
        check(True, "Rejected an invalid input.")
    else:
        raise ValueError("An invalid input was accepted.")


def main():
    rng = Random(20261104)
    for _ in range(12):
        matrix = [[I(Q(x := rng.randrange(-5, 6)) - 1, Q(x) + 1) for _ in range(3)] for _ in range(3)]
        bound = determinant(matrix)
        for choices in product((0, 1), repeat=9):
            exact = [[(matrix[i][j].low, matrix[i][j].high)[choices[3 * i + j]] for j in range(3)] for i in range(3)]
            expected = exact_determinant(exact)
            check(bound.low <= expected <= bound.high, "The interval minor lost a vertex determinant.")
    center, radius = (Q(2), Q(-3)), Q(5)
    normals = [((1 - s * s) / (1 + s * s), 2 * s / (1 + s * s)) for s in (Q(-1, 2), Q(0), Q(2, 3))]
    points = [tuple(c + radius * n for c, n in zip(center, normal)) for normal in normals]
    velocities = [(n[1], -n[0]) for n in normals]
    true_circle = data(points, velocities)
    check(circle_exclusion(true_circle, Q(4)) is None, "A genuine radius-five circle was excluded above four.")
    check(circle_exclusion(true_circle, Q(6)) == "radius_bound", "The known finite radius did not close its tail.")
    # Parallel collinear tangents allow a projective circle at infinity.
    # The rank tests must retain this unresolved case, rather than divide by zero.
    collinear = [(Q(k), Q(0)) for k in range(3)]
    check(circle_exclusion(data(collinear, [(1, 0)] * 3), Q(6)) is None,
          "A limiting line was incorrectly treated as a finite circle exclusion.")
    check(circle_exclusion(data(collinear, [(0, 1)] * 3), Q(6)) == "circle_minor",
          "The collinear finite-circle obstruction was missed.")
    repeated = data([(0, 0), (0, 0), (1, 0)], [(1, 0), (0, 1), (0, 1)])
    check(circle_exclusion(repeated, Q(6)) == "mixed_minor", "A repeated-point obstruction needs a mixed minor.")
    concurrent = data([(0, 0), (1, 0), (2, 0)], [(1, 0), (0, 1), (1, 1)])
    check(circle_exclusion(concurrent, Q(6)) == "normal_concurrency", "The nonconcurrent normals were missed.")
    for low, high in ((Q(-13, 17), Q(5, 19)), (Q(0), Q(0)), (Q(-7), Q(-7))):
        rounded = compact(I(low, high))
        check(rounded.low <= low <= high <= rounded.high, "Dyadic rounding lost a bound.")
    selected = json.loads((Path(__file__).resolve().parent / "offset_positive.json").read_text())
    for inner in (6, 8):
        cover = CircleTail(inner)
        for quarter in range(4):
            domain = (quarter, Q(1, 8), Q(1, 4))
            p, v = cover.jets(domain)
            for s in (Q(1, 8), Q(5, 32), Q(3, 16), Q(7, 32), Q(1, 4)):
                for order, bounds in ((0, p), (1, v)):
                    actual = evaluate(quarter, s, Q(inner - 6, 2), order)
                    for a, b in zip(actual, bounds):
                        check(b.low <= a.low == a.high <= b.high,
                              "The Taylor arc jets missed an independent rational Fourier value.")
        endpoint = next(e for e in selected["endpoints"] if e["inner"] == inner)
        for event in endpoint["fourfolds"]:
            visits = [cover.jets((q, *map(Q, box))) for q, box in zip(event["quarters"], event["root_box"])]
            for triple in combinations(visits, 3):
                check(circle_exclusion(triple, Q(1)) is None,
                      "A previously certified curved tangent circle was incorrectly excluded.")
        rejects(cover.jets, (0, Q(1, 2), Q(1, 3)))
        rejects(cover.jets, (4, Q(0), Q(1)))
        rejects(cover.jets, (0, 0.0, 1.0))
        CircleTail.jets.cache_clear()
        cover.evaluator.evaluate.cache_clear()
    rejects(circle_exclusion, true_circle, Q(0))
    rejects(circle_exclusion, true_circle, Q(-1))
    rejects(circle_exclusion, true_circle, 5.0)
    rejects(circle_exclusion, true_circle[:2], Q(6))
    rejects(prove, True)
    rejects(prove, 7)
    rejects(prove, 6, max_depth=-1)
    rejects(prove, 6, max_depth=0)
    rejects(prove, 8, max_depth=0)
    print(f"{CHECKS} independent determinant-vertex, true-circle, limiting-line, collinear, repeated-point, "
          "radius, rounding, Fourier-jet, preserved orbital-circle, and invalid-input controls passed.")


if __name__ == "__main__":
    main()
