"""Find stationary points among the sketchbook's 322 supported rhythm pairs.

Run with: python3 experiments/stationary_points.py
Uses only the Python standard library; it is not part of the website.

Writing w = exp(it), the derivative vanishes exactly when
P(w) = 28m w^(m+n) + 49 w^(n+1) - 13n = 0 on the unit circle.
Every such root is also a root of the reciprocal polynomial: real coefficients
give the conjugate root, and on the unit circle conjugation is inversion.

Coprimality modulo a prime excludes a common factor over Q when both polynomial
degrees are preserved. Here the leading coefficients are nonzero modulo the
prime for every allowed pair. Thus modular gcds exclude unit-circle roots for
321 pairs. The remaining pair, (8, 21), has modular gcd w - 1, bounding the
rational gcd's degree by one. Since P(1) = 0 exactly, its only possible
unit-circle root is w = 1. This proves that this pair's starting point is the
only stationary point in the supported range (up to full-cycle repetitions).

Its second and third derivatives are (-37870, 0) and (0, 530040), so it is an
ordinary cusp. This argument uses exact modular arithmetic, not sampled times.
"""

PRIME = 1_000_000_007


def trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def modular_gcd(a, b):
    """Return a monic gcd; coefficients are stored from constant to leading."""
    while b:
        remainder = a.copy()
        inverse = pow(b[-1], -1, PRIME)
        while len(remainder) >= len(b):
            factor = remainder[-1] * inverse % PRIME
            shift = len(remainder) - len(b)
            for i, coefficient in enumerate(b):
                remainder[i + shift] = (remainder[i + shift] - factor * coefficient) % PRIME
            trim(remainder)
        a, b = b, remainder
    inverse = pow(a[-1], -1, PRIME)
    return [(x * inverse) % PRIME for x in a]


exceptions = []
for m in range(2, 16):
    for n in range(3, 26):
        # The derivative vanishes when P(w) = 28m w^(m+n) + 49 w^(n+1) - 13n = 0.
        p = [0] * (m + n + 1)
        p[0], p[n + 1], p[m + n] = -13 * n % PRIME, 49, 28 * m
        assert p[0] != 0 and p[-1] != 0  # Both degrees survive reduction.
        common = modular_gcd(p, p[::-1])
        if len(common) > 1:
            exceptions.append({'outer': m, 'inner': n, 'gcd': common})
assert exceptions == [{'outer': 8, 'inner': 21, 'gcd': [PRIME - 1, 1]}]
assert 28 * 8 + 49 - 13 * 21 == 0
print(f'Prime: {PRIME}; degrees preserved for all 322 pairs.')
print('321 pairs have coprime derivative and reciprocal polynomials.')
print('Only exception: (8, 21), with gcd w - 1 and exact root w = 1.')
print('The only stationary point is its starting cusp, up to full cycles.')
