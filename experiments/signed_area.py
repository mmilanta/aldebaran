"""Measure signed area and winding for the sketchbook's original arm lengths.

Run with: python3 experiments/signed_area.py
Uses only the Python standard library. The optional companion plot program
requires NumPy and Matplotlib, but neither is used by the website.
"""

from math import atan2, cos, fsum, gcd, hypot, pi, sin


STEPS = 24000


def orbit(m, n, steps=STEPS):
    """A closed polygon, omitting the repeated endpoint."""
    return [(245*cos(t) + 140*cos(m*t) + 65*cos(n*t),
             245*sin(t) + 140*sin(m*t) - 65*sin(n*t))
            for t in (2*pi*j/steps for j in range(steps))]


def exact_area_coefficient(m, n):
    """The continuous signed area divided by pi."""
    return 245**2 + 140**2*m - 65**2*n


def polygon_area_formula(m, n, steps=STEPS):
    """Exact discrete Fourier identity, evaluated in floating-point arithmetic."""
    if steps <= m + n:
        raise ValueError('Use more samples than the largest frequency difference.')
    h = 2*pi/steps
    return steps/2 * (245**2*sin(h) + 140**2*sin(m*h) - 65**2*sin(n*h))


def measure(points):
    pairs = list(zip(points, points[1:] + points[:1]))
    area = fsum(x0*y1 - y0*x1 for (x0, y0), (x1, y1) in pairs) / 2
    angle = fsum(atan2(x0*y1 - y0*x1, x0*x1 + y0*y1)
                 for (x0, y0), (x1, y1) in pairs)
    return area, angle/(2*pi)


def main():
    negative = []
    reaches_inner_circle = 0
    max_area_error = 0
    max_polygon_error = 0
    max_winding_error = 0
    for m in range(2, 16):
        for n in range(3, 26):
            coefficient = exact_area_coefficient(m, n)
            assert coefficient != 0
            if coefficient < 0:
                negative.append((m, n, coefficient))
            points = orbit(m, n)
            area, winding = measure(points)
            discrete = polygon_area_formula(m, n)
            max_polygon_error = max(max_polygon_error, abs(area - discrete))
            max_area_error = max(max_area_error, abs(area - pi*coefficient))
            max_winding_error = max(max_winding_error, abs(winding - 1))
            assert abs(area - discrete) < 1e-5
            assert abs(winding - 1) < 1e-10
            assert min(hypot(x, y) for x, y in points) >= 40 - 1e-10
            # |sin u - u| <= |u|^3/6 bounds the polygon's area error.
            bound = pi*(245**2 + 140**2*m**3 + 65**2*n**3)*(2*pi/STEPS)**2/6
            assert abs(area - pi*coefficient) <= bound + 1e-5
            d = gcd(m-1, n+1)
            if ((m-1)//d) % 2 and ((n+1)//d) % 2:
                t = pi/d
                x = 245*cos(t) + 140*cos(m*t) + 65*cos(n*t)
                y = 245*sin(t) + 140*sin(m*t) - 65*sin(n*t)
                assert abs(hypot(x, y)-40) < 1e-10
                reaches_inner_circle += 1
    assert negative == [(2, 24, -2175), (2, 25, -6400)]
    print('All 322 sampled curves: winding one, vertex radii at least 40.')
    print(f'Negative signed areas (outer, inner, area/pi): {negative}')
    print(f'{reaches_inner_circle} pairs reach radius 40 exactly.')
    print(f'Maximum direct/Fourier polygon-area difference: {max_polygon_error:.3g}')
    print(f'Maximum 24,000-step/continuous area difference: {max_area_error:.6f}')
    print(f'Maximum winding-number error: {max_winding_error:.3g}')


if __name__ == '__main__':
    main()
