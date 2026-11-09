"""Slide the parabolas independently: total area is a secant variance.

Exact line clipping and curved integrals check general strictly convex
intercepts. A cubic intercept law has a non-midpoint best insertion.
This is a different family from the unshifted alternating-gap theorem.
Only the standard library; see shifted_parabolas.md.
"""

from fractions import Fraction as Q
from itertools import combinations
from math import isqrt
from random import Random

from blend_cusps import require
from parabolic_balance import Quadratic
from parabolic_pockets import area


def ordered(points):
    require(type(points) in (tuple, list) and len(points) >= 2
            and all(type(p) in (tuple, list) and len(p) == 2
                    and all(type(x) is Q for x in p) for p in points),
            "Use at least two rational (slope, intercept) pairs.")
    p = sorted(points)
    require(all(a[0] < b[0] for a, b in zip(p, p[1:])), "Slope labels must be distinct.")
    secants = [(b[1]-a[1])/(b[0]-a[0]) for a, b in zip(p, p[1:])]
    require(all(a < b for a, b in zip(secants, secants[1:])), "Adjacent secants must increase strictly.")
    return p


def crossing(a, b):
    y = (b[1]-a[1])/(b[0]-a[0])
    return (a[1]-a[0]*y, y)


def clip(polygon, branch, sign):
    p, q = branch
    side = lambda v: sign*(v[0]+p*v[1]-q)
    out = []
    for a, b in zip(polygon, polygon[1:]+polygon[:1]):
        fa, fb = side(a), side(b)
        if fa >= 0:
            out.append(a)
        if fa*fb < 0:
            t = fa/(fa-fb)
            out.append(tuple(x+t*(y-x) for x, y in zip(a, b)))
    return out


def bounded_faces(points):
    p = ordered(points)
    vertices = [crossing(a, b) for a, b in combinations(p, 2)]
    radius = 1+max(abs(x) for vertex in vertices for x in vertex)
    polygons = [[(-radius, -radius), (radius, -radius), (radius, radius), (-radius, radius)]]
    for branch in p:
        polygons = [face for polygon in polygons for sign in (-1, 1)
                    if len(face := clip(polygon, branch, sign)) >= 3 and area(face) > 0]
    return [polygon for polygon in polygons
            if not any(abs(x) == radius or abs(y) == radius for x, y in polygon)]


def variance_area(points):
    p = ordered(points)
    gaps = [b[0]-a[0] for a, b in zip(p, p[1:])]
    secants = [(b[1]-a[1])/g for a, b, g in zip(p, p[1:], gaps)]
    span = p[-1][0]-p[0][0]
    mean = (p[-1][1]-p[0][1])/span
    return (sum(g*s*s for g, s in zip(gaps, secants))-span*mean*mean)/2


def envelope_area(points):
    p = ordered(points)
    cuts = sorted({crossing(a, b)[1] for a, b in zip(p, p[1:])} | {crossing(p[0], p[-1])[1]})
    total = Q(0)
    for lo, hi in zip(cuts, cuts[1:]):
        middle = (lo+hi)/2
        inner = min(p, key=lambda branch: branch[1]-branch[0]*middle)
        outer = min((p[0], p[-1]), key=lambda branch: branch[1]-branch[0]*middle)
        width = lambda y: outer[1]-outer[0]*y-inner[1]+inner[0]*y
        require(width(lo) >= 0 and width(hi) >= 0, "The bounded band has a negative width.")
        total += (hi-lo)*(width(lo)+width(hi))/2
    return total


def check(points):
    p = ordered(points)
    polygons = bounded_faces(p)
    actual = sum((area(polygon) for polygon in polygons), Q(0))
    require(actual == variance_area(p) == envelope_area(p)
            and len(polygons) == (len(p)-1)*(len(p)-2)//2,
            "Independent clipping, the bounded band, and secant variance disagree.")
    runs = []
    for first in range(1, len(p)-1):
        for last in range(first, len(p)-1):
            a, b, c, d = first-1, first, last, last+1
            pairs = ((a, b), (a, d), (b, d)) if first == last else ((a, c), (a, d), (b, d), (b, c))
            branches = (a, d, b) if first == last else (a, d, b, c)
            v = [crossing(p[i], p[j]) for i, j in pairs]
            primitive = lambda branch, y: y**3/6-branch[0]*y*y/2+branch[1]*y
            curved = abs(sum(primitive(p[branch], v[(i+1) % len(v)][1])-primitive(p[branch], v[i][1])
                             for i, branch in enumerate(branches)))
            require(curved == area(v) > 0, "The common horizontal slide changed a face's area.")
            runs.append(v)
    require({frozenset(v) for v in runs} == {frozenset(v) for v in polygons},
            "The run classification misses a shifted-parabola face.")
    return actual


