"""Check the two-lobe study and optionally draw its standalone SVG.

Run: python3 experiments/two_lobes.py [--figure]
Only Python's standard library is needed. The companion note gives the
algebraic proof; sampled checks here are independent numerical cross-checks.
"""

from math import acos, atan2, cos, fsum, hypot, pi, sin, sqrt
from pathlib import Path
import sys


TAU = 2 * pi
CROSSING_COSINE = (14 - sqrt(1002)) / 26
FIRST = acos(CROSSING_COSINE)
SECOND = TAU - FIRST


def position(t):
    return (245*cos(t) + 140*cos(2*t) + 65*cos(3*t),
            245*sin(t) + 140*sin(2*t) - 65*sin(3*t))


def velocity(t):
    return (-245*sin(t) - 280*sin(2*t) - 195*sin(3*t),
            245*cos(t) + 280*cos(2*t) - 195*cos(3*t))


def primitive(t):
    """Antiderivative of (x y' - y x') / 2."""
    return 43275*t + 51450*sin(t) - 3981.25*sin(4*t) - 910*sin(5*t)


def polygon(start, end, steps):
    return [position(start + (end-start)*j/steps) for j in range(steps)]


def polygon_area(points):
    return fsum(p[0]*q[1] - p[1]*q[0]
                for p, q in zip(points, points[1:] + points[:1])) / 2


def winding_by_angles(points, point):
    vectors = [complex(x-point[0], y-point[1]) for x, y in points]
    return fsum(atan2((q*p.conjugate()).imag, (q*p.conjugate()).real)
                for p, q in zip(vectors, vectors[1:] + vectors[:1])) / TAU


