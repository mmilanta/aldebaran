"""Independent polynomial proof that the angle-and-distance route has no cusp.

Run: python3 experiments/regular_blend_algebra.py
Standard library only. This proves nonvanishing, without using the rational
arc cover or its quantitative speed bound. See regular_blend.md.
"""

from fractions import Fraction as Q
from functools import reduce
from math import gcd

from blend_cusps import (Interval, add, bound, derivative, isolate_roots,
                        product, require, scale, value)
from certify_intersections import IntersectionCertificate
from regular_blend import quotient
from tangent_turning import certify_turning


def polynomials(m, n):
    """z/5 = X(c) + i sin(t) Y(c), q = (sin(t) R(c) + i S(c))/N(c)."""
    T, U = [(1,), (0, 1)], [(1,), (0, 2)]
    for family in (T, U):
        for _ in range(2, max(m, n)+1):
            family.append(add(product((0, 2), family[-1]), scale(family[-2], -1)))
    X = add(add((0, 49), scale(T[m], 28)), scale(T[n], 13))
    Y = add(add((49,), scale(U[m-1], 28)), scale(U[n-1], -13))
    sin2 = (1, 0, -1)
    Xc, Yc = derivative(X), derivative(Y)
    vertical = add(product((0, 1), Y), scale(product(sin2, Yc), -1))
    R = add(scale(product(Xc, X), -1), product(Y, vertical))
    S = add(product(X, vertical), product(product(sin2, Y), Xc))
    N = add(product(X, X), product(sin2, product(Y, Y)))
    return X, Y, R, S, N


def primitive(p):
    require(all(x.denominator == 1 for x in p), 'The generated polynomial is not integral.')
    content = reduce(gcd, (abs(x.numerator) for x in p))
    require(content > 0, 'The alignment polynomial vanished identically.')
    return scale(p, Q(1, content))


def check_quotient(m, n, data):
    """Exact independent rational-circle evaluations check the polynomial forms."""
    X, Y, R, S, N = data
    curve = IntersectionCertificate(m, n, 1)
    try:
        for quarter in range(4):
            for k in range(17):
                s = Q(k, 16)
                c, sine = (1-s*s)/(1+s*s), 2*s/(1+s*s)
                for _ in range(quarter):
                    c, sine = -sine, c
                p, _, (vx, vy, D) = curve.evaluate(quarter, s)
                require(p == (5*value(X, c), 5*sine*value(Y, c)),
                        'The polynomial position disagrees with the rational evaluator.')
                expected = quotient((-Q(vy, D), Q(vx, D)), p)
                actual = (sine*value(R, c)/value(N, c), value(S, c)/value(N, c))
                require(actual == expected, 'The polynomial logarithmic derivative is wrong.')
    finally:
        curve.evaluate.cache_clear()


def main():
    first, second = polynomials(2, 3), polynomials(4, 7)
    check_quotient(2, 3, first)
    check_quotient(4, 7, second)
    Ra, Sa, _ = first[2:]
    Rb, Sb, _ = second[2:]
    alignment = primitive(add(product(Ra, Sb), scale(product(Sa, Rb), -1)))
    dot = add(product((1, 0, -1), product(Ra, Rb)), product(Sa, Sb))
    require(len(alignment)-1 == 15, 'Unexpected alignment polynomial degree.')
    intervals = isolate_roots(alignment)
    require(len(intervals) == 5, 'Unexpected number of alignments in (-1,1).')
    for low, high in intervals:
        c = Interval(low, high)
        require(bound(dot, c).low > 0, 'Opposing or unresolved logarithmic velocities.')
        print(f'Cosine ≈ {float(c.midpoint()):+.12f}: alignment has certified positive dot product.')
    # At sin(t)=0 both logarithmic velocities are pure imaginary and have
    # the same sign. Their norms and both endpoint regularities are separate.
    for c in [Q(-1), Q(1)]:
        require(value(Sa, c)*value(Sb, c) > 0, 'The axial velocities oppose each other.')
    require(certify_turning(2, 3).turns == certify_turning(4, 7).turns == 0,
            'The independent endpoint tangent certificates disagree.')
    print('All five non-axial cosine roots give same-direction velocities; axial times do too.')
    print('No logarithmic-velocity segment meets zero. The complete route is regular.')


if __name__ == '__main__':
    main()
