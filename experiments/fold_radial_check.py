"""Independently eliminate the radial quartic and check its phase root.

Run: python3 experiments/fold_radial_check.py
Standard library only. A formal Sylvester determinant checks the astroid
identity; a degree-twelve half-phase polynomial checks the cubic route.
"""

from fractions import Fraction as Q
from functools import lru_cache

from blend_cusps import Interval as I, add, isolate_roots, product, require, scale
from fold_contacts import PI, angle
from fold_radial import A, B, D, R, prove


def formal_add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for term, coefficient in polynomial.items():
            result[term] = result.get(term, 0)+coefficient
    return {term: c for term, c in result.items() if c}


def formal_scale(polynomial, factor):
    return {term: c*factor for term, c in polynomial.items() if c*factor}


def formal_product(a, b):
    result = {}
    for p, x in a.items():
        for q, y in b.items():
            term = tuple(v+w for v, w in zip(p, q))
            result[term] = result.get(term, 0)+x*y
    return {term: c for term, c in result.items() if c}


def run():
    u, v, delta = ({term: 1} for term in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    # Direct derivative of squared ellipse distance, in tan(theta/2),
    # with u=A*x0, v=B*y0, delta=A^2-B^2. Coefficients descend.
    f = [formal_scale(v, -1), formal_add(formal_scale(delta, 2), formal_scale(u, -2)),
         {}, formal_add(formal_scale(delta, -2), formal_scale(u, -2)), v]
    derivative = [formal_scale(p, 4-j) for j, p in enumerate(f[:-1])]
    matrix = ([[{}]*j+f+[{}]*(2-j) for j in range(3)]
              + [[{}]*j+derivative+[{}]*(3-j) for j in range(4)])

    @lru_cache(None)
    def determinant(row, mask):
        if row == 7:
            return {(0, 0, 0): 1}
        columns = [j for j in range(7) if not mask & (1 << j)]
        return formal_add(*(formal_scale(formal_product(matrix[row][j],
                                    determinant(row+1, mask | (1 << j))), (-1)**k)
                            for k, j in enumerate(columns) if matrix[row][j]))

    uu, vv, dd = (formal_product(p, p) for p in (u, v, delta))
    s = formal_add(uu, vv, formal_scale(dd, -1))
    astroid = formal_add(formal_product(formal_product(s, s), s),
                        formal_scale(formal_product(formal_product(dd, uu), vv), 27))
    require(determinant(0, 0) == formal_scale(formal_product(v, astroid), 256),
            'The formal radial-quartic resultant disagrees with the astroid.')
    print('All ten coefficients of the formal Sylvester identity agree: resultant = 256 v [(u²+v²−D²)³+27D²u²v²].')

    # Substitute a rational circle chart for psi, rather than using the
    # production cubic in cos(phi). Clear the full positive denominator.
    un, vn, dn = (A*R, 0, -A*R), (0, -2*B*R), (D, 0, D)
    uu, vv, dd = (product(p, p) for p in (un, vn, dn))
    s = add(add(uu, vv), scale(dd, -1))
    polynomial = add(product(product(s, s), s), scale(product(product(dd, uu), vv), 27))
    roots = isolate_roots(polynomial, Q(0), Q(1), bits=150)
    require(len(polynomial) == 13 and len(roots) == 1,
            'The independent half-phase elimination has a different number of transitions.')
    root = I(*roots[0])
    independent_phase = 2*angle(0, root)/PI
    expected = prove()['phase_over_pi']
    require(expected.low <= independent_phase.low <= independent_phase.high <= expected.high,
            'The independent phase root leaves the recorded phase enclosure.')
    print('The degree-twelve half-phase polynomial has exactly one root in [0,1]; its phase agrees with the cubic enclosure.')


if __name__ == '__main__':
    run()
