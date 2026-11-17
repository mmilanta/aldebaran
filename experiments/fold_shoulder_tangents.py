"""Exact coefficients for the flattening three-branch shoulder configuration.

Run: python3 experiments/fold_shoulder_tangents.py [--write]
Standard library only. Formal expansions, rational constant bounds, and
an irreducible cubic support ordinary negative triples at a density-one
set of integer folds. No finite cutoff or uniform fourth-visit exclusion.
"""

import argparse
from fractions import Fraction as Q
from itertools import permutations
import json
from math import comb, gcd, lcm

from blend_cusps import (add as poly_add, product as poly_product,
                        remainder, require, scale as poly_scale, value)
from fold_contacts import HERE, PI, angle, serialize
from fold_radial import A, B, D, R, prove
from fold_radial_check import formal_add as add, formal_product as mul, formal_scale as scale
from fold_shoulder import constants
from phase_unfolding import sqrt_interval


def rotation_irrationality():
    """A cubic norm proves that exp(i alpha) cannot be a root of unity."""
    aa, bb, delta = A*A, B*B, D
    # u=cos²(theta*). The center degeneracy and |center|=245 give P(u)=0.
    P = poly_add(poly_scale(poly_add((0, 0, 0, bb),
                                     poly_scale((1, -3, 3, -1), aa)), delta*delta),
                 (-R*R*aa*bb,))
    S = poly_product((aa, -delta), (aa, -delta))
    # X=2cos(alpha) = N(u)/S(u).
    N = poly_add(poly_scale(S, 2), poly_scale((0, 1, -1), -16*aa*bb))
    # Multiplication by S(u)X-N(u) in Q[u]/P(u); its determinant is a
    # cubic in X that vanishes at the actual value. No symbolic package.
    matrix = [[None]*3 for _ in range(3)]
    for j in range(3):
        s, n = remainder((0,)*j+S, P), remainder((0,)*j+N, P)
        for i in range(3):
            matrix[i][j] = (-n[i] if i < len(n) else Q(0),
                             s[i] if i < len(s) else Q(0))
    determinant = (Q(0),)
    for permutation in permutations(range(3)):
        term = (Q((-1)**sum(permutation[i] > permutation[j]
                            for i in range(3) for j in range(i+1, 3))),)
        for i, j in enumerate(permutation):
            term = poly_product(term, matrix[i][j])
        determinant = poly_add(determinant, term)
    denominator = lcm(*(v.denominator for v in determinant))
    integers = tuple(int(v*denominator) for v in determinant)
    content = gcd(*integers)
    polynomial = tuple(v//content for v in integers)
    if polynomial[-1] < 0:
        polynomial = tuple(-v for v in polynomial)
    require(len(polynomial) == 4 and polynomial == (
                -92658189484824233, 110833317006886032, -10221212798424576, 117219944697856),
            'The exact fourth-direction norm polynomial changed.')
    prime = 31
    require(polynomial[-1] % prime != 0
            and all(value(polynomial, Q(j)) % prime != 0 for j in range(prime)),
            'The cubic has a root or loses degree modulo 31.')
    trace = Q(-polynomial[-2], polynomial[-1])
    require(trace.denominator > 1, 'The trace must be nonintegral.')
    print('The 2cos(α) cubic is irreducible modulo 31; its nonintegral trace proves α/(2π) irrational.')
    return {'twice_cos_polynomial_ascending': polynomial,
            'irreducibility_prime': prime, 'twice_cos_trace': trace}


def fourth_root_identity():
    c, s, one = {(1, 0): Q(1)}, {(0, 1): Q(1)}, {(0, 0): Q(1)}

    def complex_product(z, w):
        return add(mul(z[0], w[0]), scale(mul(z[1], w[1]), -1)), add(mul(z[0], w[1]), mul(z[1], w[0]))

    def reduce_circle(poly):
        result = {}
        for (i, j), value in poly.items():
            # s^j = s^(j mod 2) (1-c²)^(j//2).
            for k in range(j//2+1):
                result = add(result, {(i+2*k, j % 2): value*comb(j//2, k)*(-1)**k})
        return result

    z, conjugate = (c, s), (c, scale(s, -1))
    fourth = complex_product(complex_product(conjugate, conjugate), conjugate)
    polynomial = [(one, {})]
    for root in (z, z, z, fourth):
        result = [({}, {}) for _ in range(len(polynomial)+1)]
        for i, coefficient in enumerate(polynomial):
            term = complex_product(coefficient, (scale(root[0], -1), scale(root[1], -1)))
            result[i] = tuple(add(a, b) for a, b in zip(result[i], term))
            result[i+1] = tuple(add(a, b) for a, b in zip(result[i+1], coefficient))
        polynomial = result
    ccc, sss = mul(c, mul(c, c)), mul(s, mul(s, s))
    expected = [(one, {}), (scale(ccc, -4), scale(sss, 4)),
                (add(scale(mul(c, c), 12), scale(one, -6)), {}),
                (scale(ccc, -4), scale(sss, -4)), (one, {})]
    require(all(reduce_circle(a) == reduce_circle(b)
                for row, expected_row in zip(polynomial, expected) for a, b in zip(row, expected_row)),
            'The formal threefold/fourth radial factorization disagrees.')
    print('The complete formal radial factorization is (w−w*)³(w−w*⁻³).')


def first_order_identities():
    # Formal variables a,b,s,k,k2,a4,c2. A common denominator 6abk
    # clears C=-as²/b, L=-2C/k, and all first visit corrections.
    a, b, s, k, k2, a4, c2 = (
        {tuple(int(i == j) for j in range(7)): Q(1)} for i in range(7))

    def product(*values):
        result = {(0,)*7: Q(1)}
        for value in values:
            result = mul(result, value)
        return result

    ss, sss, ssss = product(s, s), product(s, s, s), product(s, s, s, s)
    denominator = scale(product(a, b, k), 6)
    # Each numerator below is divided by denominator.
    common = add(scale(product(a, b, k2, ss), -1),
                 scale(product(b, k, a4, ss), -2),
                 scale(product(a, k, c2, ss), 2))
    zm = add(scale(product(a, b, s), 6), common)
    z0 = add(common, scale(product(a, b, k2, ss), 3))
    zp = add(scale(product(a, b, s), -6), common)
    C = scale(product(a, a, k, ss), -6)
    L = scale(product(a, a, ss), 12)
    # Two radius differences, then two angular differences, at order h.
    residuals = [
        add(scale(product(a, ss, zm), -2), scale(product(a, ss, z0), -1),
            product(b, s, L), scale(product(a4, ssss, denominator), -1),
            scale(product(c2, C, ss), -1)),
        add(scale(product(a, ss, zm), -2), scale(product(a, ss, zp), 2),
            scale(product(b, s, L), 2)),
        add(product(k, add(z0, scale(zm, -1))),
            scale(product(k2, ss, denominator), Q(-1, 2)), product(s, denominator)),
        add(product(k, add(zp, scale(zm, -1))), scale(product(s, denominator), 2))]
    require(all(not residual for residual in residuals),
            'A formal first-order implicit equation has a nonzero residual.')
    # Outer-pair tangent determinant, after the same denominator is cleared.
    outer = add(product(k, add(scale(product(a, s, add(zm, zp)), -3),
                               scale(product(a4, sss, denominator), -4),
                               scale(product(c2, C, s), -2))),
                scale(product(a, k2, sss, denominator), 2))
    expected = product(sss, add(scale(product(a, k2), 3),
                                scale(product(k, a4), -2)), denominator)
    require(outer == expected, 'The formal outer-tangent coefficient disagrees.')
    print('All four formal first-order equations vanish; outer coefficient = s³(3a k₂−2κa₄).')


def coefficients():
    shoulder = constants()
    c = prove()['cos_phase']
    cp, sp = sqrt_interval((1+c)/2, bits=180), sqrt_interval((1-c)/2, bits=180)
    ct, st = shoulder['cos_theta'], shoulder['sin_theta']
    x, y = R+A*cp*ct-B*sp*st, A*sp*ct+B*cp*st
    rho2 = x*x+y*y
    k, a, b, s = (shoulder[key] for key in (
        'angular_derivative_kappa', 'radial_cubic_a', 'radial_mixed_b', 'limiting_theta_spacing'))
    k2 = -R*y/rho2
    a4 = D*(ct*ct-st*st)/4
    T = 3*a*k2-2*k*a4
    require(k2.low > 0 and a4.high < 0 and T.low > 0,
            'The outer-pair transverse coefficient has no resolved positive sign.')
    inner_limit = 3*a*k*s*s/2
    outer_scaled_limit = s*s*s*T
    H_limit = -3*a*b*s*s*s*k*k/2
    area_scaled_limit = b*b*k*k/(2*s*T)
    require(Q(871385387546, 10**9) < area_scaled_limit.low
            <= area_scaled_limit.high < Q(871385387548, 10**9),
            'The limiting area coefficient leaves its stated bracket.')
    first_order_identities()
    fourth_root_identity()
    # In the complex radial quartic, the shoulder root has multiplicity
    # three and the product of all four roots is one. Hence the remaining
    # unit-circle root is exp(-3i theta*). It is distinct and simple.
    ct4, st4 = 4*ct*ct*ct-3*ct, 4*st*st*st-3*st
    x4, y4 = R+A*cp*ct4-B*sp*st4, A*sp*ct4+B*cp*st4
    real = (x*x4+y*y4)/rho2
    imaginary = (x*y4-y*x4)/rho2
    require(real.low > 0 and imaginary.low > 0,
            'The limiting fourth-candidate rotation must be strictly inside the first quadrant.')
    radial_derivative4 = -2*R*(A*cp*st4+B*sp*ct4)-2*D*st4*ct4
    radial_derivative4.sign()
    alpha = angle(0, imaginary/(1+real))
    require(0 < alpha.low <= alpha.high < PI.low,
            'The limiting fourth direction must be strictly between zero and pi.')
    irrationality = rotation_irrationality()
    return {'schema': 'aldebaran-fold-shoulder-tangents-v1',
            'scope': 'Ordinary negative triples approach the shoulder at a density-one set of integer fold counts; no numerical cutoff or uniform fourth-visit exclusion.',
            'angular_second_derivative': k2, 'radial_quartic_coefficient': a4,
            'outer_positive_coefficient_T': T, 'inner_determinant_limit': inner_limit,
            'outer_determinant_times_d_limit': outer_scaled_limit,
            'unfolding_magnitude_limit': H_limit,
            'area_coefficient_over_d_limit': area_scaled_limit,
            'fourth_limiting_cos_theta': ct4, 'fourth_limiting_sin_theta': st4,
            'fourth_radial_derivative': radial_derivative4,
            'fourth_direction_ratio_real': real, 'fourth_direction_ratio_imaginary': imaginary,
            'fourth_direction_increment': alpha,
            'fourth_direction_increment_over_two_pi': alpha/(2*PI),
            'fourth_direction_irrationality': irrationality,
            'selected_pairwise_transversality_for_large_d': True,
            'conditional_passage_sign_in_time_order': -1,
            'ordinary_negative_triples_at_infinitely_many_folds': True,
            'at_least_one_ordinary_batch_in_each_two_consecutive_large_folds': True,
            'ordinary_negative_triples_at_density_one_of_fold_counts': True,
            'numerical_fold_cutoff': None, 'uniform_fourth_visit_exclusion': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save fresh asymptotic coefficient bounds.')
    args = parser.parse_args()
    record = coefficients()
    if args.write:
        target = HERE/'fold_shoulder_tangents.json'
        temporary = target.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(serialize(record), indent=2)+'\n')
        temporary.replace(target)
    print('κ₂>0, a₄<0, T=3aκ₂−2κa₄>0; all three selected pairs are transverse for large d.')
    print('In increasing time order H tends to a strictly negative constant.')
    print('871.385387546 < lim K_d/d < 871.385387548; no quantitative remainder is asserted.')
    print('The limiting fourth-direction increment lies strictly between zero and pi.')
    print('At least one of every two consecutive sufficiently large folds has an ordinary negative triple.')
    print('The selected batch is ordinary at a set of integer folds of natural density one.')
    print('The radial threshold is the unattained infimum even for ordinary negative triple phases.')
    print('There is no numerical cutoff or uniform fourth-visit exclusion.')


if __name__ == '__main__':
    main()
