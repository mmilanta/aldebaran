"""Total bounded area for any finite collection of the limiting parabolas.

Rational line arrangements independently check the nearest-slope
envelope integral and the closed gap formula. These are full limit
parabolas at mu=0, not an event or face census of an orbital drawing.
Standard library only; see the addendum to parabolic_triangle.md.
"""

from fractions import Fraction as Q
from itertools import combinations

from blend_cusps import require


def ordered(slopes):
    require(type(slopes) in (tuple, list) and len(slopes) >= 2
            and all(type(p) is Q for p in slopes) and len(set(slopes)) == len(slopes),
            "Use at least two distinct rational slopes.")
    return sorted(slopes)


def area(polygon):
    return abs(sum((a[0]*b[1]-a[1]*b[0] for a, b in zip(polygon, polygon[1:]+polygon[:1])), Q(0)))/2


def clip(polygon, slope, sign):
    out = []

    def side(vertex):
        return sign*(vertex[0]+slope*vertex[1]-slope*slope/2)

    for a, b in zip(polygon, polygon[1:]+polygon[:1]):
        fa, fb = side(a), side(b)
        if fa >= 0:
            out.append(a)
        if fa*fb < 0:
            t = fa/(fa-fb)
            out.append(tuple(x+t*(y-x) for x, y in zip(a, b)))
    return out


def arrangement(slopes):
    """Split a box containing every vertex; discard cells touching its edge.

    Every bounded line face lies strictly in this box, since all its
    vertices are pairwise line intersections. Every unbounded face hits
    the box boundary. Exact clipping therefore finds all bounded faces.
    """
    p = ordered(slopes)
    vertices = [(-a*b/2, (a+b)/2) for a, b in combinations(p, 2)]
    radius = 1+max(abs(x) for vertex in vertices for x in vertex)
    polygons = [[(-radius, -radius), (radius, -radius), (radius, radius), (-radius, radius)]]
    for slope in p:
        polygons = [face for polygon in polygons for sign in (-1, 1)
                    if len(face := clip(polygon, slope, sign)) >= 3 and area(face) > 0]
    bounded = [polygon for polygon in polygons
               if not any(abs(x) == radius or abs(y) == radius for x, y in polygon)]
    return [area(polygon) for polygon in bounded]


def gap_area(slopes):
    p = ordered(slopes)
    span = p[-1]-p[0]
    return (span**3-sum((b-a)**3 for a, b in zip(p, p[1:])))/24


def envelope_area(slopes):
    """Integrate nearest-extreme squared distance minus nearest-slope error."""
    p = ordered(slopes)
    cuts = sorted({p[0], p[-1], (p[0]+p[-1])/2, *((a+b)/2 for a, b in zip(p, p[1:]))})
    total = Q(0)
    for lo, hi in zip(cuts, cuts[1:]):
        middle = (lo+hi)/2
        near = min(p, key=lambda x: abs(x-middle))
        extreme = min((p[0], p[-1]), key=lambda x: abs(x-middle))
        # Half the difference of the two squares is linear in Y.
        total += (near-extreme)*(hi*hi-lo*lo)/2+(extreme**2-near**2)*(hi-lo)/2
    return total


def check(slopes):
    p = ordered(slopes)
    faces = arrangement(p)
    actual = sum(faces, Q(0))
    require(actual == envelope_area(p) == gap_area(p),
            "The exact face census, envelope integral, and gap formula disagree.")
    span, n = p[-1]-p[0], len(p)-1
    mean = span/n
    maximum = span**3*(1-Q(1, n*n))/24
    deficit = sum((b-a-mean)**2*(b-a+2*mean) for a, b in zip(p, p[1:]))/24
    require(maximum-actual == deficit >= 0,
            "The equal-gap maximum misses its exact square deficit.")
    return len(faces), actual


def main():
    count = 0
    for size in range(2, 13):
        slopes = [Q(-2)+Q(4*k, size-1) for k in range(size)]
        faces, total = check(slopes)
        print(f"{size} equally spaced slopes in [-2,2]: {faces} bounded faces, total area {total}.")
        count += 1
    for p in (tuple(map(Q, (-5, -3, -1, 0, 2, 8))), (Q(-2), Q(-1), Q(1, 2), Q(7, 4), Q(2))):
        faces, total = check(p)
        print(f"Unequal slopes {tuple(map(str, p))}: {faces} bounded faces, total area {total}.")
        for factor, shift in ((Q(2, 3), Q(-7, 4)), (Q(-3, 2), Q(1, 3))):
            other = check(tuple(factor*x+shift for x in reversed(p)))
            require(other == (faces, abs(factor)**3*total),
                    "Slope translation or scaling changed the arrangement area incorrectly.")
            count += 1
        count += 1
    for bad in ((Q(0),), (Q(0), Q(0)), (0, 1), (Q(0), True)):
        try:
            ordered(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("Invalid slope-arrangement input was accepted.")
    print(f"{count} exact controls: full line-face clipping, nearest-slope integrals, gap cubes, equal-gap maxima, scaling, and invalid inputs.")
    print("Subtracting Y^2/2 preserves these total areas for the limiting parabolas. No full-drawing face claim.")


if __name__ == "__main__":
    main()
