"""Reproduce the small-prime cusp sieve explained in cusp_proof.md.

Run with: python3 experiments/cusp_sieve.py
Only integer arithmetic and the Python standard library are used. The proof
in the companion note justifies each exclusion; counting alone is not proof.
"""

from collections import Counter
from math import gcd


def classify(m, n):
    """Classify a pair within the website's current slider ranges."""
    if not (2 <= m <= 15 and 3 <= n <= 25):
        raise ValueError('This sieve is proved only for the current sliders.')
    if n % 7:
        return 'constant modulo 7'
    k = n // 7
    if m % 7 == 0:
        return 'constant modulo 7 after removing content'
    if ((4 * m) ** 2 - (13 * k) ** 2) % 7:
        return 'coprime binomials modulo 7'
    if m != 13 and (m * m - 25) % 13:
        return 'coprime binomials modulo 13'
    if m == 13:
        assert n == 21
        a, b, c = 28 * m, 49, 13 * n
        assert a % 13 == c % 13 == 0
        assert a % (13 * 13) and c % (13 * 13) and b % 13
        assert a != c  # Not reciprocal up to sign.
        return 'single factor of 13 at both ends'
    if (m, n) == (5, 7):
        # Equality forces w^12 = 1 and w^8 = -1, contradicting w^24.
        assert 4 * m == 7 + 13 * k
        assert (m + n) * 2 == (n + 1) * 3 == 24
        return 'incompatible triangle equality'
    assert (m, n) == (8, 21)
    assert 4 * m + 7 == 13 * k
    assert gcd(m + n, n + 1) == 1
    return 'one cusp at w = 1'


def main():
    counts = Counter(classify(m, n) for m in range(2, 16) for n in range(3, 26))
    expected = {
        'constant modulo 7': 280,
        'constant modulo 7 after removing content': 6,
        'coprime binomials modulo 7': 24,
        'coprime binomials modulo 13': 9,
        'single factor of 13 at both ends': 1,
        'incompatible triangle equality': 1,
        'one cusp at w = 1': 1,
    }
    assert counts == expected
    for reason, count in expected.items():
        print(f'{count:3}  {reason}')
    assert -245 - 140 * 8**2 - 65 * 21**2 == -37870
    assert -245 - 140 * 8**3 + 65 * 21**3 == 530040
    print('322 pairs classified; Needle is the only stationary curve.')
    print('At its cusp: z\u2033(0) = -37870, z\u2034(0) = 530040i.')


if __name__ == '__main__':
    main()
