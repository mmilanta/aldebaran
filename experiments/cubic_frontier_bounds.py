"""A uniform cubic frontier and quantitative area laws on 0 < epsilon <= 1/10.

For positive original endpoints this means 1 < b/a <= 4/3. Rational
Bernstein identities prove a complete two-branch frontier on that range.
Uniform contraction tubes turn Taylor jets into finite error bounds.
No numerical root, external package, or archived coefficient is trusted.
See cubic_frontier_bounds.md. Standard library only.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import json
from math import comb
from pathlib import Path

from blend_cusps import Interval as I, require
from cubic_frontier_limit import quantities, root_jet
from cubic_maximin import diff, plus, scaled, serialize

HERE = Path(__file__).resolve().parent
ORDER = 16
END = Q(1, 10)
RADIUS = Q(100)
SLABS = 16
GAIN = Q(8, 27)
COST = Q(16, 2187)
ROOM = ((Q(1, 7), Q(1, 2)), (Q(1, 2), Q(7, 8)), (Q(0), END))
FIRST = ((Q(1, 3), Q(9, 25)), (Q(2, 3), Q(7, 10)), (Q(0), END))
TIED = ((Q(1, 4), Q(9, 25)), (Q(2, 3), Q(39, 50)), (Q(0), END))


def zero(c):
    return c == 0 or c == I.wrap(0)


class Polynomial:
    """Untruncated univariate polynomials; coefficients may be intervals.

    An interval coefficient encloses its unknown value for each epsilon.
    Repeated occurrences may widen an enclosure, never narrow it unsafely.
    """

    def __init__(self, coefficients):
        c = list(coefficients)
        require(c, 'A polynomial needs at least one coefficient.')
        while len(c) > 1 and zero(c[-1]):
            c.pop()
        self.c = tuple(c)

    @staticmethod
    def wrap(value):
        return value if isinstance(value, Polynomial) else Polynomial((value,))

    def coefficient(self, n):
        return self.c[n] if n < len(self.c) else Q(0)

    def __add__(self, other):
        other = self.wrap(other)
        return Polynomial(tuple(self.coefficient(i)+other.coefficient(i)
                                for i in range(max(len(self.c), len(other.c)))))

    __radd__ = __add__

    def __neg__(self):
        return Polynomial(tuple(-c for c in self.c))

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        result = [Q(0)]*(len(self.c)+len(other.c)-1)
        for i, a in enumerate(self.c):
            if not zero(a):
                for j, b in enumerate(other.c):
                    if not zero(b):
                        result[i+j] += a*b
        return Polynomial(result)

    __rmul__ = __mul__

    def __pow__(self, n):
        require(type(n) is int and n >= 0, 'Use a nonnegative integer power.')
        result = self.wrap(Q(1))
        for _ in range(n):
            result *= self
        return result

    def divide_power(self, n):
        require(type(n) is int and n >= 0 and all(zero(c) for c in self.c[:n]),
                'The asserted exact power of epsilon does not divide this polynomial.')
        return Polynomial(self.c[n:] or (Q(0),))

    def bound(self, interval):
        result = I.wrap(0)
        for coefficient in reversed(self.c):
            result = result*interval+coefficient
        return result


class Derivative:
    """Value and two exact first derivatives, also over interval values."""

    def __init__(self, value, dx=0, dy=0):
        self.value, self.dx, self.dy = value, dx, dy

    @staticmethod
    def wrap(value):
        return value if isinstance(value, Derivative) else Derivative(value)

    def __add__(self, other):
        other = self.wrap(other)
        return Derivative(self.value+other.value, self.dx+other.dx, self.dy+other.dy)

    __radd__ = __add__

    def __neg__(self):
        return Derivative(-self.value, -self.dx, -self.dy)

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        return Derivative(self.value*other.value,
                          self.dx*other.value+self.value*other.dx,
                          self.dy*other.value+self.value*other.dy)

    __rmul__ = __mul__

    def __pow__(self, n):
        require(type(n) is int and n >= 0, 'Use a nonnegative integer power.')
        result = self.wrap(1)
        for _ in range(n):
            result *= self
        return result


def equations(x, y, epsilon, branch):
    require(branch in ('total', 'switch'), 'Choose total or switch.')
    p = quantities(x, y, epsilon)
    return (p['Tx'], p['Ty']) if branch == 'total' else (p['A']-p['B'], p['Ty'])


@lru_cache(maxsize=None)
def root_polynomials(branch):
    inverse = (((Q(-1), Q(-1, 2)), (Q(-1, 2), Q(-1))) if branch == 'total'
               else ((Q(2), Q(1, 2)), (Q(1), Q(-1, 2))))
    x, y, e = Polynomial((Q(1, 3),)), Polynomial((Q(2, 3),)), Polynomial((0, Q(1)))
    for n in range(1, ORDER+1):
        residual = equations(x, y, e, branch)
        corrections = [-sum(inverse[i][j]*residual[j].coefficient(n) for j in (0, 1))
                       for i in (0, 1)]
        x += Polynomial((Q(0),)*n+(corrections[0],))
        y += Polynomial((Q(0),)*n+(corrections[1],))
    residual = equations(x, y, e, branch)
    require(all(zero(p.coefficient(n)) for p in residual for n in range(ORDER+1)),
            'An exact implicit root polynomial has a nonzero low-order residual.')
    old_x, old_y, _ = root_jet(branch)
    require(x.c[:7] == old_x.c and y.c[:7] == old_y.c,
            'The new recurrence disagrees with the earlier sixth-order calculation.')
    return x, y, inverse, tuple(p.divide_power(ORDER+1) for p in residual)


def magnitude(interval):
    return max(abs(interval.low), abs(interval.high))


def outward(interval, bits=64):
    """A small readable rational enclosure, only after exact calculation."""
    denominator = 1 << bits
    low, high = interval.low*denominator, interval.high*denominator
    return (Q(low.numerator//low.denominator, denominator),
            Q(-(-high.numerator//high.denominator), denominator))


def significant(interval, bits=80):
    """Keep relative precision when recording very small nonzero areas."""
    size = magnitude(interval)
    exponent = size.numerator.bit_length()-size.denominator.bit_length() if size else 0
    return outward(interval, max(0, bits-exponent))


def tube(branch, epsilon):
    """Contract in the scaled error u=(root-P(e))/e^17 for every e in a slab."""
    x, y, inverse, residuals = root_polynomials(branch)
    tail = I(-RADIUS, RADIUS)*epsilon.high**(ORDER+1)
    xx, yy = x.bound(epsilon)+tail, y.bound(epsilon)+tail
    derivatives = equations(Derivative(xx, 1, 0), Derivative(yy, 0, 1),
                            Derivative(epsilon), branch)
    jacobian = [(p.dx, p.dy) for p in derivatives]
    defect = [[I.wrap(int(i == j))-sum(inverse[i][k]*jacobian[k][j] for k in (0, 1))
               for j in (0, 1)] for i in (0, 1)]
    rho = max(sum(magnitude(p) for p in row) for row in defect)
    residual = [p.bound(epsilon) for p in residuals]
    eta = max(magnitude(-sum(inverse[i][j]*residual[j] for j in (0, 1)))
              for i in (0, 1))
    require(rho < Q(1, 3) and eta < 20 and eta+rho*RADIUS < RADIUS,
            'A uniform implicit-root contraction failed.')
    return {'branch': branch, 'epsilon': (epsilon.low, epsilon.high),
            'contraction_norm_upper': outward(I(0, rho))[1],
            'center_displacement_upper': outward(I(0, eta))[1]}


@lru_cache(maxsize=None)
def models():
    e = Polynomial((0, Q(1)))
    roots = []
    for branch in ('total', 'switch'):
        x, y, _, _ = root_polynomials(branch)
        tail = Polynomial((Q(0),)*(ORDER+1)+(I(-RADIUS, RADIUS),))
        roots.append((x+tail, y+tail))
    total, switch = [quantities(x, y, e) for x, y in roots]
    gain = (switch['B']-total['B']).divide_power(3)
    cost = (total['T']-switch['T']).divide_power(6)
    gain_error = (gain-GAIN*(1-Q(3, 2)*e)*total['B']).divide_power(2)
    cost_error = (cost-COST*(1-3*e)*total['T']).divide_power(2)
    numerator, denominator = cost*total['B']**2, total['T']*gain**2
    ratio_error = (Q(1, 12)*denominator-numerator).divide_power(2)
    return roots, total, switch, gain, cost, gain_error, cost_error, ratio_error, denominator


def metric_bounds(epsilon):
    roots, total, switch, gain, cost, ge, ce, re, denominator = models()
    b, t = total['B'].bound(epsilon), total['T'].bound(epsilon)
    require(b.low > Q(7, 100) and t.low > 0 and gain.bound(epsilon).low > 0
            and cost.bound(epsilon).low > 0, 'An area or factored gain/cost lost positivity.')
    rg, rc = ge.bound(epsilon)/(GAIN*b), ce.bound(epsilon)/(COST*t)
    theta = re.bound(epsilon)/denominator.bound(epsilon)
    require(Q(-1, 5) < rg.low <= rg.high < Q(1, 5), 'The gain remainder bound failed.')
    require(1 < rc.low <= rc.high < 3, 'The cost remainder bound failed.')
    require(Q(1, 25) < theta.low <= theta.high < Q(1, 20), 'The ratio remainder bound failed.')
    # Remove the vanishing factor before bounding, including at epsilon=0.
    for x, y in roots:
        require((x-Q(1, 3)).divide_power(1).bound(epsilon).low > 0
                and (y-Q(2, 3)).divide_power(1).bound(epsilon).low > 0
                and x.bound(epsilon).high < Q(9, 25)
                and y.bound(epsilon).high < Q(7, 10), 'A root left the first-branch room.')
    displacement = (roots[0][0]-roots[1][0]).divide_power(3).bound(epsilon)
    require(displacement.low > 0, 'The switch does not strictly precede the total optimum.')
    return {'epsilon': (epsilon.low, epsilon.high), 'gain_remainder': outward(rg),
            'cost_remainder': outward(rc), 'ratio_remainder': outward(theta),
            'total_endpoint_B': outward(b), 'switch_x_displacement_over_epsilon_cubed': outward(displacement)}


def multiply(*polynomials):
    out = {(0, 0, 0): Q(1)}
    for p in polynomials:
        new = {}
        for key, a in out.items():
            for other, b in p.items():
                power = tuple(i+j for i, j in zip(key, other))
                new[power] = new.get(power, Q(0))+a*b
        out = {key: c for key, c in new.items() if c}
    return out


def sparse_quantities():
    one = {(0, 0, 0): Q(1)}
    x, y, e = [{tuple(int(i == j) for j in range(3)): Q(1)} for i in range(3)]
    square = lambda p: multiply(p, p)
    A = multiply(x, plus(y, scaled(x, -1)), y,
                 square(plus(one, multiply(e, plus(x, y, scaled(one, -1))))))
    B = multiply(plus(y, scaled(x, -1)), plus(one, scaled(y, -1)),
                 plus(one, scaled(x, -1)), square(plus(one, multiply(e, plus(x, y)))))
    F = lambda z: multiply(z, plus(one, scaled(z, -1)), square(plus(one, multiply(e, z))))
    C = plus(F(x), scaled(A, -1))
    require(C == plus(F(y), scaled(B, -1)), 'The two common quadrilateral formulas differ.')
    T = plus(A, C, B)
    require(diff(T, 0) == diff(A, 0) and diff(T, 1) == diff(B, 1),
            'The single-insertion total derivative identities failed.')
    return A, C, B, T


def bernstein(polynomial, box):
    """Exact tensor Bernstein coefficients after an affine box map."""
    degree = tuple(max(key[j] for key in polynomial) for j in range(3))
    affine = {}
    for powers, c in polynomial.items():
        for key in product(*(range(n+1) for n in powers)):
            coefficient = c
            for n, k, (lo, hi) in zip(powers, key, box):
                coefficient *= comb(n, k)*lo**(n-k)*(hi-lo)**k
            affine[key] = affine.get(key, Q(0))+coefficient
    result = []
    for index in product(*(range(n+1) for n in degree)):
        coefficient = Q(0)
        for key, c in affine.items():
            if all(k <= i for k, i in zip(key, index)):
                for i, k, n in zip(index, key, degree):
                    c *= Q(comb(i, k), comb(n, k))
                coefficient += c
        result.append(coefficient)
    require(all(c > 0 for c in result), 'A continuous Bernstein sign certificate failed.')
    return {'degree': degree, 'box': box, 'minimum_coefficient': min(result),
            'coefficient_count': len(result), 'coefficients_lexicographic': result}


@lru_cache(maxsize=None)
def frontier_certificate():
    A, C, B, T = sparse_quantities()
    tx, ty = diff(T, 0), diff(T, 1)
    xx, yy, xy = diff(tx, 0), diff(ty, 1), diff(tx, 1)
    determinant = plus(multiply(xx, yy), scaled(multiply(xy, xy), -1))
    J = plus(multiply(diff(A, 0), diff(B, 1)), scaled(multiply(diff(A, 1), diff(B, 0)), -1))
    results = [dict(name=name, **bernstein(p, box)) for name, p, box in (
        ('negative_total_xx', scaled(xx, -1), ROOM),
        ('total_hessian_determinant', determinant, ROOM),
        ('first_branch_C_minus_B', plus(C, scaled(B, -1)), FIRST),
        ('tied_branch_gradient_determinant', J, TIED))]
    require([r['coefficient_count'] for r in results] == [36, 245, 75, 320],
            'The uniform frontier certificate changed degree.')
    F = lambda x: x*(1-x)*(1+END*x)**2
    require(F(Q(1, 7)) < Q(7, 50) and F(Q(7, 8)) < Q(7, 50)
            and Q(1, 32) < Q(7, 100) and Q(9, 200) < Q(7, 100),
            'A competitor localization bound failed.')
    # The general equal-area cubic, multiplied by epsilon, is affine in it.
    P = lambda u, e: 32*e*u**3+(32+8*e)*u*u-(4+13*e)*u-1
    require(P(Q(1, 4), END) < 0 and P(Q(1, 4), Q(0)) == 0
            and min(P(Q(27, 100), e) for e in (Q(0), END)) > 0
            and 9*Q(27, 100)/(8*Q(27, 100)+1) < Q(39, 50),
            'The maximin endpoint escaped the tied-branch box.')
    return results


def sample(epsilon):
    require(type(epsilon) is Q and 0 < epsilon <= END,
            'Use a rational epsilon in (0, 1/10].')
    _, total, _, gain, cost, *_ = models()
    point = I.wrap(epsilon)
    b, t = total['B'].bound(point), total['T'].bound(point)
    # Retain the exact small factors; subtracting independently bounded
    # endpoint areas would destroy accuracy close to constant curvature.
    g = gain.bound(point)/b*epsilon**3
    c = cost.bound(point)/t*epsilon**6
    ratio = cost.bound(point)*b*b/(t*gain.bound(point)*gain.bound(point))
    return {'epsilon': epsilon, 'relative_minimum_gain': significant(g),
            'relative_total_cost': significant(c),
            'cost_over_squared_gain': significant(ratio)}


def controls():
    e = Polynomial((0, Q(1)))
    require(((1+e)**8).c == tuple(Q(comb(8, k)) for k in range(9)),
            'Exact polynomial multiplication failed its binomial control.')
    z = Derivative(Q(2), 1, 0)*Derivative(Q(3), 0, 1)
    require((z.value, z.dx, z.dy) == (6, 3, 2), 'The product derivative control failed.')
    rejected = 0
    for value in (Q(0), Q(-1), Q(101, 1000), 0.1):
        try:
            sample(value)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('An invalid epsilon was accepted.')
    try:
        (1+e).divide_power(1)
    except ValueError:
        rejected += 1
    else:
        raise ValueError('An invalid vanishing-factor cancellation was accepted.')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write the reconstructed rational certificate.')
    parser.add_argument('--epsilon', type=Q, help='Also enclose a rational perturbation in (0, 1/10].')
    args = parser.parse_args()
    query = sample(args.epsilon) if args.epsilon is not None else None
    signs = frontier_certificate()
    tubes, metrics = [], []
    for n in range(SLABS):
        interval = I(END*Q(n, SLABS), END*Q(n+1, SLABS))
        tubes.extend(tube(branch, interval) for branch in ('total', 'switch'))
        metrics.append(metric_bounds(interval))
    invalid = controls()
    examples = [sample(e) for e in (END, Q(1, 20), Q(1, 100), Q(1, 1 << 160))]
    data = {'scope': 'Complete four-curve cubic frontier and finite area-law errors for 0 < epsilon <= 1/10; equivalently 1 < b/a <= 4/3.',
            'root_polynomial_degree': ORDER, 'root_error_radius_over_epsilon_power_17': RADIUS,
            'root_polynomials': {branch: {'x': root_polynomials(branch)[0].c,
                                          'y': root_polynomials(branch)[1].c}
                                 for branch in ('total', 'switch')},
            'continuous_signs': signs, 'uniform_root_tubes': tubes,
            'metric_remainders': metrics, 'examples': examples}
    if args.write:
        (HERE/'cubic_frontier_bounds.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    print('Uniform frontier: 676 strictly positive three-variable Bernstein coefficients.')
    print('32 contraction boxes cover [0,1/10]; norm < 1/3, center displacement < 20, radius 100.')
    print('64 exact zero root-equation coefficients after the constant term; independent sixth-order agreement.')
    print('gain = (8/27)e^3 [1 - 3e/2 + r_g e^2], -1/5 < r_g < 1/5.')
    print('cost = (16/2187)e^6 [1 - 3e + r_c e^2], 1 < r_c < 3.')
    print('cost/gain^2 = 1/12 - theta e^2, 1/25 < theta < 1/20.')
    print(f'{invalid} rejected controls; four factored examples, including epsilon = 2^-160.')
    if query:
        for name, value in query.items():
            if name != 'epsilon':
                print(name+': ['+', '.join(f'{float(v):.14g}' for v in value)+'] (rounded display)')


if __name__ == '__main__':
    main()
