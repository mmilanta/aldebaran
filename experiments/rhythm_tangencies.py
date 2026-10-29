"""Four reflected pairs of ordinary touches on the 11/6 -> 11/8 blend.

Run: python3 experiments/rhythm_tangencies.py
     python3 experiments/rhythm_tangencies.py --snapshots
Only the standard library is used. Rational contraction boxes certify the
eight selected events and their local area laws. They do not count all
events on the route. See rhythm_tangencies.md.
"""

import argparse
from fractions import Fraction as Q
from math import pi, tan
from time import monotonic

from blend_cusps import Interval as I, require
from phase_unfolding import inverse, sqrt_interval
from rhythm_passages import RhythmBlend, orbit, snapshot
from strangeness import from_faces


# Newton suggestions only. Every claim below must pass rational inequalities.
HINTS = ((.57192015867318, 1.11875422743698, .10386013617856),
         (.98278579484950, 5.86606571110834, .32297509657704),
         (1.46428697263621, 2.89841222710463, .39371013549163),
         (2.46898037673606, 3.00811456812421, .86394091539713))
EXPECTED_COEFFICIENTS = ((5073452, 5073453), (511945, 511946),
                         (2364817, 2364818), (924950, 924951))
EXPECTED_SIDE = (-1, 1, -1, 1)
EXPECTED_DIRECT = (True, False, False, True)


def cross(p, q):
    return p[0]*q[1]-p[1]*q[0]


def multiply(p, q):
    return p[0]*q[0]-p[1]*q[1], p[0]*q[1]+p[1]*q[0]


def evaluate(quarter, s, weight, order=0, weight_derivative=False):
    """Interval t-jets on a rational unit-circle chart, without trig floats.

    exp(it) = i^quarter (1+is)^2/(1+s^2), 0 <= s <= 1.
    `order` differentiates in t, not s. Weight derivatives are exact since
    the family is affine in weight. The interval powers enclose all inputs.
    """
    require(type(quarter) is int and 0 <= quarter < 4, 'Invalid circle quarter.')
    require(type(order) is int and 0 <= order <= 3, 'Use a t-jet order from zero to three.')
    s, weight = I.wrap(s), I.wrap(weight)
    require(0 <= s.low <= s.high <= 1, 'A circle chart left [0,1].')
    require(0 <= weight.low <= weight.high <= 1, 'A weight left [0,1].')
    denominator = 1+s*s
    w = ((1-s*s)/denominator, 2*s/denominator)
    for _ in range(quarter):
        w = -w[1], w[0]
    powers = [(I.wrap(1), I.wrap(0))]
    for _ in range(11):
        powers.append(multiply(powers[-1], w))
    terms = ((-6, I.wrap(-65)), (-8, I.wrap(65))) if weight_derivative else (
        (1, I.wrap(245)), (11, I.wrap(140)), (-6, 65*(1-weight)), (-8, 65*weight))
    result = [I.wrap(0), I.wrap(0)]
    for k, radius in terms:
        x, y = powers[abs(k)]
        if k < 0:
            y = -y
        for _ in range(order):
            x, y = -k*y, k*x
        result[0] += radius*x
        result[1] += radius*y
    return tuple(result)


def equations(quarters, box):
    """Equal position and parallel raw t-velocities; Jacobian in (s,u,a)."""
    s, u, weight = box
    points, velocities, accelerations, motions, changes = [
        [evaluate(q, x, weight, order, derivative) for q, x in zip(quarters, (s, u))]
        for order, derivative in ((0, False), (1, False), (2, False),
                                  (0, True), (1, True))]
    p, q = points
    v, w = velocities
    A, B = accelerations
    factor_s, factor_u = [I.wrap(2)/(1+x*x) for x in (s, u)]
    F = [p[0]-q[0], p[1]-q[1], cross(v, w)]
    J = [[v[axis]*factor_s, -w[axis]*factor_u, motions[0][axis]-motions[1][axis]]
         for axis in range(2)]
    J.append([cross(A, w)*factor_s, cross(v, B)*factor_u,
              cross(changes[0], w)+cross(v, changes[1])])
    return F, J


