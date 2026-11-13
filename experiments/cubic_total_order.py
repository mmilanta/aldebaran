"""At the four-curve cubic total optimum, C > A+B and A > B.

These strict inequalities hold on every positive endpoint span. Two
cleared polynomial identities, reduced by the exact midpoint equation,
prove them without numerical signs. A second scalar root construction
checks the earlier shooting optimizer, including a span of 2^-120.
Standard library only; see cubic_total_order.md.
"""

from fractions import Fraction as Q

from blend_cusps import Interval as I, require
from cubic_frontier_bounds import multiply
from cubic_maximin import plus, scaled
from shifted_maximin import check_arrangement, run_area
from shifted_placement import partition


def power(p, n):
    out = {(0, 0, 0): Q(1)}
    for _ in range(n):
        out = multiply(out, p)
    return out


def reduce_span(p, numerator, denominator):
    """Clear D^k and substitute l^2=N/D, retaining the parity of l."""
    degree = max(key[2]//2 for key in p)
    powers_n = [power(numerator, n) for n in range(degree+1)]
    powers_d = [power(denominator, n) for n in range(degree+1)]
    terms = []
    for (i, j, k), coefficient in p.items():
        quotient, parity = divmod(k, 2)
        terms.append(multiply({(i, j, parity): coefficient},
                              powers_n[quotient], powers_d[degree-quotient]))
    return plus(*terms)


def certificate():
    c, h, l = [{tuple(int(i == j) for j in range(3)): Q(1)} for i in range(3)]
    n, k = plus(scaled(c, 3), h), plus(scaled(c, 9), scaled(h, 10))
    D = plus(scaled(power(c, 2), 72), scaled(multiply(c, h), 195), scaled(power(h, 2), 106))
    N = multiply(h, plus(scaled(power(c, 3), 243), scaled(multiply(power(c, 2), h), 702),
                         scaled(multiply(c, power(h, 2)), 660), scaled(power(h, 3), 200)))
    # Original labels multiplied by k; d=l*n/k.
    a, b = multiply(k, plus(c, scaled(l, -1))), multiply(k, plus(c, l))
    x = plus(multiply(k, plus(c, h)), scaled(multiply(l, n), -1))
    y = plus(multiply(k, plus(c, h)), multiply(l, n))
    ex = plus(scaled(power(x, 2), 4), scaled(multiply(x, plus(a, y)), -1),
              scaled(power(a, 2), -1), scaled(power(y, 2), -1))
    ey = plus(scaled(power(y, 2), 4), scaled(multiply(y, plus(x, b)), -1),
              scaled(power(x, 2), -1), scaled(power(b, 2), -1))
    require(not plus(ex, scaled(ey, -1)) and plus(ex, ey) == scaled(plus(N, scaled(multiply(power(l, 2), D), -1)), 2),
            'The total stationarity equations miss their midpoint reduction.')

    def area(a, p, b):
        # This is 18*k^5 times the original triangular pocket area.
        return multiply(plus(p, scaled(a, -1)), plus(b, scaled(p, -1)),
                        plus(b, scaled(a, -1)), power(plus(a, p, b), 2))

    A, B = area(a, x, y), area(x, y, b)
    C = plus(area(a, x, b), scaled(A, -1))
    asymmetry = scaled(multiply(power(h, 3), power(n, 3),
                                power(plus(scaled(c, 3), scaled(h, 2)), 2), power(k, 6)), 64)
    quartic = plus(scaled(power(c, 4), 324), scaled(multiply(power(c, 3), h), 1539),
                   scaled(multiply(power(c, 2), power(h, 2)), 2574),
                   scaled(multiply(c, power(h, 3)), 1839), scaled(power(h, 4), 478))
    excess = scaled(multiply(power(h, 2), l, power(n, 3), quartic, power(k, 4)), 128)
    for name, lhs, rhs in (
        ('A-B', plus(A, scaled(B, -1)), asymmetry),
        ('C-A-B', plus(C, scaled(A, -1), scaled(B, -1)), excess)):
        require(all(value > 0 for value in rhs.values()), 'A factored numerator lost positivity.')
        cleared = plus(multiply(lhs, power(D, 2)), scaled(rhs, -1))
        require(not reduce_span(cleared, N, D), 'A universal area-order identity failed: '+name)
    return len(asymmetry), len(excess)


def ipower(interval, n):
    result = I.wrap(1)
    for _ in range(n):
        result *= interval
    return result


def optimum(left, right, bits=96):
    require(type(left) is Q and type(right) is Q and 0 < left < right
            and type(bits) is int and 16 <= bits <= 512,
            'Use positive ordered rational endpoints and 16 through 512 integer bits.')
    c, l = (left+right)/2, (right-left)/2
    tau = l/c
    P = lambda v: 200*v**4+660*v**3+(702-106*tau*tau)*v*v+(243-195*tau*tau)*v-72*tau*tau
    lo, hi = tau*tau/4, tau*tau/3
    require(P(lo) < 0 < P(hi), 'The relative midpoint root bracket failed.')
    while hi-lo > tau*tau*Q(1, 1 << bits):
        middle = (lo+hi)/2
        value = P(middle)
        if value == 0:
            lo = hi = middle
        elif value < 0:
            lo = middle
        else:
            hi = middle
    require(P(lo) <= 0 <= P(hi), 'The midpoint root enclosure has incorrect signs.')
    v = I(lo, hi)
    h, d = c*v, l*(3+v)/(9+10*v)
    nodes = [I.wrap(left), c+h-d, c+h+d, I.wrap(right)]
    require(all(a.high < b.low for a, b in zip(nodes, nodes[1:])), 'The total nodes are not strictly ordered.')
    D = 72*c*c+195*c*h+106*h*h
    asymmetry = 32*ipower(h, 3)*ipower(3*c+h, 3)*ipower(3*c+2*h, 2)*(9*c+10*h)/(9*D*D)
    quartic = 324*c**4+1539*c**3*h+2574*c*c*h*h+1839*c*ipower(h, 3)+478*ipower(h, 4)
    excess = 64*h*h*l*ipower(3*c+h, 3)*quartic/(9*(9*c+10*h)*D*D)
    require(asymmetry.low > 0 and excess.low > 0, 'A strict total-order enclosure includes zero.')
    return {'nodes': [(v.low, v.high) for v in nodes], 'A_minus_B': (asymmetry.low, asymmetry.high),
            'C_minus_A_minus_B': (excess.low, excess.high), 'normalized_midpoint_shift': (lo, hi)}


def controls():
    rows = []
    for a, b in ((Q(1), Q(3)), (Q(3), Q(4)), (Q(1, 1000), Q(1)),
                 (Q(1), Q(1000)), (Q(100), Q(101)), (Q(1), Q(1)+Q(1, 1 << 120))):
        row = optimum(a, b)
        earlier = partition(3, a, b)
        require(all(max(p[0], q[0]) <= min(p[1], q[1]) for p, q in zip(row['nodes'], earlier['nodes'])),
                'The midpoint and shooting constructions disagree.')
        nodes = [sum(box)/2 for box in row['nodes']]
        points = [(p, p**3/3) for p in nodes]
        check_arrangement(points, lambda a, b: (2*a, 2*b))
        A, C, B = [run_area(points, i, j)[0] for i, j in ((1, 1), (1, 2), (2, 2))]
        # Evaluate the factor identities at the exact optimum, not at these
        # rational midpoint controls: the latter need not retain a tiny sign.
        require(A > 0 and C > 0 and B > 0, 'A full clipped control face has nonpositive area.')
        rows.append(row)
    invalid = 0
    for a, b, bits in ((Q(0), Q(1), 96), (Q(3), Q(2), 96), (1, Q(3), 96),
                        (Q(1), Q(3), True), (Q(1), Q(3), 513)):
        try:
            optimum(a, b, bits)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid midpoint query was accepted.')
    return rows, invalid


def main():
    terms = certificate()
    rows, invalid = controls()
    print('Two exact positive area-order identities on every positive endpoint span.')
    print('Cleared positive numerators:', terms, 'terms; midpoint stationarity identities agree.')
    print(f'{len(rows)} independent shooting comparisons and clipped arrangements; 18 full faces; {invalid} rejected controls.')
    print('At the unique largest-total placement: C > A+B and A > B.')
    print('The midpoint root uses a relative tolerance even for a span of 2^-120.')


if __name__ == '__main__':
    main()
