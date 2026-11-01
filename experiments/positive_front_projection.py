"""Locate the local model's plane triple, distinct from its front triple.

Exact rational alternating Taylor bounds certify a unique positive x
and its delta. The geometry and uniqueness argument are in
positive_front.md. This is the three-arc local model, not a global
plane-route event census. Standard library only.
"""

from fractions import Fraction as Q
from math import factorial

from blend_cusps import Interval as I, require


def f(x):
    return x * (15 + x * x * (-10 + 3 * x * x)) / 8


def first(x):
    return Q(15, 8) * (1 - x * x) ** 2


def second(x):
    return -Q(15, 2) * x * (1 - x * x)


def trig(x, cosine=False):
    require(type(x) is Q and 0 <= x <= Q(1, 8), "Use a rational angle in [0,1/8].")
    shift = 0 if cosine else 1
    partial = sum((-1) ** k * x ** (2 * k + shift) / factorial(2 * k + shift) for k in range(12))
    remainder = x ** (24 + shift) / factorial(24 + shift)
    # Twelve terms end with a negative term; the next one is positive.
    return I(partial, partial + remainder)


def equation(x, offset):
    return (f(x) - offset) * trig(x) + first(x) * trig(x, True)


def certify(offset, bits=60):
    require(type(offset) is int and offset >= 25, "Use an integer offset at least 25.")
    require(type(bits) is int and bits >= 40, "Use at least forty rational bisections.")
    low, high = Q(0), Q(1, 8)
    require(equation(low, offset).low > 0 and equation(high, offset).high < 0, "The triple bracket failed.")
    for _ in range(bits):
        middle = (low + high) / 2
        result = equation(middle, offset)
        if result.low > 0:
            low = middle
        else:
            require(result.high < 0, "Taylor terms do not determine a bisection sign.")
            high = middle
    require(equation(low, offset).low > 0 and equation(high, offset).high < 0, "The final exact sign bracket failed.")
    # f increases and f' decreases on this positive interval.
    height = I(f(low), f(high))
    slope = I(first(high), first(low))
    half_sine = I(trig(low / 2).low, trig(high / 2).high)
    half_cosine = I(trig(high / 2, True).low, trig(low / 2, True).high)
    delta = height - slope * half_sine / half_cosine
    require(0 < low < high < Q(1, 8), "The normal separation left its positive bracket.")
    require(0 < delta.low <= delta.high < Q(1, 4), "The plane triple lies outside the model's controls.")
    require(delta.high - delta.low < Q(1, 10**15), "The delta enclosure is too wide.")
    # Absolute four-variable triple-equation determinant, in variables
    # (x_outer, x_middle, x_other_outer, delta). Reflection makes the two
    # outer speed factors equal; sin(2x)=2 sin(x) cos(x) stays positive.
    outer_radius = offset - height - I(second(high), second(low))
    middle_radius = offset + 5 * delta
    sine = I(trig(low).low, trig(high).high)
    cosine = I(trig(high, True).low, trig(low, True).high)
    determinant = outer_radius * outer_radius * middle_radius * 2 * sine * cosine
    require(outer_radius.low > 0 and determinant.low > 0, "The ordinary triple determinant is not separated from zero.")
    return I(low, high), delta


def decimal_enclosure(interval, places=15):
    scale = 10 ** places
    low = (interval.low * scale) // 1
    high = -((-interval.high * scale) // 1)
    return f"({low // scale}.{low % scale:0{places}d}, {high // scale}.{high % scale:0{places}d})"


def main():
    require(trig(Q(0)).low == trig(Q(0)).high == 0, "The sine origin changed.")
    require(trig(Q(0), True).low == trig(Q(0), True).high == 1, "The cosine origin changed.")
    for bad in (0, 24, 25.0, True):
        try:
            certify(bad)
        except ValueError:
            pass
        else:
            raise ValueError("An invalid offset control was accepted.")
    for offset in (25, 100, 1000):
        angle, delta = certify(offset)
        if offset == 25:
            require(Q("0.074448001102865") < angle.low <= angle.high < Q("0.074448001102866"), "The advertised angle enclosure changed.")
            require(Q("0.070019709433310") < delta.low <= delta.high < Q("0.070019709433311"), "The advertised delta enclosure changed.")
        print(f"M={offset}: x in {decimal_enclosure(angle)}; delta in {decimal_enclosure(delta)}.")
        print(f"  M*delta in {decimal_enclosure(delta * offset, 12)}; the limit is 225/128.")
    print("The unique local plane triple has normal angles x, 0, -x, all distinct. The front triple remains at delta=0.")
    print("Analytic monotonicity gives uniqueness; rational Taylor signs certify the brackets and a nonzero four-variable triple determinant. The full plane route is not counted.")


if __name__ == "__main__":
    main()
