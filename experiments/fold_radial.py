"""A fold-independent interval with no triple or higher meeting.

Run: python3 experiments/fold_radial.py [--write]
Standard library only. Exact polynomial isolation and radial-critical
counts support the elementary argument in fold_radial.md. No sampled
curve crossing count enters this calculation.
"""

import argparse
from fractions import Fraction as Q
import json
from math import gcd, lcm

from blend_cusps import (Interval as I, add, bound, derivative, isolate_roots,
                        product, require, scale, sturm_sequence, value)
from fold_contacts import HERE, PI, angle, round_interval, serialize
from phase_unfolding import sqrt_interval

A, B, R = 205, 75, 245
D = A*A-B*B


def threshold_polynomial():
    """The unit astroid, with squared coordinates affine in cos(phi)."""
    alpha, beta = Q(R*A, D)**2, Q(R*B, D)**2
    x2, y2 = (alpha/2, alpha/2), (beta/2, -beta/2)
    total = add(add(x2, y2), (-1,))
    polynomial = add(product(product(total, total), total), scale(product(x2, y2), 27))
    denominator = lcm(*(c.denominator for c in polynomial))
    integer = tuple(int(c*denominator) for c in polynomial)
    common = gcd(*integer)
    return tuple(c//common for c in integer)


def critical_polynomial(p):
    """Radius derivative in t=tan(theta/2), for psi=2 atan(p).

    The ellipse is (R cos(psi)+A cos(theta),
                    -R sin(psi)+B sin(theta)).
    Multiplication by (1+t^2)^2 removes only a positive denominator.
    """
    x, y = R*(1-p*p)/(1+p*p), -2*R*p/(1+p*p)
    return (B*y, -2*A*x-2*D, Q(0), -2*A*x+2*D, -B*y)


def real_root_count(polynomial):
    sequence = sturm_sequence(polynomial)

    def infinity_variations(positive):
        signs = [(1 if p[-1] > 0 else -1)*(1 if positive or len(p) % 2 else -1)
                 for p in sequence]
        return sum(a != b for a, b in zip(signs, signs[1:]))

    return infinity_variations(False)-infinity_variations(True)


def radius_polynomial(p, radius):
    """Exact circle/ellipse equation, again in tan(theta/2)."""
    x0, y0 = R*(1-p*p)/(1+p*p), -2*R*p/(1+p*p)
    x, y = (x0+A, 0, x0-A), (y0, 2*B, y0)
    return add(add(product(x, x), product(y, y)),
               scale(product((1, 0, 1), (1, 0, 1)), -radius*radius))


def prove():
    polynomial = threshold_polynomial()
    require(polynomial == (265240041066937, 1261235890824, -252094190659584, 45392319784448),
            'The radial threshold polynomial changed.')
    roots = isolate_roots(polynomial, bits=180)
    require(len(roots) == 1, 'More than one radial transition occurs on the half-turn.')
    lo, hi = roots[0]
    cosine = I(lo, hi)
    require(-1 < lo < hi < 0 and value(polynomial, lo) < 0 < value(polynomial, hi),
            'The threshold is not a simple interior crossing.')
    # Gcd/Sturm isolation already proves simplicity. This independent local
    # sign also fixes the direction in which the radial shape changes.
    require(bound(derivative(polynomial), cosine).low > 0,
            'The threshold polynomial is not increasing at its root.')
    sine = sqrt_interval(1-cosine*cosine, bits=180)
    chart = -cosine/(1+sine)
    phase = angle(1, chart)/PI
    require(Q(894940827171, 10**12) < phase.low < phase.high < Q(894940827172, 10**12),
            'The threshold phase leaves the stated decimal bracket.')
    counts = []
    for p, expected in ((Q(1, 2), 2), (Q(9, 10), 4)):
        count = real_root_count(critical_polynomial(p))
        require(count == expected, 'An independent radial critical-point count differs.')
        counts.append({'half_phase_chart': p, 'simple_radial_critical_points': count})
    examples = []
    for p, expected in ((Q(4, 5), 2), (Q(19, 20), 4)):
        polynomial_at_radius = radius_polynomial(p, Q(321))
        require(polynomial_at_radius[-1] != 0, 'An illustrated intersection meets the missing chart point.')
        require(real_root_count(polynomial_at_radius) == expected,
                'An illustrated circle has a different number of ellipse intersections.')
        examples.append({'half_phase_chart': p, 'radius': 321,
                         'ellipse_points': expected})
    # At zero phase r^2 is strictly increasing as a function of cos(theta).
    require(100450-72800 > 0, 'The zero-phase radius is not unimodal.')
    # At pi, sin(theta)=-735/1456 supplies two extra critical points.
    require(Q(-36750, 72800) == Q(-735, 1456) and -1 < Q(-735, 1456) < 1,
            'The half-turn endpoint does not have four radial critical points.')
    return {'schema': 'aldebaran-fold-radial-v1',
            'scope': 'All positive integer d, lengths 245/140/65: no triple or higher meeting for 0<=phi<=phi_star.',
            'threshold_polynomial_in_cos_phase': polynomial,
            'cos_phase': round_interval(cosine),
            'phase_quarter': 1, 'phase_chart': round_interval(chart),
            'phase_over_pi': round_interval(phase, 20),
            'radial_critical_counts': counts,
            'circle_examples': examples,
            'before_and_at_threshold_maximum_visits': 2,
            'after_threshold_maximum_radial_preimages': 4,
            'after_threshold_maximum_visits': 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save the fresh rational bounds.')
    args = parser.parse_args()
    record = prove()
    if args.write:
        path = HERE/'fold_radial.json'
        temporary = path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(serialize(record), indent=2)+'\n')
        temporary.replace(path)
    print('Exactly one radial transition on the phase half-turn.')
    print('0.894940827171 < phi_star/pi < 0.894940827172.')
    print('Every positive fold count has at most two visits per point through phi_star; hence no triples there.')
    print('Beyond phi_star, four radial preimages are possible; this does not assert four visits to one point.')


if __name__ == '__main__':
    main()