def insertion_gain(points, new):
    p = ordered(points)
    require(type(new) in (tuple, list) and len(new) == 2 and all(type(x) is Q for x in new)
            and p[0][0] < new[0] < p[-1][0] and all(new[0] != x[0] for x in p),
            "Insert a rational point with a new interior slope.")
    ordered(p+[new])
    left = max((x for x in p if x[0] < new[0]), key=lambda x: x[0])
    right = min((x for x in p if x[0] > new[0]), key=lambda x: x[0])
    a, b = new[0]-left[0], right[0]-new[0]
    s, t = (new[1]-left[1])/a, (right[1]-new[1])/b
    return a*b*(t-s)**2/(2*(a+b))


def cubic_area(r):
    require(type(r) in (Q, Quadratic) and 1 <= r <= 3, "Use an exact slope between one and three.")
    return (r-1)*(3-r)*(r+4)**2/9


def main():
    examples = insertions = invalid = 0
    for size in range(2, 10):
        for original_family, h in ((True, lambda x: x*x/2), (False, lambda x: x**3/3),
                                   (False, lambda x: x*x/2+x**4/4)):
            points = [(Q(1)+Q(2*i, size-1), Q(0)) for i in range(size)]
            points = [(p, h(p)) for p, _ in points]
            original = check(points)
            # Adding an affine function to all intercepts translates the
            # arrangement; changing the slope labels rescales/shears it.
            require(check([(p, q+Q(7, 3)*p-Q(2)) for p, q in points]) == original,
                    "Affine intercept translations changed an area.")
            require(check([(Q(3, 2)*p-Q(5), q) for p, q in points]) == Q(2, 3)*original,
                    "Slope rescaling misses its determinant factor.")
            examples += 3
            new_p = (points[0][0]+points[1][0])/2
            new = (new_p, h(new_p))
            gain = insertion_gain(points, new)
            require(check(points+[new])-original == gain,
                    "The local insertion formula misses the fresh complete arrangement.")
            if original_family:
                g = points[1][0]-points[0][0]
                require(gain == g**3/32, "The original quadratic-intercept midpoint law was not recovered.")
            insertions += 1
    random = Random(20261109)
    for size in range(3, 9):
        points = [(Q(-2), Q(5))]
        s = Q(-7)
        for _ in range(size-1):
            gap = Q(random.randrange(1, 8), 3)
            p, q = points[-1]
            points.append((p+gap, q+gap*s))
            s += Q(random.randrange(1, 10), 4)
        original = check(points)
        examples += 1
        first, second = points[:2]
        g = second[0]-first[0]
        s0 = (second[1]-first[1])/g
        s1 = (points[2][1]-second[1])/(points[2][0]-second[0])
        new = ((first[0]+second[0])/2, (first[1]+second[1])/2-g*(s1-s0)/8)
        require(check(points+[new])-original == insertion_gain(points, new),
                "A nonuniform discrete-convex insertion misses its actual new area.")
        insertions += 1
    best = Quadratic(11, Q(1, 2), Q(1, 2))
    maximum = Quadratic(11, Q(-71, 36), Q(11, 6))
    require(2*best*best-2*best-5 == 0 and cubic_area(best) == maximum > 4,
            "The non-midpoint maximizer misses its exact root or area.")
    for step in range(101):
        r = Q(1)+Q(step, 50)
        require(cubic_area(r) <= maximum, "A rational cubic-intercept insertion beats the exact maximum.")
    for bits in (12, 24, 48, 96):
        scale = 2**bits
        root_lo = Q(isqrt(11*scale*scale), scale)
        root_hi = root_lo+Q(1, scale)
        r = Q(1, 2)+(root_lo+root_hi)/4
        actual = check([(Q(1), Q(1, 3)), (r, r**3/3), (Q(3), Q(9))])
        require(actual == cubic_area(r) < maximum, "A near-optimal clipped pocket violates the exact bound.")
    for points in ([(Q(1), Q(1)), (Q(1), Q(2))], [(Q(1), Q(1)), (Q(2), Q(2)), (Q(3), Q(3))],
                   [(Q(1), Q(1)), (Q(2), Q(3)), (Q(3), Q(4))], [(1, Q(1)), (Q(2), Q(3))]):
        try:
            ordered(points)
        except ValueError:
            invalid += 1
        else:
            raise ValueError("Invalid or nonconvex intercepts were accepted.")
    print(f'{examples} exact arrangement/affine controls and {insertions} independent insertion controls passed.')
    print(f'101 rational maximum controls, four near-optimal clipped pockets, and {invalid} invalid controls passed.')
    print(f'Cubic intercept h(p)=p^3/3 on [1,3]: best insertion (1+sqrt(11))/2 ≈ {float(best):.12f}.')
    print(f'Its area (66*sqrt(11)-71)/36 ≈ {float(maximum):.12f}; midpoint area is exactly 4.')
    print('The weighted secant-variance identity and the written derivative prove the general statements.')


if __name__ == '__main__':
    main()
