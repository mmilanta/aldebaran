"""Exact constants and nonsingularity for meetings approaching the shoulder.

Run: python3 experiments/fold_shoulder.py [--write]
Standard library only. fold_shoulder.md supplies the analytic implicit-
function argument. This does not certify a numerical fold cutoff,
ordinary-passage signs, or exclusion of a fourth visit.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json

from blend_cusps import Interval as I, require
from fold_contacts import HERE, PI, serialize
from fold_radial import A, B, D, R, prove
from fold_radial_check import formal_add, formal_product, formal_scale
from phase_unfolding import sqrt_interval


def cube_root(x, bits=180):
    require(0 < x.low <= x.high < 1, 'Use a positive cube-root argument below one.')

    def enclose(value):
        low, high = Q(0), Q(1)
        for _ in range(bits):
            middle = (low+high)/2
            if middle**3 <= value:
                low = middle
            else:
                high = middle
        require(low**3 <= value <= high**3, 'A cube-root bound failed.')
        return low, high

    return I(enclose(x.low)[0], enclose(x.high)[1])


def jacobian_identity():
    # Formal variables a,b,s,kappa; no numerical determinant is used.
    a, b, s, k = ({tuple(int(j == i) for j in range(4)): 1} for i in range(4))
    ass = formal_product(a, formal_product(s, s))
    bs = formal_product(b, s)
    matrix = [[formal_scale(ass, -2), formal_scale(ass, -1), {}, bs],
              [formal_scale(ass, -2), {}, formal_scale(ass, 2), formal_scale(bs, 2)],
              [formal_scale(k, -1), k, {}, {}],
              [formal_scale(k, -1), {}, k, {}]]

    @lru_cache(None)
    def determinant(row, mask):
        if row == 4:
            return {(0, 0, 0, 0): 1}
        columns = [j for j in range(4) if not mask & (1 << j)]
        return formal_add(*(formal_scale(formal_product(matrix[row][j],
                                    determinant(row+1, mask | (1 << j))), (-1)**i)
                            for i, j in enumerate(columns) if matrix[row][j]))

    require(determinant(0, 0) == {(1, 1, 3, 2): -6},
            'The limiting implicit-function Jacobian has a different determinant.')


def constants():
    radial = prove()
    c = radial['cos_phase']
    cp, sp = sqrt_interval((1+c)/2, bits=180), sqrt_interval((1-c)/2, bits=180)
    ct, st = -cube_root(A*R*cp/D), -cube_root(B*R*sp/D)
    require((ct*ct+st*st).low <= 1 <= (ct*ct+st*st).high,
            'The shoulder direction is inconsistent with the astroid root.')
    x, y = R+A*cp*ct-B*sp*st, A*sp*ct+B*cp*st
    xt, yt = -A*cp*st-B*sp*ct, -A*sp*st+B*cp*ct
    kappa = (x*yt-y*xt)/(x*x+y*y)
    a = D*ct*st
    b = 50225*sp*st-18375*cp*ct
    require(a.low > 0 and b.high < 0 and kappa.low > 0,
            'A limiting coefficient has an unresolved sign.')
    spacing = 2*PI/kappa
    coefficient = -a*spacing*spacing/b
    normalized = coefficient/PI
    correction = -2*coefficient/kappa
    require(Q(20284022161534, 10**12) < normalized.low < normalized.high < Q(20284022161536, 10**12),
            'The asymptotic phase coefficient leaves its stated bracket.')
    require(Q(-75180367462928, 10**12) < (correction/PI).low
            <= (correction/PI).high < Q(-75180367462925, 10**12),
            'The first phase correction leaves its stated bracket.')
    jacobian_identity()
    return {'schema': 'aldebaran-fold-shoulder-v1',
            'scope': 'At least three distinct visits for every sufficiently large positive integer d; no numerical cutoff or fourth-visit exclusion.',
            'phase_over_pi': radial['phase_over_pi'], 'cos_theta': ct, 'sin_theta': st,
            'radial_cubic_a': a, 'radial_mixed_b': b, 'angular_derivative_kappa': kappa,
            'limiting_theta_spacing': spacing, 'phase_coefficient': coefficient,
            'phase_coefficient_over_pi': normalized,
            'phase_correction': correction, 'phase_correction_over_pi': correction/PI,
            'limiting_jacobian': '-6 a b s^3 kappa^2; strictly positive',
            'law': 'phi_d = phi_star + C/d^2 - 2C/(kappa*d^3) + O(d^-4)',
            'numerical_fold_cutoff': None, 'ordinary_triple_asserted': False,
            'fourth_visit_excluded': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save the fresh exact coefficient bounds.')
    args = parser.parse_args()
    record = constants()
    if args.write:
        path = HERE/'fold_shoulder.json'
        temporary = path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(serialize(record), indent=2)+'\n')
        temporary.replace(path)
    print('a>0, b<0, kappa>0; the limiting Jacobian equals -6 a b s³ kappa² and is nonzero.')
    print('20.284022161534 < C/pi < 20.284022161536.')
    print('The next coefficient is -2C/kappa; divided by pi it lies in (-75.180367462928, -75.180367462925).')
    print('The analytic branch gives at least three visits for all sufficiently large integer folds.')
    print('No numerical cutoff, ordinary sign, or fourth-visit exclusion is asserted.')


if __name__ == '__main__':
    main()
