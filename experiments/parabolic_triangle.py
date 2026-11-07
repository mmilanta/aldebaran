"""Three limiting parabolas, straightened without changing their area.

Standard library only. Exact polynomial integrals and rational line
intersections check the formulas in parabolic_triangle.md. Numerical
finite-offset controls are separate from the exact limit geometry.
Run with --write to regenerate the illustration's rational data.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations, permutations, product
import json
from math import cos, fsum, sin
from pathlib import Path

from blend_cusps import require
from radial_limit import triple_drift
from triple_area import coefficient, cross, linear_intersection

HERE = Path(__file__).resolve().parent
PAIRS = ((0, 1), (1, 2), (0, 2))


def inputs(slopes, rates):
    require(type(slopes) in (tuple, list) and type(rates) in (tuple, list)
            and len(slopes) == len(rates) == 3
            and all(type(x) is Q for x in (*slopes, *rates)),
            "Use three rational slopes and three rational route rates.")
    require(len(set(slopes)) == 3, "The three slopes must be distinct.")


def rate_polynomial(slopes, rates):
    """Return A,B,C with b_i=A p_i^2+B p_i+C, by divided differences."""
    inputs(slopes, rates)
    p, b = slopes, rates
    first = (b[1]-b[0])/(p[1]-p[0])
    second = (b[2]-b[1])/(p[2]-p[1])
    A = (second-first)/(p[2]-p[0])
    B = first-A*(p[0]+p[1])
    C = b[0]-A*p[0]**2-B*p[0]
    return A, B, C


def clock(slopes, rates):
    A, _, _ = rate_polynomial(slopes, rates)
    require(A != 0, "An ordinary triple needs a nonzero quadratic rate coefficient.")
    return -1/(2*A)


def geometry(slopes, rates, mu):
    """Exact vertices and areas of X_i=(Y-p_i)^2/2+b_i*mu.

    Vertices follow 01 -> 12 -> 02 -> 01. Its three edges belong to
    branches 1,2,0, respectively. The same closed walk works on either
    side of the event and contracts to a point at the limiting clock.
    """
    inputs(slopes, rates)
    require(type(mu) is Q, "Use a rational scaled route parameter.")
    p, b = slopes, rates
    vertices, straight = [], []
    for i, j in PAIRS:
        y = (p[i]+p[j])/2 + (b[i]-b[j])*mu/(p[i]-p[j])
        x = (y-p[i])**2/2+b[i]*mu
        vertices.append((x, y))
        straight.append((x-y*y/2, y))

    def primitive(which, y):
        return y**3/6-p[which]*y*y/2+(p[which]**2/2+b[which]*mu)*y

    integral = sum(primitive(which, vertices[(k+1) % 3][1])
                   - primitive(which, vertices[k][1]) for k, which in enumerate((1, 2, 0)))
    shoelace = sum(cross(v, straight[(k+1) % 3]) for k, v in enumerate(straight))/2
    V = abs((p[0]-p[1])*(p[0]-p[2])*(p[1]-p[2]))
    A, B, C = rate_polynomial(p, b)
    predicted = V*(1+2*A*mu)**2/8
    return {"vertices": vertices, "straight_vertices": straight,
            "signed_integral": integral, "signed_shoelace": shoelace,
            "area": abs(integral), "predicted_area": predicted,
            "rate_polynomial": (A, B, C), "slope_product": V}


def exact_controls():
    checks = 0
    for p in combinations(tuple(map(Q, (-3, -1, 0, 2, 5))), 3):
        for b in product(tuple(map(Q, (-2, 0, 3))), repeat=3):
            A, B, C = rate_polynomial(p, b)
            require(all(A*x*x+B*x+C == y for x, y in zip(p, b)),
                    "The interpolating rate polynomial misses an input.")
            checks += 1
            times = [Q(-2), Q(0), Q(2, 3), Q(5)]
            if A:
                c = clock(p, b)
                drift = triple_drift(p, b)
                require(c == drift["parameter"] and -c*B == drift["angle"]
                        and c*C == drift["height"],
                        "The divided-difference clock disagrees with the event Jacobian.")
                checks += 1
                times.extend((c, c+Q(1, 3)))
            for mu in times:
                g = geometry(p, b, mu)
                require(g["signed_integral"] == g["signed_shoelace"]
                        and g["area"] == g["predicted_area"],
                        "The exact curved integral and straight triangle disagree.")
                positions = [(Q(0), x*x/2+y*mu) for x, y in zip(p, b)]
                tangents = [(Q(1), x) for x in p]
                require(g["area"] == coefficient(tangents, positions),
                        "The parabolic area disagrees with the older determinant formula.")
                for (i, j), (x, y), (u, sy) in zip(PAIRS, g["vertices"], g["straight_vertices"]):
                    require(x == (y-p[i])**2/2+b[i]*mu == (y-p[j])**2/2+b[j]*mu,
                            "A curved vertex is not on both branches.")
                    # Independently solve the two lines in the (zeta,Z) frame.
                    zeta, Z = linear_intersection(positions[i], tangents[i], positions[j], tangents[j])
                    require((Z, -zeta) == (u, sy), "The straightened vertex misses a line intersection.")
                checks += 1
                if A:
                    at_event = geometry(p, b, c)
                    require(all(v == (c*C, c*B) for v in at_event["straight_vertices"]),
                            "The limiting event vertices do not coincide.")
                    initial = geometry(p, b, Q(0))["straight_vertices"]
                    factor = 1-mu/c
                    for v, start in zip(g["straight_vertices"], initial):
                        expected = (c*C+factor*(start[0]-c*C), c*B+factor*(start[1]-c*B))
                        require(v == expected, "The straight triangles are not homothetic about their meeting.")
                    checks += 1

    # Labels, a shifted slope origin, and a common height do not affect area.
    p, b, mu = (Q(-2), Q(1), Q(2)), (Q(0), Q(1), Q(0)), Q(2, 3)
    original = geometry(p, b, mu)
    for order in permutations(range(3)):
        relabeled = geometry(tuple(p[i] for i in order), tuple(b[i] for i in order), mu)
        require(relabeled["area"] == original["area"], "Relabeling changed the pocket area.")
        require(clock(tuple(p[i] for i in order), tuple(b[i] for i in order)) == clock(p, b),
                "Relabeling changed the event clock.")
        checks += 1
    for shift in (Q(-7, 3), Q(0), Q(9, 4)):
        translated = geometry(tuple(x+shift for x in p), b, mu)
        require(translated["vertices"] == [(x, y+shift) for x, y in original["vertices"]],
                "A common slope shift did not translate the parabolic pocket.")
        lifted = geometry(p, tuple(x+shift for x in b), mu)
        require(lifted["vertices"] == [(x+shift*mu, y) for x, y in original["vertices"]],
                "A common route rate did not translate the pocket.")
        checks += 1

    # The fixed-span maximum is an exact square identity, including its
    # one-sided degenerate limits (those endpoints are not ordinary triples).
    L = Q(4)
    for middle in (Q(-2)+Q(k, 32) for k in range(129)):
        left, right = middle+2, 2-middle
        actual = L*left*right/8
        require(actual == L**3/32-L*middle**2/8 and 0 <= actual <= L**3/32,
                "The fixed-span area maximum is not the stated square identity.")
        if -2 < middle < 2:
            require(geometry((Q(-2), middle, Q(2)), b, Q(0))["area"] == actual,
                    "The gap formula disagrees with exact arc integration.")
        checks += 1

    for bad_slopes, bad_rates in (((Q(0),)*3, b), ((0, 1, 2), b), (p[:2], b),
                                  (p, (Q(0), Q(1), True))):
        try:
            geometry(bad_slopes, bad_rates, Q(0))
        except ValueError:
            checks += 1
        else:
            raise ValueError("An invalid parabolic input was accepted.")
    for bad_mu in (0, 0.0, True):
        try:
            geometry(p, b, bad_mu)
        except ValueError:
            checks += 1
        else:
            raise ValueError("A non-rational route parameter was accepted.")
    for affine_rates in ((Q(1),)*3, tuple(2*x+1 for x in p)):
        require(geometry(p, affine_rates, mu)["area"] == original["slope_product"]/8,
                "Affine rates should preserve the initial area.")
        try:
            clock(p, affine_rates)
        except ValueError:
            checks += 1
        else:
            raise ValueError("A singular event was assigned an ordinary clock.")
    return checks


def finite_point(sigma, offset, slope, rate, mu, height=0., second=0., mixed=0.):
    """Independent smooth support model, in the stretched Cartesian frame.

    h=h0+p*theta+second*theta^2/2+rate*mu/M+mixed*theta*mu/M.
    The cancellation-free formula is also usable at very large offsets.
    """
    theta = sigma/offset
    change = slope*theta+second*theta*theta/2+rate*mu/offset+mixed*theta*mu/offset
    p = slope+second*theta+mixed*mu/offset
    half = sin(theta/2)**2
    X = offset*(2*(offset-height)*half+change*cos(theta)-p*sin(theta))
    Y = (height+change-offset)*sin(theta)+p*cos(theta)
    radius = height+change+second-offset
    return (X, Y), (-radius*sin(theta), radius*cos(theta)/offset)


def finite_crossing(offset, slopes, rates, mu, i, j):
    """Numerical Newton control, never used in an exact proof decision."""
    initial = geometry(tuple(map(Q, slopes)), tuple(map(Q, rates)), Q(mu))["vertices"][PAIRS.index((i, j))]
    y = float(initial[1])
    s, t = slopes[i]-y, slopes[j]-y
    for _ in range(12):
        a, v = finite_point(s, offset, slopes[i], rates[i], mu)
        b, w = finite_point(t, offset, slopes[j], rates[j], mu)
        difference = (a[0]-b[0], a[1]-b[1])
        determinant = cross(v, w)
        require(abs(determinant) > .1, "A numerical pair lost transversality.")
        ds, dt = -cross(difference, w)/determinant, -cross(difference, v)/determinant
        s, t = s+ds, t+dt
        if max(abs(ds), abs(dt)) < 1e-13:
            break
    a = finite_point(s, offset, slopes[i], rates[i], mu)[0]
    b = finite_point(t, offset, slopes[j], rates[j], mu)[0]
    require(max(abs(x-y) for x, y in zip(a, b)) < 2e-12,
            "The finite-offset Newton residual is unresolved.")
    return s, t


def finite_area(offset, slopes, rates, mu, steps=128):
    ab, bc, ac = [finite_crossing(offset, slopes, rates, mu, i, j) for i, j in PAIRS]
    points = []
    for which, start, end in ((1, ab[1], bc[0]), (2, bc[1], ac[1]), (0, ac[0], ab[0])):
        points.extend(finite_point(start+(end-start)*k/steps, offset, slopes[which], rates[which], mu)[0]
                      for k in range(steps))
    return abs(fsum(cross(p, q) for p, q in zip(points, points[1:]+points[:1]))/2)


def numerical_controls():
    checks, worst = 0, 0.
    for slope, rate, second, mixed, mu, sigma in product((-2., 1., 2.), (-1., 0., 1.),
                                                       (-3., 2.), (-2., 1.), (-1., 0., 2.),
                                                       (-3., -.5, 0., 2.5)):
        expected = (sigma*sigma/2+rate*mu, slope-sigma)
        previous = float("inf")
        for offset in (32, 128, 512, 2048, 8192):
            point, _ = finite_point(sigma, offset, slope, rate, mu, height=.6, second=second, mixed=mixed)
            error = max(abs(x-y) for x, y in zip(point, expected))
            require(error < 100/offset and error <= previous/3.5+1e-14,
                    "The independent smooth support model misses its parabolic limit.")
            previous = error
            worst = max(worst, offset*error)
            checks += 1
    for middle in (0, 1, Q(7, 4)):
        p, b = (-2, middle, 2), (0, 1, 0)
        c = clock(tuple(map(Q, p)), tuple(map(Q, b)))
        for mu in (Q(0), c/3, 2*c):
            expected = float(geometry(tuple(map(Q, p)), tuple(map(Q, b)), mu)["area"])
            previous = float("inf")
            for offset in (32, 128, 512, 2048):
                area = finite_area(offset, p, b, float(mu))
                finer = finite_area(offset, p, b, float(mu), steps=512)
                require(abs(area-finer) < expected*3e-5,
                        "Independent curved-area sampling needs more resolution.")
                error = abs(finer-expected)
                require(error < previous/12+expected*1e-12 and error < expected*40/offset**2,
                        "The unequal-slope finite pocket does not approach its exact limit.")
                previous = error
                checks += 1
    return checks, worst


def record():
    b = (Q(0), Q(1), Q(0))

    def row(p, mu):
        result = geometry(p, b, mu)
        return {"slopes": list(map(str, p)), "rates": list(map(str, b)), "mu": str(mu),
                "clock": str(clock(p, b)), "area": str(result["area"]),
                "rate_polynomial": list(map(str, result["rate_polynomial"])),
                "vertices": [list(map(str, v)) for v in result["vertices"]],
                "straight_vertices": [list(map(str, v)) for v in result["straight_vertices"]]}

    return {"scope": "Exact limiting parabolas of three selected arcs, not finite-distance enclosures or a full-drawing face census.",
            "shear": "U=X-Y^2/2", "area": "abs(product of three slope differences)*(1+2*A*mu)^2/8",
            "gap_examples": [row((Q(-2), middle, Q(2)), Q(0)) for middle in (Q(0), Q(1), Q(7, 4))],
            "clock_examples": [row((Q(-2), Q(1), Q(2)), mu) for mu in (Q(0), Q(3, 2), Q(3))]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the exact illustration data")
    args = parser.parse_args()
    exact = exact_controls()
    numerical, worst = numerical_controls()
    print(f"{exact} exact controls: curved integrals, line intersections, determinant areas, rate interpolation, clocks, homotheties, gap maxima, and invalid inputs.")
    print(f"{numerical} numerical controls: smooth support limits and independent finite-distance curved pockets; max M*point error {worst:.6g}.")
    result = record()
    destination = HERE/"parabolic_triangle.json"
    if args.write:
        destination.write_text(json.dumps(result, indent=2)+"\n")
        print("Wrote parabolic_triangle.json from fresh rational geometry.")
    else:
        require(json.loads(destination.read_text()) == result, "The illustration record differs from fresh exact geometry.")
    print("The shear U=X-Y^2/2 preserves area. Equal slope gaps maximize the residual area at fixed slope span.")
    print("These are exact limit curves; numerical finite-offset checks do not provide a uniform offset threshold.")


if __name__ == "__main__":
    main()
