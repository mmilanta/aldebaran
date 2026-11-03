"""Selected positive passages force at least 992 triples on the distant route.

Eight rational fourfold certificates and five reflected ordinary-triple
pairs force 18 and 10 positive passages on the outward legs. The route
bound also uses the separately proved radial signed changes and middle
movie. This is not a complete offset-event census. Standard library only.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations, permutations
import json
from math import pi, tan
from pathlib import Path
from time import monotonic

from blend_cusps import Interval as I, require
from normal_front import dot
from offset_fourfold import certify as fourfold
from parallel_offset_events import compact_interval, isolate_contact
from parallel_offset_triple import equations
from phase_unfolding import inverse, sqrt_interval
from positive_front_projection import decimal_enclosure
from rhythm_tangencies import cross

HERE = Path(__file__).resolve().parent
# Suggestions only. Every accepted event needs a fresh exact proof.
FOURFOLDS = {
    6: ((.2984144840557619, 2.202712969118725, 2),
        (.3023082119765989, 1.5723396995095589, 2),
        (.30278630664966877, 2.811898496819036, 2),
        (.5332739499897539, 1.0908915660590388, 4),
        (.3104394015634566, .8719034046957562, 2)),
    8: ((.30876327937934533, 2.8157434097407013, 2),
        (.3088298868188617, 2.163837279522111, 2),
        (.30901085176064447, 1.510120409485809, 2)),
}
TRIPLES = {
    6: ((.7670861882766609, 1.3390210948056431, 2.441701053407183),
        (.7636467134724487, 1.345390694680269, 2.9968294542222598),
        (1.940474065432614, 3.0691506602851106, 3.6633837929664335)),
    8: ((2.0188610747689406, 3.089403403154593, 3.6280687704165864),
        (1.3880581990205858, 2.4489113639551157, 2.989640179801288)),
}


def dyadic(x):
    return I(*map(Q, compact_interval(x)))


def preconditioner(matrix):
    # Any rational matrix is allowed in the contraction. Inverting compact
    # midpoint suggestions avoids unnecessary huge exact denominators.
    rounded = [[dyadic(x).midpoint() for x in row] for row in matrix]
    return [[dyadic(I.wrap(x)).midpoint() for x in row] for row in inverse(rounded)]


def ordered(quarters, box):
    return all(0 <= q < 4 and 0 < s.low < s.high < 1 for q, s in zip(quarters, box)) and all(
        q < r or q == r and a.high < b.low
        for q, r, a, b in zip(quarters, quarters[1:], box, box[1:]))


def direction_controls():
    """Exact controls for the circle-area interpretation of the signs.

    Three distinct circle points have nonzero oriented area. Six cyclic
    orders of four visits give only 0, 2, or 4 positive triple subsets.
    The tangent-half-angle area identity is checked independently against
    the actual three-line intersection triangle over rational normals.
    """
    from triple_area import coefficient, linear_intersection

    normals = [(Q(1) - s * s, 2 * s) for s in map(Q, (0, Q(1, 3), 1, 3))]
    normals = [(x / (1 + s * s), y / (1 + s * s))
               for (x, y), s in zip(normals, map(Q, (0, Q(1, 3), 1, 3)))]
    inventories = []
    for rest in permutations(range(1, 4)):
        order = (0, *rest)
        positives = 0
        for indices in combinations(order, 3):
            a, b, c = [normals[i] for i in indices]
            H = -(cross(a, b) + cross(b, c) + cross(c, a))
            area2 = cross((b[0] - a[0], b[1] - a[1]), (c[0] - a[0], c[1] - a[1]))
            require(H == -area2 and H != 0, "A direction-triangle sign control failed.")
            positives += H > 0
        inventories.append(positives)
    require(sorted(inventories) == [0, 2, 2, 2, 2, 4], "The fourfold cyclic sign inventory changed.")
    values = [Q(k, 4) for k in range(-9, 10)]
    points = [((1 - s * s) / (1 + s * s), 2 * s / (1 + s * s)) for s in values]
    tested = 0
    for selected in combinations(points, 3):
        if any(cross(a, b) == 0 for a, b in combinations(selected, 2)):
            continue
        tangents = [(n[1], -n[0]) for n in selected]
        motions = [(-n[0], -n[1]) for n in selected]
        actual = [linear_intersection(motions[i], tangents[i], motions[j], tangents[j])
                  for i, j in ((0, 1), (1, 2), (2, 0))]
        area = abs(cross((actual[1][0] - actual[0][0], actual[1][1] - actual[0][1]),
                         (actual[2][0] - actual[0][0], actual[2][1] - actual[0][1]))) / 2
        half_angle_product = Q(1)
        for i, j in ((0, 1), (1, 2), (2, 0)):
            half_angle_product *= cross(selected[i], selected[j]) / (1 + dot(selected[i], selected[j]))
        require(area == abs(half_angle_product) == coefficient(tangents, motions),
                "The normal-only area identity failed its independent triangle control.")
        tested += 1
    print(f"Six cyclic fourfold orders and {tested} exact normal-circle / tangent-triangle area controls passed.", flush=True)
    return tested


def triple(inner, quarters, centers, radius=Q(1, 10**16)):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(len(quarters) == len(centers) == 3, "A triple needs three visits.")
    require(all(type(q) is int for q in quarters) and all(type(c) is Q for c in centers)
            and type(radius) is Q and radius > 0, "Use exact centers and a positive radius.")
    require(ordered(quarters, [I(c - radius, c + radius) for c in centers]),
            "The triple boxes must be disjoint and in orbit order.")
    # These steps choose compact centers, not proof decisions. The complete
    # box is verified afterward, without assuming Newton convergence.
    for _ in range(2):
        F, J, *_ = equations(quarters, tuple(I.wrap(c) for c in centers), inner)
        R = preconditioner(J)
        centers = [dyadic(I.wrap(c - sum(R[i][k] * F[k].midpoint()
                                        for k in range(3)))).midpoint()
                   for i, c in enumerate(centers)]
    box = [I(c - radius, c + radius) for c in centers]
    require(ordered(quarters, box), "Refined visits left their disjoint ordered charts.")
    F0, J0, *_ = equations(quarters, tuple(I.wrap(c) for c in centers), inner)
    _, J, _, _, _ = equations(quarters, box, inner)
    R = preconditioner(J0)
    F0 = [dyadic(x) for x in F0]
    J = [[dyadic(x) for x in row] for row in J]
    E = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in E)
    require(norm < Q(1, 10**5), "The triple box is not a strong contraction.")
    image = [-sum(R[i][k] * F0[k] for k in range(3))
             + sum(E[i][j] * I(-radius, radius) for j in range(3)) for i in range(3)]
    require(all(-radius < x.low <= x.high < radius for x in image),
            "The triple contraction is not strictly interior.")
    root_box = [dyadic(c + d) for c, d in zip(centers, image)]
    _, _, location, radii, velocities = equations(quarters, root_box, inner)
    require(all(dot(r, (-v[1], v[0])).low > 0 for r, v in zip(radii, velocities)),
            "A circle is not an outward offset meeting.")
    for a, b in combinations(velocities, 2):
        cross(a, b).sign()
    normals = [(-v[1] / sqrt_interval(dot(v, v)), v[0] / sqrt_interval(dot(v, v)))
               for v in velocities]
    H = -sum((cross(normals[i], normals[j]) for i, j in ((0, 1), (1, 2), (2, 0))), I.wrap(0))
    require(H.low > 0, "The selected ordinary passage is not positive.")
    offset = sqrt_interval(dot(radii[0], radii[0]))
    record = {"inner": inner, "quarters": list(quarters), "center": list(map(str, centers)),
              "radius": str(radius), "root_box": [compact_interval(x) for x in root_box],
              "norm_upper": compact_interval(I.wrap(norm))[1],
              "offset": compact_interval(offset), "point": [compact_interval(x) for x in location],
              "strangeness_jump": 1, "normalized_unfolding": compact_interval(H)}
    record["isolation"] = isolate_contact(record, inner)
    # Exact central differences audit the full three-variable Jacobian.
    # A smaller step is needed at the distant, ill-conditioned circles.
    epsilon = Q(1, 10**15)
    errors = []
    for axis in range(3):
        plus, minus = centers[:], centers[:]
        plus[axis] += epsilon
        minus[axis] -= epsilon
        fp = equations(quarters, tuple(I.wrap(c) for c in plus), inner)[0]
        fm = equations(quarters, tuple(I.wrap(c) for c in minus), inner)[0]
        for row in range(3):
            error = (fp[row] - fm[row]) / (2 * epsilon) - J0[row][axis]
            require(-Q(1, 1000) < error.low <= error.high < Q(1, 1000),
                    "The triple Jacobian disagrees with exact differences.")
            errors.append(max(abs(error.low), abs(error.high)))
    record["jacobian_difference_comparisons"] = len(errors)
    print(f"11/{inner}: positive ordinary triple, M in {decimal_enclosure(offset, 10)}; "
          f"no fourth branch ({record['isolation']['excluded_arcs']} arc exclusions).", flush=True)
    return record


def reflected_pair(inner, hints):
    quarters = [int(t / (pi / 2)) for t in hints]
    centers = [Q(str(tan((t - q * pi / 2) / 2))) for q, t in zip(quarters, hints)]
    first = triple(inner, quarters, centers)
    require(Q(first["point"][1][0]) > 0, "The first event must lie strictly above the mirror axis.")
    centers = [(1 - Q(c)) / (1 + Q(c)) for c in first["center"][::-1]]
    second = triple(inner, [3 - q for q in quarters[::-1]], centers)
    reflected = [(I.wrap(1) - s) / (1 + s)
                 for s in [I(*map(Q, b)) for b in first["root_box"][::-1]]]
    require(all(c - Q(second["radius"]) < s.low <= s.high < c + Q(second["radius"])
                for c, s in zip(map(Q, second["center"]), reflected)),
            "The exact reflected root left its unique mate's box.")
    require(Q(second["point"][1][1]) < 0, "The reflected meeting must lie below the axis.")
    return [first, second]


def prove():
    endpoints = []
    for inner in (6, 8):
        circles, ordinary = [], []
        for t, u, positive in FOURFOLDS[inner]:
            signs = (1,) * positive + (-1,) * (4 - positive)
            circles.append(fourfold(inner, (t, u), signs, radius=Q(1, 10**16), refinement_steps=2))
        for hints in TRIPLES[inner]:
            ordinary.extend(reflected_pair(inner, hints))
        events = circles + ordinary
        for a, b in combinations(events, 2):
            A, B = [a["offset"], *a["point"]], [b["offset"], *b["point"]]
            require(any(Q(x[1]) < Q(y[0]) or Q(y[1]) < Q(x[0]) for x, y in zip(A, B)),
                    "Two selected event neighborhoods may coincide.")
        positives = sum(t["strangeness_jump"] == 1 for c in circles for t in c["triples"]) + len(ordinary)
        endpoints.append({"inner": inner, "fourfolds": circles, "ordinary_triples": ordinary,
                          "positive_lower_bound": positives})
    require([e["positive_lower_bound"] for e in endpoints] == [18, 10],
            "The selected positive passage inventory changed.")
    # These are separately established input theorems, not a consequence
    # of the selected local boxes. Audit their saved arithmetic here.
    radial = json.loads((HERE / "radial_word.json").read_text())
    signed = [e["outward_signed_triples"] for e in radial["endpoints"]]
    middle = radial["movie"]
    require(signed == [-102, -112] and (middle["positive_triples"], middle["negative_triples"])
            == (354, 368), "The separate radial-word inputs changed.")
    for endpoint, net in zip(endpoints, signed):
        endpoint["negative_lower_bound"] = endpoint["positive_lower_bound"] - net
        endpoint["triple_lower_bound"] = endpoint["positive_lower_bound"] + endpoint["negative_lower_bound"]
    positive = endpoints[0]["positive_lower_bound"] + middle["positive_triples"] + endpoints[1]["negative_lower_bound"]
    negative = endpoints[0]["negative_lower_bound"] + middle["negative_triples"] + endpoints[1]["positive_lower_bound"]
    require((positive, negative) == (494, 498), "The full-route signed bookkeeping failed.")
    return {"scope": "Selected local event certificates, not a complete offset census. Lower bounds additionally use the separate radial-word theorem, for a sufficiently distant common offset with no numerical threshold.",
            "endpoints": endpoints, "full_route_positive_lower_bound": positive,
            "full_route_negative_lower_bound": negative, "full_route_triple_lower_bound": positive + negative,
            "radial_input_signed_changes": signed, "middle_positive_triples": middle["positive_triples"],
            "middle_negative_triples": middle["negative_triples"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="save only freshly certified local events")
    args = parser.parse_args()
    started = monotonic()
    direction_controls()
    result = prove()
    if args.write:
        (HERE / "offset_positive.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Selected positives force at least 138 and 132 outward triples; the sufficiently distant full route needs at least 992 (494 positive, 498 negative).", flush=True)
    print(f"Elapsed {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
