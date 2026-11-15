"""Independent rational derivative audits for the complete phase movie.

Run: python3 experiments/fold_movie_check.py
Standard library only. This checks implementation at exact rational states;
fold_movie_census.py proves the continuous global census separately.
"""

from fractions import Fraction as Q
from itertools import product

from blend_cusps import require
from fold_contacts_check import Jet, independent
from fold_movie import PhaseCurve


def run():
    states = components = 0
    for d, quarter, phase_quarter, shift, s in product(
            (7, 14), range(4), (0, 1, 2), (Q(0), Q(1, 3)),
            (Q(0), Q(1, 7), Q(1, 2), Q(2, 3), Q(1))):
        for p in ((Q(0),) if phase_quarter == 2 else (Q(0), Q(1, 3), Q(1))):
            curve = PhaseCurve(d, phase_quarter, p, shift)
            try:
                # Independent complex division and tangent addition. The
                # production evaluator instead uses integer complex powers
                # and one common denominator; its motion subtracts two arms.
                sj, pj = Jet(s, (1, 0)), Jet(p, (0, 1))
                u = (sj+shift)/(1-shift*sj)
                expected = independent(d, quarter, u, phase_quarter, pj)
                position, velocity, raw = curve.evaluate(quarter, s)
                motion = curve.phase_motion(quarter, s)
                for axis in range(2):
                    require(expected[axis].value == position[axis], 'The independent position differs.')
                    require(expected[axis].gradient[0] == velocity[axis], 'The independent time-chart derivative differs.')
                    require(expected[axis].gradient[1] == motion[axis], 'The nonlinear phase derivative differs.')
                raw_expected = independent(d, quarter, (s+shift)/(1-shift*s), phase_quarter, p, order=1)
                require((-Q(raw[1], raw[2]), Q(raw[0], raw[2])) == raw_expected,
                        'The independent raw physical velocity differs.')
                states += 1
                components += 8
            finally:
                curve.clear()
    print(f'{components} exact position/derivative components agree at {states} rational states, including both seams and endpoints.')


if __name__ == '__main__':
    run()
