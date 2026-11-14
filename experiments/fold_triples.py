"""Four selected triple batches on the phase turns, not a complete census.

Run: python3 experiments/fold_triples.py [--write]
Standard library only. Rational four-variable contractions, transverse
tangents, and whole-orbit fourth-branch exclusions certify selected events.
See fold_triples.md. The global triple-passage question remains open.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
import json
from math import pi, tan
from time import monotonic

from blend_cusps import Interval as I, require
from fold_contacts import (HERE, PI, angle, dot, evaluate, inverse,
                           round_interval, serialize)
from triple_area import coefficient, linear_data

# Numerical suggestions only. Each accepted event needs a rational proof.
HINTS = (
    (7, (.2340854602520724, .8976135026882747, 1.5958506835613915), 3.0214292863026118, 1),
    (14, (.12297456568759878, .8826675587790815, 1.2827003309762377), 2.9042527503243547, 1),
    (14, (.010627798311122094, .4133858556152633, .7967466691380778), 3.057897017043672, -1),
    (14, (.03292146815804937, .8325084655235154, 5.939275130195776), 3.0705253777198664, 1),
)


def equations(d, quarters, box):
    phase = box[3]
    points, velocities, motions = [
        [evaluate(d, q, x, quarters[3], phase, order, motion)
         for q, x in zip(quarters[:3], box[:3])]
        for order, motion in ((0, False), (1, False), (0, True))]
    factors = [I.wrap(2)/(1+x*x) for x in box]
    f, J = [], []
    for other in (1, 2):
        for axis in range(2):
            f.append(points[0][axis]-points[other][axis])
            row = [velocities[0][axis]*factors[0], I.wrap(0), I.wrap(0),
                   (motions[0][axis]-motions[other][axis])*factors[3]]
            row[other] = -velocities[other][axis]*factors[other]
            J.append(row)
    return f, J


def chart(times, phase):
    angles = list(times)+[phase]
    quarters = [int(t/(pi/2)) for t in angles]
    centers = [Q(str(tan((t-q*pi/2)/2))) for q, t in zip(quarters, angles)]
    return quarters, centers


def contract(d, quarters, center, radius=Q(1, 10**11)):
    require(type(d) is int and d in (7, 14) and radius > 0 and len(quarters) == len(center) == 4,
            'Use three visits, a phase, supported folds, and a positive radius.')
    require(type(radius) is Q and all(type(c) is Q for c in center),
            'Use exact rational triple centers and radius.')
    require(quarters[3] in (0, 1), 'Use phase between zero and pi.')
    box = [I(c-radius, c+radius) for c in center]
    require(all(quarters[i] < quarters[i+1] or quarters[i] == quarters[i+1]
                and box[i].high < box[i+1].low for i in range(2)),
            'The three visit boxes must be distinct and in orbit order.')
    f, J0 = equations(d, quarters, list(map(I.wrap, center)))
    _, J = equations(d, quarters, box)
    R = inverse([[x.midpoint() for x in row] for row in J0])
    defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(4))
               for j in range(4)] for i in range(4)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 100), 'The triple cube is not a strong contraction.')
    offset = [-sum(R[i][k]*f[k] for k in range(4))
              + sum(defect[i][j]*I(-radius, radius) for j in range(4)) for i in range(4)]
    require(all(-radius < x.low <= x.high < radius for x in offset),
            'The triple contraction does not map the cube into its interior.')
    image = [round_interval(center[j]+offset[j], 30) for j in range(4)]
    require(all(box[j].low < x.low <= x.high < box[j].high for j, x in enumerate(image)),
            'Outward rounding left the triple cube.')
    velocities, motions = [
        [evaluate(d, q, x, quarters[3], image[3], order, motion)
         for q, x in zip(quarters[:3], image[:3])]
        for order, motion in ((1, False), (0, True))]
    determinants, H = linear_data(velocities, motions)
    signs = [x.sign() for x in determinants]
    K = coefficient(velocities, motions)
    require(K.low > 0, 'The triple triangle area coefficient is unresolved.')
    return {'folds': d, 'quarters': quarters, 'center': center,
            'radius': radius, 'root_image': image,
            'contraction_norm': round_interval(norm).high,
            'phase_over_pi': angle(quarters[3], image[3])/PI,
            'times': [angle(q, x) for q, x in zip(quarters[:3], image[:3])],
            'position': evaluate(d, quarters[0], image[0], quarters[3], image[3]),
            'tangent_determinant_signs': signs, 'passage_sign': H.sign(),
            'unfolding_H': H, 'area_coefficient': K}


def isolate(event):
    d, qs, cs = event['folds'], event['quarters'], event['center']
    slots = []
    for q, c in zip(qs[:3], cs[:3]):
        r = min(Q(1, 200), c/2, (1-c)/2)
        require(r > 0, 'An admitted slot crosses a quarter boundary.')
        slots.append((q, c-r, c+r))
    require(all(qa != qb or ha < lb or hb < la
                for (qa, la, ha), (qb, lb, hb) in combinations(slots, 2)),
            'The admitted triple slots overlap.')
    phase = I(cs[3]-Q(1, 10000), cs[3]+Q(1, 10000))
    require(all(lo < x.low <= x.high < hi
                for (_, lo, hi), x in zip(slots, event['root_image'][:3]))
            and phase.low < event['root_image'][3].low <= event['root_image'][3].high < phase.high,
            'The triple root leaves its isolation slots or phase window.')
    origin = [x.low for x in evaluate(d, qs[0], cs[0], qs[3], cs[3])]
    require(sum(max(abs(x.low-o), abs(x.high-o))**2 for x, o in zip(event['position'], origin)) < 1,
            'The triple is outside its unit-radius disk.')
    require(dot(event['position'], event['position']).low > 10000,
            'The rotational triple copies may coincide at the center.')
    minimum_speed = None
    for q, low, high in slots:
        vmid = evaluate(d, q, (low+high)/2, qs[3], cs[3], 1)
        axis = max(range(2), key=lambda j: abs(vmid[j].midpoint()))
        signs = []
        for j in range(64):
            s = I(low+(high-low)*Q(j, 64), low+(high-low)*Q(j+1, 64))
            v = evaluate(d, q, s, qs[3], phase, 1)[axis]
            signs.append(v.sign())
            speed = min(abs(v.low), abs(v.high))
            minimum_speed = speed if minimum_speed is None else min(minimum_speed, speed)
        require(len(set(signs)) == 1, 'An admitted branch is not uniformly monotone.')
    V = 245+140*(d+1)+65*(d-1)
    M = 245+140*(d+1)**2+65*(d-1)**2
    L2 = 4*M+2*V
    count = 0

    @lru_cache(maxsize=4096)
    def endpoint(q, s):
        return tuple(x.low for x in evaluate(d, q, s, qs[3], cs[3]))

    def exclude(q, a, b, depth=0):
        nonlocal count
        p, r = endpoint(q, a), endpoint(q, b)
        error = L2*(b-a)**2/8+Q(13, 1000)
        distance2 = sum(max(min(p[j], r[j])-error-origin[j],
                            origin[j]-max(p[j], r[j])-error, 0)**2 for j in range(2))
        if distance2 > 1:
            count += 1
            return
        require(depth < 16, 'A fourth branch may enter the selected triple disk.')
        mid = (a+b)/2
        exclude(q, a, mid, depth+1)
        exclude(q, mid, b, depth+1)

    for q in range(4):
        cuts = sorted({Q(k, 256) for k in range(257)} |
                      {x for quarter, lo, hi in slots if quarter == q for x in (lo, hi)})
        for lo, hi in zip(cuts, cuts[1:]):
            if any(quarter == q and a <= lo < hi <= b for quarter, a, b in slots):
                continue
            exclude(q, lo, hi)
    return {'radius': Q(1), 'origin': origin, 'slots': slots, 'phase_chart': phase,
            'excluded_arcs': count, 'coordinate_speed_low': round_interval(minimum_speed).low}


def controls():
    d, times, phase, _ = HINTS[0]
    qs, cs = chart(times, phase)
    shifted = cs.copy()
    shifted[3] += Q(1, 100000)
    for quarters, center, radius in ((qs, shifted, Q(1, 10**11)),
                                     ([qs[0]]*3+[qs[3]], [cs[0]]*3+[cs[3]], Q(1, 10**11)),
                                     (qs, cs, Q(-1))):
        try:
            contract(d, quarters, center, radius)
        except ValueError:
            pass
        else:
            raise ValueError('An invalid triple box was accepted.')
    return 3


def run():
    result = []
    for d, times, phase, expected_sign in HINTS:
        qs, cs = chart(times, phase)
        event = contract(d, qs, cs)
        require(event['passage_sign'] == expected_sign, 'The selected triple sign changed.')
        event['isolation'] = isolate(event)
        result.append(event)
        print(f'{d} folds: selected phase/pi ~ {float(event["phase_over_pi"].midpoint()):.12f}, '
              f'sign {expected_sign:+d}, K ~ {float(event["area_coefficient"].midpoint()):.6f}, '
              f'{event["isolation"]["excluded_arcs"]} arcs exclude every fourth branch.', flush=True)
    require(all(a['phase_over_pi'].high < b['phase_over_pi'].low
                for a, b in zip(result[1:], result[2:])), 'The fourteenfold phases are not distinct.')
    return {'scope': 'Four selected ordinary triple batches, not a complete phase-event census.',
            'invalid_controls': controls(), 'events': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Archive fresh local certificates.')
    args = parser.parse_args()
    start = monotonic()
    result = run()
    if args.write:
        (HERE/'fold_triples.json').write_text(json.dumps(serialize(result), indent=2)+'\n')
    print(f'Four selected triple batches certified in {monotonic()-start:.2f}s; completeness remains open.')


if __name__ == '__main__':
    main()
