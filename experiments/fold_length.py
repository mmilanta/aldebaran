"""Certified constants for the length of the finer weave.

Run: python3 experiments/fold_length.py [--numeric]
The uniform length estimate is derived in fold_length.md.
Exact binomial-series tails enclose the two elliptic integrals.
Optional direct three-frequency quadrature is a numerical cross-check.
"""

import argparse
from fractions import Fraction as Q
from math import cos, fsum, pi, sin, sqrt

from blend_cusps import Interval as I, require
from fold_contacts import PI, round_interval

A, B, R = 205, 75, 245


def constants(terms=512):
    require(type(terms) is int and terms >= 1, 'Use a positive binomial-series length.')
    q = Q(A*A-B*B, A*A)
    require(q == Q(1456, 1681) and 0 < q < 1, 'The ellipse modulus changed.')
    c, power = Q(1), Q(1)
    k_sum, e_sum = Q(1), Q(0)
    for n in range(1, terms+1):
        c *= Q(2*n-1, 2*n)
        power *= q
        term = c*c*power
        k_sum += term
        e_sum += term/(2*n-1)
    # c_n <= 1, and 1/(2n-1) <= 1. The positive geometric tail
    # bounds the omitted terms of either series independently.
    tail = q**(terms+1)/(1-q)
    K = PI*I(k_sum, k_sum+tail)/2
    E = PI*I(1-e_sum-tail, 1-e_sum)/2
    require(E.low > 0 and K.low > E.high, 'The elliptic constants lost their signs.')
    return {'perimeter': round_interval(4*A*E, 28),
            'constant_correction': round_interval(4*B*K, 28)}


def length_bounds(d, data):
    require(type(d) is int and d >= 7, 'The uniform upper error bound needs at least seven folds.')
    lead = d*data['perimeter']+data['constant_correction']
    error = PI*450**2/(75*d-450)
    return I(lead.low, lead.high+error.high)


def prove():
    require(R+A == 450 and A > B == 75 > 0, 'The uniform norm bounds changed.')
    data = constants()
    require(all(x.high-x.low < Q(1, 10**25) for x in data.values()),
            'A length constant is wider than 1e-25.')
    # d>=12 gives 75d-450 >= (75/2)d, so the same upper error is
    # bounded by 5400pi/d uniformly over all phases.
    require(Q(2*450**2, 75) == 5400, 'The uniform asymptotic error coefficient changed.')
    return data


def numeric_length(d, phase):
    count = 1024*d
    step = 2*pi/count
    def speed(i):
        t = i*step
        vx = -245*sin(t)-140*(d+1)*sin((d+1)*t)+65*(d-1)*sin(phase-(d-1)*t)
        vy = 245*cos(t)+140*(d+1)*cos((d+1)*t)-65*(d-1)*cos(phase-(d-1)*t)
        return sqrt(vx*vx+vy*vy)
    # Periodic midpoint quadrature, against the original derivative rather
    # than the single-ellipse formula. Not an interval proof of the integral.
    return step*fsum(speed(i+0.5) for i in range(count))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numeric', action='store_true', help='Compare a separate direct-orbit quadrature at twelve settings.')
    args = parser.parse_args()
    data = prove()
    for key, value in data.items():
        print(f'{key}: [{value.low}, {value.high}]')
        print(f'  approximately {float(value.midpoint()):.12f}')
    print('For every d>=7 and every phase: dP+C <= length <= dP+C+pi*450^2/(75d-450).')
    print('For d>=12 the excess is at most 5400pi/d; both constants are phase independent.')
    if args.numeric:
        P, C = [float(data[key].midpoint()) for key in ('perimeter', 'constant_correction')]
        for d in (7, 14, 60, 240):
            bounds = length_bounds(d, data)
            for phase in (0, pi/2, pi):
                length = numeric_length(d, phase)
                require(float(bounds.low)-1e-6 <= length <= float(bounds.high)+1e-6,
                        'The independent numerical length misses its analytic bounds.')
                print(f'd={d:3}, phi/pi={phase/pi:.1f}: length={length:.9f}; d*(length-dP-C)={d*(length-d*P-C):.9f}')
        print('All twelve independent quadratures lie within their analytic bounds (numerical audit).')


if __name__ == '__main__':
    main()
