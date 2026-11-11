"""Four cubic-intercept parabolas: unique maximin on any positive endpoints.

Global gap-coordinate polynomial signs and factored positive supports
extend cubic_maximin.md beyond [1,3]. All acceptance arithmetic is exact.
Only the standard library; see cubic_four_general.md.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path

from arm_detour_lens import bernstein
from blend_cusps import Interval as I, add, product, require, trim
from cubic_maximin import diff, plus, scaled, serialize, optimum as fixed_optimum
from cubic_five import face_area
from shifted_maximin import check_arrangement, run_area

HERE = Path(__file__).resolve().parent


def constant(c):
    return {(0, 0, 0, 0): Q(c)} if c else {}


def multiply(*polys):
    out = constant(1)
    for p in polys:
        result = {}
        for key, c in out.items():
            for other, d in p.items():
                new = tuple(a+b for a, b in zip(key, other))
                result[new] = result.get(new, Q(0))+c*d
        out = {key: c for key, c in result.items() if c}
    return out


def triangle_polynomial(a, p, b):
    s = plus(a, p, b)
    return scaled(multiply(plus(p, scaled(a, -1)), plus(b, scaled(p, -1)),
                           plus(b, scaled(a, -1)), s, s), Q(1, 18))


def global_certificate():
    variables = [{tuple(int(i == j) for j in range(4)): Q(1)} for i in range(4)]
    a, u, v, w = variables
    x, y, b = plus(a, u), plus(a, u, v), plus(a, u, v, w)
    C = plus(triangle_polynomial(a, x, b), scaled(triangle_polynomial(a, x, y), -1))
    # Hold a,b fixed: changing x raises u and lowers v; changing y raises
    # v and lowers w. Differentiate before any endpoint specialization.
    dx = lambda p: plus(diff(p, 1), scaled(diff(p, 2), -1))
    dy = lambda p: plus(diff(p, 2), scaled(diff(p, 3), -1))
    cx, cy = dx(C), dy(C)
    A = plus(multiply(cx, cx), scaled(multiply(C, dx(cx)), -1))
    B = plus(multiply(cy, cy), scaled(multiply(C, dy(cy)), -1))
    E = plus(multiply(cx, cy), scaled(multiply(C, dy(cx)), -1))
    D = plus(multiply(A, B), scaled(multiply(E, E), -1))
    require(all(c > 0 for c in C.values()), 'The quadrilateral polynomial lost positivity.')
    records = []
    for name, p, degree, terms in (('negative_log_hessian_xx_numerator', A, 8, 80),
                                    ('log_hessian_determinant_numerator', D, 16, 431)):
        require(len(p) == terms and all(sum(key) == degree and c > 0 for key, c in p.items()),
                'A global endpoint-independent concavity certificate failed.')
        records.append({'polynomial': name, 'degree': degree, 'positive_terms': terms,
                        'coefficients': [{'powers_a_u_v_w': key, 'coefficient': c}
                                         for key, c in sorted(p.items())]})
    return records


class RationalPolynomial:
    """Univariate rational functions for exact continuous support identities."""
    def __init__(self, numerator, denominator=(Q(1),)):
        self.numerator, self.denominator = trim(numerator), trim(denominator)
        require(self.denominator != (0,), 'A rational function has zero denominator.')

    @staticmethod
    def wrap(a):
        return a if isinstance(a, RationalPolynomial) else RationalPolynomial((Q(a),))

    def __add__(self, other):
        other = self.wrap(other)
        return RationalPolynomial(add(product(self.numerator, other.denominator),
                                      product(other.numerator, self.denominator)),
                                  product(self.denominator, other.denominator))

    __radd__ = __add__

    def __neg__(self):
        return RationalPolynomial(tuple(-a for a in self.numerator), self.denominator)

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        return RationalPolynomial(product(self.numerator, other.numerator), product(self.denominator, other.denominator))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.wrap(other)
        return RationalPolynomial(product(self.numerator, other.denominator), product(self.denominator, other.numerator))

    def __rtruediv__(self, other):
        return self.wrap(other)/self


def support_identities():
    u = RationalPolynomial((Q(0), Q(1)))
    y = 9*u/(8*u+1)
    q = u*(13-8*u-32*u*u)/((4*u-1)*(8*u+1))
    A = u*(y-u)*y*(q-1+u+y)*(q-1+u+y)/18
    B = (y-u)*(1-y)*(1-u)*(q+u+y)*(q+u+y)/18
    F = u*(1-u)*(q+u)*(q+u)/18
    require((A-B).numerator == (0,) and (F-2*A).numerator == (0,),
            'The normalized candidate does not have three equal areas.')
    gA = (1/u-1/(y-u)+2/(q-1+u+y), 1/(y-u)+1/y+2/(q-1+u+y))
    gB = (-1/(y-u)-1/(1-u)+2/(q+u+y), 1/(y-u)-1/(1-y)+2/(q+u+y))
    gC = (2*(1/u-1/(1-u)+2/(q+u))-gA[0], -gA[1])
    weights = ((64*u*u-32*u+19)*(160*u*u-32*u+7),
               -2*(7168*u*u*u*u-6400*u*u*u+2208*u*u-496*u+31),
               (32*u*u-16*u+5)*(512*u*u-16*u+17))
    for j in (0, 1):
        require((weights[0]*gA[j]+weights[1]*gC[j]+weights[2]*gB[j]).numerator == (0,),
                'A continuous positive-weight support identity failed.')
    for a, b, c in ((64, -32, 19), (160, -32, 7), (32, -16, 5), (512, -16, 17)):
        require(a > 0 and b*b-4*a*c < 0, 'A support quadratic is not everywhere positive.')
    coefficients = bernstein((31, -496, 2208, -6400, 7168), Q(1, 4), Q(2, 5))
    require(coefficients == (Q(-27), Q(-162, 5), Q(-936, 25), Q(-5184, 125), Q(-25137, 625)),
            'The middle support weight lost its strict Bernstein sign proof.')
    return coefficients


def optimum(left, right, bits=96):
    require(type(left) is Q and type(right) is Q and 0 < left < right
            and type(bits) is int and bits >= 16,
            'Use ordered positive rational endpoints and integer precision of at least 16 bits.')
    L = right-left
    q = 1+3*left/L
    P = lambda u: 32*u**3+(32*q+8)*u*u-(4*q+13)*u-q
    lo, hi = Q(1, 4), Q(2, 5)
    require(P(lo) == Q(-9, 4) and P(hi) == (315*q-234)/125 > 0,
            'The universal normalized root bracket changed.')
    while hi-lo > Q(1, 1 << bits):
        mid = (lo+hi)/2
        if P(mid) == 0:
            lo = hi = mid
        elif P(mid) < 0:
            lo = mid
        else:
            hi = mid
    require(P(lo) <= 0 <= P(hi), 'The general cubic root bracket has invalid signs.')
    u = I(lo, hi)
    yy = I(9*lo/(8*lo+1), 9*hi/(8*hi+1))
    nodes = [I.wrap(left), left+L*u, left+L*yy, I.wrap(right)]
    S = L**5*u*(1-u)*(q+u)*(q+u)/36
    areas = [face_area(nodes, i, j) for i, j in ((1, 1), (1, 2), (2, 2))]
    require(max([S.low]+[a.low for a in areas]) <= min([S.high]+[a.high for a in areas]),
            'The general candidate face enclosures do not overlap at a common area.')
    return {'endpoints': (left, right), 'q': q, 'normalized_root': (lo, hi),
            'nodes': [(a.low, a.high) for a in nodes], 'smallest_area': (S.low, S.high)}


def controls():
    rows = []
    for left, right in ((Q(1), Q(3)), (Q(1, 1000), Q(1)), (Q(1), Q(1000)),
                         (Q(10), Q(11)), (Q(100), Q(101)), (Q(1), Q(1)+Q(1, 2**120))):
        row = optimum(left, right)
        nodes = [sum(box)/2 for box in row['nodes']]
        points = [(p, p*p*p/3) for p in nodes]
        check_arrangement(points, lambda a, b: (2*a, 2*b))
        boxes = [I(a, b) for a, b in row['nodes']]
        for i, j in ((1, 1), (1, 2), (2, 2)):
            area = run_area(points, i, j)[0]
            enclosure = face_area(boxes, i, j)
            require(enclosure.low <= area <= enclosure.high, 'A rational full face escapes its general enclosure.')
        rows.append(row)
    fixed = fixed_optimum()
    require(all(max(a[0], b[0]) <= min(a[1], b[1]) for a, b in zip(rows[0]['nodes'], fixed['nodes']))
            and max(rows[0]['smallest_area'][0], fixed['smallest_area'][0])
            <= min(rows[0]['smallest_area'][1], fixed['smallest_area'][1]),
            'The general theorem disagrees with the independent fixed-endpoint certificate.')
    invalid = 0
    for a, b, bits in ((Q(0), Q(1), 96), (Q(2), Q(1), 96), (1, Q(3), 96), (Q(1), Q(3), True)):
        try:
            optimum(a, b, bits)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid general placement was accepted.')
    return rows, invalid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Archive the global polynomial signs and selected rational root enclosures.')
    args = parser.parse_args()
    coefficients = global_certificate()
    weights = support_identities()
    rows, invalid = controls()
    if args.write:
        data = {'scope': 'Unique four-curve cubic maximin on every fixed positive endpoint pair.',
                'gap_coordinate_concavity': coefficients, 'negative_middle_quartic_bernstein': weights, 'examples': rows}
        (HERE/'cubic_four_general.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    print('Global proof: 80 + 431 positive gap-coordinate coefficients; exact equal-area and support identities.')
    print(f'{len(rows)} complete rational arrangements, 18 enclosed faces, {invalid} invalid controls; independent [1,3] agreement.')
    print('The unique normalized root solves 32u^3+(32q+8)u^2-(4q+13)u-q=0, q=1+3a/(b-a).')


if __name__ == '__main__':
    main()
