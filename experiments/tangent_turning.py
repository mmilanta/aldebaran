"""Certify how often an orbital curve's tangent turns, using exact integers.

Run: python3 experiments/tangent_turning.py [--table]
No dependencies beyond Python's standard library. The optional companion plot
uses NumPy and Matplotlib, outside the website's runtime.
"""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from math import atan2, cos, fsum, gcd, pi, sin
import sys


class CertificationError(ValueError):
    """The requested partition could not be certified; no count is returned."""


@dataclass(frozen=True)
class Certificate:
    turns: int
    edges: int
    deepest_split: int


def multiply(z, w):
    """Multiply Gaussian integers without converting to floating point."""
    return z[0]*w[0] - z[1]*w[1], z[0]*w[1] + z[1]*w[0]


def certify_turning(outer, inner, radius=65, max_depth=32):
    """Exact winding of z'(t), when disks certify an origin-avoiding homotopy.

    A rational parameter s in [0,1] traces a quarter of the unit circle:
        w = i^q (1 - s^2 + 2is) / (1 + s^2).
    Its angle changes by at most 2 ds. Evaluate z'/i at those rational w's
    exactly, and subdivide until each velocity arc and its chord fit inside
    a disk that excludes zero. The companion note proves the disk bound.

    A zero velocity at an evaluated endpoint, or exhaustion of max_depth,
    raises CertificationError. Failure does not imply a particular index.
    """
    radius = Fraction(radius)
    if not (isinstance(outer, int) and outer >= 2 and
            isinstance(inner, int) and inner >= 1 and radius > 0):
        raise ValueError('Use integer rhythms outer >= 2, inner >= 1, and positive radius.')
    if max_depth < 0:
        raise ValueError('max_depth must be nonnegative.')
    # Scale by radius's denominator so every coefficient is an integer.
    a = 245 * radius.denominator
    b = 140 * outer * radius.denominator
    c = -inner * radius.numerator
    speed_bound = a + 140 * outer**2 * radius.denominator + inner**2 * radius.numerator
    degree = max(outer, inner)
    vertices = []
    deepest = 0

    def vertex(quarter, parameter):
        num, den = parameter.numerator, parameter.denominator
        w = den**2 - num**2, 2*num*den
        for _ in range(quarter):
            w = -w[1], w[0]
        denominator = den**2 + num**2
        powers = [(1, 0)]
        denominators = [1]
        for _ in range(degree):
            powers.append(multiply(powers[-1], w))
            denominators.append(denominators[-1] * denominator)
        # w^(-inner) is conjugate(w)^inner because |w| = 1.
        value = (
            a*w[0]*denominators[degree-1] +
            b*powers[outer][0]*denominators[degree-outer] +
            c*powers[inner][0]*denominators[degree-inner],
            a*w[1]*denominators[degree-1] +
            b*powers[outer][1]*denominators[degree-outer] -
            c*powers[inner][1]*denominators[degree-inner]
        )
        return value, denominators[degree]

    def subdivide(quarter, low, high, depth, start):
        nonlocal deepest
        value, denominator = start
        if value == (0, 0):
            raise CertificationError('The velocity is exactly zero at a partition endpoint.')
        width = high - low
        # |v(low)| > 2 L (high-low), squared and cleared of denominators.
        if ((value[0]**2 + value[1]**2) * width.denominator**2 >
                (2 * speed_bound * width.numerator * denominator)**2):
            vertices.append(value)
            deepest = max(deepest, depth)
            return
        if depth >= max_depth:
            raise CertificationError('The disk bound needs a deeper partition.')
        middle = (low + high) / 2
        subdivide(quarter, low, middle, depth + 1, start)
        subdivide(quarter, middle, high, depth + 1, vertex(quarter, middle))

    for quarter in range(4):
        subdivide(quarter, Fraction(0), Fraction(1), 0, vertex(quarter, Fraction(0)))
    turns = 0
    for p, q in zip(vertices, vertices[1:] + vertices[:1]):
        # Vertex denominators are positive and do not affect signs. These
        # determinants therefore count the rational polygon exactly.
        cross = p[0]*q[1] - p[1]*q[0]
        if p[1] <= 0 < q[1] and cross > 0:
            turns += 1
        elif q[1] <= 0 < p[1] and cross < 0:
            turns -= 1
    return Certificate(turns, len(vertices), deepest)


def sampled_turning(outer, inner, radius=65, steps=24000):
    """Independent floating-point angle sum, used only as a cross-check."""
    velocities = [complex(
        -245*sin(t) - 140*outer*sin(outer*t) - radius*inner*sin(inner*t),
        245*cos(t) + 140*outer*cos(outer*t) - radius*inner*cos(inner*t))
        for t in (2*pi*j/steps for j in range(steps))]
    increments = [atan2((q*p.conjugate()).imag, (q*p.conjugate()).real)
                  for p, q in zip(velocities, velocities[1:] + velocities[:1])]
    return fsum(increments) / (2*pi)


