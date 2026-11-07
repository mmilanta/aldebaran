"""Enclose the symmetric pocket at the leading corrected triple clock.

The parameter is exactly delta=225/(128M). Two rational normal-angle
boxes enclose the outer/middle intersection by a contraction. The
existing outer/outer root is enclosed independently. Polynomial Green
primitives enclose their tiny area, including cancellation. This is a
finite local certificate, separate from the analytic M^-5 limit.
Standard library only; see parabolic_retiming.md.
"""

from fractions import Fraction as Q
from math import factorial

from blend_cusps import Interval as I, add, bound, derivative, product, require, scale
from positive_front_projection import certify
from radial_limit import FIRST, THIRD
from radial_triangle import F, G0, G1, primitive

G = tuple(map(Q, (1, 0, -3, 0, 3, 0, -1)))
F1, F2, G_1, G_2 = derivative(F), derivative(derivative(F)), derivative(G), derivative(derivative(G))
H0 = primitive(add(scale(G, 2), G_2))
H1 = primitive(product(G, add(G, G_2)))
SINE = tuple(Q((-1)**((k-1)//2), factorial(k)) if k % 2 else Q(0) for k in range(48))
COSINE = tuple(Q((-1)**(k//2), factorial(k)) if k % 2 == 0 else Q(0) for k in range(47))
LIMIT = Q(8, 15)*THIRD**2


def trig(theta, cosine=False):
    radius = max(abs(theta.low), abs(theta.high))
    require(radius <= Q(1, 8), "The local trigonometric bound needs |theta|<=1/8.")
    power = 48 if cosine else 49
    error = radius**power/factorial(power)
    approximation = bound(COSINE if cosine else SINE, theta)
    return approximation+I(-error, error)


def point(which, sigma, offset):
    theta, delta = sigma/offset, FIRST/offset
    h, p, k = ([bound(v, theta) for v in (F, F1, F2)] if which == 0
               else [delta*bound(v, theta) for v in (G, G_1, G_2)])
    sine, cosine, half = trig(theta), trig(theta, True), trig(theta/2)
    coordinates = (offset*(2*offset*half*half+h*cosine-p*sine),
                   (h-offset)*sine+p*cosine)
    radius = h+k-offset
    velocity = (-radius*sine, radius*cosine/offset)
    return coordinates, velocity


def equations(box, offset):
    p, v = point(0, box[0], offset)
    q, w = point(1, box[1], offset)
    return [a-b for a, b in zip(p, q)], [[v[j], -w[j]] for j in range(2)]


def rounded(x, bits):
    return Q(round(x*2**bits), 2**bits)


def inverse_midpoint(matrix, bits):
    a, b = [entry.midpoint() for entry in matrix[0]]
    c, d = [entry.midpoint() for entry in matrix[1]]
    determinant = a*d-b*c
    require(determinant != 0, "A candidate pair Jacobian is singular.")
    return [[rounded(x/determinant, bits) for x in row] for row in ((d, -b), (-c, a))]


def pair_certificate(offset, bits):
    center = [Q(15, 8), Q(0)]
    for _ in range(20):
        values, jacobian = equations([I.wrap(x) for x in center], offset)
        R = inverse_midpoint(jacobian, bits)
        candidate = [rounded(center[i]-sum(R[i][j]*values[j].midpoint() for j in range(2)), bits)
                     for i in range(2)]
        if candidate == center:
            break
        center = candidate
    else:
        raise ValueError("The rational pair candidate did not stabilize.")
    radius = Q(8, 2**bits)
    box = [I(x-radius, x+radius) for x in center]
    values, _ = equations([I.wrap(x) for x in center], offset)
    _, jacobian = equations(box, offset)
    R = inverse_midpoint(jacobian, bits)
    defect = [[Q(i == j)-sum(R[i][k]*jacobian[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 100), "The retimed pair box is not a strong contraction.")
    image = [-sum(R[i][k]*values[k] for k in range(2))
             +sum(defect[i][j]*I(-radius, radius) for j in range(2)) for i in range(2)]
    require(all(-radius < x.low <= x.high < radius for x in image),
            "The retimed pair contraction does not map the box strictly into itself.")
    determinant = jacobian[0][0]*jacobian[1][1]-jacobian[0][1]*jacobian[1][0]
    determinant.sign()
    return box, norm


def area_certificate(offset, bits):
    require(type(offset) is int and offset >= 25 and type(bits) is int and bits >= 100,
            "Use an integer local offset at least 25 and at least 100 bits.")
    pair, norm = pair_certificate(offset, bits)
    outer, _ = certify(offset, bits=bits)
    u, t = [x/offset for x in pair]
    delta = FIRST/offset
    outer_primitive = add(add((Q(0), Q(offset**2)), scale(G0, -offset)), G1)
    middle_primitive = add(add((Q(0), Q(offset**2)), scale(H0, -offset*delta)), scale(H1, delta**2))
    signed = bound(outer_primitive, outer)-bound(outer_primitive, u)+bound(middle_primitive, t)
    area = signed*signed.sign()
    require(area.low > 0, "The retimed area did not separate from zero.")

    # Each selected branch is a monotone height graph. Their disjoint
    # normal slots make dX/dY=-M*tan(theta) strictly ordered. Thus each
    # pair crosses at most once here, and the three arcs bound a pocket.
    require(Q(3, 2) < offset*outer.low < offset*outer.high < Q(17, 8)
            and Q(3, 2) < pair[0].low < pair[0].high < Q(17, 8)
            and -Q(1, 8) < pair[1].low < pair[1].high < Q(1, 8),
            "The certified crossings left the disjoint normal slots.")
    for which, slot in ((0, I(Q(3, 2), Q(17, 8))), (1, I(-Q(1, 8), Q(1, 8)))):
        _, velocity = point(which, slot, offset)
        require(velocity[1].high < 0, "A pocket arc is not a decreasing height graph.")
    require(t.low > 0 and u.low > outer.high,
            "The retimed crossings have the wrong local order.")
    return {"area": area, "scaled_area": area*offset**5, "outer": outer,
            "pair": pair, "contraction": norm}


def decimal(interval, places=12):
    unit = 10**places
    low = (interval.low*unit)//1
    high = -((-interval.high*unit)//1)
    return f"({low//unit}.{low%unit:0{places}d}, {high//unit}.{high%unit:0{places}d})"


def main():
    require(LIMIT == Q(1537734375, 134217728), "The fifth-order limit coefficient changed.")
    for offset, bits in ((25, 128), (100, 160), (10**6, 256), (10**20, 640)):
        proof = area_certificate(offset, bits)
        # A finite-distance check against the analytic limit; not a tail proof.
        require(0 < LIMIT-proof["scaled_area"].high
                < LIMIT-proof["scaled_area"].low < Q(200, offset**2),
                "A fresh finite retimed area missed the fifth-order limit.")
        print(f"M={offset}: exact M^5*area in {decimal(proof['scaled_area'])}; contraction < 1/100.", flush=True)
        if offset == 25:
            from parabolic_retiming import SymmetricModel, pocket
            sampled = pocket(SymmetricModel(), offset, float(FIRST), 1024)*offset**4
            require(abs(sampled-float(proof["scaled_area"].midpoint())) < 1e-7,
                    "The independent sampled pocket misses the exact Green integral.")
    print("Four positive finite areas certified with rational contraction boxes and polynomial Green primitives.")
    print("Even M=10^20 retains a nonzero pocket at the leading clock. The all-offset error tail is not certified here.")


if __name__ == "__main__":
    main()
