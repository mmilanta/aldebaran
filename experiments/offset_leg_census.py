"""A complete tangent-circle cover of the two outward offset legs.

Pairwise coplanarity of lifted circle lines supplies a complete graph.
Its triangles cover every possible triple, for every outward M >= 0.
Integer interval minors exclude boxes; rational contractions isolate roots.
No numerical hints or archived roots guide the cover. Standard library only.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

from blend_cusps import Interval as I, require
from normal_front import dot as rational_dot
from normal_front_census import ACCELERATION, MIN_SPEED, SPEED
from offset_circle_tail import compact
from parallel_offset_events import compact_interval
from parallel_offset_triple import solve
from phase_unfolding import inverse, sqrt_interval
from rhythm_tangencies import cross as rational_cross

HERE = Path(__file__).resolve().parent
SCALE = 2 ** 50
JERK = 245 + 140 * 11 ** 3 + 65 * 8 ** 3
PAIRS = tuple(combinations(range(3), 2))


def integer(interval):
    """Outward integer bounds on SCALE times a rational interval."""
    return interval.low * SCALE // 1, -(-interval.high * SCALE // 1)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def minus(a, b):
    return a[0] - b[1], a[1] - b[0]


def times(a, b):
    products = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return min(products), max(products)


def scale(a, n):
    return (a[0] * n, a[1] * n) if n >= 0 else (a[1] * n, a[0] * n)


def cross(a, b):
    return minus(times(a[0], b[1]), times(a[1], b[0]))


def dot(a, b):
    return plus(times(a[0], b[0]), times(a[1], b[1]))


def strict(a):
    return a[0] > 0 or a[1] < 0


def determinant(rows):
    a, b, c = rows
    return plus(plus(times(cross(a, b), c[2]),
                     times(minus(times(a[1], b[2]), times(a[2], b[1])), c[0])),
                times(minus(times(a[2], b[0]), times(a[0], b[2])), c[1]))


def pair_exclusion(first, second):
    """Necessary conditions for a common outward tangent circle.

    With h=q-p, Delta=det(v,w), normal-line parameters are
    L_p=-h.w/Delta, L_q=-h.v/Delta. They must both be nonnegative.
    Coplanarity of the two lifted circle lines is the division-free test
    |h|^2 Delta - 2(v.h)det(h,w)=0, also valid at parallel tangents.
    """
    p, v = first
    q, w = second
    h = tuple(minus(y, x) for x, y in zip(p, q))
    delta = cross(v, w)
    hv, hw = dot(h, v), dot(h, w)
    if delta[0] > 0 and (hv[0] > 0 or hw[0] > 0):
        return "inward"
    if delta[1] < 0 and (hv[1] < 0 or hw[1] < 0):
        return "inward"
    if strict(minus(times(dot(h, h), delta), times(scale(hv, 2), cross(h, w)))):
        return "skew"
    return None


def minor_exclusion(data):
    """All five homogeneous rows annihilate (P_x,P_y,-1).

    Multiply every row by SCALE^2. No interval division is needed, even
    for parallel normals, collinear original points, and infinite centers.
    """
    tangent = [[*[scale(x, SCALE) for x in v], dot(p, v)] for p, v in data]
    if strict(determinant(tangent)):
        return "normal_minor"
    points = [p for p, _ in data]
    chords = [[*[scale(minus(points[j][k], points[0][k]), 2 * SCALE)
                 for k in (0, 1)],
               minus(dot(points[j], points[j]), dot(points[0], points[0]))]
              for j in (1, 2)]
    for row in tangent:
        if strict(determinant([*chords, row])):
            return "chord_minor"
    for chord in chords:
        for i, j in PAIRS:
            if strict(determinant([chord, tangent[i], tangent[j]])):
                return "mixed_minor"
    return None


@lru_cache(maxsize=65536)
def exact_jets(quarter, s, inner):
    """Exact Fourier position, t-velocity, and t-acceleration at one point."""
    require(type(quarter) is int and 0 <= quarter < 4
            and type(s) is Q and 0 <= s <= 1
            and type(inner) is int and inner in (6, 8), "Invalid rational circle-chart point.")
    a, b = s.numerator, s.denominator
    w = (b * b - a * a, 2 * a * b)
    for _ in range(quarter):
        w = (-w[1], w[0])
    denominator = b * b + a * a
    powers, denominators = [(1, 0)], [1]
    for _ in range(11):
        x, y = powers[-1]
        powers.append((x * w[0] - y * w[1], x * w[1] + y * w[0]))
        denominators.append(denominators[-1] * denominator)
    result = []
    for order in range(3):
        coordinates = [0, 0]
        for k, radius in ((1, 245), (11, 140), (-inner, 65)):
            x, y = powers[abs(k)]
            if k < 0:
                y = -y
            for _ in range(order):
                x, y = -k * y, k * x
            coordinates[0] += radius * x * denominators[11 - abs(k)]
            coordinates[1] += radius * y * denominators[11 - abs(k)]
        result.append(tuple(Q(x, denominators[11]) for x in coordinates))
    return tuple(result)


@lru_cache(maxsize=65536)
def jets(domain, inner):
    """Taylor bounds on complete arcs, rounded outward to 80-bit dyadics."""
    quarter, low, high = domain
    require(type(low) is Q and type(high) is Q and 0 <= low <= high <= 1,
            "Invalid rational circle-chart interval.")
    p, v, a = exact_jets(quarter, (low + high) / 2, inner)
    radius_t = high - low  # dt/ds=2/(1+s^2) <= 2
    position_error, velocity_error = ACCELERATION * radius_t ** 2 / 2, JERK * radius_t ** 2 / 2
    position = [compact(I.wrap(x) + y * I(-radius_t, radius_t)
                        + I(-position_error, position_error)) for x, y in zip(p, v)]
    velocity = [compact(I.wrap(x) + y * I(-radius_t, radius_t)
                        + I(-velocity_error, velocity_error)) for x, y in zip(v, a)]
    acceleration = [compact(I(x - JERK * radius_t, x + JERK * radius_t)) for x in a]
    return tuple(position), tuple(velocity), tuple(acceleration)


@lru_cache(maxsize=65536)
def integer_jets(domain, inner):
    return tuple(tuple(integer(x) for x in row) for row in jets(domain, inner)[:2])


def equations(domains, inner):
    """Circumcenter tangency equations and their full chart Jacobian.

    A zero is a circle tangent at all three visits. A denominator containing
    zero must remain unresolved; it is never interpreted as an exclusion.
    Compact intermediate bounds prevent exact fraction sizes from exploding.
    """
    points, velocities, accelerations = zip(*(jets(d, inner) for d in domains))
    A = [tuple(2 * (x - y) for x, y in zip(points[k], points[0])) for k in (1, 2)]
    b = [rational_dot(points[k], points[k]) - rational_dot(points[0], points[0]) for k in (1, 2)]
    center = tuple(map(compact, solve(A, b)))
    center_derivatives = []
    for j in range(3):
        db = [2 * ((rational_dot(points[k], velocities[k]) if j == k else 0)
                   - (rational_dot(points[0], velocities[0]) if j == 0 else 0)) for k in (1, 2)]
        dA = [tuple(2 * ((velocities[k][i] if j == k else 0)
                        - (velocities[0][i] if j == 0 else 0)) for i in (0, 1)) for k in (1, 2)]
        center_derivatives.append(tuple(map(compact, solve(A, [x - rational_dot(row, center)
                                                              for x, row in zip(db, dA)]))))
    radii = [tuple(x - y for x, y in zip(point, center)) for point in points]
    F = [compact(rational_dot(r, v)) for r, v in zip(radii, velocities)]
    J = [[compact(((rational_dot(velocities[i], velocities[i])
                    + rational_dot(radii[i], accelerations[i])) if i == j else 0)
                  - rational_dot(center_derivatives[j], velocities[i]))
          for j in range(3)] for i in range(3)]
    parameters = [I(d[1], d[2]) for d in domains]
    factors = [I.wrap(2) / (1 + s * s) for s in parameters]
    J = [[compact(x * factors[j]) for j, x in enumerate(row)] for row in J]
    return F, J, center, radii, velocities


def contract(domains, inner):
    centers = [(d[1] + d[2]) / 2 for d in domains]
    radii = [(d[2] - d[1]) / 2 for d in domains]
    midpoint_domains = tuple((d[0], c, c) for d, c in zip(domains, centers))
    try:
        F, J0, *_ = equations(midpoint_domains, inner)
        _, J, *_ = equations(domains, inner)
        R = inverse([[x.midpoint() for x in row] for row in J0])
    except (ValueError, ZeroDivisionError):
        return "unknown", None
    R = [[compact(I.wrap(x)).midpoint() for x in row] for row in R]
    E = [[Q(i == j) - sum(R[i][k] * J[k][j] for k in range(3))
          for j in range(3)] for i in range(3)]
    image = [-sum(R[i][k] * F[k] for k in range(3))
             + sum(E[i][j] * I(-radii[j], radii[j]) for j in range(3)) for i in range(3)]
    if any(x.low > r or x.high < -r for x, r in zip(image, radii)):
        return "empty", None
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in E)
    data = {"norm": norm, "image": [compact(c + x) for c, x in zip(centers, image)]}
    if norm < 1 and all(-r < x.low <= x.high < r for x, r in zip(image, radii)):
        return "root", data
    return "unknown", data


def near(difference, partition):
    # A fixed open velocity half-plane excludes offset self-intersections:
    # positive curvature keeps each offset derivative a positive velocity
    # multiple. The complete intervening arc turns strictly less than pi.
    return 2 * ACCELERATION * (difference + 1) < 3 * MIN_SPEED * partition


def candidates(inner, partition=512):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(type(partition) is int and partition >= 128, "Use at least 128 cells per quarter.")
    grid = [(q, Q(k, partition), Q(k + 1, partition)) for q in range(4) for k in range(partition)]
    data = [integer_jets(d, inner) for d in grid]
    adjacency, stats = defaultdict(set), Counter()
    total = len(grid)
    for i in range(total):
        for j in range(i + 1, total):
            if near(min(j - i, total - (j - i)), partition):
                stats["near"] += 1
                continue
            reason = pair_exclusion(data[i], data[j])
            if reason:
                stats[reason] += 1
            else:
                adjacency[i].add(j)
                stats["retained"] += 1
    require(sum(stats.values()) == total * (total - 1) // 2, "The pair cover lost a product.")
    triples = [(i, j, k) for i in sorted(adjacency) for j in sorted(adjacency[i])
               for k in sorted(adjacency[i] & adjacency[j])]
    return grid, triples, stats


def clear_caches():
    for function in (exact_jets, jets, integer_jets):
        function.cache_clear()


def refine(domains, inner):
    """Intersect mean-value images while retaining an already proved root."""
    original = domains
    for _ in range(24):
        status, data = contract(domains, inner)
        require(status != "empty" and data is not None, "A proved root was lost during refinement.")
        narrowed = tuple((d[0], max(d[1], x.low), min(d[2], x.high))
                         for d, x in zip(domains, data["image"]))
        require(all(d[1] < d[2] for d in narrowed), "A retained root enclosure became empty.")
        domains = narrowed
        if max(d[2] - d[1] for d in domains) < Q(1, 10 ** 18) and data["norm"] < Q(1, 10 ** 5):
            require(all(a[0] == b[0] and a[1] < b[1] < b[2] < a[2]
                        for a, b in zip(original, domains)), "A refined root left its unique leaf.")
            return domains
    raise ValueError("The proved root did not refine to the requested precision.")


def classify(domains, data, inner):
    refined = refine(domains, inner)
    _, _, center, radii, velocities = equations(refined, inner)
    directions = [rational_dot(r, (-v[1], v[0])) for r, v in zip(radii, velocities)]
    if any(d.high < 0 for d in directions):
        return None
    require(all(d.low > 0 for d in directions), "A circle's outward direction remains unresolved.")
    for i, j in PAIRS:
        rational_cross(velocities[i], velocities[j]).sign()
    normals = [(-v[1] / sqrt_interval(rational_dot(v, v)),
                v[0] / sqrt_interval(rational_dot(v, v))) for v in velocities]
    H = -sum((rational_cross(normals[i], normals[j]) for i, j in ((0, 1), (1, 2), (2, 0))), I.wrap(0))
    jump = H.sign()
    offsets = [sqrt_interval(rational_dot(r, r)) for r in radii]
    offset = I(max(x.low for x in offsets), min(x.high for x in offsets))
    require(offset.low > 0, "The circle radius is not strictly positive.")
    return {"quarters": [d[0] for d in domains],
            "coarse_box": [[str(d[1]), str(d[2])] for d in domains],
            "root_box": [[str(d[1]), str(d[2])] for d in refined],
            "norm_upper": compact_interval(I.wrap(data["norm"]))[1],
            "point": [compact_interval(x) for x in center], "offset": compact_interval(offset),
            "strangeness_jump": jump, "normalized_unfolding": compact_interval(H)}


def root_domains(record, key="root_box"):
    return tuple((q, *map(Q, b)) for q, b in zip(record["quarters"], record[key]))


def inside(first, second):
    return all(a[0] == b[0] and b[1] < a[1] < a[2] < b[2] for a, b in zip(first, second))


def reflect(domains):
    return tuple((3 - q, (1 - hi) / (1 + hi), (1 - lo) / (1 + lo))
                 for q, lo, hi in reversed(domains))


def axis_domains(event):
    """Four exact chart enclosures from an independently proved axis circle."""
    upper = []
    # Increasing upper-half time means decreasing cosine.
    for bounds in reversed(event["cosine_box"]):
        c = I(*map(Q, bounds))
        sine = sqrt_interval(1 - c * c, bits=120)
        if c.low > 0:
            quarter, s = 0, sine / (1 + c)
        else:
            require(c.high < 0, "An axis box crosses a quarter seam.")
            quarter, s = 1, -c / (1 + sine)
        upper.append((quarter, s.low, s.high))
    return tuple(upper) + reflect(tuple(upper))


def identify(records, axis):
    """Identify fourfold subsets by uniqueness, then pair the off-axis roots.

    Axis proofs are repeated independently. Strict nesting in a unique
    three-variable root leaf establishes identity, without rounded matching.
    Distinct event locations exclude all additional branches globally.
    """
    coarse = [root_domains(r, "coarse_box") for r in records]
    used = set()
    for event_index, event in enumerate(axis["events"]):
        four = axis_domains(event)
        for subset in combinations(range(4), 3):
            domains = tuple(four[k] for k in subset)
            matches = [i for i, box in enumerate(coarse) if inside(domains, box)]
            require(len(matches) == 1 and matches[0] not in used,
                    "An axis subset does not identify exactly one fresh root.")
            i = matches[0]
            expected = next(t for t in event["triples"] if t["visits"] == list(subset))
            require(records[i]["strangeness_jump"] == expected["strangeness_jump"],
                    "An axis triple sign disagrees with the independent circle proof.")
            records[i]["axis_event"] = event_index
            records[i]["axis_visits"] = list(subset)
            used.add(i)
    off_axis = [i for i in range(len(records)) if i not in used]
    for i in off_axis:
        domains = reflect(root_domains(records[i]))
        matches = [j for j in off_axis if inside(domains, coarse[j])]
        require(len(matches) == 1 and matches[0] != i, "An off-axis root lacks its unique reflected partner.")
        j = matches[0]
        require(records[i]["strangeness_jump"] == records[j]["strangeness_jump"],
                "Reflection changed a triple sign.")
        records[i]["reflection"] = j
        y = I(*map(Q, records[i]["point"][1]))
        y.sign()
    # Different circles are either separated in radius or in one center
    # coordinate. Only four subsets identified above may coincide.
    separations = 0
    for i, first in enumerate(records):
        for j, second in enumerate(records[:i]):
            if "axis_event" in first and first.get("axis_event") == second.get("axis_event"):
                continue
            boxes = [(first["offset"], second["offset"]), *zip(first["point"], second["point"])]
            require(any(Q(a[1]) < Q(b[0]) or Q(b[1]) < Q(a[0]) for a, b in boxes),
                    "Two roots may share a circle; a higher meeting remains unresolved.")
            separations += 1
    events = []
    for k, event in enumerate(axis["events"]):
        indices = [i for i, r in enumerate(records) if r.get("axis_event") == k]
        require(len(indices) == 4, "An axis event lost a triple subset.")
        events.append({"kind": "axis_fourfold", "roots": indices, "offset": event["offset"],
                       "positive_triples": event["positive_triples"],
                       "negative_triples": event["negative_triples"]})
    for i in off_axis:
        j = records[i]["reflection"]
        require(records[j]["reflection"] == i, "Reflected root pairing is not an involution.")
        if i > j:
            continue
        first, second = records[i]["offset"], records[j]["offset"]
        low, high = max(Q(first[0]), Q(second[0])), min(Q(first[1]), Q(second[1]))
        require(low <= high, "Reflected circles disagree on their shared radius.")
        sign = records[i]["strangeness_jump"]
        events.append({"kind": "reflected_triples", "roots": [i, j], "offset": [str(low), str(high)],
                       "positive_triples": 2 if sign > 0 else 0,
                       "negative_triples": 2 if sign < 0 else 0})
    events.sort(key=lambda e: Q(e["offset"][0]))
    require(all(Q(a["offset"][1]) < Q(b["offset"][0]) for a, b in zip(events, events[1:])),
            "Two distinct event weights remain unresolved.")
    last = Q(events[-1]["offset"][1])
    return {"axis_fourfolds": len(axis["events"]), "axis_subsets": len(used),
            "off_axis_triples": len(off_axis), "separated_circle_pairs": separations,
            "event_weights": len(events), "no_higher_meeting_from": str(last // 1 + 1), "events": events}


def cover(inner, partition=512, max_depth=48):
    require(type(max_depth) is int and max_depth >= 0, "Use a nonnegative depth limit.")
    started, stats, roots = monotonic(), Counter(), []
    grid, triples, pair_stats = candidates(inner, partition)
    print(f"11/{inner}: {pair_stats['retained']} retained pairs; {len(triples)} complete triple products.", flush=True)
    for index, triple in enumerate(triples):
        pending = [(tuple(grid[k] for k in triple), 0)]
        while pending:
            domains, depth = pending.pop()
            stats["max_depth"] = max(stats["max_depth"], depth)
            data = [integer_jets(d, inner) for d in domains]
            if any(pair_exclusion(data[i], data[j]) for i, j in PAIRS):
                stats["pair_exclusion"] += 1
                continue
            reason = minor_exclusion(data)
            if reason:
                stats[reason] += 1
                continue
            if depth >= 9 and depth % 3 == 0:
                status, result = contract(domains, inner)
                if status == "empty":
                    stats["mean_value_exclusion"] += 1
                    continue
                if status == "root":
                    roots.append((domains, result))
                    stats["root_leaves"] += 1
                    continue
                stats["unknown_contractions"] += 1
            require(depth < max_depth, f"An unresolved triple product rejects the census: {domains}.")
            axis = max(range(3), key=lambda i: domains[i][2] - domains[i][1])
            quarter, low, high = domains[axis]
            middle = (low + high) / 2
            for a, b in ((low, middle), (middle, high)):
                child = list(domains)
                child[axis] = (quarter, a, b)
                pending.append((tuple(child), depth + 1))
            stats["bisections"] += 1
        if (index + 1) % 10000 == 0:
            print(f"  {index + 1}/{len(triples)} products; {len(roots)} root leaves; "
                  f"{monotonic() - started:.2f}s.", flush=True)
    leaves = sum(stats[k] for k in ("pair_exclusion", "normal_minor", "chord_minor", "mixed_minor",
                                    "mean_value_exclusion", "root_leaves"))
    require(leaves == len(triples) + stats["bisections"], "The binary cover lost a leaf.")
    print(f"11/{inner}: complete cover, {len(roots)} root leaves; {dict(stats)}; "
          f"{monotonic() - started:.2f}s.", flush=True)
    return roots, {"inner": inner, "partition_per_quarter": partition, "pair_cover": dict(pair_stats),
                   "triple_products": len(triples), "cover": dict(stats)}


def prove(inner, partition=512, max_depth=48):
    from offset_axis_census import prove as prove_axis
    from offset_axis_visits import prove as prove_fixed

    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    require(type(partition) is int and partition >= 128, "Use at least 128 cells per quarter.")
    require(type(max_depth) is int and max_depth >= 0, "Use a nonnegative depth limit.")
    require(SPEED == 245 + 140 * 11 + 65 * 8 == 2305
            and ACCELERATION == 245 + 140 * 11 ** 2 + 65 * 8 ** 2 == 21345
            and MIN_SPEED == 1540 - 765 == 775 and JERK == 219865
            and 1540 * 16940 - 1540 * 4405 - 765 * 16940 - 765 * 4405 == 2974975 > 0,
            "The uniform derivative or positive-curvature bounds changed.")
    prove_fixed(inner)
    axis = prove_axis(inner)
    roots, result = cover(inner, partition, max_depth)
    records = []
    for domains, data in roots:
        record = classify(domains, data, inner)
        if record is not None:
            records.append(record)
    records.sort(key=lambda r: tuple((q, Q(b[0])) for q, b in zip(r["quarters"], r["root_box"])))
    result.update(identify(records, axis))
    result["inward_root_leaves"] = len(roots) - len(records)
    result["positive_triples"] = sum(r["strangeness_jump"] > 0 for r in records)
    result["negative_triples"] = sum(r["strangeness_jump"] < 0 for r in records)
    result["roots"] = records
    # Check the advertised conclusions only AFTER the complete discovery,
    # classification, reflection, and separation proofs have succeeded.
    conclusions = (result["off_axis_triples"], result["axis_fourfolds"], result["positive_triples"],
                   result["negative_triples"], result["event_weights"], result["no_higher_meeting_from"])
    require(conclusions == ((94, 11, 18, 120, 58, "16173") if inner == 6 else (96, 9, 10, 122, 57, "818")),
            "The freshly proved conclusions differ from the advertised theorem.")
    print(f"11/{inner}: {result['off_axis_triples']} ordinary off-axis triples, "
          f"{result['axis_fourfolds']} fourfolds; local resolution gives "
          f"{result['positive_triples']} positive and {result['negative_triples']} negative triples.", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", type=int, choices=(6, 8))
    parser.add_argument("--partition", type=int, default=512)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    require(not args.write or args.inner is None, "A saved complete record requires both endpoints.")
    started, endpoints = monotonic(), []
    for inner in ((args.inner,) if args.inner is not None else (6, 8)):
        try:
            endpoints.append(prove(inner, args.partition))
        finally:
            clear_caches()
    if args.write:
        record = {"scope": "Complete higher-meeting census of both unperturbed outward offset legs for every M>=0. Fourfolds are counted as four triple subsets only after a local generic resolution. No middle-family stability threshold.",
                  "endpoints": endpoints}
        (HERE / "offset_leg_census.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Elapsed {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
