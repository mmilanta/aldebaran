"""Enclose the local plane pocket still present at the front triple.

At delta=0 the middle arc is a circle. Rational polynomial bisection
isolates its crossing with each outer arc. Exact arc integrals and an
alternating arctangent bound enclose the curved pocket's area. This is
the isolated three-arc model, not a face census for the entire movie.
Standard library only; see radial_limit.md.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations, permutations, product as combinations_product
import json
from math import atan, cos, factorial, fsum, sin
from unittest.mock import patch

from blend_cusps import Interval as I, add, bound, derivative, product, require, scale, value
from positive_front_projection import certify, f, first
from radial_limit import HERE, outward, power, trig_polynomial, triple_drift
from triple_area import coefficient, cross, linear_intersection

F = (Q(0), Q(15, 8), Q(0), Q(-5, 4), Q(0), Q(3, 8))
SECOND = derivative(derivative(F))
LIMIT = Q(3375, 2048)


def primitive(polynomial):
    return (Q(0),) + tuple(c/Q(i+1) for i, c in enumerate(polynomial))


G0 = primitive(add(scale(F, 2), SECOND))
G1 = primitive(product(F, add(F, SECOND)))


def arctangent(x):
    require(type(x) is Q and 0 <= x <= Q(1, 8), "Use a rational arctangent argument in [0,1/8].")
    partial = sum(Q((-1)**k, 2*k+1)*x**(2*k+1) for k in range(12))
    return I(partial, partial+x**25/25)


def area_certificate(offset, bits=120):
    require(type(offset) is int and offset >= 25, "Use an integer offset at least 25.")
    require(type(bits) is int and bits >= 80, "Use at least eighty rational bisections.")
    outer, delta = certify(offset, bits=bits)

    def equation(u):
        return f(u)**2-2*offset*f(u)+first(u)**2

    lo, hi = Q(0), Q(1, 8)
    require(equation(lo) > 0 and equation(hi) < 0, "The circle crossing has no sign bracket.")
    for _ in range(bits):
        mid = (lo+hi)/2
        result = equation(mid)
        require(result != 0, "An exact rational circle root needs a separate bracket.")
        if result > 0:
            lo = mid
        else:
            hi = mid
    require(equation(lo) > 0 and equation(hi) < 0, "The circle bracket lost its strict signs.")
    circle = I(lo, hi)
    require(0 < circle.low < circle.high < outer.low < outer.high < Q(1, 8),
            "The two outer arc endpoints are not ordered.")
    ratio = I(f(lo), f(hi))/I(first(hi), first(lo))
    angle = I(arctangent(ratio.low).low, arctangent(ratio.high).high)
    polar = 2*angle-circle
    area = (offset**2*(2*angle-outer)
            + offset*(bound(G0, outer)-bound(G0, circle))
            - (bound(G1, outer)-bound(G1, circle)))
    require(polar.low > 0 and area.low > 0, "The curved pocket area or polar opening was not positive.")
    return {"outer": outer, "circle": circle, "polar": polar, "parameter": delta, "area": area}


def certify_area_tail():
    """Prove 0<LIMIT/M-area<5/M³ on the entire real half-line M>=25.

    Four scaled polynomial brackets enclose the two crossing angles.
    Monotonicity of the exact integral in each endpoint bounds its area
    by two corners. Clearing a positive denominator permits cancellation
    of tau² before rational interval evaluation, including tau=0.
    """
    domain = I(Q(0), Q(1, 625))
    tau = (Q(0), Q(1))
    a, b, c = Q(15, 8), Q(-5, 4), Q(3, 8)
    outer_low = (a, Q(-1125, 128), Q(860625, 8192), Q(-1650))
    outer_high = (a, Q(-1125, 128), Q(860625, 8192), Q(-1500))
    circle_low = (a/2, Q(-7875, 4096), Q(10479375, 1048576), Q(-70))
    circle_high = (a/2, Q(-7875, 4096), Q(10479375, 1048576), Q(-64))
    root_proofs = []

    def jets(U):
        odd = add(add(scale(U, a), scale(product(tau, power(U, 3)), b)),
                  scale(product(power(tau, 2), power(U, 5)), c))
        p = add(add((a,), scale(product(tau, power(U, 2)), 3*b)),
                scale(product(power(tau, 2), power(U, 4)), 5*c))
        return odd, p

    def magnitude(polynomial):
        interval = bound(polynomial, domain)
        return max(abs(interval.low), abs(interval.high))

    for kind, side, U in (("outer", "lower", outer_low), ("outer", "upper", outer_high),
                          ("circle", "lower", circle_low), ("circle", "upper", circle_high)):
        enclosure = bound(U, domain)
        require(0 < enclosure.low <= enclosure.high < 2, "An area-tail root bracket left its Taylor window.")
        odd, p = jets(U)
        error = Q(0)
        if kind == "outer":
            z = product(tau, power(U, 2))
            coefficient = add(product(tau, product(odd, U)), scale(U, -1))
            equation = add(product(coefficient, trig_polynomial(z, sinc=True)), product(p, trig_polynomial(z)))
            error = (magnitude(coefficient)*Q(4**5, factorial(11))
                     + magnitude(p)*Q(4**5, factorial(10))) * domain.high**2
        else:
            equation = add(add(product(tau, product(odd, odd)), scale(odd, -2)), product(p, p))
        require(equation[:3] == (0, 0, 0), "The scaled area-root coefficients did not cancel.")
        residual = bound(equation[3:], domain)
        residual = I(residual.low-error, residual.high+error)
        require(residual.low > 0 if side == "lower" else residual.high < 0,
                "A scaled area-root bracket lost its strict sign.")
        root_proofs.append({"kind": kind, "side": side, "polynomial": list(map(str, U)),
                            "residual": outward(residual)})

    require(bound(outer_low, domain).low > bound(circle_high, domain).high,
            "The globally bracketed pocket endpoints overlap.")
    # A_x<0. For A_u, 1<=f'<=2, 0<=f<=1/4 and -3<=f''<=0
    # give A_u >= (32/65)M²-(7/2)M-13/16 > 0 for M>=25.
    require(a*(Q(63, 64))**2 > 1 and Q(15, 64) < Q(1, 4), "The endpoint monotonicity bounds failed.")
    require(Q(32, 65)*25**2-Q(7, 2)*25-Q(13, 16) > 0
            and Q(64, 65)*25-Q(7, 2) > 0, "The endpoint area derivative is not uniformly positive.")

    def scaled_primitive(polynomial, U, shift):
        result = (Q(0),)
        for k, coefficient in enumerate(polynomial):
            if coefficient:
                require(k >= shift and (k-shift) % 2 == 0, "An area primitive has the wrong parity.")
                term = product(power(tau, (k-shift)//2), power(U, k))
                result = add(result, scale(term, coefficient))
        return result

    area_proofs = []
    for side, X, U, correction in (("lower", outer_high, circle_low, Q(-5)),
                                  ("upper", outer_low, circle_high, Q(0))):
        odd, p = jets(U)
        p5 = power(p, 5)
        # Three arctangent terms, after multiplying by the positive p^5.
        angle = add(add(scale(product(odd, power(p, 4)), 2),
                        scale(product(tau, product(power(odd, 3), power(p, 2))), Q(-2, 3))),
                    scale(product(power(tau, 2), power(odd, 5)), Q(2, 5)))
        numerator = add(angle, scale(product(X, p5), -1))
        rest = add(add(scaled_primitive(G0, X, 2), scale(scaled_primitive(G0, U, 2), -1)),
                   scale(product(tau, add(scaled_primitive(G1, X, 3),
                                          scale(scaled_primitive(G1, U, 3), -1))), -1))
        rest = add(rest, (-LIMIT, -correction))
        numerator = add(numerator, product(tau, product(p5, rest)))
        require(numerator[:2] == (0, 0), "The area-limit coefficient did not cancel.")
        interval = bound(numerator[2:], domain)
        po = bound(p, domain)
        require(po.low > 0 and bound(odd, domain).low > 0,
                "The cleared area denominator or arctangent argument is not positive.")
        ratio = magnitude(odd)/po.low
        require(domain.high*ratio**2 < Q(1, 64), "The uniform arctangent argument left its window.")
        error = 2*po.high**5*domain.high*ratio**7/7
        # Three terms end positive: atan lies below this partial sum.
        residual = I(interval.low-error, interval.high)
        require(residual.low > 0 if side == "lower" else residual.high < 0,
                "The uniform curved-area residual lost its strict sign.")
        area_proofs.append({"side": side, "correction": str(correction),
                            "numerator_degree": len(numerator)-1, "residual": outward(residual)})
    return {"offset_from": 25, "positive_area_deficit_upper": "5/M^3",
            "root_proofs": root_proofs, "area_proofs": area_proofs}


def point(theta, offset, which):
    """Independent numerical coordinates, shifted by (+M,0) for stability."""
    sign = 1 if which == 0 else -1 if which == 2 else 0
    h = sign*(3*theta**5-10*theta**3+15*theta)/8
    p = sign*(15*theta**4-30*theta**2+15)/8
    return (2*offset*sin(theta/2)**2+h*cos(theta)-p*sin(theta),
            -offset*sin(theta)+h*sin(theta)+p*cos(theta))


def polygon_area(offset, proof, steps):
    outer, circle, polar = (float(proof[k].midpoint()) for k in ("outer", "circle", "polar"))
    points = []
    for start, end, which in ((circle, outer, 0), (-outer, -circle, 2), (polar, -polar, 1)):
        points.extend(point(start+(end-start)*i/steps, offset, which) for i in range(steps))
    return -fsum(a[0]*b[1]-a[1]*b[0] for a, b in zip(points, points[1:]+points[:1]))/2


def controls():
    require(derivative(G0) == add(scale(F, 2), SECOND), "The first area primitive changed.")
    require(derivative(G1) == product(F, add(F, SECOND)), "The second area primitive changed.")
    require(arctangent(Q(0)) == I(Q(0), Q(0)), "The exact angle at the origin changed.")
    require(Q(15, 8)**3/4 == LIMIT, "The parabolic limiting area constant changed.")
    checks = 4
    tail = certify_area_tail()
    require(len(tail["root_proofs"]) == 4 and len(tail["area_proofs"]) == 2,
            "The area-tail proof is incomplete.")
    checks += 1
    with patch(__name__+".LIMIT", LIMIT+Q(1, 10**12)):
        try:
            certify_area_tail()
        except ValueError:
            checks += 1
        else:
            raise ValueError("A corrupt area-limit coefficient passed the uniform proof.")
    for offset in (25, 100, 1000, 10000):
        proof = area_certificate(offset)
        actual = float(proof["area"].midpoint())
        require(0 < LIMIT/offset-proof["area"].high < LIMIT/offset-proof["area"].low < Q(5, offset**3),
                "Fresh area brackets left the all-offset area remainder law.")
        checks += 1
        for root in tail["root_proofs"]:
            angle = value(tuple(map(Q, root["polynomial"])), Q(1, offset**2))/offset
            bracket = proof[root["kind"]]
            require(angle < bracket.low if root["side"] == "lower" else angle > bracket.high,
                    "The independent finite root does not nest in its global polynomial bracket.")
            checks += 1
        if offset == 25:
            require(Q("0.065642804255745") < proof["area"].low < proof["area"].high
                    < Q("0.065642804255746"), "The advertised area interval changed.")
            checks += 1
        coarse = polygon_area(offset, proof, 256)
        fine = polygon_area(offset, proof, 1024)
        require(0 < abs(fine-actual) < abs(coarse-actual)/12,
                "Independent polygon area did not converge quadratically to the arc integral.")
        require(abs(fine-actual) < actual*2e-6,
                "Independent polygon area misses the enclosed arc area.")
        u = float(proof["circle"].midpoint())
        p = point(u, offset, 0)
        require(abs((p[0]-offset)**2+p[1]**2-offset**2) < offset**2*5e-16,
                "The isolated endpoint is not on the middle circle.")
        require(abs(float(proof["polar"].midpoint())-(2*atan(float(f(proof["circle"].midpoint())/first(proof["circle"].midpoint())))-u)) < 1e-15,
                "The independent circle angle disagrees.")
        checks += 4
    # Resolve a correction far below floating-point relative precision,
    # and independently nest the angles inside the global tail brackets.
    for offset, bits in ((10**8, 224), (10**20, 512)):
        proof = area_certificate(offset, bits=bits)
        require(0 < LIMIT/offset-proof["area"].high < LIMIT/offset-proof["area"].low < Q(5, offset**3),
                "An extreme-distance exact area left the uniform remainder.")
        checks += 1
        for root in tail["root_proofs"]:
            angle = value(tuple(map(Q, root["polynomial"])), Q(1, offset**2))/offset
            bracket = proof[root["kind"]]
            require(angle < bracket.low if root["side"] == "lower" else angle > bracket.high,
                    "An extreme-distance root left its global polynomial bracket.")
            checks += 1
    for offset in (0, 24, True, 25.0):
        try:
            area_certificate(offset)
        except ValueError:
            checks += 1
        else:
            raise ValueError("An invalid local pocket offset was accepted.")
    for bad in (Q(-1), Q(1, 4), 0.0, True):
        try:
            arctangent(bad)
        except ValueError:
            checks += 1
        else:
            raise ValueError("An invalid arctangent control was accepted.")
    for integers in combinations((-3, -1, 0, 2, 5), 3):
        slopes = tuple(map(Q, integers))
        V = abs((slopes[0]-slopes[1])*(slopes[0]-slopes[2])*(slopes[1]-slopes[2]))
        for order in permutations(range(3)):
            tangents = [(Q(1), slopes[i]) for i in order]
            positions = [(Q(0), slopes[i]**2/2) for i in order]
            require(coefficient(tangents, positions) == V/8,
                    "The universal residual triangle area disagrees with the older determinant formula.")
            checks += 1
        for rates in combinations_product((Q(-2), Q(0), Q(3)), repeat=3):
            determinant = ((slopes[0]-slopes[1])*(rates[0]-rates[2])
                           - (slopes[0]-slopes[2])*(rates[0]-rates[1]))
            if determinant == 0:
                continue
            clock = triple_drift(slopes, rates)["parameter"]
            for mu in (Q(-1), Q(0), Q(2, 3), clock, clock+1):
                tangents = [(Q(1), p) for p in slopes]
                positions = [(Q(0), p*p/2+b*mu) for p, b in zip(slopes, rates)]
                vertices = [linear_intersection(positions[i], tangents[i], positions[j], tangents[j])
                            for i, j in ((0, 1), (1, 2), (0, 2))]
                shoelace = abs(cross(tuple(vertices[1][i]-vertices[0][i] for i in range(2)),
                                    tuple(vertices[2][i]-vertices[0][i] for i in range(2))))/2
                expected = determinant**2*(mu-clock)**2/(2*V)
                require(shoelace == coefficient(tangents, positions) == expected,
                        "The rescaled quadratic area law disagrees with exact line geometry.")
                checks += 1
    return checks


def record():
    rows = []
    for offset in (25, 100, 1000, 10000):
        proof = area_certificate(offset)
        rows.append({"offset": offset,
                     **{k: outward(v, bits=96) for k, v in proof.items()},
                     "scaled_area": outward(proof["area"]*offset, bits=96)})
    return {"scope": "Curved pocket of the isolated three-arc plane model at delta=0; no global face claim.",
            "scaled_area_limit": str(LIMIT), "uniform_area_tail": certify_area_tail(), "examples": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write fresh exact arc-area enclosures")
    args = parser.parse_args()
    print(f"{controls()} controls: polynomial primitives, polygon convergence, circle endpoints, universal area and clock formulas, and invalid inputs.")
    result = record()
    for row in result["examples"]:
        area = sum(map(Q, row["area"]))/2
        print(f"M={row['offset']}: area about {float(area):.14g}; M*area about {float(area*row['offset']):.14g}.")
    if args.write:
        (HERE/"radial_triangle.json").write_text(json.dumps(result, indent=2)+"\n")
        print("Wrote radial_triangle.json from fresh rational circle and outer roots and exact arc integrals.")
    else:
        require(json.loads((HERE/"radial_triangle.json").read_text()) == result,
                "The archived pocket areas differ from fresh exact arc integrals.")
    print("The analytic scaled-area limit is 3375/2048; this counts the isolated three-arc pocket only.")
    print("Every real M>=25: 0 < 3375/(2048M)-area < 5/M^3, by a fresh rational polynomial certificate.")


if __name__ == "__main__":
    main()
