"""Two finite-Fourier detours connecting all three original zero-turn curves.

Run: python3 experiments/arm_detour.py
Standard library only. Every leg certifies all orbit times and all blend
weights. The companion arm_detour.md explains the segment-distance cover.
"""

from fractions import Fraction as Q

from certify_intersections import IntersectionCertificate, require
from regular_blend import segment_distance_squared, sqrt_lower
from tangent_turning import certify_turning


# Each endpoint is (outer rhythm, inner rhythm, first-arm length).
BRIDGES = [
    [(2, 3, 245), (2, 3, 300), (4, 7, 300), (4, 7, 245)],
    [(4, 7, 245), (4, 7, 700), (6, 11, 700), (6, 11, 245)],
]


def certify_leg(first, second, max_depth=24):
    """Certify speed > 1 on a straight interpolation of two Fourier curves."""
    pairs = [first, second]
    require(all(length >= 245 for _, _, length in pairs),
            'These detours keep the first-arm length at least 245.')
    curves = [IntersectionCertificate(m, n, 1) for m, n, _ in pairs]
    M = max(length+140*m*m+65*n*n for m, n, length in pairs)
    intervals, deepest, minimum = 0, 0, None

    def vertex(curve, pair, quarter, s):
        x, y, denominator = curve.evaluate(quarter, s)[2]
        # The original evaluator has first length 245. Correct its z'/i
        # by (length-245) w, entirely in rational arithmetic.
        w = ((1-s*s)/(1+s*s), 2*s/(1+s*s))
        for _ in range(quarter):
            w = (-w[1], w[0])
        return (Q(x, denominator)+(pair[2]-245)*w[0],
                Q(y, denominator)+(pair[2]-245)*w[1])

    def visit(quarter, low, high, depth, vertices):
        nonlocal intervals, deepest, minimum
        # The angular acceleration bound is valid for every blend weight.
        error = 2*M*(high-low)
        margin = sqrt_lower(segment_distance_squared(*vertices))-error
        if margin > 1:
            intervals += 1
            deepest = max(deepest, depth)
            minimum = margin if minimum is None else min(minimum, margin)
            return
        require(depth < max_depth, 'A detour leg needs a deeper partition; no certificate returned.')
        mid = (low+high)/2
        visit(quarter, low, mid, depth+1, vertices)
        visit(quarter, mid, high, depth+1,
              [vertex(curve, pair, quarter, mid) for curve, pair in zip(curves, pairs)])

    try:
        for quarter in range(4):
            visit(quarter, Q(0), Q(1), 0,
                  [vertex(curve, pair, quarter, Q(0)) for curve, pair in zip(curves, pairs)])
        require(minimum is not None and minimum > 1, 'No positive speed bound was certified.')
        return {'intervals': intervals, 'deepest_split': deepest, 'speed_lower_bound': minimum}
    finally:
        for curve in curves:
            curve.evaluate.cache_clear()


def main():
    for pair in [(2, 3), (4, 7), (6, 11)]:
        require(certify_turning(*pair).turns == 0, 'An original endpoint has nonzero tangent index.')
    total = 0
    for bridge in BRIDGES:
        print('BRIDGE', bridge[0][:2], 'to', bridge[-1][:2])
        for first, second in zip(bridge, bridge[1:]):
            result = certify_leg(first, second)
            total += result['intervals']
            print(f'  {first} -> {second}: speed > 1; {result["intervals"]} intervals; '
                  f'deepest split {result["deepest_split"]}.')
    # The unmodified straight blend really has cusps. The same cover must
    # fail there, rather than quietly assuming every endpoint blend works.
    try:
        certify_leg((2, 3, 245), (4, 7, 245), max_depth=16)
    except ValueError as error:
        require('deeper partition' in str(error), 'An unexpected negative-control failure occurred.')
    else:
        raise ValueError('The known singular straight blend incorrectly received a certificate.')
    print(f'All six continuous legs certified in {total} intervals. The singular straight route was rejected.')
    print('Both detours preserve tangent index 0 and center winding +1.')


if __name__ == '__main__':
    main()
