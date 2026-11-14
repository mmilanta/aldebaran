"""Independent exact automatic-differentiation audit of the triple Jacobian."""

from fractions import Fraction as Q
from itertools import permutations, product

from blend_cusps import Interval as I, require
from fold_contacts_check import Jet, independent
from fold_triples import HINTS, chart, equations
from triple_area import linear_data


def run():
    states = [(d, [qt, (qt+1) % 4, (qt+2) % 4, qp],
               [Q(1, 7), Q(2, 5), Q(2, 3), Q(3, 5)])
              for d, qt, qp in product((7, 14), range(4), range(2))]
    states += [(d, *chart(times, phase)) for d, times, phase, _ in HINTS]
    comparisons = 0
    determinants = 0
    for d, quarters, center in states:
        variables = [Jet(c, tuple(int(i == j) for i in range(4))) for j, c in enumerate(center)]
        phase = variables[3]
        points = [independent(d, q, x, quarters[3], phase)
                  for q, x in zip(quarters[:3], variables[:3])]
        expected = [points[0][axis]-points[other][axis] for other in (1, 2) for axis in range(2)]
        f, J = equations(d, quarters, list(map(I.wrap, center)))
        for i, e in enumerate(expected):
            require(f[i].low == f[i].high == e.value, 'The independent triple equation disagrees.')
            for j in range(4):
                require(J[i][j].low == J[i][j].high == e.gradient[j],
                        'Automatic differentiation disagrees with the triple Jacobian.')
                comparisons += 1
        velocities, motions = [[independent(d, q, c, quarters[3], center[3], order, motion)
                                for q, c in zip(quarters[:3], center[:3])]
                               for order, motion in ((1, False), (0, True))]
        _, H = linear_data(velocities, motions)
        det = Q(0)
        for permutation in permutations(range(4)):
            term = Q((-1)**sum(permutation[i] > permutation[j]
                               for i in range(4) for j in range(i+1, 4)))
            for i, j in enumerate(permutation):
                term *= J[i][j].low
            det += term
        factors = Q(1)
        for c in center:
            factors *= 2/(1+c*c)
        require(det == -H*factors, 'The unfolding determinant does not equal -H times chart factors.')
        determinants += 1
    print(f'{comparisons} exact automatic-differentiation triple-Jacobian entries '
          f'passed across {len(states)} rational states.')
    print(f'{determinants} exact unfolding determinant / passage-sign identities passed.')


if __name__ == '__main__':
    run()
