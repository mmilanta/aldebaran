"""Certify an explicit cusp-free deformation from rhythms 2/3 to 4/7.

Run: python3 experiments/regular_blend.py
Standard library only. Every interval covers ALL blend weights, not a grid
of sampled curves. See regular_blend.md for the logarithmic interpolation.
"""

from fractions import Fraction as Q
from math import isqrt
from time import monotonic
import cmath

from certify_intersections import IntersectionCertificate, require
from tangent_turning import certify_turning


def position(t, a):
    """Floating-point illustration only; the certificate never calls this."""
    w = cmath.exp(1j*t)
    fa, fb = 245+140*w+65*w**-4, 245+140*w**3+65*w**-8
    return w*cmath.exp((1-a)*cmath.log(fa)+a*cmath.log(fb))


def velocity(t, a):
    """Independent complex implementation for the standalone illustration."""
    w = cmath.exp(1j*t)
    za, zb = 245*w+140*w**2+65*w**-3, 245*w+140*w**4+65*w**-7
    va, vb = 1j*(245*w+280*w**2-195*w**-3), 1j*(245*w+560*w**4-455*w**-7)
    return position(t, a)*((1-a)*va/za+a*vb/zb)


def dot(p, q):
    return p[0]*q[0]+p[1]*q[1]


def segment_distance_squared(p, q):
    """Exact squared distance from zero to a closed rational segment."""
    d = (q[0]-p[0], q[1]-p[1])
    d2 = dot(d, d)
    a = max(Q(0), min(Q(1), -dot(p, d)/d2)) if d2 else Q(0)
    closest = (p[0]+a*d[0], p[1]+a*d[1])
    return dot(closest, closest)


def sqrt_lower(x, bits=40):
    """A dyadic lower bound for a nonnegative rational square root."""
    require(x >= 0, 'A squared norm was negative.')
    return Q(isqrt((x.numerator << (2*bits)) // x.denominator), 2**bits)


def quotient(v, z):
    norm2 = dot(z, z)
    require(norm2 > 0, 'A logarithmic derivative has zero denominator.')
    return ((v[0]*z[0]+v[1]*z[1])/norm2,
            (v[1]*z[0]-v[0]*z[1])/norm2)


def certify(minimum=Q(1, 10), max_depth=24):
    """Prove |(1-a)z_A'/z_A + a z_B'/z_B| > minimum for all t,a."""
    require(minimum > 0, 'Use a positive requested lower bound.')
    curves = [IntersectionCertificate(2, 3, 1), IntersectionCertificate(4, 7, 1)]
    edges, deepest, lower_bound = 0, 0, None
    start = monotonic()

    def vertex(curve, quarter, s):
        p, _, (x, y, D) = curve.evaluate(quarter, s)
        v = (-Q(y, D), Q(x, D))  # Angular velocity, not the quarter derivative.
        return p, v, quotient(v, p)

    def visit(quarter, low, high, depth, vertices):
        nonlocal edges, deepest, lower_bound
        width = high-low
        bounds = []
        for curve, (p, v, _) in zip(curves, vertices):
            # Angular span <= 2 width. The global radius lower bound is 40;
            # max(|x|,|y|) is another rational lower bound at the anchor.
            radius = max(Q(40), max(abs(p[0]), abs(p[1]))-2*curve.V*width)
            speed = abs(v[0])+abs(v[1])+2*curve.M*width
            bounds.append(2*(curve.M/radius+speed*speed/(radius*radius)))
        error = max(bounds)*width
        distance = sqrt_lower(segment_distance_squared(vertices[0][2], vertices[1][2]))
        margin = distance-error
        if margin > minimum:
            edges += 1
            deepest = max(deepest, depth)
            lower_bound = margin if lower_bound is None else min(lower_bound, margin)
            return
        require(depth < max_depth, 'The full-family certificate needs a deeper partition.')
        mid = (low+high)/2
        visit(quarter, low, mid, depth+1, vertices)
        visit(quarter, mid, high, depth+1,
              [vertex(curve, quarter, mid) for curve in curves])

    try:
        for quarter in range(4):
            visit(quarter, Q(0), Q(1), 0, [vertex(curve, quarter, Q(0)) for curve in curves])
        require(lower_bound is not None and lower_bound > minimum, 'No positive family bound was obtained.')
        return {'intervals': edges, 'deepest_split': deepest,
                'log_speed_lower_bound': lower_bound, 'seconds': monotonic()-start}
    finally:
        for curve in curves:
            curve.evaluate.cache_clear()


def main():
    # Exact geometric examples check the projection and clamping cases.
    require(segment_distance_squared((Q(1), Q(1)), (Q(1), Q(-1))) == 1,
            'Interior segment projection failed.')
    require(segment_distance_squared((Q(2), Q(0)), (Q(3), Q(0))) == 4,
            'Endpoint segment projection failed.')
    require(segment_distance_squared((Q(-1), Q(0)), (Q(1), Q(0))) == 0,
            'A zero-crossing segment was not detected.')
    require(sqrt_lower(Q(2))**2 <= 2 < (sqrt_lower(Q(2))+Q(1, 2**40))**2,
            'The dyadic square-root bound failed.')
    result = certify()
    require(certify_turning(2, 3).turns == certify_turning(4, 7).turns == 0,
            'The independent endpoint tangent certificates disagree.')
    print(f'All continuous blend weights certified in {result["intervals"]} parameter intervals; '
          f'deepest split {result["deepest_split"]}; {result["seconds"]:.3f}s.')
    print(f'Certified |z_safe\'/z_safe| > 1/10 '
          f'(smallest rational margin ≈ {float(result["log_speed_lower_bound"]):.9f}).')
    print('Since |z_safe| >= 40, its speed is greater than 4 everywhere in the entire family.')
    print('Endpoints are 2/3 and 4/7. Tangent index stays 0; center winding stays +1.')


if __name__ == '__main__':
    main()
