"""Every efficient total/smallest-area compromise for limit parabolas.

The all-count proof is in parabolic_tradeoff.md. These exact rational
and quadratic-field controls audit its positive supporting weights,
cube remainder, complete face minima, and cubic drawing coordinates.
No numerical optimizer or rounded radical is a proof predicate.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from random import Random

from blend_cusps import require
from parabolic_balance import Quadratic, face_areas, optimum
from parabolic_pockets import area, bounded_faces, example, run_faces

HERE = Path(__file__).resolve().parent


def endpoint(size, span=Q(4)):
    """Last normalized half-gap difference u=(b-a)/(2L)."""
    require(type(size) is int and size >= 4 and size % 2 == 0,
            "Choose an even slope count of at least four.")
    gaps = optimum(size, span)
    return (gaps[1]-gaps[0])/(2*span)


def frontier(size, u, span=Q(4)):
    """Exact gaps and the two areas along the complete efficient curve."""
    top = endpoint(size, span)
    require(type(u) in (Q, Quadratic) and 0 <= u <= top,
            "Use an exact parameter on the closed compromise interval.")
    m = size-1
    c, h = span*(1+u)/m, span*u
    a, b = c-h, c+h
    gaps = [a if i % 2 == 0 else b for i in range(m)]
    total = (span**3-sum(g**3 for g in gaps))/24
    smallest = a*b*(a+b)/8
    require(sum(gaps) == span and 0 < a <= b <= 2*a,
            "The alternating candidate misses its span or the triangle-minimum range.")
    require(total == span**3*(1-Q(1, m*m))/24
            - span**3*Q(m*m-1, 24*m*m)*u*u*(3+2*u)
            and smallest == span**3/(4*m**3)*((1+u)**3-m*m*u*u*(1+u)),
            "The area polynomials disagree with the gap formulas.")
    require(min(face_areas(gaps)) == smallest,
            "A longer-run pocket undercuts the adjacent triangles.")
    return {"gaps": gaps, "total": total, "smallest": smallest}


def derivatives(size, u, span=Q(4)):
    m = size-1
    return (-span**3*Q(m*m-1, 4*m*m)*u*(1+u),
            span**3/(4*m**3)*(3-2*(m*m-3)*u-3*(m*m-1)*u*u))


def support(size, u, span=Q(4)):
    """A positive weighted AM-GM support at an interior candidate."""
    candidate = frontier(size, u, span)
    require(0 < u < endpoint(size, span), "Use an interior compromise for the finite support.")
    k = (size-2)//2
    a, b = candidate["gaps"][:2]
    U, V = (1/a+1/(a+b))/3, (1/b+1/(a+b))/3
    r = U/V
    lam = 3*((k+1)*a*a-k*r*b*b)/(k*r-k-1)
    H = (3*a*a+lam)/U
    weights = [(k-i//2)*H/k if i % 2 == 0 else ((i+1)//2)*H/k
               for i in range(2*k)]
    coefficients = [0]*(2*k+1)
    for i, weight in enumerate(weights):
        coefficients[i] += weight*(U if i % 2 == 0 else V)
        coefficients[i+1] += weight*(V if i % 2 == 0 else U)
    require(r == (b/a)*(b/a+2)/(2*b/a+1) and k*r < k+1
            and H > 0 and all(w > 0 for w in weights),
            "The compromise needs strictly positive supporting weights.")
    require(all(coefficient == 3*g*g+lam for coefficient, g in zip(coefficients, candidate["gaps"]))
            and sum(weights) == (k+1)*H,
            "The pair weights miss a gap's cube gradient.")
    return {**candidate, "U": U, "V": V, "lambda": lam, "H": H, "weights": weights}


def challenger_control(size, u, gaps, span=Q(4)):
    """Check the exact support identity and the cubed AM-GM inequalities.

    Arbitrary challengers may lie on either side of the target minimum.
    The final conditional check is the bound used in the written proof.
    """
    target = support(size, u, span)
    require(len(gaps) == size-1 and sum(gaps) == span and all(g > 0 for g in gaps),
            "A challenger needs positive gaps with the same count and span.")
    a, b = target["gaps"][:2]
    linear = []
    for i, (x, y) in enumerate(zip(gaps, gaps[1:])):
        U, V = (target["U"], target["V"]) if i % 2 == 0 else (target["V"], target["U"])
        ell = U*x+V*y
        require(ell > 0 and ell**3*a*b*(a+b) >= x*y*(x+y),
                "A positive cubed AM-GM bound failed.")
        linear.append(ell)
    remainder = sum((x-y)**2*(x+2*y) for x, y in zip(gaps, target["gaps"]))
    difference = sum(x**3-y**3 for x, y in zip(gaps, target["gaps"]))
    weighted = sum(w*(ell-1) for w, ell in zip(target["weights"], linear))
    require(difference == remainder+weighted and remainder >= 0,
            "The cube-support remainder is not the claimed exact identity.")
    require((remainder == 0) == all(x == y for x, y in zip(gaps, target["gaps"])),
            "The positive cube remainder lost equality rigidity.")
    smallest = min(face_areas(gaps))
    W = sum(target["weights"])
    average = 1+weighted/W
    require(average > 0 and average**3*target["smallest"] >= smallest,
            "The weighted support fails its global smallest-area bound.")
    if smallest >= target["smallest"]:
        require(all(ell >= 1 for ell in linear) and difference >= remainder,
                "A challenger preserves the minimum but beats the total-area support.")
        require(remainder >= 2*a*sum((x-y)**2 for x, y in zip(gaps, target["gaps"])),
                "The quantitative rigidity bound failed.")
    return 1


def exact_controls(maximum):
    random = Random(20261109)
    counts = {"arrangements": 0, "challengers": 0, "clipped": 0, "invalid": 0}
    for size in range(4, maximum+1, 2):
        top = endpoint(size)
        last = None
        for step in range(13):
            u = top*Q(step, 12)
            point = frontier(size, u)
            dB, dS = derivatives(size, u)
            require(dB <= 0 and dS >= 0, "A compromise moves an objective in the wrong direction.")
            if last:
                require(point["total"] < last["total"] and point["smallest"] > last["smallest"],
                        "The alternating route fails strict tradeoff monotonicity.")
            last = point
            counts["arrangements"] += 1
            if step in (0, 12):
                continue
            if size <= 12:
                counts["challengers"] += challenger_control(size, u, point["gaps"])
                # Permuting equal-span gaps preserves total but usually damages
                # the minimum. Adjacent swaps also audit the equality condition.
                for j in (0, size//2-1, size-3):
                    permuted = point["gaps"][:]
                    permuted[j], permuted[j+1] = permuted[j+1], permuted[j]
                    counts["challengers"] += challenger_control(size, u, permuted)
                for _ in range(3):
                    integers = [random.randrange(1, 25) for _ in range(size-1)]
                    gaps = [Q(4*x, sum(integers)) for x in integers]
                    counts["challengers"] += challenger_control(size, u, gaps)
        require(last["gaps"] == optimum(size), "The compromise endpoint misses the independent optimum.")
        scaled = frontier(size, top/2, Q(7, 3))
        original = frontier(size, top/2)
        require(all(y == Q(7, 12)*x for x, y in zip(original["gaps"], scaled["gaps"]))
                and scaled["total"] == Q(7, 12)**3*original["total"]
                and scaled["smallest"] == Q(7, 12)**3*original["smallest"],
                "The whole frontier does not scale cubically.")
        counts["arrangements"] += 1
    # Rational points permit fresh, independent full line arrangements and
    # curved integrals, rather than only the gap formulas used by the support.
    for size in (4, 6, 8, 10):
        for u in (Q(0), Q(1, 10*size), Q(1, 8*size)):
            point = frontier(size, u)
            slopes = [Q(-2)]
            for g in point["gaps"]:
                slopes.append(slopes[-1]+g)
            polygons = bounded_faces(slopes)
            integrated = run_faces(slopes)
            actual = sorted(area(p) for p in polygons)
            require(actual == sorted(f["area"] for f in integrated) == sorted(face_areas(point["gaps"]))
                    and sum(actual) == point["total"] and min(actual) == point["smallest"],
                    "A fresh clipped arrangement disagrees with the claimed frontier coordinates.")
            counts["clipped"] += 1
    for size, u, span in ((3, Q(0), Q(4)), (True, Q(0), Q(4)), (6, .02, Q(4)),
                          (6, Q(-1), Q(4)), (6, Q(1), Q(4)), (6, Q(0), 4), (6, Q(0), Q(0))):
        try:
            frontier(size, u, span)
        except ValueError:
            counts["invalid"] += 1
        else:
            raise ValueError("An invalid frontier problem was accepted.")
    return counts


def bezier(size, span=Q(4)):
    """Every coordinate is cubic in u, including algebraic endpoints."""
    top = endpoint(size, span)
    first, last = frontier(size, Q(0), span), frontier(size, top, span)
    start, finish = tuple(first[k] for k in ("total", "smallest")), tuple(last[k] for k in ("total", "smallest"))
    controls = (start,
                tuple(x+top*d/3 for x, d in zip(start, derivatives(size, Q(0), span))),
                tuple(x-top*d/3 for x, d in zip(finish, derivatives(size, top, span))),
                finish)
    for step in range(37):
        s = Q(step, 36)
        actual = tuple((1-s)**3*controls[0][i]+3*s*(1-s)**2*controls[1][i]
                       +3*s*s*(1-s)*controls[2][i]+s**3*controls[3][i] for i in (0, 1))
        point = frontier(size, top*s, span)
        require(actual == (point["total"], point["smallest"]), "The cubic path misses the exact frontier.")
    return controls


def record():
    rows = []
    for name, u in (("Largest total", Q(0)), ("A rational compromise", Q(1, 24))):
        point = frontier(6, u)
        slopes = [Q(-2)]
        for g in point["gaps"]:
            slopes.append(slopes[-1]+g)
        row = example(name, slopes)
        row.update({"parameter": u, "smallest": point["smallest"]})
        rows.append(row)
    require(rows[1]["area"] == Q(275, 108) and rows[1]["smallest"] == Q(5, 36),
            "The illustrated rational arrangement misses its ten independently integrated pockets.")
    top = endpoint(6)
    optimal = frontier(6, top)
    return {"scope": "Complete exact limit parabolas at mu=0; no finite-offset or orbital face claim.",
            "slopes": 6, "span": Q(4), "parameter": "u=(b-a)/(2L)",
            "interval": (Q(0), top), "examples": rows, "bezier": bezier(6),
            "endpoint": optimal}


def serialize(value):
    if type(value) is Q:
        return str(value)
    if type(value) is Quadratic:
        return {"rational": str(value.a), "radical": str(value.b), "radicand": value.d}
    if type(value) is dict:
        return {key: serialize(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return [serialize(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-slopes", type=int, default=20, help="Largest even count to audit (at least 12).")
    parser.add_argument("--write", action="store_true", help="Regenerate exact six-slope drawing data.")
    args = parser.parse_args()
    require(args.max_slopes >= 12, "Check through at least twelve slopes.")
    counts = exact_controls(args.max_slopes)
    for size in (4, 6, 8, 10, 12):
        bezier(size)
    data = record()
    if args.write:
        (HERE/"parabolic_tradeoff.json").write_text(json.dumps(serialize(data), indent=2)+"\n")
    print(f"{counts['arrangements']} exact frontier arrangements, {counts['challengers']} weighted-support challengers,")
    print(f"{counts['clipped']} independent clipped/curved arrangements, and {counts['invalid']} invalid controls passed.")
    print("185 exact cubic matches passed across four through twelve slopes.")
    for row in data["examples"]:
        print(f"Six slopes, {row['name'].lower()}: total {row['area']}, smallest {row['smallest']}.")
    print(f"Six-slope endpoint: total ≈ {float(data['endpoint']['total']):.12f}; smallest ≈ {float(data['endpoint']['smallest']):.12f}.")
    print("The complete frontier follows from positive AM-GM supports and the exact cube remainder; finite controls audit the algebra.")


if __name__ == "__main__":
    main()