def parameters(hint, reflected=False):
    t, u, weight = hint
    if reflected:
        t, u = 2*pi-u, 2*pi-t
    quarters = [int(x/(pi/2)) for x in (t, u)]
    return quarters, [Q(str(tan((x-q*pi/2)/2))) for q, x in zip(quarters, (t, u))]+[Q(str(weight))]


def certify_box(quarters, center, radius=Q(1, 10**11)):
    require(len(quarters) == 2 and len(center) == 3, 'A touch needs two visits and one weight.')
    require(all(type(x) is Q for x in center) and type(radius) is Q and radius > 0,
            'Use exact rational centers and a positive rational radius.')
    box = [I(x-radius, x+radius) for x in center]
    require(quarters[0] < quarters[1] or quarters[0] == quarters[1] and box[0].high < box[1].low,
            'The two visit boxes must be distinct and in orbit order.')
    F, center_J = equations(quarters, [I.wrap(x) for x in center])
    _, J = equations(quarters, box)
    R = inverse([[x.midpoint() for x in row] for row in center_J])
    defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(3))
               for j in range(3)] for i in range(3)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 100), 'The touch box is not a strong contraction.')
    offsets = [-sum(R[i][k]*F[k] for k in range(3))
               + sum(defect[i][j]*I(-radius, radius) for j in range(3)) for i in range(3)]
    require(all(-radius < x.low <= x.high < radius for x in offsets),
            'The touch contraction does not map the box into its interior.')

    velocities = [evaluate(q, x, box[2], 1) for q, x in zip(quarters, box[:2])]
    accelerations = [evaluate(q, x, box[2], 2) for q, x in zip(quarters, box[:2])]
    motions = [evaluate(q, x, box[2], 0, True) for q, x in zip(quarters, box[:2])]
    # Use the better-conditioned physical coordinate as the graph variable.
    axis = max(range(2), key=lambda j: min(abs(v[j].midpoint()) for v in velocities))
    other = 1-axis
    for v in velocities:
        v[axis].sign()
    slopes = [v[other]/v[axis] for v in velocities]
    alpha = (motions[0][other]-slopes[0]*motions[0][axis]
             - motions[1][other]+slopes[1]*motions[1][axis])
    curvatures = [(A[other]*v[axis]-A[axis]*v[other])/(v[axis]*v[axis]*v[axis])
                  for v, A in zip(velocities, accelerations)]
    beta = curvatures[0]-curvatures[1]
    alpha_sign, beta_sign = alpha.sign(), beta.sign()
    magnitude = alpha*alpha_sign
    coefficient = Q(4, 3)*magnitude*sqrt_interval(2*magnitude/(beta*beta_sign))
    direct = (velocities[0][axis]*velocities[1][axis]).sign() > 0
    return {'quarters': quarters, 'center': center, 'box': box, 'norm': norm,
            'axis': axis, 'alpha': alpha, 'beta': beta, 'coefficient': coefficient,
            'pocket_side': -alpha_sign*beta_sign, 'direct': direct,
            'position': evaluate(quarters[0], box[0], box[2])}


