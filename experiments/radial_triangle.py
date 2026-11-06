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
from math import atan, cos, fsum, sin

from blend_cusps import Interval as I, add, bound, derivative, product, require, scale
from positive_front_projection import certify, f, first
from radial_limit import HERE, outward, triple_drift
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
    for offset in (25, 100, 1000, 10000):
        proof = area_certificate(offset)
        actual = float(proof["area"].midpoint())
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
            "scaled_area_limit": str(LIMIT), "examples": rows}


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


if __name__ == "__main__":
    main()
