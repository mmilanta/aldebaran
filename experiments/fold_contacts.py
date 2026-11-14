"""Every two-branch tangency while the seven- and fourteenfold arms turn.

Run: python3 experiments/fold_contacts.py [--write]
Standard library only. A one-variable elimination, complete Sturm counts,
and rational local contractions prove the contact census on 0 <= phi <= pi.
This does not classify triple passages. See fold_contacts.md.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from math import pi, tan
from pathlib import Path
from time import monotonic

from arm_detour_events import isolate, quotient
from blend_cusps import (Interval as I, add, bound, derivative, product,
                        require, scale, sturm_sequence, trim, value, variations)
from phase_unfolding import inverse, sqrt_interval
from rhythm_axis import gcd

HERE = Path(__file__).resolve().parent
BITS = 160
# Numerical suggestions only; the exhaustive polynomial proof uses no seeds.
HINTS = {
    7: ((4.135414805966, 3.056947948643, .341592201887*pi),
        (2.519999237409, 1.808820283348, .951535764936*pi)),
    14: ((3.960631470808, 3.563992363130, .914296764567*pi),
         (5.747704515643, 4.953919744825, .962912214409*pi)),
}


def square(p):
    return product(p, p)


def even(p):
    require(all(c == 0 for c in p[1::2]), 'Expected an even polynomial.')
    return trim(p[::2])


@lru_cache(maxsize=2)
def polynomials(d):
    require(type(d) is int and d in (7, 14), 'Use seven or fourteen folds.')
    U = [(Q(1),), (Q(0), Q(2))]
    for _ in range(2, d+1):
        U.append(add(product((0, 2), U[-1]), scale(U[-2], -1)))
    p, q = scale(U[d], 28), scale(U[d-2], 13)
    pp, qq = square(p), square(q)
    delta = add(qq, scale(pp, -1))
    N = add(square(delta), scale(add(pp, qq), -2401))
    H = scale(product(p, q), 4802)
    D = add(scale(pp, 9604), scale(square(add(delta, (-2401,))), -1))
    # 1 - (N/H)^2 = D * (q^2-p^2)^2 / H^2, before cancellation.
    require(add(square(H), scale(square(N), -1)) == product(D, square(delta)),
            'The triangle discriminant identity failed.')
    N, H, D, delta = map(even, (N, H, D, delta))
    common = gcd(N, H)
    N, H = quotient(N, common), quotient(H, common)
    # Odd U's share x=0, an impossible antipodal meeting. Cancel its y factor.
    delta = quotient(delta, gcd(delta, common))
    W = add(product(derivative(N), H), scale(product(N, derivative(H)), -1))
    R = quotient(W, delta)
    R = scale(R, 1/R[-1])
    require(gcd(R, H) == (1,) and gcd(R, delta) == (1,),
            'A critical numerator needs an exceptional-denominator analysis.')
    require(gcd(D, derivative(D)) == (1,) and gcd(delta, derivative(delta)) == (1,)
            and gcd(D, delta) == (1,), 'An endpoint contact needs separate analysis.')
    # If p=0, |q| <= 26 < 49 by the sine recurrence. If q=0,
    # a meeting would require p^2=49^2. Exclude that exactly over C.
    require(gcd(q, add(pp, (-2401,))) == (1,),
            'A zero backward coefficient could support a meeting.')
    # Antipodal visits: p=q=0 for d odd; |p|+|q|=41<49 for d even.
    require(abs(value(p, 0))+abs(value(q, 0)) < 49,
            'Antipodal visits were not excluded.')
    # b -> 0 is the diagonal. The ellipse speed bound keeps it regular.
    require(75*d-40 > 0 and value(D, 1) != 0,
            'The diagonal needs a different local argument.')
    return {'p': p, 'q': q, 'N': N, 'H': H, 'D': D, 'delta': delta, 'R': R}


def root_count(p):
    require(value(p, 0) != 0 and value(p, 1) != 0,
            'A root-count witness meets an endpoint.')
    seq = sturm_sequence(p)
    return variations(seq, Q(0))-variations(seq, Q(1))


def census(d):
    p = polynomials(d)
    critical = []
    rejected = []
    for y in isolate(p['R'], bits=BITS):
        c = bound(p['N'], y)/bound(p['H'], y)
        record = {'y': y, 'cos_phase': c}
        if -1 < c.low <= c.high < 1:
            # A simple R root and nonzero delta,H make a nondegenerate
            # stationary point of C(y), not just a stationary cos(phi).
            bound(derivative(p['R']), y).sign()
            bound(p['delta'], y).sign()
            critical.append(record)
        else:
            require(c.high < -1 or c.low > 1,
                    'A candidate straddles an admissibility boundary.')
            rejected.append(record)
    critical.sort(key=lambda r: -r['cos_phase'].midpoint())
    require(len(critical) == 2, 'The two-phase census changed.')
    require(critical[1]['cos_phase'].high < critical[0]['cos_phase'].low,
            'The two event phases are not separated.')
    witnesses = (Q(9, 10), Q(0), Q(-99, 100)) if d == 7 else (
        Q(0), Q(-99, 100), Q(-999, 1000))
    expected = (1, 3, 5) if d == 7 else (5, 7, 9)
    require(witnesses[0] > critical[0]['cos_phase'].high
            and critical[0]['cos_phase'].low > witnesses[1]
            > critical[1]['cos_phase'].high
            and critical[1]['cos_phase'].low > witnesses[2],
            'The witnesses do not separate the event phases.')
    counts = [root_count(add(p['N'], scale(p['H'], -c))) for c in witnesses]
    require(tuple(counts) == expected, 'The crossing-pair Sturm counts changed.')
    # At phase 0 or pi, triangle boundaries contribute one midpoint
    # solution, and feasible delta=0 roots contribute two. The latter
    # have two distinct signs of sin(d a), with the same cos(phi).
    endpoints = {1: 0, -1: 0}
    endpoint_roots = []
    for kind in ('D', 'delta'):
        for y in isolate(p[kind], bits=BITS):
            csign = (bound(p['N'], y)/bound(p['H'], y)).sign()
            feasible = kind == 'D' or bound(p['D'], y).sign() > 0
            if feasible:
                endpoints[csign] += d*(1 if kind == 'D' else 2)
            endpoint_roots.append({'kind': kind, 'y': y,
                                   'phase': '0' if csign > 0 else 'pi',
                                   'feasible': feasible})
    require((endpoints[1], endpoints[-1]) == (d*counts[0], d*counts[-1]),
            'Endpoint crossing counts do not meet the open-phase counts.')
    print(f'{d} folds: {len(critical)+len(rejected)} isolated critical candidates, '
          f'{len(rejected)} rejected; crossing pairs {d*counts[0]} -> '
          f'{d*counts[1]} -> {d*counts[2]}.', flush=True)
    return {'folds': d, 'critical': critical, 'rejected': rejected,
            'witness_cosines': witnesses, 'witness_root_counts': counts,
            'crossing_pairs': [d*k for k in counts],
            'endpoint_pairs': [endpoints[1], endpoints[-1]],
            'endpoint_roots': endpoint_roots}


def circle(quarter, s):
    require(type(quarter) is int and 0 <= quarter < 4, 'Invalid circle quarter.')
    s = I.wrap(s)
    require(0 <= s.low <= s.high <= 1, 'A circle chart left its quarter.')
    den = 1+s*s
    w = (1-s*s)/den, 2*s/den
    for _ in range(quarter):
        w = -w[1], w[0]
    return w


def multiply(z, w):
    return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]


def cross(z, w):
    return z[0]*w[1]-z[1]*w[0]


def dot(z, w):
    return z[0]*w[0]+z[1]*w[1]


def evaluate(d, quarter, s, phase_quarter, phase, order=0, phase_derivative=False):
    require(type(order) is int and 0 <= order <= 2, 'Use t-jet orders zero to two.')
    w, phase_w = circle(quarter, s), circle(phase_quarter, phase)
    powers = [(I.wrap(1), I.wrap(0))]
    for _ in range(d+1):
        powers.append(multiply(powers[-1], w))
    backward = multiply((powers[d-1][0], -powers[d-1][1]), phase_w)
    terms = [(65, -(d-1), backward)]
    if not phase_derivative:
        terms += [(245, 1, powers[1]), (140, d+1, powers[d+1])]
    result = [I.wrap(0), I.wrap(0)]
    for radius, frequency, z in terms:
        for _ in range(order):
            z = -frequency*z[1], frequency*z[0]
        if phase_derivative:
            z = -z[1], z[0]
        for j in range(2):
            result[j] += radius*z[j]
    return tuple(result)


def equations(d, quarters, box):
    s, u, phase = box
    def jets(order=0, motion=False):
        return [evaluate(d, q, x, quarters[2], phase, order, motion)
                for q, x in zip(quarters[:2], (s, u))]
    p, q = jets()
    v, w = jets(1)
    a, b = jets(2)
    m, n = jets(0, True)
    dv, dw = jets(1, True)
    factors = [I.wrap(2)/(1+x*x) for x in box]
    f = [p[0]-q[0], p[1]-q[1], cross(v, w)]
    J = [[v[j]*factors[0], -w[j]*factors[1], (m[j]-n[j])*factors[2]]
         for j in range(2)]
    J.append([cross(a, w)*factors[0], cross(v, b)*factors[1],
              (cross(dv, w)+cross(v, dw))*factors[2]])
    return f, J


def hint_chart(hint):
    quarters = [int(t/(pi/2)) for t in hint]
    centers = [Q(str(tan((t-q*pi/2)/2))) for q, t in zip(quarters, hint)]
    return quarters, centers


def contract(d, quarters, center, radius=Q(1, 10**11)):
    require(len(quarters) == len(center) == 3 and radius > 0,
            'A contact needs two visits, a phase, and a positive radius.')
    require(type(radius) is Q and all(type(c) is Q for c in center),
            'Use exact rational contact centers and radius.')
    require(quarters[0] != quarters[1] or abs(center[0]-center[1]) > 2*radius,
            'Coincident visits are excluded.')
    require(quarters[2] in (0, 1), 'Use a phase in (0,pi).')
    box = [I(c-radius, c+radius) for c in center]
    f, center_J = equations(d, quarters, list(map(I.wrap, center)))
    _, J = equations(d, quarters, box)
    R = inverse([[a.midpoint() for a in row] for row in center_J])
    defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(3))
               for j in range(3)] for i in range(3)]
    norm = max(sum(max(abs(a.low), abs(a.high)) for a in row) for row in defect)
    require(norm < Q(1, 100), 'The contact cube is not a strong contraction.')
    offset = [-sum(R[i][k]*f[k] for k in range(3))
              + sum(defect[i][j]*I(-radius, radius) for j in range(3))
              for i in range(3)]
    require(all(-radius < a.low <= a.high < radius for a in offset),
            'The contraction does not map the cube into its interior.')
    image = [round_interval(center[j]+offset[j], 30) for j in range(3)]
    require(all(box[j].low < x.low <= x.high < box[j].high for j, x in enumerate(image)),
            'Outward rounding left the contraction cube.')
    velocities, accelerations, motions = [
        [evaluate(d, q, x, quarters[2], image[2], order, motion)
         for q, x in zip(quarters[:2], image[:2])]
        for order, motion in ((1, False), (2, False), (0, True))]
    axis = max(range(2), key=lambda j: min(abs(v[j].midpoint()) for v in velocities))
    other = 1-axis
    for v in velocities:
        v[axis].sign()
    slopes = [v[other]/v[axis] for v in velocities]
    alpha = (motions[0][other]-slopes[0]*motions[0][axis]
             - motions[1][other]+slopes[1]*motions[1][axis])
    curvatures = [(a[other]*v[axis]-a[axis]*v[other])/(v[axis]*v[axis]*v[axis])
                  for a, v in zip(accelerations, velocities)]
    beta = curvatures[0]-curvatures[1]
    require((alpha*beta).high < 0, 'This contact does not create a pair as phase grows.')
    direct = dot(*velocities).sign() > 0
    # ds = sqrt(1+slope^2) dX, dn = dg / sqrt(1+slope^2), so
    # the parabolic lens-area coefficient is the same in graph coordinates.
    amag, bmag = alpha*alpha.sign(), beta*beta.sign()
    coefficient = Q(4, 3)*amag*sqrt_interval(2*amag/bmag)
    return {'quarters': quarters, 'center': center, 'radius': radius,
            'box': box, 'root_image': image,
            'contraction_norm': round_interval(norm).high,
            'axis': axis, 'alpha': alpha, 'beta': beta,
            'direct': direct, 'area_coefficient': coefficient,
            'position': evaluate(d, quarters[0], image[0], quarters[2], image[2])}


def round_interval(a, digits=22):
    a = I.wrap(a)
    den = 10**digits
    return I(Q((a.low*den)//1, den), Q(-((-a.high*den)//1), den))


def small_atan(x):
    if x < 0:
        return -small_atan(-x)
    require(x <= Q(1, 2), 'The arctangent series needs range reduction.')
    result = sum((-1)**k*x**(2*k+1)/Q(2*k+1) for k in range(50))
    return I(result, result+x**101/101)


PI = round_interval(16*small_atan(Q(1, 5))-4*small_atan(Q(1, 239)), 40)


def angle(quarter, parameter):
    def endpoint(x):
        return small_atan(x) if x <= Q(1, 2) else PI/4+small_atan((x-1)/(x+1))
    return round_interval(quarter*PI/2+2*I(endpoint(parameter.low).low,
                                       endpoint(parameter.high).high))


def isolate_contact(d, event):
    """A whole-orbit disk admits only the two selected monotone branches.

    The proof covers a continuous phase-chart interval, not just the
    isolated root. It does not classify all crossings inside that window.
    """
    quarters, center = event['quarters'], event['center']
    slots = [(q, c-Q(1, 100), c+Q(1, 100))
             for q, c in zip(quarters[:2], center[:2])]
    require(all(0 < low < high < 1 for _, low, high in slots),
            'An isolation slot crosses a chart boundary.')
    require(slots[0][0] != slots[1][0] or slots[0][2] < slots[1][1]
            or slots[1][2] < slots[0][1], 'The two admitted slots overlap.')
    phase = I(center[2]-Q(1, 10000), center[2]+Q(1, 10000))
    require(all(low < root.low <= root.high < high
                for (_, low, high), root in zip(slots, event['root_image'][:2]))
            and phase.low < event['root_image'][2].low <= event['root_image'][2].high < phase.high,
            'A contact root leaves its admitted slots or phase window.')
    origin = [x.low for x in evaluate(d, quarters[0], center[0], quarters[2], center[2])]
    radius = Q(1)
    require(sum(max(abs(x.low-o), abs(x.high-o))**2
                for x, o in zip(event['position'], origin)) < radius**2,
            'The certified contact is outside its isolation disk.')
    require(dot(event['position'], event['position']).low > 10000,
            'Rotation copies of the contact might coincide at the origin.')
    minimum_speed = None
    for q, low, high in slots:
        signs = []
        for k in range(16):
            s = I(low+(high-low)*Q(k, 16), low+(high-low)*Q(k+1, 16))
            v = evaluate(d, q, s, quarters[2], phase, 1)[event['axis']]
            signs.append(v.sign())
            speed = min(abs(v.low), abs(v.high))
            minimum_speed = speed if minimum_speed is None else min(minimum_speed, speed)
        require(len(set(signs)) == 1, 'An admitted branch is not uniformly monotone.')
    V = 245+140*(d+1)+65*(d-1)
    M = 245+140*(d+1)**2+65*(d-1)**2
    L2 = 4*M+2*V
    # |dz/d(phi-chart)| <= 130; its interval radius is exactly 1/10000.
    motion = Q(13, 1000)
    count = 0

    @lru_cache(maxsize=4096)
    def endpoint(q, s):
        return tuple(x.low for x in evaluate(d, q, s, quarters[2], center[2]))

    def exclude(q, low, high, depth=0):
        nonlocal count
        a, b = endpoint(q, low), endpoint(q, high)
        error = L2*(high-low)**2/8+motion
        rectangles = [(min(a[j], b[j])-error, max(a[j], b[j])+error)
                      for j in range(2)]
        distance2 = sum(max(lo-origin[j], origin[j]-hi, 0)**2
                        for j, (lo, hi) in enumerate(rectangles))
        if distance2 > radius**2:
            count += 1
            return
        require(depth < 16, 'An unselected branch may enter the contact disk.')
        middle = (low+high)/2
        exclude(q, low, middle, depth+1)
        exclude(q, middle, high, depth+1)

    for q in range(4):
        cuts = sorted({Q(k, 256) for k in range(257)} |
                      {x for quarter, low, high in slots if quarter == q for x in (low, high)})
        for low, high in zip(cuts, cuts[1:]):
            if any(quarter == q and a <= low < high <= b for quarter, a, b in slots):
                continue
            exclude(q, low, high)
    print(f'    Whole-orbit disk: {count} excluded arcs; '
          f'two monotone slots, coordinate speed > {int(minimum_speed)}.', flush=True)
    return {'radius': radius, 'origin': origin, 'phase_chart': phase,
            'slots': slots, 'excluded_arcs': count,
            'coordinate_speed_low': round_interval(minimum_speed).low}


def controls():
    """Meaningful failure controls for local proof acceptance and domains."""
    quarters, center = hint_chart(HINTS[7][0])
    shifted = center.copy()
    shifted[2] += Q(1, 100000)
    cases = [(7, quarters, shifted, Q(1, 10**11)),
             (7, [quarters[0], quarters[0], quarters[2]],
              [center[0], center[0], center[2]], Q(1, 10**11)),
             (7, quarters, center, Q(-1)),
             (7, [quarters[0], quarters[1], 2], center, Q(1, 10**11))]
    for d, qs, cs, radius in cases:
        try:
            contract(d, qs, cs, radius)
        except ValueError:
            pass
        else:
            raise ValueError('An invalid contact proof was accepted.')
    for d in (True, 6, 7.0):
        try:
            polynomials(d)
        except ValueError:
            pass
        else:
            raise ValueError('Unsupported fold input was accepted.')
    print('Seven shifted-contact, diagonal, radius, phase, and fold controls rejected.')
    return len(cases)+3


def serialize(obj):
    if isinstance(obj, I):
        a = round_interval(obj)
        return {'low': str(a.low), 'high': str(a.high)}
    if type(obj) is Q:
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [serialize(v) for v in obj]
    return obj


def run():
    results = []
    for d in (7, 14):
        result = census(d)
        result['events'] = []
        for index, hint in enumerate(HINTS[d]):
            quarters, center = hint_chart(hint)
            event = contract(d, quarters, center)
            image = event['root_image']
            wt, ws = [circle(q, x) for q, x in zip(quarters[:2], image[:2])]
            ybox = (1+dot(wt, ws))/2
            # The complete critical list and disjoint y enclosures identify
            # the local root with exactly one global critical phase.
            admissible = result['critical']
            overlaps = [j for j, r in enumerate(admissible)
                        if max(ybox.low, r['y'].low) <= min(ybox.high, r['y'].high)]
            require(overlaps == [index], 'The local contact is not identified globally.')
            event['phase_over_pi'] = angle(quarters[2], image[2])/PI
            event['times'] = [angle(q, x) for q, x in zip(quarters[:2], image[:2])]
            require(event['direct'] == (index > 0 or d == 14),
                    'The certified travel directions changed.')
            event['isolation'] = isolate_contact(d, event)
            result['events'].append(event)
            print(f'  phase/pi = {float(event["phase_over_pi"].midpoint()):.12f}; '
                  f'{"matching" if event["direct"] else "opposing"} travel; '
                  f'area K ~ {float(event["area_coefficient"].midpoint()):.6f}; '
                  f'contraction < {float(event["contraction_norm"]):.2g}.', flush=True)
        results.append(result)
    checked = controls()
    return {'scope': 'All two-visit tangencies on 0 <= phase <= pi for d=7,14; '
                     'crossing-pair counts, not a triple-passage census.',
            'root_bits': BITS, 'invalid_controls': checked, 'families': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Archive a freshly repeated proof.')
    args = parser.parse_args()
    start = monotonic()
    result = run()
    if args.write:
        (HERE/'fold_contacts.json').write_text(json.dumps(serialize(result), indent=2)+'\n')
    print(f'Complete rational proof passed in {monotonic()-start:.2f}s.')


if __name__ == '__main__':
    main()
