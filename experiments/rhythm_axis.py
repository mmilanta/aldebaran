"""The halfway visit stays alone on the complete 11/6 -> 11/8 blend.

Run: python3 experiments/rhythm_axis.py
Standard library only. Exact elimination and Sturm isolation exclude a
second visit to z(pi) = -320 for all weights in [0,1]. Consequently this
mirror-symmetric family has no point with exactly three visits on its axis.
It also excludes ordinary two-visit axis tangencies. This does not
classify off-axis events or higher multiple meetings. See rhythm_passages.md.
"""

from fractions import Fraction as Q

from arm_detour_events import quotient
from blend_cusps import (Interval as I, add, bound, isolate_roots, product,
                        remainder, require, scale, value)


def chebyshev():
    T, U = [(Q(1),), (Q(0), Q(1))], [(Q(1),), (Q(0), Q(2))]
    for family in (T, U):
        for _ in range(2, 19):
            family.append(add(product((0, 2), family[-1]), scale(family[-2], -1)))
    return T, U


def gcd(p, q):
    while q != (0,):
        p, q = q, remainder(p, q)
    return scale(p, 1/p[-1])


def exclude_axis_contact(N, D, H0, H1, name, expected):
    """Eliminate a between N-aD=0 and H0+aH1=0, then reject weights."""
    polynomial = add(product(N, H1), product(D, H0))
    # A zero of D cannot be an axis visit, since gcd(N,D)=1.
    polynomial = quotient(polynomial, gcd(polynomial, D))
    for endpoint in (-1, 1):
        while value(polynomial, endpoint) == 0:
            polynomial = quotient(polynomial, (-endpoint, 1))
    roots = isolate_roots(polynomial, bits=54)
    require(len(roots) == expected, 'The axis-contact Sturm count changed.')
    for low, high in roots:
        weight = bound(N, I(low, high))/bound(D, I(low, high))
        require(weight.high < 0 or weight.low > 1, 'An axis-contact candidate has admissible weight.')
    print(f'{name}: all {len(roots)} interior contact candidates have exact weight bounds outside [0,1].')


def main():
    T, U = chebyshev()
    N = add((245,), add(scale(U[10], 140), scale(U[5], -65)))
    D = scale(T[7], 130)
    R = add((320, 245), add(scale(T[11], 140), scale(T[6], 65)))
    delta_T = add(T[8], scale(T[6], -1))
    P = add(add(scale(T[8], 49), scale(T[18], 28)), add((0, 13), scale(T[7], 64)))
    require(add(product(R, D), scale(product(delta_T, N), 65)) == scale(P, 650),
            'The exact elimination identity failed.')
    # If D vanished at a return, N would vanish too. Their constant gcd
    # rules out that exceptional denominator over the complex numbers.
    require(gcd(N, D) == (1,), 'An elimination denominator needs separate analysis.')
    require(value(P, -1) == 0 and value(P, 1) != 0, 'The boundary factor changed.')
    interior = quotient(P, (1, 1))
    require(len(interior) == 18 and value(interior, -1) != 0, 'The remaining polynomial has the wrong degree or boundary root.')
    roots = isolate_roots(interior, bits=54)
    require(len(roots) == 9, 'The interior Sturm root count changed.')
    outside = [0, 0]
    for low, high in roots:
        c = I(low, high)
        weight = bound(N, c)/bound(D, c)
        require(weight.high < 0 or weight.low > 1, 'An axis return has an admissible blend weight.')
        outside[int(weight.low > 1)] += 1
        print(f'cos(t) ~= {float(c.midpoint()):+.12f}; '
              f'a ~= {float(weight.midpoint()):+.12f}; exact interval lies '
              f'{"below 0" if weight.high < 0 else "above 1"}.')
    require(outside == [4, 5], 'The rejected-weight census changed.')
    print('All 9 interior candidates rejected by exact rational intervals: 4 below 0, 5 above 1.')
    print('For every a in [0,1], z(t,a)=-320 only at t=pi modulo 2pi.')
    print('The rightmost visit is also unique; no axis point has exactly three visits.')
    # On y=0, x'/sin(t) simplifies after eliminating sin(11t).
    X0 = add((2450,), scale(U[5], -1105))
    X1 = add(scale(U[5], 1105), scale(U[7], -1235))
    # Check that simplification modulo the y/sin(t) equation exactly.
    raw_X0 = add((-245,), add(scale(U[10], -1540), scale(U[5], -390)))
    raw_X1 = add(scale(U[5], 390), scale(U[7], -520))
    require(add(raw_X0, scale(N, 11)) == X0 and add(raw_X1, scale(D, -11)) == X1,
            'The horizontal-velocity simplification failed.')
    Y0 = add((0, 245), add(scale(T[11], 1540), scale(T[6], -390)))
    Y1 = add(scale(T[6], 390), scale(T[8], -520))
    exclude_axis_contact(N, D, X0, X1, 'Horizontal velocity', 14)
    exclude_axis_contact(N, D, Y0, Y1, 'Vertical velocity', 6)
    print('Every reflected pair of axis visits is transverse; no ordinary two-visit axis tangency occurs.')
    print('Off-axis events and higher multiple meetings remain outside this exclusion.')


if __name__ == '__main__':
    main()
