"""Independent exact automatic-differentiation checks of the contact equations.

Run: python3 experiments/fold_contacts_check.py
Standard library only. This audits the evaluator and its analytic Jacobian;
fold_contacts.py repeats the complete geometric certificate.
"""

from fractions import Fraction as Q
from itertools import product

from fold_contacts import HINTS, equations, evaluate, hint_chart
from blend_cusps import Interval as I, require


class Jet:
    """A rational value and three formal first derivatives."""

    def __init__(self, value, gradient=(0, 0, 0)):
        self.value, self.gradient = Q(value), tuple(map(Q, gradient))

    @staticmethod
    def wrap(x):
        return x if isinstance(x, Jet) else Jet(x)

    def __add__(self, other):
        other = self.wrap(other)
        return Jet(self.value+other.value, tuple(a+b for a, b in zip(self.gradient, other.gradient)))

    __radd__ = __add__

    def __neg__(self):
        return Jet(-self.value, tuple(-a for a in self.gradient))

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        return Jet(self.value*other.value,
                   tuple(a*other.value+self.value*b for a, b in zip(self.gradient, other.gradient)))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.wrap(other)
        return Jet(self.value/other.value,
                   tuple((a*other.value-self.value*b)/other.value**2
                         for a, b in zip(self.gradient, other.gradient)))


def mul(z, w):
    return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]


def div(z, w):
    den = w[0]*w[0]+w[1]*w[1]
    return (z[0]*w[0]+z[1]*w[1])/den, (z[1]*w[0]-z[0]*w[1])/den


def power(z, k):
    if k < 0:
        return div((1, 0), power(z, -k))
    result = (1, 0)
    for _ in range(k):
        result = mul(result, z)
    return result


def mobius(quarter, parameter):
    # Independent quotient construction; negative powers use actual complex
    # division, rather than the main evaluator's conjugated positive powers.
    return mul(power((0, 1), quarter), div((1, parameter), (1, -parameter)))


def independent(d, quarter, s, phase_quarter, phase, order=0, motion=False):
    w, phase_w = mobius(quarter, s), mobius(phase_quarter, phase)
    result = [0, 0]
    terms = ((65, 1-d),) if motion else ((245, 1), (140, d+1), (65, 1-d))
    for radius, frequency in terms:
        z = power(w, frequency)
        if frequency < 0:
            z = mul(z, phase_w)
        z = mul(z, power((0, frequency), order))
        if motion:
            z = mul(z, (0, 1))
        for j in range(2):
            result[j] += radius*z[j]
    return tuple(result)


def run():
    comparisons = 0
    # Positions, raw t-jets, and phase jets at every quarter, with exact
    # rational controls on both circles. All arithmetic here is pointwise.
    for d, qt, qp, s, p in product((7, 14), range(4), range(4),
                                  (Q(0), Q(1, 7), Q(2, 3), Q(1)),
                                  (Q(0), Q(1, 5), Q(1))):
        for order, motion in product(range(3), (False, True)):
            expected = independent(d, qt, s, qp, p, order, motion)
            actual = evaluate(d, qt, s, qp, p, order, motion)
            require(all(a.low == a.high == e for a, e in zip(actual, expected)),
                    'The independent Fourier jet disagrees with the interval evaluator.')
            comparisons += 2

    states = []
    for d, qt, qu, qp in product((7, 14), range(4), range(4), range(2)):
        states.append((d, [qt, qu, qp], [Q(1, 7), Q(2, 3), Q(3, 5)]))
    for d, hints in HINTS.items():
        states.extend((d, *hint_chart(hint)) for hint in hints)
    jacobian_entries = 0
    for d, quarters, center in states:
        variables = [Jet(c, tuple(int(i == j) for i in range(3))) for j, c in enumerate(center)]
        s, u, phase = variables
        p, q = [independent(d, qt, x, quarters[2], phase)
                for qt, x in zip(quarters[:2], (s, u))]
        v, w = [independent(d, qt, x, quarters[2], phase, 1)
                for qt, x in zip(quarters[:2], (s, u))]
        expected = (p[0]-q[0], p[1]-q[1], v[0]*w[1]-v[1]*w[0])
        f, J = equations(d, quarters, list(map(I.wrap, center)))
        for i, e in enumerate(expected):
            require(f[i].low == f[i].high == e.value, 'The independent contact equation disagrees.')
            for j in range(3):
                require(J[i][j].low == J[i][j].high == e.gradient[j],
                        'Automatic differentiation disagrees with the analytic contact Jacobian.')
                jacobian_entries += 1
    print(f'{comparisons} independent exact Fourier-jet component comparisons passed.')
    print(f'{jacobian_entries} exact automatic-differentiation Jacobian entries passed '
          f'across {len(states)} states, including all four proposed contact centers.')


if __name__ == '__main__':
    run()