def needle_transitions():
    """Approximate the 14 paired cusp lengths; the fifteenth length is exactly 65.

    F(t) = 245 exp(22it) + 1120 exp(29it) has strictly increasing argument.
    Its 14 positive-real crossings in 0 < t < pi occur when that argument
    equals 2*pi*j. The companion note proves completeness and distinctness.
    These bisections are numerical locations, not the exact certificates above.
    """
    result = []
    for j in range(1, 15):
        low, high = 0, pi
        for _ in range(60):
            t = (low + high) / 2
            phase = 29*t + atan2(-245*sin(7*t), 1120 + 245*cos(7*t))
            if phase < 2*pi*j:
                low = t
            else:
                high = t
        t = (low + high) / 2
        radius = (245*cos(22*t) + 1120*cos(29*t)) / 21
        result.append((radius, t))
    return sorted(result)


def check_last_transition():
    """Exact rational inequalities excluding other stationary points near 65."""
    radius = Fraction(649, 10)
    theta = Fraction(3, 20)
    phi = Fraction(3, 100)
    loss = (1365**2 - (21*radius)**2) / (2*245*1120)
    assert loss < theta**2/2 - theta**4/24
    assert 245*theta / (1120 + 245*(1-theta**2/2)) < phi
    assert 29*theta + 7*phi < 6  # And 6 < 2*pi.
    assert 29 * (phi/29) < 1 and 22 * (phi/29) < 1
    # At every critical radius, the second and third derivatives are independent.
    assert 29 + Fraction(7*5390, 32480-5390) < 42


def atlas():
    """Return certificates for the 321 regular slider pairs, checking identities."""
    result = {}
    for outer in range(2, 16):
        for inner in range(3, 26):
            if (outer, inner) == (8, 21):
                continue  # Its known cusp makes the tangent direction undefined.
            certificate = certify_turning(outer, inner)
            folds = gcd(outer-1, inner+1)
            assert (certificate.turns - 1) % folds == 0
            if 140*outer > 245 + 65*inner:
                assert certificate.turns == outer
            elif 65*inner > 245 + 140*outer:
                assert certificate.turns == -inner
            result[outer, inner] = certificate
    return result


def main():
    certificates = atlas()
    for pair, name in [((7, 13), 'Garden'), ((7, 14), 'Clover'),
                       ((6, 9), 'Star'), ((9, 23), 'Crown'), ((2, 25), 'A negative total')]:
        print(f'{name:16} {pair[0]:2}/{pair[1]:2}: tangent turns {certificates[pair].turns:+d}')
    assert {pair: certificates[pair].turns for pair in [(7, 13), (7, 14), (6, 9), (9, 23), (2, 25)]} == {
        (7, 13): 1, (7, 14): 1, (6, 9): 6, (9, 23): -15, (2, 25): -25}
    try:
        certify_turning(8, 21)
    except CertificationError as error:
        print(f'Needle           8/21: {error}')
    else:
        raise AssertionError('A cusp must not receive a tangent index.')
    before = certify_turning(8, 21, Fraction(649, 10))
    after = certify_turning(8, 21, Fraction(651, 10))
    assert before.turns == -20 and after.turns == -21
    print(f'Inner length 64.9 -> 65.1: tangent turns {before.turns} -> {after.turns}.')
    check_last_transition()
    transitions = needle_transitions()
    assert 14 == len(transitions) and all(Fraction(125, 3) < r < 65 for r, _ in transitions)
    # Check one rational radius in every predicted regular interval, independent
    # of the phase bisection and crossing-count formula used to predict the index.
    endpoints = [Fraction(40)] + [Fraction(str(r)) for r, _ in transitions] + [Fraction(65), Fraction(72)]
    for j, (low, high) in enumerate(zip(endpoints, endpoints[1:])):
        radius = Fraction(round(10000 * (low+high)/2), 10000)
        expected = 8 - 2*j if j <= 14 else -21
        assert certify_turning(8, 21, radius).turns == expected
    print('Needle family: 14 paired critical lengths below 65, then the single cusp at 65.')
    print('Critical lengths in the lens range (approximate): ' +
          ', '.join(f'{r:.9f}' for r, _ in transitions if r >= 58) + ', 65 (exact).')
    differences = [abs(sampled_turning(*pair) - cert.turns) for pair, cert in certificates.items()]
    assert max(differences) < 1e-9
    print(f'321 exact certificates agree with independent sampled angle sums (max error {max(differences):.3g}).')
    print(f'Certified edges: {sum(c.edges for c in certificates.values()):,}; deepest split: {max(c.deepest_split for c in certificates.values())}.')
    counts = Counter(c.turns for c in certificates.values())
    print(f'Zero tangent turns: {counts[0]} regular pairs. Every index is 1 modulo its fold count.')
    if '--table' in sys.argv:
        print('Outer \\ inner: ' + ' '.join(f'{n:3}' for n in range(3, 26)))
        for outer in range(2, 16):
            print(f'{outer:13}: ' + ' '.join(
                f'{certificates[outer, inner].turns:3}' if (outer, inner) in certificates else '  *'
                for inner in range(3, 26)))


if __name__ == '__main__':
    main()
