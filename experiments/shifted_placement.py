"""The unique finite total-area optimum for cubic-intercept parabolas.

Monotone ratio shooting locates every slope using rational enclosures.
The proof covers every count and every fixed positive endpoint pair;
finite controls audit the interval arithmetic and independent areas.
The shared solver also supports integer derivative powers; the separate
power_placement.py audits that extension. Only the standard library.
See shifted_placement.md.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from math import comb, isqrt
from pathlib import Path
from random import Random

from blend_cusps import require
from parabolic_balance import Quadratic
from parabolic_tradeoff import serialize
from shifted_parabolas import check, root_bracket, variance_area

HERE = Path(__file__).resolve().parent


def sqrt_bounds(value, bits):
    """Enclose a nonnegative rational square root on a dyadic grid."""
    require(type(value) is Q and value >= 0 and type(bits) is int and bits >= 1,
            "Use a nonnegative rational radicand and positive integer precision.")
    grid = 1 << bits
    numerator = isqrt(value.numerator*grid*grid//value.denominator)
    lower = Q(numerator, grid)
    upper = lower if lower*lower == value else Q(numerator+1, grid)
    require(lower*lower <= value <= upper*upper, "The exact square-root enclosure failed.")
    return lower, upper


def next_ratio(r, bits, power=2):
    """T(r) is strictly increasing for r>=1; its rational bounds are exact."""
    require(type(r) is Q and r >= 1 and type(power) is int and power >= 1
            and type(bits) is int and bits >= 1,
            "Use a rational ratio at least one, a positive integer power, and positive precision.")
    if power == 2:
        low, high = sqrt_bounds(17-4/r-4/(r*r), bits)
        return (low-1)/2, (high-1)/2
    if power == 1:
        exact = 2-1/r
        return exact, exact
    # For f(p)=p^power, stationarity says sum(t^j)+sum(r^-j)
    # =2(power+1). Its t polynomial is increasing and convex on [1,2].
    target = 2*(power+1)-sum(r**(-j) for j in range(power+1))
    def polynomial(t):
        value, derivative = Q(1), Q(0)
        for _ in range(power):
            derivative, value = derivative*t+value, value*t+1
        return value-target, derivative
    lo, hi, grid = Q(1), Q(2), 1 << bits
    while hi-lo > Q(2, grid):
        flo, _ = polynomial(lo)
        fhi, dhi = polynomial(hi)
        require(flo <= 0 <= fhi, "The monotone power-law root lost its bracket.")
        if flo == 0:
            return lo, lo
        if fhi == 0:
            return hi, hi
        chord = lo-flo*(hi-lo)/(fhi-flo)
        tangent = hi-fhi/dhi
        lower = max(lo, Q((chord*grid).__floor__(), grid))
        upper = min(hi, Q((tangent*grid).__ceil__(), grid))
        if lower == lo and upper == hi:
            middle = (lo+hi)/2
            value, _ = polynomial(middle)
            if value <= 0:
                lower = middle
            else:
                upper = middle
        lo, hi = lower, upper
    require(polynomial(lo)[0] <= 0 <= polynomial(hi)[0], "A power-law root has invalid exact signs.")
    return lo, hi


def orbit(initial, gaps, bits, power=2):
    """Enclose all p_j/p_0, including accumulated product roundoff."""
    lo, hi = initial
    require(type(gaps) is int and gaps >= 1 and type(bits) is int and bits >= 8
            and type(lo) is Q and type(hi) is Q and 1 <= lo <= hi,
            "Use an ordered rational initial-ratio interval and a positive gap count.")
    nodes = [(Q(1), Q(1))]
    grid = 1 << bits
    rlo, rhi = lo, hi
    for _ in range(gaps):
        low, high = nodes[-1][0]*rlo, nodes[-1][1]*rhi
        # Outward rounding keeps the fractions short, even for many gaps.
        low = Q((low*grid).__floor__(), grid)
        high = Q((high*grid).__ceil__(), grid)
        nodes.append((low, high))
        rlo = next_ratio(rlo, bits, power)[0]
        rhi = next_ratio(rhi, bits, power)[1]
    return nodes


@lru_cache(maxsize=None)
def variance_coefficients(power):
    """Positive coefficients of E(a,a+g) for f(p)=p^power."""
    return tuple((2*power-i-j, i+j+1,
                  Q(comb(power, i)*comb(power, j)*i*j,
                    2*(i+j+1)*(i+1)*(j+1)))
                 for i in range(1, power+1) for j in range(1, power+1))


def interval_error(left, right, power=2):
    """Positive interval polynomial for E(a,b), when a<b throughout."""
    a, A = left
    b, B = right
    require(0 < a <= A < b <= B, "The interval gap endpoints must be positive and separated.")
    g, G = b-A, B-a
    if power != 2:
        terms = variance_coefficients(power)
        return (sum(c*a**i*g**j for i, j, c in terms),
                sum(c*A**i*G**j for i, j, c in terms))
    q, R = (a+b)/2, (A+B)/2
    return q*q*g**3/6+g**5/360, R*R*G**3/6+G**5/360


def continuous_area(left, right, power=2):
    return ((right**(2*power+1)-left**(2*power+1))/(2*power+1)
            -(right**(power+1)-left**(power+1))**2/((power+1)**2*(right-left)))/2


def partition(gaps, left=Q(1), right=Q(3), bits=80, power=2):
    require(type(gaps) is int and gaps >= 1 and type(bits) is int and bits >= 16
            and type(left) is Q and type(right) is Q and 0 < left < right
            and type(power) is int and power >= 1,
            "Use a positive gap count and integer power, at least 16 bits, and positive ordered rational endpoints.")
    if gaps == 1:
        nodes = [(left, left), (right, right)]
        total = continuous_area(left, right, power)
        return {"gaps": gaps, "endpoints": (left, right), "initial_ratio": (right/left, right/left),
                "nodes": nodes, "deficit": (total, total), "area": (Q(0), Q(0))}
    target = right/left
    relative_span = target-1
    tolerance = min(Q(1), relative_span)*Q(1, 1 << bits)
    lo, hi = Q(1), target
    # Resolve even a span far below one working-grid unit. The tolerance
    # scales with such a span, so adjacent certified nodes still separate.
    narrow = max(0, relative_span.denominator.bit_length()-relative_span.numerator.bit_length())
    work = bits+48+2*gaps.bit_length()+narrow
    while hi-lo > tolerance:
        middle = (lo+hi)/2
        low, high = orbit((middle, middle), gaps, work, power)[-1]
        if high < target:
            lo = middle
        elif low > target:
            hi = middle
        else:
            # This also handles an exact rational shooting root: do not infer
            # a sign from interval overlap or from a rounded midpoint.
            newlo, newhi = max(lo, middle-tolerance/2), min(hi, middle+tolerance/2)
            if (orbit((newlo, newlo), gaps, work, power)[-1][1] < target
                    < orbit((newhi, newhi), gaps, work, power)[-1][0]):
                lo, hi = newlo, newhi
            else:
                work += 32
    require(orbit((lo, lo), gaps, work, power)[-1][1] < target
            < orbit((hi, hi), gaps, work, power)[-1][0],
            "Shooting endpoints must have strictly certified opposite signs.")
    nodes = [(left*a, left*b) for a, b in orbit((lo, hi), gaps, work, power)]
    nodes[0], nodes[-1] = (left, left), (right, right)
    errors = [interval_error(a, b, power) for a, b in zip(nodes, nodes[1:])]
    lower, upper = sum(a for a, _ in errors), sum(b for _, b in errors)
    total = continuous_area(left, right, power)
    return {"gaps": gaps, "endpoints": (left, right), "initial_ratio": (lo, hi),
            "nodes": nodes, "deficit": (lower, upper), "area": (total-upper, total-lower)}


def density_nodes(gaps, bits=96):
    """Rational enclosures of the asymptotic density quantiles on [1,3]."""
    lo, hi = root_bracket(Q(243), 3, Q(6), Q(7), bits)
    out = [(Q(1), Q(1))]
    for j in range(1, gaps):
        low = root_bracket((1+(lo-1)*Q(j, gaps))**3, 5, Q(1), Q(3), bits)[0]
        high = root_bracket((1+(hi-1)*Q(j, gaps))**3, 5, Q(1), Q(3), bits)[1]
        out.append((low, high))
    return out+[(Q(3), Q(3))]


def controls():
    counts = {"root_enclosures": 0, "monotone_ratios": 0, "partitions": 0,
              "clipped_arrangements": 0, "rational_challengers": 0, "invalid": 0}
    random = Random(20261110)
    for bits in (8, 24, 80):
        for i in range(81):
            q = Q(i, 7)
            a, b = sqrt_bounds(q, bits)
            require(a*a <= q <= b*b and b-a <= Q(1, 1 << bits),
                    "A square-root enclosure lost its exact width or sign.")
            counts['root_enclosures'] += 1
    previous = Q(1)
    for i in range(1, 151):
        r = 1+Q(i, 50)
        low, high = next_ratio(r, 80)
        require(previous < low <= high < r and r*(high-1) < r-1,
                "The ratio recurrence lost monotonicity or decreasing physical gaps.")
        previous = high
        counts['monotone_ratios'] += 1
    rows = []
    for gaps in (2, 3, 4, 5, 8, 16, 32, 64, 128):
        row = partition(gaps)
        nodes = row['nodes']
        mid = [(a+b)/2 for a, b in nodes]
        actual = variance_area([(p, p**3/3) for p in mid])
        integrated = sum(((a+b)/2)**2*(b-a)**3/6+(b-a)**5/360
                         for a, b in zip(mid, mid[1:]))
        require(actual == Q(244, 45)-integrated and row['area'][0] <= actual <= row['area'][1],
                "Independent interval integrals miss the full-band area enclosure.")
        for j in range(1, gaps):
            a, p, b = nodes[j-1:j+2]
            # Natural interval bounds on the stationarity polynomial.
            low = 4*p[0]**2-p[1]*(a[1]+b[1])-a[1]**2-b[1]**2
            high = 4*p[1]**2-p[0]*(a[0]+b[0])-a[0]**2-b[0]**2
            require(low <= 0 <= high, "A certified node box excludes its stationarity equation.")
        if gaps == 2:
            best = Quadratic(11, Q(1, 2), Q(1, 2))
            require(nodes[1][0] < best < nodes[1][1]
                    and row['area'][0] < Quadratic(11, Q(-71, 36), Q(11, 6)) < row['area'][1],
                    "Shooting misses the separately known exact three-slope solution.")
        if gaps <= 8:
            require(check([(p, p**3/3) for p in mid]) == actual,
                    "Fresh complete clipping misses a near-optimal arrangement.")
            counts['clipped_arrangements'] += 1
            for _ in range(16):
                challenger = [Q(1)]+sorted(Q(p, 1000) for p in random.sample(range(1001, 3000), gaps-1))+[Q(3)]
                require(variance_area([(p, p**3/3) for p in challenger]) < row['area'][0],
                        "A rational challenger beats the proved global optimum's lower bound.")
                counts['rational_challengers'] += 1
        uniform_deficit = Q(52, 9*gaps*gaps)-Q(16, 45*gaps**4)
        density = density_nodes(gaps)
        density_mid = [(a+b)/2 for a, b in density]
        density_deficit = Q(244, 45)-variance_area([(p, p**3/3) for p in density_mid])
        # This is an audit against the exact density partition's own interval,
        # not a claim that a rational midpoint is the exact quantile.
        dlow = sum(interval_error(a, b)[0] for a, b in zip(density, density[1:]))
        require(row['deficit'][1] < dlow <= density_deficit < uniform_deficit,
                "Finite placement should improve on density quantiles and equal spacing.")
        rows.append({**row, "density_nodes": density, "density_deficit_control": density_deficit,
                     "equal_gap_deficit": uniform_deficit})
        counts['partitions'] += 1
    # Positive endpoint changes and homogeneity: p -> c p multiplies area by c^5.
    base = partition(4, bits=64)
    scaled = partition(4, Q(2), Q(6), bits=64)
    require(scaled['nodes'] == [(2*a, 2*b) for a, b in base['nodes']]
            and scaled['area'] == tuple(32*x for x in base['area']),
            "The cubic family's fifth-power scaling is incorrect.")
    for left, right in ((Q(1, 5), Q(2)), (Q(3), Q(7, 2)), (Q(7), Q(50))):
        row = partition(5, left, right, 64)
        midpoint = [(a+b)/2 for a, b in row['nodes']]
        require(row['area'][0] <= variance_area([(p, p**3/3) for p in midpoint]) <= row['area'][1],
                "A positive endpoint variation misses its exact area interval.")
        counts['partitions'] += 1
    counts['partitions'] += 2
    single = partition(1)
    require(single['area'] == (Q(0), Q(0)) and single['deficit'] == (Q(244, 45), Q(244, 45)),
            "One unsplit gap must leave no bounded pocket.")
    counts['partitions'] += 1
    rational_root = partition(2, Q(2), Q(26), bits=64)
    require(rational_root['nodes'][1][0] < 17 < rational_root['nodes'][1][1],
            "An exact rational midpoint root must trigger a certified bracket, not an inferred sign.")
    narrow = partition(3, Q(1), Q(1)+Q(1, 1 << 120), bits=32)
    require(all(a[1] < b[0] for a, b in zip(narrow['nodes'], narrow['nodes'][1:])),
            "A very narrow positive endpoint span must retain disjoint node enclosures.")
    counts['partitions'] += 2
    for args in ((0,), (True,), (2, Q(0), Q(3)), (2, Q(3), Q(1)), (2, 1, Q(3)), (2, Q(1), Q(3), 8)):
        try:
            partition(*args)
        except ValueError:
            counts['invalid'] += 1
        else:
            raise ValueError('An invalid finite-placement problem was accepted.')
    return counts, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save freshly certified rational enclosures.')
    args = parser.parse_args()
    counts, rows = controls()
    print(', '.join(f'{value} {key.replace("_", " ")}' for key, value in counts.items())+' passed.')
    for row in rows:
        low, high = row['deficit']
        print(f'{row["gaps"]:3} gaps: optimal scaled deficit ≈ {float((low+high)*row["gaps"]**2/2):.12f}; '
              f'certified area interval width < {float(row["area"][1]-row["area"][0]):.3g}.')
    print('Decimal readouts are illustrative; every root sign and saved enclosure uses rational arithmetic.')
    if args.write:
        data = {"scope": "Unique total-area optima of X=Y^2/2-pY+p^3/3 on [1,3], not smallest-pocket optima.",
                "proof": "Monotone ratio shooting plus existence and interior stationarity; shifted_placement.md.",
                "rows": rows}
        (HERE/'shifted_placement.json').write_text(json.dumps(serialize(data), indent=2)+'\n')


if __name__ == '__main__':
    main()
