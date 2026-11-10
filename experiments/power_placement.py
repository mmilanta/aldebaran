"""Audit finite total-area placement for power-law intercepts.

The written proof covers every real k>0 for h(p)=p^(k+1)/(k+1).
These exact controls cover selected positive integer k, using increasing
polynomial ratio roots, positive interval variances, and full clipping.
Only the standard library; see shifted_placement.md.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from random import Random

from blend_cusps import require
from parabolic_tradeoff import serialize
from shifted_parabolas import check, root_bracket, variance_area
from shifted_placement import continuous_area, interval_error, next_ratio, partition, variance_coefficients

HERE = Path(__file__).resolve().parent


def density_nodes(power, gaps, bits=96):
    # On [1,3], p^((2k+1)/3) is affine in the density coordinate.
    exponent = 2*power+1
    if exponent % 3 == 0:
        lo = hi = Q(3)**(exponent//3)
    else:
        lo, hi = root_bracket(Q(3)**exponent, 3, Q(1), Q(3)**(power+1), bits)
    nodes = [(Q(1), Q(1))]
    for j in range(1, gaps):
        lower = root_bracket((1+(lo-1)*Q(j, gaps))**3, exponent, Q(1), Q(3), bits)[0]
        upper = root_bracket((1+(hi-1)*Q(j, gaps))**3, exponent, Q(1), Q(3), bits)[1]
        nodes.append((lower, upper))
    return nodes+[(Q(3), Q(3))]


def controls():
    random = Random(20261110)
    counts = {"ratio_roots": 0, "partitions": 0, "variance_polynomials": 0,
              "clipped_arrangements": 0, "challengers": 0, "invalid": 0}
    records = []
    for power in (1, 2, 3, 4, 8):
        previous = Q(1)
        for j in range(1, 49):
            r = 1+Q(j, 12)
            lo, hi = next_ratio(r, 80, power)
            target = 2*(power+1)-sum(r**(-i) for i in range(power+1))
            f = lambda t: sum(t**i for i in range(power+1))-target
            require(previous < lo <= hi < 2 and f(lo) <= 0 <= f(hi),
                    "A power-law ratio root misses its polynomial signs or monotonicity.")
            previous = hi
            counts['ratio_roots'] += 1
        for _ in range(24):
            a, g = Q(random.randrange(1, 12), 5), Q(random.randrange(1, 9), 7)
            b = a+g
            integral = ((b**(2*power+1)-a**(2*power+1))/(2*power+1)
                        -(b**(power+1)-a**(power+1))**2/((power+1)**2*g))/2
            expanded = sum(c*a**i*g**j for i, j, c in variance_coefficients(power))
            require(expanded == integral > 0
                    and interval_error((a, a), (b, b), power) == (integral, integral),
                    "A positive variance polynomial disagrees with independent integration.")
            counts['variance_polynomials'] += 1
        for gaps in (2, 3, 4, 8, 16, 32):
            row = partition(gaps, bits=80, power=power)
            nodes = [(a+b)/2 for a, b in row['nodes']]
            points = [(p, p**(power+1)/(power+1)) for p in nodes]
            actual = variance_area(points)
            require(row['area'][0] <= actual <= row['area'][1],
                    "A power-law area enclosure misses its full-band secant variance.")
            if power == 1:
                require(all(lo <= Q(1)+Q(2*j, gaps) <= hi for j, (lo, hi) in enumerate(row['nodes']))
                        and row['area'][0] <= (Q(8)-Q(8, gaps*gaps))/24 <= row['area'][1],
                        "Quadratic intercepts must recover exact equal spacing and area.")
            else:
                require(all(a[0]+c[0] < 2*b[1] and a[1]+c[1] < 2*b[0]
                            for a, b, c in zip(row['nodes'], row['nodes'][1:], row['nodes'][2:])),
                        "Optimal physical gaps must decrease for these convex powers.")
            if gaps <= 4:
                require(check(points) == actual, "Fresh complete power-law clipping misses the band area.")
                counts['clipped_arrangements'] += 1
            for _ in range(12):
                challenger = [Q(1)]+sorted(Q(p, 1000) for p in random.sample(range(1001, 3000), gaps-1))+[Q(3)]
                require(variance_area([(p, p**(power+1)/(power+1)) for p in challenger]) < row['area'][0],
                        "A rational placement beats a certified global maximum's lower bound.")
                counts['challengers'] += 1
            density = density_nodes(power, gaps)
            if power > 1:
                error_low = sum(interval_error(a, b, power)[0] for a, b in zip(density, density[1:]))
                require(row['deficit'][1] < error_low,
                        "The selected finite optimum must improve strictly on its density quantiles.")
            if gaps == 4:
                records.append({"derivative_power": power, "intercept_degree": power+1,
                                **row, "density_nodes": density})
            counts['partitions'] += 1
    for power in (0, -1, True, Q(3, 2), 1.5):
        try:
            partition(4, power=power)
        except ValueError:
            counts['invalid'] += 1
        else:
            raise ValueError('The rational integer-power program accepted an unsupported power.')
    return counts, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save selected freshly certified power-law placements.')
    args = parser.parse_args()
    counts, rows = controls()
    print(', '.join(f'{v} {k.replace("_", " ")}' for k, v in counts.items())+' passed.')
    for row in rows:
        interior = ', '.join(f'{float((a+b)/2):.12f}' for a, b in row['nodes'][1:-1])
        print(f'h(p)=p^{row["intercept_degree"]}/{row["intercept_degree"]}: interior labels ≈ {interior}.')
    if args.write:
        data = {"scope": "Selected finite total-area optima for integer-power intercepts on [1,3]. The written theorem covers every real derivative power k>0.",
                "rows": rows}
        (HERE/'power_placement.json').write_text(json.dumps(serialize(data), indent=2)+'\n')


if __name__ == '__main__':
    main()
