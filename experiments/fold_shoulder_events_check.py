"""Independent exact algebra and differentiation audit of finite shoulder events.

Run: python3 experiments/fold_shoulder_events_check.py
Standard library only. Reconstructs the radial polynomial, compares the
binary evaluator and Jacobian to independent Fourier arithmetic, and
repeats every certificate before comparing all archived fields, and
independently eliminates the limiting fourth-direction cubic.
"""

from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import json
from math import gcd, lcm

from blend_cusps import (Interval as I, add as poly_add, product as poly_product,
                        require, scale as poly_scale)
from fold_contacts import HERE, serialize
from fold_contacts_check import Jet, independent
from fold_radial_check import formal_add, formal_product, formal_scale
from fold_shoulder_events import HINTS, evaluate, power, radial_quartic, replay_close, run
from fold_shoulder_tangents import coefficients
from fold_triples import chart, contract, equations


class Formal:
    """Polynomials in cos(phi), sin(phi), and squared radius."""

    def __init__(self, terms):
        self.terms = {k: v for k, v in terms.items() if v}

    @staticmethod
    def wrap(value):
        return value if isinstance(value, Formal) else Formal({(0, 0, 0): Q(value)})

    def __add__(self, other):
        return Formal(formal_add(self.terms, self.wrap(other).terms))

    __radd__ = __add__

    def __neg__(self):
        return Formal(formal_scale(self.terms, -1))

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        return Formal(formal_product(self.terms, self.wrap(other).terms))

    __rmul__ = __mul__

    def on_circle(self):
        terms = {}
        for (i, j, k), value in self.terms.items():
            require(j <= 2, 'This reduction only needs one sin² substitution.')
            additions = {(i, j, k): value} if j < 2 else {
                (i, 0, k): value, (i+2, 0, k): -value}
            terms = formal_add(terms, additions)
        return terms


def quartic_identity():
    c, s, radius2 = (Formal({tuple(int(i == j) for j in range(3)): 1}) for i in range(3))
    # Independently expand the numerator of |245+140 e^iu+65 e^(i(phi-u))|².
    x = [385+65*c, 130*s, 105-65*c]
    y = [65*s, 280-130*c, -65*s]
    direct = [Formal.wrap(0) for _ in range(5)]
    for i, j in product(range(3), repeat=2):
        direct[i+j] += x[i]*x[j]+y[i]*y[j]
    for i, coefficient in enumerate((1, 0, 2, 0, 1)):
        direct[i] -= coefficient*radius2
    expected = radial_quartic(c, s, radius2)
    require(all(a.on_circle() == b.on_circle() for a, b in zip(direct, expected)),
            'The independently expanded radial quartic disagrees.')
    print('Every formal radial-quartic coefficient agrees after cos²+sin²=1.')


def evaluator_audit():
    components = 0
    for d, qt, qp, s, p, order, motion in product(
            (30, 60, 120), range(4), range(2), (Q(0), Q(1, 7), Q(1)),
            (Q(0), Q(3, 5), Q(1)), range(3), (False, True)):
        expected = independent(d, qt, s, qp, p, order, motion)
        actual = evaluate(d, qt, s, qp, p, order, motion)
        require(all(a.low <= e <= a.high for a, e in zip(actual, expected)),
                'Independent exact Fourier arithmetic leaves a binary jet enclosure.')
        components += 2
    # Actual boxes, including the circle seams. This also checks that the
    # outward-rounded binary powers retain dependency-safe enclosures.
    for d, qt, qp in product((30, 60, 120), range(4), range(2)):
        s, p = I(Q(0), Q(1, 10000)), I(Q(9999, 10000), Q(1))
        actual = evaluate(d, qt, s, qp, p)
        for t, phase in product((s.low, s.midpoint(), s.high), (p.low, p.midpoint(), p.high)):
            expected = independent(d, qt, t, qp, phase)
            require(all(a.low <= e <= a.high for a, e in zip(actual, expected)),
                    'A rational point leaves its containing interval evaluation.')
            components += 2
    print(f'{components} independent exact Fourier-jet and interval component comparisons passed.')


def jacobian_audit():
    states = [(d, [qt, (qt+1) % 4, (qt+2) % 4, qp],
               [Q(1, 7), Q(2, 5), Q(2, 3), Q(3, 5)])
              for d, qt, qp in product((30, 60, 120), range(4), range(2))]
    states += [(d, *chart(times, phase)) for d, times, phase in HINTS]
    components = 0
    for d, qs, center in states:
        variables = [Jet(c, tuple(int(i == j) for i in range(4))) for j, c in enumerate(center)]
        pts = [independent(d, q, t, qs[3], variables[3])
               for q, t in zip(qs[:3], variables[:3])]
        expected = [pts[0][j]-pts[i][j] for i in (1, 2) for j in range(2)]
        f, J = equations(d, qs, list(map(I.wrap, center)), evaluator=evaluate)
        for e, a, row in zip(expected, f, J):
            require(a.low <= e.value <= a.high, 'An independent equation leaves its enclosure.')
            for gradient, entry in zip(e.gradient, row):
                require(entry.low <= gradient <= entry.high,
                        'Automatic differentiation leaves the analytic Jacobian enclosure.')
                components += 1
    print(f'{components} automatic-differentiation Jacobian entries passed at {len(states)} rational states.')


