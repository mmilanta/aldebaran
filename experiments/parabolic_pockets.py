"""Total bounded area for any finite collection of the limiting parabolas.

Rational line arrangements independently check the nearest-slope
envelope integral and the closed gap formula. These are full limit
parabolas at mu=0, not an event or face census of an orbital drawing.
Standard library only; see the addendum to parabolic_triangle.md.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations
import json
from pathlib import Path

from blend_cusps import require

HERE = Path(__file__).resolve().parent


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


def bounded_faces(slopes):
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
    return bounded


def arrangement(slopes):
    return [area(polygon) for polygon in bounded_faces(slopes)]


def gap_area(slopes):
    p = ordered(slopes)
    span = p[-1]-p[0]
    return (span**3-sum((b-a)**3 for a, b in zip(p, p[1:])))/24


def envelope_cells(slopes):
    """Exact intervals on which both nearest choices stay fixed."""
    p = ordered(slopes)
    cuts = sorted({p[0], p[-1], (p[0]+p[-1])/2, *((a+b)/2 for a, b in zip(p, p[1:]))})
    cells = []
    for lo, hi in zip(cuts, cuts[1:]):
        middle = (lo+hi)/2
        near = min(p, key=lambda x: abs(x-middle))
        extreme = min((p[0], p[-1]), key=lambda x: abs(x-middle))
        # Half the difference of the two squares is linear in Y.
        integral = (near-extreme)*(hi*hi-lo*lo)/2+(extreme**2-near**2)*(hi-lo)/2
        require(integral >= 0, "An envelope slice has negative area.")
        cells.append({"lo": lo, "hi": hi, "inner": p.index(near),
                      "outer": p.index(extreme), "area": integral})
    return cells


def envelope_area(slopes):
    """Integrate nearest-extreme squared distance minus nearest-slope error."""
    return sum((cell["area"] for cell in envelope_cells(slopes)), Q(0))


def insertion_gain(slopes, new):
    """Area added by a new slope strictly inside an existing gap."""
    p = ordered(slopes)
    require(type(new) is Q and p[0] < new < p[-1] and new not in p,
            "Insert a new rational slope strictly inside a gap.")
    left = max(x for x in p if x < new)
    right = min(x for x in p if x > new)
    a, b = new-left, right-new
    return a*b*(a+b)/8


def run_face(slopes, first, last):
    """The face with precisely slopes first..last lying to its left.

    Straight vertices are cyclic; branches[k] contains the edge from
    vertices[k] to vertices[k+1]. The inverse slide bends those edges.
    """
    p = ordered(slopes)
    require(type(first) is int and type(last) is int and 1 <= first <= last < len(p)-1,
            "Choose a nonempty consecutive run of interior slope indices.")
    a, b, c, d = first-1, first, last, last+1
    pairs = ((a, b), (a, d), (b, d)) if first == last else ((a, c), (a, d), (b, d), (b, c))
    branches = (a, d, b) if first == last else (a, d, b, c)
    vertices = [(-p[i]*p[j]/2, (p[i]+p[j])/2) for i, j in pairs]
    predicted = (p[b]-p[a])*(p[d]-p[c])*(p[c]+p[d]-p[a]-p[b])/8

    def primitive(slope, y):
        return y**3/6-slope*y*y/2+slope*slope*y/2

    integral = sum((primitive(p[branch], vertices[(k+1) % len(vertices)][1])
                    - primitive(p[branch], vertices[k][1])) for k, branch in enumerate(branches))
    require(area(vertices) == abs(integral) == predicted > 0,
            "The individual face's shoelace, curved integral, and gap product disagree.")
    center = tuple(sum(v[k] for v in vertices)/len(vertices) for k in (0, 1))
    require(all((center[0]+slope*center[1]-slope*slope/2)*(1 if first <= k <= last else -1) > 0
                for k, slope in enumerate(p)), "The face's interior has the wrong run of slopes.")
    return {"first": first, "last": last, "branches": branches,
            "straight_vertices": vertices, "area": predicted}


def run_faces(slopes):
    p = ordered(slopes)
    return [run_face(p, first, last) for first in range(1, len(p)-1)
            for last in range(first, len(p)-1)]


def example(name, slopes):
    p = ordered(slopes)
    faces, total = check(p)
    gaps = [b-a for a, b in zip(p, p[1:])]
    span, n = p[-1]-p[0], len(p)-1
    maximum = span**3*(1-Q(1, n*n))/24
    return {"name": name, "slopes": p, "gaps": gaps, "area": total,
            "face_count": faces, "maximum": maximum, "deficit": maximum-total,
            "cells": envelope_cells(p), "faces": run_faces(p)}


def compromise(z, span=Q(4)):
    """Total and smallest area on the four-slope compromise curve."""
    require(type(z) is Q and Q(1, 4) <= z <= Q(1, 3)
            and type(span) is Q and span > 0, "Use a rational quarter-to-third parameter and positive span.")
    a = span*z
    slopes = (-span/2, -span/2+a, span/2-a, span/2)
    faces = run_faces(slopes)
    total = span**3*z*(1-z)**2/4
    smallest = span**3*z*(1-2*z)*(1-z)/8
    require(sum((face["area"] for face in faces), Q(0)) == total
            and min(face["area"] for face in faces) == smallest,
            "The compromise curve misses its integrated face areas.")
    return (total, smallest)


def compromise_record():
    start, end = Q(1, 4), Q(1, 3)
    first, last = compromise(start), compromise(end)

    def derivative(z):
        return (16*(1-4*z+3*z*z), 8*(1-6*z+6*z*z))

    first_control = tuple(x+(end-start)*v/3 for x, v in zip(first, derivative(start)))
    last_control = tuple(x-(end-start)*v/3 for x, v in zip(last, derivative(end)))
    controls = (first, first_control, last_control, last)
    for step in range(37):
        t = Q(step, 36)
        actual = tuple((1-t)**3*controls[0][i]+3*t*(1-t)**2*controls[1][i]
                       +3*t*t*(1-t)*controls[2][i]+t**3*controls[3][i] for i in (0, 1))
        require(actual == compromise(start+t*(end-start)), "The exact cubic drawing misses the compromise curve.")
    return {"span": Q(4), "parameter_interval": (start, end), "bezier": controls,
            "middle": {"parameter": Q(3, 10), "areas": compromise(Q(3, 10))}}


def illustration_record():
    before = tuple(map(Q, (-2, 0, 2)))
    inserted = tuple(map(Q, (-2, -1, 0, 2)))
    after = (Q(-2), Q(-2, 3), Q(2, 3), Q(2))
    return {"scope": "Complete arrangements of exact limit parabolas at mu=0; no finite-offset or orbital face claim.",
            "shear": "U=X-Y^2/2", "band_area": "(L^3-sum(gap^3))/24",
            "band_examples": [example("Equal gaps", tuple(map(Q, (-2, -1, 0, 1, 2)))),
                              example("Unequal gaps", (Q(-2), Q(-1), Q(1, 2), Q(7, 4), Q(2)))],
            "insertion_examples": [example("Three slopes", before), example("Split one gap", inserted),
                                   example("Space all four equally", after)],
            "balance_examples": [example("Largest total", after),
                                 example("Largest smallest pocket", tuple(map(Q, (-2, -1, 1, 2))))],
            "compromise": compromise_record(),
            "insertion": {"new_slope": Q(-1), "gain": insertion_gain(before, Q(-1)),
                          "fixed_gap_maximum": Q(1, 4)}}


def rational_strings(value):
    if type(value) is Q:
        return str(value)
    if type(value) is dict:
        return {key: rational_strings(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return [rational_strings(item) for item in value]
    return value


def check(slopes):
    p = ordered(slopes)
    polygons = bounded_faces(p)
    faces = [area(polygon) for polygon in polygons]
    actual = sum(faces, Q(0))
    require(actual == envelope_area(p) == gap_area(p),
            "The exact face census, envelope integral, and gap formula disagree.")
    span, n = p[-1]-p[0], len(p)-1
    mean = span/n
    maximum = span**3*(1-Q(1, n*n))/24
    deficit = sum((b-a-mean)**2*(b-a+2*mean) for a, b in zip(p, p[1:]))/24
    require(maximum-actual == deficit >= 0,
            "The equal-gap maximum misses its exact square deficit.")
    runs = run_faces(p)
    require(len(polygons) == len(runs) == (len(p)-1)*(len(p)-2)//2
            and {frozenset(polygon) for polygon in polygons}
            == {frozenset(face["straight_vertices"]) for face in runs},
            "The independent clipped faces and consecutive-run faces disagree.")
    require(sum((face["area"] for face in runs), Q(0)) == actual,
            "The individual gap products miss the total bounded area.")
    if len(set(b-a for a, b in zip(p, p[1:]))) == 1:
        g = p[1]-p[0]
        require(all(face["area"] == (face["last"]-face["first"]+1)*g**3/4 for face in runs),
                "An equally spaced face has the wrong run-length area.")
    return len(faces), actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the exact envelope illustration record.")
    args = parser.parse_args()
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
    insertion_count = 0
    for p in (tuple(map(Q, (-2, 0, 2))), (Q(-2), Q(-1), Q(1, 2), Q(7, 4), Q(2))):
        for left, right in zip(p, p[1:]):
            g = right-left
            for k in range(1, 16):
                new = left+Q(k, 16)*g
                gain = insertion_gain(p, new)
                enlarged = (*p, new)
                require(gap_area(enlarged)-gap_area(p) == envelope_area(enlarged)-envelope_area(p) == gain,
                        "The new envelope band misses its predicted gain.")
                require(g**3/32-gain == g*(new-(left+right)/2)**2/8,
                        "The midpoint insertion misses its exact square deficit.")
                insertion_count += 1
            require(sum(arrangement((*p, (left+right)/2)), Q(0))-sum(arrangement(p), Q(0)) == g**3/32,
                    "The independent face census misses a midpoint insertion.")
            insertion_count += 1
    for bad in (Q(-3), Q(3), Q(0), -1, True):
        try:
            insertion_gain(tuple(map(Q, (-2, 0, 2))), bad)
        except ValueError:
            insertion_count += 1
        else:
            raise ValueError("An invalid inserted slope was accepted.")
    for first, last in ((0, 1), (1, 3), (2, 1), (True, 1), (1, Q(1))):
        try:
            run_face(tuple(map(Q, (-2, -1, 0, 2))), first, last)
        except ValueError:
            count += 1
        else:
            raise ValueError("An invalid face run was accepted.")
    record = rational_strings(illustration_record())
    target = HERE/"parabolic_pockets.json"
    if args.write:
        target.write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
        print("Wrote parabolic_pockets.json from fresh rational envelope and line-face calculations.")
    else:
        require(target.exists() and json.loads(target.read_text(encoding="utf-8")) == record,
                "The envelope record is stale; repeat with --write.")
    print(f"{count} exact controls: full face clipping, consecutive-run vertices, individual curved integrals, envelope integrals, gap cubes, equal-gap maxima, scaling, and invalid inputs.")
    print(f"{insertion_count} insertion controls: independent band gains, exact midpoint deficits, full face sums, and invalid inputs.")
    print("Subtracting Y^2/2 preserves these total areas for the limiting parabolas. No full-drawing face claim.")


if __name__ == "__main__":
    main()