def certify_event(index, reflected=False):
    proof = certify_box(*parameters(HINTS[index], reflected))
    C = proof['coefficient']
    low, high = [Q(x, 100) for x in EXPECTED_COEFFICIENTS[index]]
    require(low < C.low <= C.high < high, 'The advertised lens-area coefficient enclosure failed.')
    require(proof['pocket_side'] == EXPECTED_SIDE[index], 'The pocket opens on the wrong side.')
    require(proof['direct'] == EXPECTED_DIRECT[index], 'The branch directions changed.')
    require(proof['norm'] < Q(23, 10**8), 'The advertised contraction bound failed.')
    weight = proof['box'][2]
    scale = 10**12
    low_weight = weight.low*scale
    high_weight = weight.high*scale
    lo = low_weight.numerator//low_weight.denominator
    hi = -(-high_weight.numerator//high_weight.denominator)
    weight_text = f'({lo//scale}.{lo%scale:012d}, {hi//scale}.{hi%scale:012d})'
    print(f'Touch {index+1}, {"below" if reflected else "above"}: '
          f'a in {weight_text}; '
          f'contraction norm (rounded) {float(proof["norm"]):.3g}; '
          f'{float(low):.2f} < K < {float(high):.2f}; '
          f'pocket {"before" if proof["pocket_side"] < 0 else "after"}, '
          f'{"same" if proof["direct"] else "opposite"} travel directions.')
    return proof


def certify_isolation(index, proof):
    """Exclude every other orbit visit from a disk around the selected touch.

    This covers the WHOLE orbit and the complete displayed weight range.
    The two admitted time slots each have a uniformly monotone physical
    coordinate, so neither slot can supply a third visit. This proves the
    event is an isolated two-branch meeting, not part of a multiple meeting.
    It does not classify all intersections between the two admitted slots.
    """
    center, quarters = proof['center'], proof['quarters']
    weight = I(center[2]-Q(3, 1000), center[2]+Q(3, 1000))
    slots = [(q, s-Q(1, 50), s+Q(1, 50)) for q, s in zip(quarters, center[:2])]
    require(all(0 < low < high < 1 for q, low, high in slots), 'An isolation slot leaves its quarter.')
    origin = [x.midpoint() for x in evaluate(quarters[0], center[0], center[2])]
    radius = (26, 12, 15, 15)[index]
    require(sum(max(abs(x.low-o), abs(x.high-o))**2 for x, o in zip(proof['position'], origin)) < radius**2,
            'The certified contact is outside its isolation disk.')
    axis = proof['axis']
    margins = []
    for q, low, high in slots:
        signs = []
        for k in range(32):
            s = I(low+(high-low)*Q(k, 32), low+(high-low)*Q(k+1, 32))
            v = evaluate(q, s, weight, 1)[axis]
            signs.append(v.sign())
            margins.append(min(abs(v.low), abs(v.high)))
        require(len(set(signs)) == 1, 'A selected isolation slot is not uniformly monotone.')
    solver = RhythmBlend(center[2])
    count = 0

    def exclude(D, depth=0):
        nonlocal count
        raw = solver.bounds(D)
        error = Q(39, 100)  # |z_a| <= 130, complete weight radius = .003
        distance2 = sum(max(raw[2*j]-error-origin[j], origin[j]-raw[2*j+1]-error, 0)**2 for j in range(2))
        if distance2 > radius**2:
            count += 1
            return
        require(depth < 16, 'An unselected visit may enter the contact disk.')
        q, low, high = D
        mid = (low+high)/2
        exclude((q, low, mid), depth+1)
        exclude((q, mid, high), depth+1)

    try:
        for q in range(4):
            cuts = sorted({Q(k, solver.K) for k in range(solver.K+1)} |
                          {x for quarter, low, high in slots if quarter == q for x in (low, high)})
            for low, high in zip(cuts, cuts[1:]):
                if any(quarter == q and a <= low < high <= b for quarter, a, b in slots):
                    continue
                exclude((q, low, high))
    finally:
        solver.evaluate.cache_clear()
    require(min(margins) > 618, 'The advertised isolation-slot speed bound failed.')
    print(f'  Whole-orbit isolation over a0 ± .003: {count} rational arcs stay outside '
          f'radius {radius}; both admitted slots are monotone, |coordinate speed| > {int(min(margins))}.')
    return {'radius': radius, 'arcs': count, 'slots': slots, 'weight': weight, 'origin': origin}


def check_evaluation():
    comparisons = 0
    for a in (Q(0), Q(1, 3), Q(1)):
        curve = RhythmBlend(a)
        try:
            for q in range(4):
                for s in (Q(0), Q(1, 7), Q(2, 3), Q(1)):
                    p, v, _ = curve.evaluate(q, s)
                    for order, expected in ((0, p), (1, tuple(x*(1+s*s)/2 for x in v))):
                        actual = evaluate(q, s, a, order)
                        require(all(x.low == x.high == y for x, y in zip(actual, expected)),
                                'A rational jet differs from the established independent evaluator.')
                        comparisons += 2
                    for order in range(4):
                        first, last = [evaluate(q, s, e, order) for e in (0, 1)]
                        change = evaluate(q, s, a, order, True)
                        actual = evaluate(q, s, a, order)
                        require(all(d.low == d.high == y.low-x.low
                                    and z.low == z.high == (1-a)*x.low+a*y.low
                                    for x, y, d, z in zip(first, last, change, actual)),
                                'An exact affine t-jet comparison failed.')
                        comparisons += 4
        finally:
            curve.evaluate.cache_clear()
    print(f'{comparisons} exact component comparisons of positions, velocities, and affine t-jets.')


def check_controls():
    quarters, center = parameters(HINTS[0])
    shifted = list(center)
    shifted[2] += Q(1, 100000)
    controls = ((quarters, shifted, Q(1, 10**11)),
                ([quarters[0]]*2, [center[0]]*2+[center[2]], Q(1, 10**11)),
                (list(reversed(quarters)), list(reversed(center[:2]))+[center[2]], Q(1, 10**11)),
                (quarters, center, Q(-1, 100)))
    for q, c, r in controls:
        try:
            certify_box(q, c, r)
        except ValueError:
            pass
        else:
            raise ValueError('A shifted event, diagonal, or negative radius was incorrectly certified.')
    print('Shifted-event, coincident-visit, reversed-visit, and negative-radius controls were rejected.')


def snapshots():
    records = []
    for index, hint in enumerate(HINTS):
        center = Q(str(hint[2]))
        ends = [snapshot(center+side*Q(1, 10000), partition=2048) for side in (-1, 1)]
        counts = [end['crossings'] for end in ends]
        expected = ((40, 36), (36, 40), (40, 36), (36, 40))[index]
        require(tuple(counts) == expected and all(end['strangeness'] == 11 for end in ends),
                'A fresh nearby smooth census changed.')
        for end in ends:
            faces = from_faces(end['word'], 2*(len(end['word'])-1)+1)
            minus = 1-sum(k*k*v for k, v in faces.face_counts.items())+sum(k*k for k in faces.indices.values())
            end['J_minus'], end['J_plus'] = minus, minus+end['crossings']
        expected_J = (((-14, -54), (-18, -54)), ((-18, -54), (-18, -58)),
                      ((-18, -58), (-18, -54)), ((-18, -54), (-14, -54)))[index]
        require(tuple((end['J_plus'], end['J_minus']) for end in ends) == expected_J,
                'A nearby Viro winding-square sum changed.')
        print(f'  Touch {index+1} nearby exact-weight snapshots: crossings {counts[0]} -> {counts[1]}, '
              f'J+/J- {expected_J[0]} -> {expected_J[1]}, St = 11 at both. '
              'These are individual snapshots, not a continuous-window census.')
        records.append(ends)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshots', action='store_true', help='Also repeat eight nearby smooth censuses.')
    args = parser.parse_args()
    start = monotonic()
    check_evaluation()
    check_controls()
    for index in range(4):
        proofs = [certify_event(index, reflected) for reflected in (False, True)]
        for proof in proofs:
            certify_isolation(index, proof)
        first, second = [p['coefficient'] for p in proofs]
        require(max(first.low, second.low) < min(first.high, second.high),
                'Reflected area coefficient intervals do not overlap.')
    if args.snapshots:
        snapshots()
    print(f'Eight selected ordinary tangencies and local area coefficients certified in {monotonic()-start:.2f}s.')
    print('No complete event census of the route or a weight window is claimed here.')


if __name__ == '__main__':
    main()