def distance_to_polygon(points, point):
    result = float('inf')
    for a, b in zip(points, points[1:] + points[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        u = max(0, min(1, ((point[0]-a[0])*dx + (point[1]-a[1])*dy) / (dx*dx+dy*dy)))
        result = min(result, hypot(point[0]-a[0]-u*dx, point[1]-a[1]-u*dy))
    return result


def checks():
    # The exact quadratic brackets the only reflected crossing cosine.
    def quadratic(c):
        return 31 + 28*c - 26*c*c
    from fractions import Fraction as F
    assert quadratic(F(-7, 10)) < 0 < quadratic(F(-6, 10))
    assert abs(quadratic(CROSSING_COSINE)) < 1e-13
    a, b = position(FIRST), position(SECOND)
    assert hypot(a[0]-b[0], a[1]-b[1]) < 1e-10
    va, vb = velocity(FIRST), velocity(SECOND)
    assert va[0]*vb[1] - va[1]*vb[0] > 10000
    assert va[0] < 0 < vb[0] and va[1] < 0 and vb[1] < 0

    # Polynomial identity used to exclude every other upward velocity.
    # 39 R(c) - (296c - 1372) = (-39c + 56) P(c).
    # Coefficients are in ascending order, checked as integers.
    P = [5, 56, 78]
    R = [-28, 83, 56, -78]
    product = [0]*4
    for i, v in enumerate(P):
        product[i] += 56*v
        product[i+1] -= 39*v
    assert product == [39*R[0]+1372, 39*R[1]-296, 39*R[2], 39*R[3]]
    assert 19**2 < 394 < 20**2
    # Both roots (-28 +/- sqrt(394))/78 are strictly between -1 and 0.
    assert -78 < -28-20 and -28+20 < 0
    assert -245-560-585 == -1390 and 245-560+585 == 270

    steps = 24000
    orbit = polygon(0, TAU, steps)
    for point, expected in [((0, 0), 1), ((-150, 0), -1), ((-200, 0), 0)]:
        assert abs(winding_by_angles(orbit, point)-expected) < 1e-10
        # These counts also apply to the smooth curve: interpolation and
        # straight homotopy stay away from the chosen point.
        clearance = distance_to_polygon(orbit, point)
        assert clearance > 1390*(TAU/steps)**2/8
        print(f'Point {point}: winding {expected:+d}, clearance {clearance:.6f}.')
    velocity_points = [velocity(TAU*j/steps) for j in range(steps)]
    assert abs(winding_by_angles(velocity_points, (0, 0))) < 1e-10

    loop_area = primitive(SECOND)-primitive(FIRST)
    large_area = 86550*pi-loop_area
    assert loop_area < 0 < large_area
    assert abs(polygon_area(polygon(FIRST, SECOND, steps))-loop_area) < 0.001
    assert abs(polygon_area(polygon(SECOND, TAU+FIRST, steps))-large_area) < 0.01
    assert abs(polygon_area(orbit)-86550*pi) < 0.01
    print(f'Clockwise loop signed area: {loop_area:.9f}.')
    print(f'Large lobe signed area:     {large_area:.9f}.')
    print(f'Total signed area:         {86550*pi:.9f} = 86550 pi.')
    print('Tangent index 0 agrees with an independent velocity angle sum.')


def draw_figure(destination):
    """A static mathematical illustration, including the magnified loop."""
    def main_map(p):
        return 195 + 0.75*p[0], 375 - 0.75*p[1]

    def inset_map(p):
        return 810 + 2*(p[0]+145), 300 - 2*p[1]

    def path(start, end, transform):
        steps = max(1, round((end-start)/TAU*1536))
        points = [transform(position(start+(end-start)*j/steps)) for j in range(steps+1)]
        return ' '.join(f'{"M" if j == 0 else "L"}{x:.3f} {y:.3f}'
                        for j, (x, y) in enumerate(points))

    def arrow(t, transform, length=22):
        x, y = transform(position(t))
        vx, vy = velocity(t)
        speed = hypot(vx, vy)
        dx, dy = vx/speed, -vy/speed
        return (f'<path d="M{x-length*dx/2:.3f} {y-length*dy/2:.3f} '
                f'l{length*dx:.3f} {length*dy:.3f}" class="arrow" marker-end="url(#arrow)"/>')

    large = path(SECOND, TAU+FIRST, main_map)
    small = path(FIRST, SECOND, main_map)
    inset = path(FIRST, SECOND, inset_map)
    crossing_x = main_map(position(FIRST))[0]
    inset_crossing_x = inset_map(position(FIRST))[0]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="740" viewBox="0 0 1000 740" role="img" aria-labelledby="title description">
  <title id="title">Two lobes, two ways to turn</title>
  <desc id="description">Rhythms 2 / 3 make a large gold lobe with winding count plus one and a little blue loop with count minus one. White arrows show their opposite directions. A close-up shows the narrow clockwise loop. Over a whole orbit the curve winds once around the center, while the tangent makes zero net turns.</desc>
  <style>
    text {{ font: 17px ui-sans-serif, system-ui, sans-serif; fill: #c7c7d4; }}
    .title {{ font-size: 29px; font-weight: 600; fill: #f4f1e8; }}
    .label {{ font-size: 24px; fill: #e8b66e; }}
    .small {{ font-size: 15px; fill: #9999ae; }}
    .arrow {{ fill: none; stroke: #f4f1e8; stroke-width: 2; }}
  </style>
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto"><path d="M1 1L9 5L1 9" fill="none" stroke="#f4f1e8" stroke-width="1.5"/></marker></defs>
  <rect width="1000" height="740" rx="20" fill="#101323"/>
  <text x="30" y="45" class="title">Two lobes, two ways to turn</text>
  <text x="970" y="43" text-anchor="end" class="small">ALDEBARAN · 2 / 3</text>
  <rect x="20" y="80" width="580" height="610" rx="14" fill="#0b0e1a" stroke="#383b50"/>
  <path d="{large} Z" fill="#30281e" stroke="#e8b66e" stroke-width="1.6"/>
  <path d="{small} Z" fill="#172c40" stroke="#9fc7eb" stroke-width="1.6"/>
  <path d="M190 375h10 M195 370v10" stroke="#e8b66e"/>
  <text x="207" y="400" class="small">Center</text>
  <text x="330" y="365" class="label">+1</text>
  <circle cx="{crossing_x:.3f}" cy="375" r="3.5" fill="#0b0e1a" stroke="#f4f1e8"/>
  {arrow(0.12*TAU, main_map)}
  {arrow(0.76*TAU, main_map)}
  <text x="45" y="666">The large lobe goes counterclockwise.</text>
  <rect x="630" y="80" width="350" height="445" rx="14" fill="#0b0e1a" stroke="#383b50"/>
  <text x="655" y="115">Inside the little loop</text>
  <path d="{inset} Z" fill="#172c40" stroke="#9fc7eb" stroke-width="1.6"/>
  <text x="788" y="308" class="label" style="fill:#9fc7eb">−1</text>
  <circle cx="{inset_crossing_x:.3f}" cy="300" r="3.5" fill="#0b0e1a" stroke="#f4f1e8"/>
  {arrow(0.44*TAU, inset_map)}
  {arrow(0.56*TAU, inset_map)}
  <text x="655" y="487">The little loop goes clockwise.</text>
  <text x="650" y="568">After the whole orbit:</text>
  <text x="650" y="610" class="label">+1</text><text x="700" y="610">turn around the center</text>
  <text x="650" y="650" class="label" style="fill:#f4f1e8">0</text><text x="700" y="650">net turns of the tangent</text>
  <text x="30" y="721" class="small">Region labels count turns around an interior point. Both panels preserve the shape’s proportions.</text>
</svg>
'''
    destination.write_text(svg)
    print(f'Wrote {destination.name}.')


if __name__ == '__main__':
    checks()
    if '--figure' in sys.argv:
        draw_figure(Path(__file__).with_suffix('.svg'))
