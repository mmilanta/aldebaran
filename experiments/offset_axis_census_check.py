"""Independent algebraic controls for the complete mirror-axis cover.

Toy projective curves include a genuine node and false two-equation roots
at distinct poles. Direct power-basis values audit Bernstein conversion,
degree elevation, bisection, derivatives, and retained-root refinement.
These controls supplement the fresh cover; they do not replace it.
"""

from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path

from blend_cusps import Interval as I, add, derivative, product, require, scale, value
from offset_axis_census import (Arc, bernstein, contraction, dyadic_outer,
                                enclose, prove, refine, separated)
from offset_axis_visits import polynomials
from rhythm_tangencies import evaluate

CHECKS = 0


def check(condition, message):
    global CHECKS
    require(condition, message)
    CHECKS += 1


def evaluate_controls(row, u):
    n = len(row) - 1
    return sum(a * comb(n, k) * u ** k * (1 - u) ** (n - k)
               for k, a in enumerate(row))


def rejects(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError:
        check(True, "Rejected an invalid control.")
    else:
        raise ValueError("An invalid control was accepted.")


def main():
    samples = tuple(Q(k, 8) for k in range(9))
    polys = ((Q(3, 7),), (0, 1), (1, -3, 2), (-7, 0, 5, 1), (0, 0, 0, 0, 1))
    for low, high in ((Q(-1), Q(1)), (Q(-9, 10), Q(-2, 3)), (Q(1, 7), Q(4, 5))):
        for degree in (4, 7):
            rows, factor = bernstein(polys, low, high, degree)
            bounds = enclose(polys, low, high)
            for p, row, bound in zip(polys, rows, bounds):
                for u in samples:
                    x = low + (high - low) * u
                    expected = value(p, x)
                    check(evaluate_controls(row, u) == factor * expected,
                          "Power and Bernstein values disagree.")
                    check(bound.low <= expected <= bound.high,
                          "The convex-hull enclosure missed a value.")
    curves = [((0, 1), (0, 0, 1), (1,)),
              ((0, 0, 1), (0, -1, 0, 1), (1,)),
              ((1,), (0, 1), (-1, 0, 1))]
    for polys in curves:
        arc = Arc.make(polys, Q(-6, 5), Q(7, 6))
        family = [arc, *arc.split(), *(child for half in arc.split() for child in half.split())]
        for child in family:
            values, slopes, centers, center_slopes = child.jet()
            for axis, (p, row) in enumerate(zip(polys, child.rows)):
                middle = (child.low + child.high) / 2
                check(centers[axis] == value(p, middle) * child.factor,
                      "The Bernstein midpoint lost its common scale.")
                check(center_slopes[axis] == value(derivative(p), middle) * child.factor,
                      "The differentiated midpoint is wrong.")
                for u in samples:
                    x = child.low + (child.high - child.low) * u
                    exact = value(p, x) * child.factor
                    slope = value(derivative(p), x) * child.factor
                    check(evaluate_controls(row, u) == exact,
                          "De Casteljau bisection changed the polynomial.")
                    check(values[axis].low <= exact <= values[axis].high
                          and slopes[axis].low <= slope <= slopes[axis].high,
                          "A subdivided value or derivative escaped its bound.")
    node = curves[1]
    pair = (Arc.make(node, Q(-101, 100), Q(-99, 100)),
            Arc.make(node, Q(99, 100), Q(101, 100)))
    status, _ = contraction(*pair)
    check(status == "root" and not separated(*pair), "The genuine projective node was missed.")
    for arc, root in zip(refine(node, pair), (Q(-1), Q(1))):
        check(arc.low <= root <= arc.high and arc.high - arc.low < Q(1, 10 ** 28),
              "Root refinement lost the exact node.")
    # At -1 and +1 both equations using V vanish, but [1,-1,0] and
    # [1,+1,0] are different projective points. The third chart is essential.
    poles = tuple(Arc.make(curves[2], arc.low, arc.high) for arc in pair)
    check(contraction(*poles)[0] == "root", "The false-pole control must fool the two equations.")
    check(separated(*poles), "The projective chart did not reject distinct poles.")
    for sign in (-1, 1):
        scaled = tuple(Arc(a.low, a.high,
                           tuple(tuple(sign * 7 * x for x in row) for row in a.rows),
                           a.factor) for a in poles)
        check(separated(*scaled), "A projective rescaling changed the pole exclusion.")
    parabola = tuple(Arc.make(curves[0], arc.low, arc.high) for arc in pair)
    check(separated(*parabola), "Two disjoint parabola arcs were not separated.")
    for low, high in ((Q(-13, 17), Q(-7, 23)), (Q(1, 3), Q(2, 3)), (Q(0), Q(0))):
        a, b = dyadic_outer(low, high, bits=13)
        check(a <= low <= high <= b and low - a < Q(1, 8192)
              and b - high < Q(1, 8192), "Dyadic rounding narrowed an enclosure.")
    for inner in (6, 8):
        x, Y, V, w, A, P = polynomials(inner)
        D = add(add(P, scale(A, 640)), scale(V, 102400))
        # Audit high-degree, highly cancelling orbital coordinates too,
        # independently of the small projective toy curves above.
        for low, high in ((Q(-1), Q(1)), (Q(9, 10), Q(19, 20))):
            rows, factor = bernstein((A, D, V), low, high)
            for p, row in zip((A, D, V), rows):
                for u in samples:
                    check(evaluate_controls(row, u) == factor * value(p, low + (high - low) * u),
                          "The orbital projective coefficients changed in Bernstein form.")
        for quarter in (0, 1):
            for chart in (Q(1, 7), Q(1, 3), Q(3, 5), Q(4, 5)):
                c, s = (1 - chart * chart) / (1 + chart * chart), 2 * chart / (1 + chart * chart)
                if quarter:
                    c, s = -s, c
                p, v, a = [[component.low for component in evaluate(quarter, chart, Q(inner - 6, 2), order)]
                           for order in range(3)]
                length = p[1] / v[0]
                center = p[0] + length * v[1]
                radius2 = length * length * sum(z * z for z in v)
                check(center == value(A, c) / value(V, c), "The original Fourier circle center disagrees.")
                check(radius2 - center * center == value(D, c) / value(V, c),
                      "The original Fourier circle radius disagrees.")
                center_prime = (value(derivative(A), c) * value(V, c)
                                - value(A, c) * value(derivative(V), c)) / value(V, c) ** 2
                expected = (sum(z * z for z in v) + length * (v[0] * a[1] - v[1] * a[0])) / (s * s * value(V, c))
                check(center_prime == expected, "The monotone-center derivative identity disagrees with Fourier jets.")
    here = Path(__file__).resolve().parent
    census = json.loads((here / "offset_axis_census.json").read_text())
    selected = json.loads((here / "offset_positive.json").read_text())
    for endpoint, previous in zip(census["endpoints"], selected["endpoints"]):
        check(endpoint["inner"] == previous["inner"], "The archived endpoint order changed.")
        for event in previous["fourfolds"]:
            cosine = []
            for quarter, box in zip(event["quarters"][:2], event["root_box"][:2]):
                u = I(*map(Q, box))
                check(quarter in (0, 1), "A selected upper visit left its two charts.")
                cosine.append(((1 - u * u) if quarter == 0 else -2 * u) / (1 + u * u))
            cosine.reverse()
            matches = [e for e in endpoint["events"] if all(Q(b[0]) < c.low <= c.high < Q(b[1])
                       for b, c in zip(e["coarse_box"], cosine))]
            check(len(matches) == 1, "An old selected root did not enter exactly one fresh unique box.")
            match, = matches
            check(max(Q(match["offset"][0]), Q(event["offset"][0]))
                  <= min(Q(match["offset"][1]), Q(event["offset"][1])),
                  "The identified circles have disjoint distance enclosures.")
            check(match["positive_triples"] == sum(t["strangeness_jump"] > 0 for t in event["triples"]),
                  "A previously selected circle changed its certified signs.")
    rejects(bernstein, ((0, 1),), Q(0), Q(1), degree=0)
    rejects(bernstein, ((0.5, 1),), Q(0), Q(1))
    rejects(bernstein, ((1,),), Q(1), Q(0))
    rejects(bernstein, (), Q(0), Q(1))
    rejects(bernstein, ((1,),), Q(0), Q(1), degree=True)
    rejects(prove, True)
    rejects(prove, 7)
    rejects(prove, 6, max_depth=-1)
    rejects(prove, 6, max_depth=0)
    rejects(prove, 8, max_depth=0)
    print(f"{CHECKS} exact power/Bernstein, subdivision, derivative, genuine-node, "
          "false-pole, refinement, scaling, rounding, and fail-closed controls passed.")


if __name__ == "__main__":
    main()
