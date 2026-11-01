"""Rational boxes for all positive inverse-contact pairs on two offset legs.

The analytic count is established by parallel_offset.py and its note.
This file certifies 33 distinct pairs at each endpoint. Combined with that
count it supplies every positive event location. The numerical hints are
never trusted. Standard library only; --write archives the proved boxes.
"""

import argparse
from fractions import Fraction as Q
import json
from math import pi, tan
from pathlib import Path

from blend_cusps import Interval as I, require
from normal_front import check_evaluation, dot
from phase_unfolding import inverse, sqrt_interval
from rhythm_tangencies import cross, evaluate

HERE = Path(__file__).resolve().parent


def compact_interval(interval):
    """Outward dyadics keep saved enclosures short without losing a root."""
    denominator = 2 ** 80
    low = Q((interval.low * denominator) // 1, denominator)
    high = Q(-((-interval.high * denominator) // 1), denominator)
    require(low <= interval.low <= interval.high <= high, "Dyadic rounding narrowed an enclosure.")
    return list(map(str, (low, high)))


def equations(quarters, box, inner):
    """Parallel tangents and a normal chord; chart-parameter Jacobian."""
    weight = Q(inner - 6, 2)
    points, velocities, accelerations = [
        [evaluate(q, s, weight, order) for q, s in zip(quarters, box)]
        for order in range(3)
    ]
    v, w = velocities
    A, B = accelerations
    delta = tuple(a - b for a, b in zip(*points))
    factors = [I.wrap(2) / (1 + s * s) for s in box]
    F = [cross(v, w), dot(delta, v)]
    J = [
        [factors[0] * cross(A, w), factors[1] * cross(v, B)],
        [factors[0] * (dot(v, v) + dot(delta, A)), -factors[1] * dot(w, v)],
    ]
    return F, J


def certify(quarters, center, inner, radius=Q(1, 10**11)):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(len(quarters) == len(center) == 2, "An event needs two visits.")
    require(all(type(q) is int and 0 <= q < 4 for q in quarters), "Invalid circle quarter.")
    require(all(type(s) is Q for s in center) and type(radius) is Q and radius > 0, "Use rational centers and a positive radius.")
    box = tuple(I(s - radius, s + radius) for s in center)
    require(all(0 < s.low < s.high < 1 for s in box), "An event box leaves its circle quarter.")
    require(quarters[0] < quarters[1] or quarters[0] == quarters[1] and box[0].high < box[1].low, "Visit boxes must be distinct and in orbit order.")
    F, J0 = equations(quarters, tuple(I.wrap(s) for s in center), inner)
    _, J = equations(quarters, box, inner)
    R = inverse([[x.midpoint() for x in row] for row in J0])
    defect = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 10**6), "The normal-chord box is not a strong contraction.")
    offsets = [-sum(R[i][k] * F[k] for k in range(2)) + sum(defect[i][j] * I(-radius, radius) for j in range(2)) for i in range(2)]
    require(all(-radius < x.low <= x.high < radius for x in offsets), "The normal-chord map does not send its box strictly inside itself.")
    weight = Q(inner - 6, 2)
    positions = [evaluate(q, s, weight) for q, s in zip(quarters, box)]
    velocities = [evaluate(q, s, weight, 1) for q, s in zip(quarters, box)]
    require(dot(*velocities).high < 0, "The velocities are not opposite.")
    delta = tuple(a - b for a, b in zip(*positions))
    v = velocities[0]
    require(dot(delta, (-v[1], v[0])).low > 0, "This chord gives a negative offset.")
    distance = sqrt_interval(dot(delta, delta)) / 2
    require(0 < distance.low <= distance.high < 157, "The positive offset bound failed.")
    require(distance.high - distance.low < Q(1, 10**4), "The event weight enclosure is too wide.")
    midpoint = [(a + b) / 2 for a, b in zip(*positions)]
    root_box = [I(s + shift.low, s + shift.high) for s, shift in zip(center, offsets)]
    return {"quarters": list(quarters), "center": list(map(str, center)), "radius": str(radius),
            "offset": compact_interval(distance),
            "point": [compact_interval(x) for x in midpoint],
            "root_box": [compact_interval(x) for x in root_box],
            "norm_upper": compact_interval(I.wrap(norm))[1]}, box


def parameters(hint):
    require(len(hint) == 2 and 0 < hint[0] < hint[1] < 2 * pi, "Order two interior times.")
    quarters = tuple(int(t / (pi / 2)) for t in hint)
    center = tuple(Q(str(tan((t - q * pi / 2) / 2))) for q, t in zip(quarters, hint))
    return quarters, center


def isolate_contact(record, inner):
    """Exclude every other visit from the contact box for its whole M interval.

    q_M'=(1+M*kappa)q' has the sign of the original coordinate velocity.
    Thus each admitted slot contains at most one visit to the contact.
    All other rational arcs are excluded from the full position box.
    """
    weight = Q(inner - 6, 2)
    offset = I(*map(Q, record["offset"]))
    origin = [I(*map(Q, bounds)) for bounds in record["point"]]
    slots, saved_slots = [], []
    for quarter, center in zip(record["quarters"], map(Q, record["center"])):
        radius = min(Q(1, 1000), center / 2, (1 - center) / 2)
        require(radius > Q(record["radius"]), "An isolation slot does not contain its root box.")
        domain = I(center - radius, center + radius)
        velocity = evaluate(quarter, domain, weight, 1)
        margins = [min(abs(v.low), abs(v.high)) if v.low * v.high > 0 else Q(0) for v in velocity]
        axis = max(range(2), key=lambda j: margins[j])
        require(margins[axis] > 0, "An admitted contact slot is not monotone.")
        slots.append((quarter, domain.low, domain.high))
        saved_slots.append({"quarter": quarter, "low": str(domain.low), "high": str(domain.high), "axis": axis,
                            "coordinate_speed_lower": compact_interval(I.wrap(margins[axis]))[0]})
    stats = {"excluded_arcs": 0, "max_depth": 0}

    def square(x):
        low = Q(0) if x.low <= 0 <= x.high else min(x.low ** 2, x.high ** 2)
        return I(low, max(x.low ** 2, x.high ** 2))

    def exclude(quarter, low, high, depth=0):
        domain = I(low, high)
        point = evaluate(quarter, domain, weight)
        velocity = evaluate(quarter, domain, weight, 1)
        speed2 = sum((square(v) for v in velocity), I.wrap(0))
        # The earlier uniform 775 <= |q'| <= 2305 bound sharpens wide arcs.
        speed = sqrt_interval(I(max(Q(775 ** 2), speed2.low), min(Q(2305 ** 2), speed2.high)))
        normal = (-velocity[1] / speed, velocity[0] / speed)
        shifted = [p - offset * n for p, n in zip(point, normal)]
        if any(a.high < b.low or b.high < a.low for a, b in zip(shifted, origin)):
            stats["excluded_arcs"] += 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            return
        require(depth < 24, "An unresolved arc may supply a third branch.")
        middle = (low + high) / 2
        exclude(quarter, low, middle, depth + 1)
        exclude(quarter, middle, high, depth + 1)

    for quarter in range(4):
        cuts = sorted({Q(k, 32) for k in range(33)} |
                      {x for q, low, high in slots if q == quarter for x in (low, high)})
        for low, high in zip(cuts, cuts[1:]):
            if any(q == quarter and a <= low < high <= b for q, a, b in slots):
                continue
            exclude(quarter, low, high)
    return {**stats, "slots": saved_slots}


def controls():
    # Independent exact rational central differences audit all Jacobian entries.
    count = 0
    for inner in (6, 8):
        for quarters, center in (((0, 2), (Q(1, 5), Q(2, 3))), ((1, 3), (Q(2, 7), Q(3, 4)))):
            _, J = equations(quarters, tuple(I.wrap(s) for s in center), inner)
            epsilon = Q(1, 10**9)
            for axis in range(2):
                plus, minus = list(center), list(center)
                plus[axis] += epsilon
                minus[axis] -= epsilon
                fp, _ = equations(quarters, tuple(I.wrap(s) for s in plus), inner)
                fm, _ = equations(quarters, tuple(I.wrap(s) for s in minus), inner)
                for row in range(2):
                    numerical = (fp[row].low - fm[row].low) / (2 * epsilon)
                    require(abs(numerical - J[row][axis].low) < Q(1, 10**5), "The normal-chord Jacobian failed its independent difference check.")
                    count += 1
    return count


def prove(isolate=True):
    hints = json.loads((HERE / "parallel_offset_hints.json").read_text())["hints"]
    count = controls()
    evaluator_count = check_evaluation()
    results = []
    for inner in (6, 8):
        rows, domains = [], []
        for hint in hints[str(inner)]:
            record, box = certify(*parameters(hint), inner)
            if isolate:
                record["isolation"] = isolate_contact(record, inner)
            rows.append(record)
            domains.append((record["quarters"], box))
            if isolate and len(rows) % 11 == 0:
                print(f"11/{inner}: {len(rows)}/33 contact points isolated from every third branch.", flush=True)
        require(len(rows) == 33, "The independent offset theorem requires 33 certified positive pairs.")
        comparisons = 0
        for i, (quarters, box) in enumerate(domains):
            for other_quarters, other_box in domains[:i]:
                require(any(q != r or a.high < b.low or b.high < a.low for q, r, a, b in zip(quarters, other_quarters, box, other_box)), "Two event boxes may describe the same unordered visit pair.")
                comparisons += 1
        # Positive and negative direction controls must not be interchangeable.
        quarters, center = parameters(hints[str(inner)][0])
        for q, c, radius in (
            (quarters[::-1], center[::-1], Q(1, 10**11)),
            (quarters, (center[0] + Q(1, 100), center[1]), Q(1, 10**11)),
            (quarters, center, Q(-1, 10**11)),
            ((quarters[0], quarters[0]), (center[0], center[0]), Q(1, 10**11)),
        ):
            try:
                certify(q, c, inner, radius)
            except ValueError:
                pass
            else:
                raise ValueError("An invalid normal-chord control was accepted.")
        negative = {6: (0.24525877584703498, 0.4683599014636729),
                    8: (0.2199706852464711, 0.4354800431076645)}[inner]
        try:
            certify(*parameters(negative), inner)
        except ValueError as error:
            require("negative offset" in str(error), "The negative-offset control failed before its sign test.")
        else:
            raise ValueError("A negative-offset root was accepted as positive.")
        # Reflection sends s to (1-s)/(1+s), reverses the visits, and
        # preserves M. Tiny fixed-point enclosures identify the other
        # unique-root box exactly; rounded M agreement is not trusted.
        mates = []
        for row in rows:
            quarters = [3 - q for q in row["quarters"][::-1]]
            small = [I(*map(Q, bounds)) for bounds in row["root_box"][::-1]]
            reflected = [(I.wrap(1) - s) / (1 + s) for s in small]
            targets = [j for j, (q, box) in enumerate(domains) if q == quarters
                       and all(a.low < b.low <= b.high < a.high for a, b in zip(box, reflected))]
            require(len(targets) == 1, "The reflected root has no unique certified mate.")
            mates.append(targets[0])
        require(all(mates[j] == i for i, j in enumerate(mates)), "Reflection is not an involution.")
        groups, seen = [], set()
        for i, mate in enumerate(mates):
            if i in seen:
                continue
            members = sorted({i, mate})
            seen.update(members)
            bounds = [tuple(map(Q, rows[j]["offset"])) for j in members]
            interval = [max(b[0] for b in bounds), min(b[1] for b in bounds)]
            require(interval[0] <= interval[1], "Reflected offsets have disjoint enclosures.")
            groups.append({"members": members, "offset": list(map(str, interval))})
        groups.sort(key=lambda group: Q(group["offset"][0]))
        require(all(Q(a["offset"][1]) < Q(b["offset"][0]) for a, b in zip(groups, groups[1:])), "Different weight groups are not separately ordered.")
        require(len(groups) == 18 and sum(len(g["members"]) == 1 for g in groups) == 3, "The reflection orbit count changed.")
        results.append({"inner": inner, "distinct_pair_comparisons": comparisons, "events": rows, "reflection_mates": mates, "ordered_weight_groups": groups})
        print(f"11/{inner}: 33 distinct positive inverse-contact pairs in rational boxes; {comparisons} pair separations.", flush=True)
        print("  Reflection certifies 15 pairs and 3 fixed events at 18 strictly ordered offset weights.", flush=True)
    print(f"{count} exact Jacobian difference controls and {evaluator_count} independent evaluator/previous-Jacobian comparisons; shifted, reversed, coincident, negative-radius, and certified negative-offset controls rejected.", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="save freshly proved boxes, conditional on the separate analytic completeness count")
    parser.add_argument("--pairs-only", action="store_true", help="skip the third-branch covers; cannot write a new full record")
    args = parser.parse_args()
    require(not (args.write and args.pairs_only), "Repeat third-branch covers before writing a full record.")
    results = prove(isolate=not args.pairs_only)
    if args.write:
        (HERE / "parallel_offset_events.json").write_text(json.dumps({
            "description": "Fresh rational contractions for 33 distinct positive inverse-contact pairs per endpoint, whole-orbit third-branch exclusions, exact reflection pairing, and ordered event weights. Completeness uses the analytic offset-count theorem and the separate plane/front counts; this is not an independent whole-orbit event product cover.",
            "endpoints": results,
        }, indent=2) + "\n")
    print("Given the separate count of 33 positive pairs per endpoint, these boxes exhaust both outward offset legs.")


if __name__ == "__main__":
    main()
