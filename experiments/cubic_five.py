"""Certify the unique five-curve cubic smallest-pocket optimum on [1,3].

A rational contraction proves a positive stationary support for the three
triangular log-areas. Their strict concavity proves a global upper bound;
interval bounds check that none of the other three faces undercuts it.
Only the standard library. See cubic_five.md.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from random import Random

from blend_cusps import Interval as I, require
from cubic_maximin import serialize
from phase_unfolding import inverse
from shifted_maximin import check_arrangement, run_area
from shifted_placement import partition

HERE = Path(__file__).resolve().parent
DIMENSION = 5


class Dual:
    """A rational interval value and its five first partial derivatives."""
    def __init__(self, value, gradient=None):
        self.value = I.wrap(value)
        self.gradient = gradient if gradient is not None else [I.wrap(0)]*DIMENSION

    @staticmethod
    def wrap(value):
        return value if isinstance(value, Dual) else Dual(value)

    def __add__(self, other):
        other = self.wrap(other)
        return Dual(self.value+other.value, [a+b for a, b in zip(self.gradient, other.gradient)])

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value, [-a for a in self.gradient])

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        return Dual(self.value*other.value,
                    [a*other.value+self.value*b for a, b in zip(self.gradient, other.gradient)])

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.wrap(other)
        quotient = self.value/other.value
        return Dual(quotient, [(a-quotient*b)/other.value for a, b in zip(self.gradient, other.gradient)])

    def __rtruediv__(self, other):
        return self.wrap(other)/self


def triangle(a, p, b):
    s = a+p+b
    return (p-a)*(b-p)*(b-a)*s*s/18


def log_gradient(a, p, b):
    """Partials with respect to the left, middle and right slope labels."""
    # Writing 1 / a Dual also works when one endpoint is a plain integer.
    return (-1/(p-a)-1/(b-a)+2/(a+p+b),
            1/(p-a)-1/(b-p)+2/(a+p+b),
            1/(b-p)+1/(b-a)+2/(a+p+b))


def equations(box):
    variables = [Dual(v, [I.wrap(int(i == j)) for j in range(DIMENSION)]) for i, v in enumerate(box)]
    x, y, z, l1, l2 = variables
    l3 = 1-l1-l2
    A, B, C = triangle(1, x, y), triangle(x, y, z), triangle(y, z, 3)
    g1, g2, g3 = log_gradient(1, x, y), log_gradient(x, y, z), log_gradient(y, z, 3)
    result = (A-B, B-C, l1*g1[1]+l2*g2[0],
              l1*g1[2]+l2*g2[1]+l3*g3[0], l2*g2[2]+l3*g3[1])
    return [a.value for a in result], [a.gradient for a in result]


def proposed_center(bits=144):
    """Rational Newton steps suggest a center; they are not acceptance tests."""
    require(type(bits) is int and bits >= 64, 'Use an integer proposal precision of at least 64 bits.')
    seed = tuple(map(Q, ('1.648370786436389', '2.160107434272252', '2.603183034847801',
                         '0.496343048058099', '0.000762037190085')))
    grid = 1 << bits
    center = seed
    for _ in range(3):
        f, jac = equations(center)
        require(all(a.low == a.high for a in f) and all(a.low == a.high for row in jac for a in row),
                'Point automatic differentiation produced a non-point interval.')
        R = inverse([[a.low for a in row] for row in jac])
        updated = [center[i]-sum(R[i][j]*f[j].low for j in range(DIMENSION)) for i in range(DIMENSION)]
        center = tuple(Q(round(a*grid), grid) for a in updated)
    return center


def magnitude(a):
    return max(abs(a.low), abs(a.high))


def certify(center, radius):
    require(type(center) in (tuple, list) and len(center) == DIMENSION
            and all(type(x) is Q for x in center) and type(radius) is Q and radius > 0,
            'Use five rational coordinates and a positive rational radius.')
    box = [I(x-radius, x+radius) for x in center]
    x, y, z, l1, l2 = box
    l3 = 1-l1-l2
    require(1 < x.low <= x.high < y.low <= y.high < z.low <= z.high < 3
            and min(l1.low, l2.low, l3.low) > 0,
            'The support needs ordered interior labels and three positive weights.')
    f, point_jac = equations(center)
    _, jac = equations(box)
    R = inverse([[a.midpoint() for a in row] for row in point_jac])
    defect = [[I.wrap(int(i == j))-sum(R[i][k]*jac[k][j] for k in range(DIMENSION))
               for j in range(DIMENSION)] for i in range(DIMENSION)]
    norm = max(sum(magnitude(a) for a in row) for row in defect)
    require(norm < Q(1, 10), 'The proposed box is not a strong contraction.')
    offsets = [-sum(R[i][k]*f[k] for k in range(DIMENSION))
               +sum(defect[i][j]*I(-radius, radius) for j in range(DIMENSION))
               for i in range(DIMENSION)]
    require(all(-radius < a.low <= a.high < radius for a in offsets),
            'The stationary support map does not send the box into itself.')
    return {'box': box, 'contraction_bound': norm, 'image_offsets': offsets,
            'weights': [l1, l2, l3]}


def face_area(nodes, first, last):
    require(type(first) is int and type(last) is int and 1 <= first <= last < len(nodes)-1,
            'Use a nonempty interior run.')
    p = [I.wrap(x) for x in nodes]
    require(p[0].low > 0 and all(a.high < b.low for a, b in zip(p, p[1:])),
            'Cubic face boxes need positive, separated slope intervals.')
    if first == last:
        return triangle(p[first-1], p[first], p[first+1])
    a, b = p[first]-p[first-1], p[last+1]-p[last]
    H = p[last]-p[first]
    # Secant differences factor positively for the cubic intercept law.
    A = (p[last]-p[first-1])*(p[first-1]+p[first]+p[last])/3
    B = (p[last+1]-p[first])*(p[first]+p[last]+p[last+1])/3
    return (a*a*b*A*A/(2*(a+H+b)*(a+H))
            +a*b*A*B/(a+H+b)+a*b*b*B*B/(2*(a+H+b)*(H+b)))


def rounded(a, bits=192):
    """A short outward dyadic interval for an already certified enclosure."""
    a = I.wrap(a)
    grid = 1 << bits
    lo, hi = Q((a.low*grid).__floor__(), grid), Q((a.high*grid).__ceil__(), grid)
    require(lo <= a.low <= a.high <= hi, 'Outward certificate rounding failed.')
    return lo, hi


def optimum(bits=96):
    require(type(bits) is int and 48 <= bits <= 192,
            'Use an integer certificate precision between 48 and 192 bits.')
    center = proposed_center(bits+64)
    radius = Q(1, 1 << bits)
    certificate = certify(center, radius)
    nodes = [I.wrap(1)]+certificate['box'][:3]+[I.wrap(3)]
    areas = [face_area(nodes, i, j) for i in range(1, 4) for j in range(i, 4)]
    triangular = [areas[i] for i in (0, 3, 5)]
    smallest = I(max(a.low for a in triangular), min(a.high for a in triangular))
    require(all(areas[i].low > smallest.high for i in (1, 2, 4)),
            'A longer-run face can undercut the triangular upper bound.')
    short = lambda a: rounded(a, max(192, bits+64))
    offsets = [short(a) for a in certificate['image_offsets']]
    require(all(-radius < a <= b < radius for a, b in offsets),
            'Rounded image offsets do not retain the strict self-map certificate.')
    return {'precision_bits': bits, 'nodes': [short(a) for a in nodes],
            'smallest_area': short(smallest), 'total_area': short(sum(areas)),
            'face_areas': [short(a) for a in areas],
            'support_weights': [short(a) for a in certificate['weights']],
            'root_center': center, 'root_radius': radius, 'image_offsets': offsets,
            'contraction_upper': short(certificate['contraction_bound'])[1]}


def controls():
    random = Random(2026111105)
    arrangements = faces = 0
    for _ in range(24):
        interior = sorted(random.sample([Q(i, 40) for i in range(41, 120)], 3))
        nodes = [Q(1)]+interior+[Q(3)]
        points = [(a, a*a*a/3) for a in nodes]
        faces += check_arrangement(points, lambda a, b: (2*a, 2*b))
        arrangements += 1
        for i in range(1, 4):
            for j in range(i, 4):
                actual = run_area(points, i, j)[0]
                bound = face_area(nodes, i, j)
                require(bound.low == actual == bound.high,
                        'The interval face formula misses an independent exact polygon area.')
    solutions = [optimum(bits) for bits in (48, 64, 96, 128, 192)]
    for key in ('nodes', 'support_weights', 'face_areas'):
        for boxes in zip(*(r[key] for r in solutions)):
            require(max(a for a, b in boxes) <= min(b for a, b in boxes),
                    'Separately certified precisions give disjoint enclosures.')
    center = proposed_center()
    # A precise nearby nonroot must fail the self-map acceptance predicate.
    bad = list(center)
    bad[0] += Q(1, 10**6)
    try:
        certify(bad, Q(1, 2**96))
    except ValueError as error:
        require('send the box into itself' in str(error), 'A nonroot failed for an unexpected reason.')
    else:
        raise ValueError('The nearby nonroot received a stationary certificate.')
    invalid = 0
    for bits in (True, 0, 47, 193, 96.0):
        try:
            optimum(bits)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid certificate precision was accepted.')
    return {'complete_arrangements': arrangements, 'clipped_faces': faces,
            'certified_precisions': len(solutions), 'nonroot_rejections': 1, 'invalid_controls': invalid}


def record():
    best = optimum()
    total = partition(4)
    nodes = [I(a, b) for a, b in total['nodes']]
    areas = [face_area(nodes, i, j) for i in range(1, 4) for j in range(i, 4)]
    require(best['smallest_area'][0] > min(a.high for a in areas)
            and best['total_area'][1] < total['area'][0],
            'The finite five-curve minimum/total tradeoff is not strict.')
    return {'scope': 'Five complete cubic-intercept parabolas, fixed outer labels 1 and 3. Unique finite maximin.',
            'equation': 'X_p(Y)=Y^2/2-pY+p^3/3', 'maximin': best,
            'total_optimizer': {'nodes': total['nodes'], 'total_area': total['area'],
                                'face_areas': [rounded(a) for a in areas]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate the rational contraction and complete six-face bounds.')
    args = parser.parse_args()
    counts = controls()
    data = record()
    if args.write:
        (HERE/'cubic_five.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    print(', '.join(f'{v} {k.replace("_", " ")}' for k, v in counts.items())+'.')
    mid = lambda box: float(sum(box)/2)
    print('Unique five-curve maximin labels:', ', '.join(f'{mid(a):.12f}' for a in data['maximin']['nodes']))
    print(f'Three triangles each have area ≈ {mid(data["maximin"]["smallest_area"]):.12f}.')
    print('Positive log-area support weights:', ', '.join(f'{mid(a):.12f}' for a in data['maximin']['support_weights']))
    print(f'Rational contraction norm < {float(data["maximin"]["contraction_upper"]):.3g}; all three longer faces are larger.')


if __name__ == '__main__':
    main()
