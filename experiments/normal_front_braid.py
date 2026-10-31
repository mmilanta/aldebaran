"""Certify the conormal braid words, conjugacy, and Alexander polynomials.

Run: python3 experiments/normal_front_braid.py [--saved] [--write]
The default repeats fresh complete front censuses. --saved checks the words
conditional on the archived census, without repeating completeness proofs.
Only the standard library is used. See normal_front_braid.md.
"""

import argparse
import json
import math
from math import factorial
from pathlib import Path
from time import monotonic
from fractions import Fraction as Q
from blend_cusps import Interval as I, require
from phase_unfolding import sqrt_interval
from rhythm_tangencies import evaluate, multiply
from normal_front import dot
from normal_front_census import FrontCensus, controls as census_controls
from normal_front_conjugacy import (
    CONJUGATOR,
    controls as conjugacy_controls,
    verify as verify_conjugacy,
)


def roundI(x, bits=80):
    """Outward dyadic rounding keeps transcendental bounds manageable."""
    D = 2**bits
    return I(Q((x.low * D) // 1, D), Q(-((-x.high * D) // 1), D))


def small_atan(x):
    """Forty alternating terms, plus the signed next-term remainder."""
    if x < 0:
        return -small_atan(-x)
    require(x <= Q(1, 2), "atan reduction")
    total = Q(0)
    power = x
    for k in range(40):
        total += (-1) ** k * power / (2 * k + 1)
        power *= x * x
    return I(total, total + power / 81)


PI = roundI(16 * small_atan(Q(1, 5)) - 4 * small_atan(Q(1, 239)))
TAU = 2 * PI


def atan_endpoint(x):
    """Reduce all real arguments to the alternating series on [-1/2,1/2]."""
    if x < 0:
        return -atan_endpoint(-x)
    if x > 1:
        return PI / 2 - atan_endpoint(1 / x)
    if x > Q(1, 2):
        return PI / 4 + small_atan((x - 1) / (x + 1))
    return small_atan(x)


def atan(x):
    x = roundI(x)
    return roundI(I(atan_endpoint(x.low).low, atan_endpoint(x.high).high))


SEAM = atan(I.wrap(Q(4, 3)))
N = (Q(3, 5), Q(4, 5))


def phase(quarter, s, n):
    """An interval for the continuous left-normal angle, without unwrap guesses."""
    s = I.wrap(s)
    den = 1 + s * s
    w = ((1 - s * s) / den, 2 * s / den)
    for _ in range(quarter):
        w = (-w[1], w[0])
    power = (I.wrap(1), I.wrap(0))
    for _ in range(11):
        power = multiply(power, (w[0], -w[1]))
    v = evaluate(quarter, s, Q(n - 6, 2), 1)
    prod = multiply(v, power)
    B = (prod[1], -prod[0])
    require(B[0].low > 0, "B half-plane")
    return PI + 11 * (quarter * PI / 2 + 2 * atan(s)) + atan(B[1] / B[0])


def certify_section(n):
    """Exactly eleven visits at normal (3/5,4/5), with certified height order."""
    result = []

    def ph(t):
        return (
            math.pi
            + 11 * t
            + math.atan2(
                -245 * math.sin(10 * t) + 65 * n * math.sin((11 + n) * t),
                1540 + 245 * math.cos(10 * t) - 65 * n * math.cos((11 + n) * t),
            )
        )

    for k in range(1, 12):
        target = math.atan2(4, 3) + 2 * math.pi * k
        lo = 0
        hi = 2 * math.pi
        for _ in range(60):
            m = (lo + hi) / 2
            if ph(m) < target:
                lo = m
            else:
                hi = m
        t = (lo + hi) / 2
        q = int(t / (math.pi / 2))
        c = Q(str(math.tan((t - q * math.pi / 2) / 2)))
        r = Q(1, 10**11)
        s = I(c - r, c + r)
        v0 = evaluate(q, I.wrap(c), Q(n - 6, 2), 1)
        a0 = evaluate(q, I.wrap(c), Q(n - 6, 2), 2)
        v = evaluate(q, s, Q(n - 6, 2), 1)
        a = evaluate(q, s, Q(n - 6, 2), 2)
        F = dot(v0, N)
        J0 = dot(a0, N) * I.wrap(2) / (1 + c * c)
        R = 1 / J0.low
        J = dot(a, N) * I.wrap(2) / (1 + s * s)
        E = 1 - R * J
        image = -R * F + E * I(-r, r)
        require(
            -r < image.low <= image.high < r and max(abs(E.low), abs(E.high)) < 1,
            "section contraction",
        )
        require(dot((-v[1], v[0]), N).low > 0, "section coorientation")
        idx = (phase(q, s, n) - SEAM) / TAU
        require(k - Q(1, 2) < idx.low <= idx.high < k + Q(1, 2), "section sheet")
        h = dot(evaluate(q, s, Q(n - 6, 2)), N)
        result.append({"label": k % 11, "h": h, "quarter": q, "center": str(c)})
    result.sort(key=lambda x: x["h"].low)
    require(
        all(a["h"].high < b["h"].low for a, b in zip(result, result[1:])),
        "section height order",
    )
    return result


def certify_word(record):
    """Replay root boxes and certify their order, sheet labels, and adjacent swaps.

    Completeness comes from the whole-front census, fresh by default. No
    floating-point angle, height, or sort decision is accepted as a proof.
    """
    n = record["inner"]
    census = FrontCensus(n)
    events = []
    front_boxes = []
    for item in record["roots"]:
        require(
            len(item["quarters"]) == len(item["center"]) == 2,
            "A bitangent needs two visits.",
        )
        r = Q(item["radius"])
        domains = [
            (q, Q(s) - r, Q(s) + r) for q, s in zip(item["quarters"], item["center"])
        ]
        require(
            r > 0
            and all(
                type(q) is int and 0 <= q < 4 and 0 < l < h < 1 for q, l, h in domains
            ),
            "Invalid root domains.",
        )
        require(
            domains[0][0] < domains[1][0]
            or domains[0][0] == domains[1][0]
            and domains[0][2] < domains[1][1],
            "The bitangent visits must be distinct and ordered.",
        )
        require(census.contract(*domains)[0] == "root", "root replay")
        jets = [evaluate(q, I(l, h), Q(n - 6, 2), 1) for q, l, h in domains]
        require(dot(*jets).low > 0, "The bitangent is not cooriented.")
        points = [evaluate(q, I(l, h), Q(n - 6, 2)) for q, l, h in domains]
        require(
            any((a - b).low > 0 or (a - b).high < 0 for a, b in zip(*points)),
            "The bitangent points may coincide.",
        )
        phases = [phase(q, I(l, h), n) for q, l, h in domains]
        ks = [
            math.floor(float((p.midpoint() - SEAM.midpoint()) / TAU.midpoint()))
            for p in phases
        ]
        require(
            all(0 <= k <= 11 for k in ks), "An unwrapped sheet label left its range."
        )
        phases = [p - k * TAU for p, k in zip(phases, ks)]
        p = I(max(x.low for x in phases), min(x.high for x in phases))
        require(
            all(SEAM.high < x.low <= x.high < (SEAM + TAU).low for x in phases),
            "angular seam",
        )
        boxes = [census.bounds(d) for d in domains]
        box = tuple(I(max(a.low, b.low), min(a.high, b.high)) for a, b in zip(*boxes))
        front_boxes.append(box)
        h = box[2] / sqrt_interval(box[0] * box[0] + box[1] * box[1])
        labels = [k % 11 for k in ks]
        require(labels[0] != labels[1], "two sheet labels")
        events.append({"phase": p, "h": h, "labels": labels})
    require(
        all(
            any(a.high < b.low or b.high < a.low for a, b in zip(box, other))
            for i, box in enumerate(front_boxes)
            for other in front_boxes[:i]
        ),
        "Two archived roots may describe the same front point.",
    )
    events.sort(key=lambda e: e["phase"].low)
    groups = []
    for e in events:
        if groups and e["phase"].low <= groups[-1]["high"]:
            groups[-1]["events"].append(e)
            groups[-1]["high"] = max(groups[-1]["high"], e["phase"].high)
        else:
            groups.append(
                {"low": e["phase"].low, "high": e["phase"].high, "events": [e]}
            )
    section = certify_section(n)
    initial = [x["label"] for x in section]
    order = initial.copy()
    word = []
    for group in groups:
        width = group["high"] - group["low"]
        rows = sorted(group["events"], key=lambda e: e["h"].low)
        bands = [e["h"] + I(-450 * width, 450 * width) for e in rows]
        require(
            all(a.high < b.low for a, b in zip(bands, bands[1:])),
            "commuting height bands",
        )
        labels = [x for e in rows for x in e["labels"]]
        require(len(set(labels)) == len(labels), "cluster shares strand")
        for e in rows:
            a, b = sorted(order.index(label) for label in e["labels"])
            require(b == a + 1, "nonadjacent crossing")
            word.append(a + 1)
            order[a], order[b] = order[b], order[a]
    require(order == [(k - 1) % 11 for k in initial], "closure sheet permutation")
    print(
        f"11 / {n}: {len(word)} positive generators in {len(groups)} ordered groups; closure permutation verified.",
        flush=True,
    )
    census.bounds.cache_clear()
    census.evaluator.evaluate.cache_clear()
    return {
        "inner": n,
        "word": word,
        "initial": initial,
        "section": [
            {
                "label": x["label"],
                "quarter": x["quarter"],
                "center": x["center"],
                "radius": "1/100000000000",
            }
            for x in section
        ],
        "ordered_groups": len(groups),
        "group_sizes": [len(g["events"]) for g in groups],
    }


def determinant(M):
    """Fraction-free integer Bareiss elimination, including pivot changes."""
    M = [r[:] for r in M]
    n = len(M)
    previous = 1
    sign = 1
    if n == 0:
        return 1
    for i in range(n - 1):
        if M[i][i] == 0:
            j = next((j for j in range(i + 1, n) if M[j][i]), None)
            if j is None:
                return 0
            M[i], M[j] = M[j], M[i]
            sign = -sign
        pivot = M[i][i]
        for j in range(i + 1, n):
            for k in range(i + 1, n):
                num = M[j][k] * pivot - M[j][i] * M[i][k]
                q, r = divmod(num, previous)
                require(r == 0, "Bareiss division was not exact.")
                M[j][k] = q
            M[j][i] = 0
        previous = pivot
    return sign * M[-1][-1]


def burau_matrix(word, n, t):
    require(type(n) is int and n >= 1, "Use a positive strand count.")
    require(
        all(type(k) is int and 1 <= k < n for k in word),
        "Use positive Artin generators.",
    )
    require(type(t) is int, "Use integer Burau evaluations.")
    M = [[int(i == j) for j in range(n)] for i in range(n)]
    for k in word:
        i = k - 1
        j = k
        for row in M:
            a, b = row[i], row[j]
            row[i] = (1 - t) * a + b
            row[j] = t * a
    require(
        all(sum(row) == 1 for row in M),
        "The Burau matrix must fix the all-ones vector.",
    )
    return M


def burau_value(word, n, t):
    """det(I-reduced Burau); quotient out the invariant all-ones vector."""
    M = burau_matrix(word, n, t)
    R = [[M[i][j] - M[-1][j] for j in range(n - 1)] for i in range(n - 1)]
    return determinant(
        [[int(i == j) - R[i][j] for j in range(n - 1)] for i in range(n - 1)]
    )


def polynomial(word, n):
    """Exact Alexander polynomial via interpolation of a bounded-degree determinant.

    Each generator has rank-one dependence on its own variable. The
    determinant is multiaffine in those variables, hence degree <= len(word)
    after identifying them. len(word)+1 exact evaluations determine it.
    """
    degree = len(word)
    values = [burau_value(word, n, t) for t in range(degree + 1)]
    differences = []
    while values:
        differences.append(values[0])
        values = [b - a for a, b in zip(values, values[1:])]
    # Newton forward formula, with monomial expansion of the falling factorial.
    falling = [1]
    coeff = [Q(0)] * (degree + 1)
    for k, difference in enumerate(differences):
        for j, c in enumerate(falling):
            coeff[j] += Q(difference * c, factorial(k))
        new = [0] * (len(falling) + 1)
        for j, c in enumerate(falling):
            new[j] -= k * c
            new[j + 1] += c
        falling = new
    require(
        all(c.denominator == 1 for c in coeff),
        "The interpolated determinant has noninteger coefficients.",
    )
    coeff = [int(c) for c in coeff]
    if not any(coeff):
        return [0]
    require(len(coeff) >= n, "The nonzero numerator has insufficient degree.")
    quot = [0] * (len(coeff) - n + 1)
    for k in reversed(range(len(quot))):
        quot[k] = coeff[k + n - 1]
        for j in range(n):
            coeff[k + j] -= quot[k]
    require(
        not any(coeff), "The Burau numerator is not divisible by the closure factor."
    )
    while len(quot) > 1 and quot[-1] == 0:
        quot.pop()
    return quot


def value(coefficients, t):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * t + coefficient
    return result


def controls():
    from itertools import permutations
    from random import Random

    # Machin's identity: tan(4 atan(1/5)) = 120/119, then subtract
    # atan(1/239) to obtain tan(pi/4)=1 in the first quadrant.
    x = Q(1, 5)
    tangent = (4 * x - 4 * x**3) / (1 - 6 * x * x + x**4)
    require(
        tangent == Q(120, 119)
        and (tangent - Q(1, 239)) / (1 + tangent * Q(1, 239)) == 1,
        "Machin identity failed.",
    )
    require(
        Q("3.141592653589793238462") < PI.low <= PI.high < Q("3.141592653589793238463"),
        "The rational pi enclosure failed.",
    )
    require(
        dot(N, N) == 1 and 0 < SEAM.low <= SEAM.high < PI.low,
        "The initial normal changed.",
    )
    for x in (Q(-4), Q(-1), Q(-1, 2), Q(0), Q(1, 2), Q(1), Q(4)):
        a, b = atan(I.wrap(x)), atan(I.wrap(-x))
        require(a.low == -b.high and a.high == -b.low, "Arctangent lost odd symmetry.")
    a = atan(I.wrap(1))
    require(
        a.low <= (PI / 4).low and a.high >= (PI / 4).high,
        "Arctangent reduction at one failed.",
    )
    for word, n, expected in [
        ([], 1, [1]),
        ([], 3, [0]),
        ([1], 2, [1]),
        ([1, 1, 1], 2, [1, -1, 1]),
        ([1, 2], 3, [1]),
        ([1, 2, 1, 2], 3, [1, -1, 1]),
        ([1, 1, 1, 2], 3, [1, -1, 1]),
    ]:
        require(
            polynomial(word, n) == expected,
            "An unknot, split-link, trefoil, or stabilization control failed.",
        )
    for t in (-2, 0, 1, 3):
        require(
            burau_matrix([1, 2, 1], 3, t) == burau_matrix([2, 1, 2], 3, t),
            "The braid relation failed.",
        )
        require(
            burau_matrix([1, 3], 4, t) == burau_matrix([3, 1], 4, t),
            "Distant generators failed to commute.",
        )
    require(
        determinant([[0, 1], [1, 0]]) == -1 and determinant([[1, 2], [2, 4]]) == 0,
        "A determinant pivot or singularity control failed.",
    )
    rng = Random(106)
    for _ in range(24):
        matrix = [[rng.randrange(-4, 5) for _ in range(4)] for _ in range(4)]
        leibniz = 0
        for permutation in permutations(range(4)):
            inversions = sum(
                permutation[i] > permutation[j]
                for i in range(4)
                for j in range(i + 1, 4)
            )
            product = (-1) ** inversions
            for i in range(4):
                product *= matrix[i][permutation[i]]
            leibniz += product
        require(
            determinant(matrix) == leibniz,
            "Bareiss and the independent Leibniz formula disagree.",
        )
    for bad in ([0], [11], [-1], [1.5]):
        try:
            burau_matrix(bad, 11, 2)
        except ValueError:
            pass
        else:
            raise ValueError("An invalid positive braid word was accepted.")
    print(
        "Rational angle, matrix, braid-relation, unknot, trefoil, and stabilization controls passed.",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    require(
        not (args.saved and args.write),
        "Writing requires fresh complete census proofs.",
    )
    start = monotonic()
    controls()
    conjugacy_controls()
    census_controls()
    here = Path(__file__).resolve().parent
    if args.saved:
        source = json.loads((here / "normal_front_census.json").read_text())[
            "endpoints"
        ]
        require(
            [r["inner"] for r in source] == [6, 8],
            "Both endpoint records are required.",
        )
        print(
            "Using archived front censuses: completeness is conditional on their separate proofs.",
            flush=True,
        )
    else:
        source = [FrontCensus(n).run() for n in (6, 8)]
    results = []
    for record in source:
        result = certify_word(record)
        require(len(result["word"]) == 106, "The certified braid length changed.")
        coefficients = polynomial(result["word"], 11)
        require(
            len(coefficients) == 97
            and coefficients[0] == coefficients[-1] == 1
            and coefficients == coefficients[::-1]
            and value(coefficients, 1) == 1,
            "The Alexander normalization failed.",
        )
        for t in (-2, -1, 107):
            require(
                value(coefficients, t) * sum(t**k for k in range(11))
                == burau_value(result["word"], 11, t),
                "An evaluation outside the interpolation grid disagrees.",
            )
        require(value(coefficients, -1) == 189, "The knot determinant changed.")
        result["alexander_coefficients"] = coefficients
        results.append(result)
    require(
        results[0]["alexander_coefficients"] == results[1]["alexander_coefficients"],
        "The endpoint Alexander polynomials differ.",
    )
    print(
        "Both degree-96 Alexander polynomials agree coefficient by coefficient; determinant 189.",
        flush=True,
    )
    images = verify_conjugacy(results[0]["word"], results[1]["word"])
    try:
        verify_conjugacy(results[0]["word"], results[1]["word"], list(CONJUGATOR) + [1])
    except ValueError:
        pass
    else:
        raise ValueError("The altered-conjugator control was accepted.")
    print(
        f"Explicit conjugacy A C = C B verified by both Artin actions, |C|={len(CONJUGATOR)}. The ordinary braid closures are isotopic.",
        flush=True,
    )
    if args.write:
        output = {
            "description": "Fresh complete front covers, rational strand-order proofs, faithful Artin conjugacy, and integer Burau determinants.",
            "strands": 11,
            "normal_section": ["3/5", "4/5"],
            "endpoints": results,
            "conjugator": list(CONJUGATOR),
            "common_artin_images": images,
        }
        (here / "normal_front_braid.json").write_text(
            json.dumps(output, indent=2) + "\n"
        )
        print("Wrote normal_front_braid.json after both complete proofs.", flush=True)
    print(
        f"Completed in {monotonic()-start:.2f}s. Ordinary knot equivalence is certified; explicit Legendrian and plane-curve isotopies are not constructed.",
        flush=True,
    )


if __name__ == "__main__":
    main()
