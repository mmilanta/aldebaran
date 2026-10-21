"""Check the arithmetic and numerics in loop_birth.md with the standard library.

Run with: python3 experiments/loop_birth.py
The accompanying proof establishes existence and uniqueness throughout the
lens; numerical checks alone would not establish those facts.
"""

from fractions import Fraction
from math import fsum, sin


SPAN = 0.05


def position(t, radius):
    x = -2 * fsum([245 * sin(t / 2)**2, 140 * sin(4 * t)**2,
                   radius * sin(10.5 * t)**2])
    y = fsum([245 * sin(t), 140 * sin(8 * t), -radius * sin(21 * t)])
    return x, y


def crossing(radius):
    assert 65 < radius <= 72
    low, high = 0, SPAN
    assert position(high, radius)[1] > 0
    for _ in range(60):
        t = (low + high) / 2
        if position(t, radius)[1] < 0:
            low = t
        else:
            high = t
    return (low + high) / 2


def loop_area(radius, root):
    """Unsigned area, by Simpson integration of X dY over the closed loop."""
    def integrand(t):
        # This form avoids cancellation between the three large velocities.
        dy = fsum([-21 * (radius - 65), -490 * sin(t / 2)**2,
                   -2240 * sin(4 * t)**2, 42 * radius * sin(10.5 * t)**2])
        return position(t, radius)[0] * dy

    intervals = 1024
    h = root / intervals
    odd = fsum(integrand(i * h) for i in range(1, intervals, 2))
    even = fsum(integrand(i * h) for i in range(2, intervals, 2))
    return abs(2 * h / 3 * (integrand(0) + integrand(root) + 4 * odd + 2 * even))


def main():
    t = Fraction(1, 20)
    convexity = -245 - 8960 * 8 + 441 * 58 * 21 * (1 - (21 * t)**2 / 6)
    endpoint = (245 * (t - t**3 / 6) + 140 * (8*t - (8*t)**3 / 6)
                - 72 * (21*t - (21*t)**3 / 6 + (21*t)**5 / 120))
    assert convexity == Fraction(146605557, 400) > 0
    assert endpoint == Fraction(68436697, 16000000) > 0
    print(f'Y double prime / t > {convexity}; Y(.05) >= {endpoint}.')

    for tick in range(580, 721):
        radius = tick / 10
        assert position(0, radius) == (0, 0)
        for sample in range(1, 101):
            time = SPAN * sample / 100
            x, y = position(time, radius)
            mirror = position(-time, radius)
            assert mirror == (x, -y)
            assert x < 0
            if radius <= 65:
                assert y > 0
        if radius > 65:
            root = crossing(radius)
            x, residual = position(root, radius)
            assert 0 < root < SPAN and x < 0 and abs(residual) < 1e-12
            assert position(root / 2, radius)[1] < 0
            assert position((root + SPAN) / 2, radius)[1] > 0
    print('All 141 lengths: reflected branches, smooth half-arcs, expected crossings.')

    width_coefficient = 397635 / 88340
    print(f'Predicted width / delta as delta tends to zero: {width_coefficient:.9f}')
    errors = []
    for delta in [0.1, 0.01, 0.001, 0.0001]:
        radius = 65 + delta
        root = crossing(radius)
        width = -position(root, radius)[0]
        ratio = width / delta
        errors.append(abs(ratio - width_coefficient))
        print(f'delta={delta:.4f}: width / delta = {ratio:.9f}')
    assert all(a > b for a, b in zip(errors, errors[1:]))
    assert errors[-1] < 0.00002

    area_coefficient = (8 / 15) * 18935 * 21**2.5 / 88340**1.5
    print(f'Predicted area / delta^(5/2): {area_coefficient:.9f}')
    errors = []
    for delta in [0.1, 0.01, 0.001, 0.0001]:
        radius = 65 + delta
        area = loop_area(radius, crossing(radius))
        ratio = area / delta**2.5
        errors.append(abs(ratio - area_coefficient))
        print(f'delta={delta:.4f}: area / delta^(5/2) = {ratio:.9f}')
    assert all(a > b for a, b in zip(errors, errors[1:]))
    assert errors[-1] < 0.00001


if __name__ == '__main__':
    main()
