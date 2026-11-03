"""Two selected mirror-axis fourfold meetings on outward offset legs.

Rational contractions certify two upper-half parameter visits; reflection
supplies the other two. Whole-orbit covers exclude a fifth branch. Each
of the four triples has transverse unfolding, and explicit small normal
shifts separate their first-order event weights. These are selected
events, not a complete offset census. Standard library only.
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
from parallel_offset_events import compact_interval, isolate_contact
from phase_unfolding import inverse, sqrt_interval
from positive_front_projection import decimal_enclosure
from rhythm_tangencies import cross, evaluate

HINTS = {6: (0.2984144840557619, 2.202712969118725),
         8: (0.30876327937934533, 2.8157434097407013)}


def axis_jet(quarter, parameter, inner):
    p, v, a = [evaluate(quarter, parameter, Q(inner - 6, 2), order) for order in range(3)]
    length = p[1] / v[0]
    length_prime = (v[1] * v[0] - p[1] * a[0]) / (v[0] * v[0])
    center = p[0] + length * v[1]
    center_prime = v[0] + length_prime * v[1] + length * a[1]
    radius2 = length * length * dot(v, v)
    radius2_prime = 2 * length * length_prime * dot(v, v) + 2 * length * length * dot(v, a)
    factor = I.wrap(2) / (1 + parameter * parameter)
    return (center, radius2), (center_prime * factor, radius2_prime * factor), length


def equations(quarters, parameters, inner):
    first, second = [axis_jet(q, s, inner) for q, s in zip(quarters, parameters)]
    F = [a - b for a, b in zip(first[0], second[0])]
    J = [[first[1][k], -second[1][k]] for k in range(2)]
    return F, J


def determinant(matrix):
    total = I.wrap(0)
    for perm in permutations(range(len(matrix))):
        inversions = sum(perm[i] > perm[j] for i in range(len(perm)) for j in range(i + 1, len(perm)))
        term = I.wrap((-1) ** inversions)
        for i, j in enumerate(perm):
            term *= matrix[i][j]
        total += term
    return total


def certify(inner, hints=None, expected_signs=(-1, -1, 1, 1), radius=Q(1, 10**12), refinement_steps=0):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    hints = HINTS[inner] if hints is None else hints
    require(len(hints) == 2 and 0 < hints[0] < hints[1] < pi,
            "Order two distinct upper-half visits.")
    quarters = [int(t / (pi / 2)) for t in hints]
    centers = [Q(str(tan((t - q * pi / 2) / 2))) for q, t in zip(quarters, hints)]
    require(type(radius) is Q and radius > 0, "Use a positive rational chart radius.")
    require(type(refinement_steps) is int and 0 <= refinement_steps <= 4,
            "Use zero to four untrusted center refinements.")
    for _ in range(refinement_steps):
        F, J = equations(quarters, [I.wrap(c) for c in centers], inner)
        R = inverse([[x.midpoint() for x in row] for row in J])
        centers = [I(*map(Q, compact_interval(I.wrap(c - sum(R[i][k] * F[k].midpoint()
                           for k in range(2)))))).midpoint() for i, c in enumerate(centers)]
    box = [I(c - radius, c + radius) for c in centers]
    require(all(0 < s.low < s.high < 1 for s in box)
            and (quarters[0] < quarters[1] or quarters[0] == quarters[1] and box[0].high < box[1].low),
            "The upper-half visit boxes must be disjoint and in orbit order.")
    F0, J0 = equations(quarters, [I.wrap(c) for c in centers], inner)
    _, J = equations(quarters, box, inner)
    R = inverse([[x.midpoint() for x in row] for row in J0])
    E = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in E)
    require(norm < Q(1, 10**5), "The axis-circle root is not a strong contraction.")
    image = [-sum(R[i][k] * F0[k] for k in range(2)) + sum(E[i][j] * I(-radius, radius) for j in range(2)) for i in range(2)]
    require(all(-radius < x.low <= x.high < radius for x in image), "The axis-circle image is not strictly interior.")
    half_root = [I(*map(Q, compact_interval(I(c + shift.low, c + shift.high))))
                 for c, shift in zip(centers, image)]
    data = [axis_jet(q, s, inner) for q, s in zip(quarters, half_root)]
    require(all(row[2].low > 0 for row in data), "A selected radius gives an inward offset.")
    offset = sqrt_interval(data[0][0][1])
    location = data[0][0][0]
    # Reflection in the real axis: quarter q -> 3-q, s -> (1-s)/(1+s).
    reflected = [(I.wrap(1) - s) / (1 + s) for s in half_root[::-1]]
    reflected_centers = [(1 - c) / (1 + c) for c in centers[::-1]]
    full_centers = centers + reflected_centers
    full_quarters = quarters + [3 - q for q in quarters[::-1]]
    full_radius = 4 * radius
    full_box = [I(c - full_radius, c + full_radius) for c in full_centers]
    require(all(a.low < b.low <= b.high < a.high for a, b in zip(full_box[2:], reflected)),
            "Reflected root intervals left the four-visit boxes.")
    require(all(q < r or q == r and a.high < b.low
                for q, r, a, b in zip(full_quarters, full_quarters[1:], full_box, full_box[1:])),
            "The four visit boxes must be disjoint and in orbit order.")
    root_box = [I(*map(Q, compact_interval(x))) for x in half_root + reflected]
    record = {"inner": inner, "quarters": full_quarters,
              "center": list(map(str, full_centers)), "radius": str(full_radius),
              "half_radius": str(radius), "norm_upper": compact_interval(I.wrap(norm))[1],
              "root_box": [compact_interval(x) for x in root_box],
              "offset": compact_interval(offset), "point": [compact_interval(location), ["0", "0"]]}
    normals, velocities = [], []
    for quarter, s in zip(full_quarters, root_box):
        v = evaluate(quarter, s, Q(inner - 6, 2), 1)
        speed = sqrt_interval(dot(v, v))
        velocities.append(v)
        normals.append((-v[1] / speed, v[0] / speed))
    for i, j in combinations(range(4), 2):
        cross(velocities[i], velocities[j]).sign()
    # A concrete local normal perturbation, h_i -> h_i+epsilon*a_i.
    # First-order triple weights solve N_i.X + d = a_i.
    shifts = [0, 1, 3, 7]
    triples = []
    for indices in combinations(range(4), 3):
        a, b, c = [normals[i] for i in indices]
        H = -(cross(a, b) + cross(b, c) + cross(c, a))
        sign = H.sign()
        matrix = [[*normals[i], I.wrap(1)] for i in indices]
        denominator = determinant(matrix)
        denominator.sign()
        replaced = [[*normals[i], I.wrap(shifts[i])] for i in indices]
        weight = determinant(replaced) / denominator
        triples.append({"visits": list(indices), "strangeness_jump": sign,
                        "normalized_unfolding": compact_interval(H),
                        "first_order_weight": compact_interval(weight)})
    signs = sorted(t["strangeness_jump"] for t in triples)
    require(signs == sorted(expected_signs), "The selected fourfold's sign inventory changed.")
    ordered = sorted(range(4), key=lambda i: Q(triples[i]["first_order_weight"][0]))
    require(all(Q(triples[a]["first_order_weight"][1]) < Q(triples[b]["first_order_weight"][0])
                for a, b in zip(ordered, ordered[1:])), "The explicit perturbation did not separate all four weights.")
    record["normal_shifts"] = shifts
    record["triples"] = triples
    record["perturbed_order"] = ordered
    record["isolation"] = isolate_contact(record, inner)
    # Independent exact differences of the two-variable rational equations.
    epsilon = Q(1, 10**13)
    for axis in range(2):
        plus, minus = centers[:], centers[:]
        plus[axis] += epsilon
        minus[axis] -= epsilon
        fp = equations(quarters, [I.wrap(c) for c in plus], inner)[0]
        fm = equations(quarters, [I.wrap(c) for c in minus], inner)[0]
        for row in range(2):
            error = (fp[row] - fm[row]) / (2 * epsilon) - J0[row][axis]
            require(-Q(1, 1000) < error.low <= error.high < Q(1, 1000), "The axis-circle Jacobian disagrees with exact differences.")
    print(f"11/{inner}: one certified four-visit axis circle, M in {decimal_enclosure(offset, 12)}; no fifth branch ({record['isolation']['excluded_arcs']} arc exclusions).", flush=True)
    print(f"  Normal shifts {shifts} separate four ordinary triples, {signs.count(1)} positive and {signs.count(-1)} negative; perturbed order {ordered}.", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    started = monotonic()
    records = [certify(inner) for inner in (6, 8)]
    if args.write:
        target = Path(__file__).resolve().parent / "offset_fourfold.json"
        target.write_text(json.dumps({
            "scope": "Two selected fourfold meetings; fifth-branch exclusions and explicit generic local resolutions. Not a global event census.",
            "events": records,
            "strengthened_outward_lower_bounds": [106, 116],
            "strengthened_full_route_lower_bound": 944,
        }, indent=2) + "\n")
    print("Two unavoidable positive triples on each outward leg raise its triple lower bound by four: 106 and 116, hence at least 944 for the sufficiently distant full route.", flush=True)
    print(f"Elapsed {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