def invalid_controls():
    d, times, phase = HINTS[0]
    qs, cs = chart(times, phase)
    shifted = cs.copy()
    shifted[3] += Q(1, 100000)
    calls = [lambda: contract(d, qs, shifted, evaluator=evaluate),
             lambda: contract(d, [qs[0]]*3+[qs[3]], [cs[0]]*3+[cs[3]], evaluator=evaluate),
             lambda: contract(d, qs, cs, radius=Q(-1), evaluator=evaluate),
             lambda: contract(True, qs, cs, evaluator=evaluate),
             lambda: power((I.wrap(1), I.wrap(0)), -1)]
    for call in calls:
        try:
            call()
        except ValueError:
            pass
        else:
            raise ValueError('A degenerate or invalid control was accepted.')
    print(f'{len(calls)} invalid or degenerate mathematical controls were rejected.')


def rotation_audit(record):
    # Independent Sylvester elimination, rather than quotient multiplication.
    aa, bb, delta = 205**2, 75**2, 36400
    p = [delta*delta*aa-245**2*aa*bb, -3*delta*delta*aa,
         3*delta*delta*aa, delta*delta*(bb-aa)]
    ss = (aa*aa, -2*aa*delta, delta*delta)
    nn = (2*ss[0], 2*ss[1]-16*aa*bb, 2*ss[2]+16*aa*bb)
    f = [(Q(v),) for v in reversed(p)]
    g = [(-Q(n), Q(s)) for n, s in reversed(list(zip(nn, ss)))]
    zero = (Q(0),)
    matrix = [[zero]*j+f+[zero]*(1-j) for j in range(2)]
    matrix += [[zero]*j+g+[zero]*(2-j) for j in range(3)]

    @lru_cache(None)
    def determinant(row, mask):
        if row == 5:
            return (Q(1),)
        result = zero
        columns = [j for j in range(5) if not mask & (1 << j)]
        for sign, j in enumerate(columns):
            term = poly_product(matrix[row][j], determinant(row+1, mask | (1 << j)))
            result = poly_add(result, poly_scale(term, (-1)**sign))
        return result

    coefficients = determinant(0, 0)
    denominator = lcm(*(v.denominator for v in coefficients))
    integers = [int(v*denominator) for v in coefficients]
    content = gcd(*integers)
    primitive = [v//content for v in integers]
    if primitive[-1] < 0:
        primitive = [-v for v in primitive]
    witness = record['fourth_direction_irrationality']
    require(primitive == list(witness['twice_cos_polynomial_ascending']),
            'The independent Sylvester elimination disagrees with the quotient norm.')
    prime = witness['irreducibility_prime']
    require(prime == 31 and primitive[-1] % prime != 0
            and all(sum(c*pow(j, k, prime) for k, c in enumerate(primitive)) % prime
                    for j in range(prime)), 'The independent finite-field irreducibility check failed.')
    require((-primitive[-2]) % primitive[-1] != 0,
            'The independently reconstructed cubic trace is integral.')
    print('Independent 5×5 Sylvester elimination, all 31 modular residues, and the nonintegral trace agree.')


def main():
    quartic_identity()
    evaluator_audit()
    jacobian_audit()
    invalid_controls()
    fresh = serialize(run())
    archived = json.loads((HERE/'fold_shoulder_events.json').read_text())
    require(fresh == archived, 'The archived finite events differ from the fresh complete record.')
    print('Every archived event, bound, sign, and fourth-visit residual agrees with fresh proofs.')
    tangent_proof = coefficients()
    rotation_audit(tangent_proof)
    tangent_record = serialize(tangent_proof)
    require(tangent_record == json.loads((HERE/'fold_shoulder_tangents.json').read_text()),
            'The archived analytic coefficients differ from the fresh record.')
    print('The analytic coefficients, formal expansions, radial factorization, and fourth-direction signs agree too.')
    for name, d, low, high in (
            ('fold_shoulder_close.json', 10115, Q(35508, 10**10), Q(35509, 10**10)),
            ('fold_shoulder_near_79866.json', 79866, Q(8555, 10**11), Q(8556, 10**11))):
        close = replay_close(HERE/name)
        distance = close['nearest_equal_radius_point_distance']
        require(close['event']['folds'] == d and low < distance.low <= distance.high < high,
                'A selected near-fourth point leaves its advertised distance bracket.')
        print(f'The {d:,}-fold near-fourth certificate and every archived field pass a fresh replay.')


if __name__ == '__main__':
    main()
