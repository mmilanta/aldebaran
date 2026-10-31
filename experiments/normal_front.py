"""Certify the two displayed cooriented bitangents with rational arithmetic.

Run: python3 experiments/normal_front.py
Only the standard library is used. Small contraction boxes certify selected
examples, not an exhaustive census of bitangents. See normal_front.md.
"""

from fractions import Fraction as Q
from math import pi, tan

from blend_cusps import Interval as I, require
from phase_unfolding import inverse, sqrt_interval
from rhythm_tangencies import cross, evaluate


# Numerical hints place boxes; no proof decision uses their accuracy.
HINTS = {6: (.16874586467096045, 3.597870435945988),
         8: (.1610406641612784, 3.591708637698189)}


def dot(v, w):
    return v[0]*w[0]+v[1]*w[1]


def equations(quarters, box, inner):
    """Parallel velocities and a common line; Jacobian in circle parameters."""
    weight = Q(inner-6, 2)
    points, velocities, accelerations = [
        [evaluate(q, s, weight, order) for q, s in zip(quarters, box)]
        for order in range(3)]
    p, q = points
    v, w = velocities
    A, B = accelerations
    delta = tuple(x-y for x, y in zip(p, q))
    factors = [I.wrap(2)/(1+s*s) for s in box]
    F = [cross(v, w), cross(delta, v)]
    J = [[factors[0]*cross(A, w), factors[1]*cross(v, B)],
         [factors[0]*cross(delta, A), factors[1]*cross(v, w)]]
    return F, J


def parameters(inner):
    times = HINTS[inner]
    quarters = tuple(int(t/(pi/2)) for t in times)
    center = tuple(Q(str(tan((t-q*pi/2)/2))) for q, t in zip(quarters, times))
    return quarters, center


def certify(quarters, center, inner, radius=Q(1, 10**11)):
    require(inner in (6, 8) and type(inner) is int, 'Choose inner rhythm 6 or 8.')
    require(len(quarters) == len(center) == 2, 'A shared line needs two visits.')
    require(all(type(q) is int and 0 <= q < 4 for q in quarters), 'Invalid circle quarter.')
    require(all(type(s) is Q for s in center) and type(radius) is Q and radius > 0,
            'Use rational centers and a positive rational radius.')
    box = tuple(I(s-radius, s+radius) for s in center)
    require(all(0 < s.low < s.high < 1 for s in box), 'A box leaves its circle quarter.')
    require(quarters[0] < quarters[1] or quarters[0] == quarters[1] and box[0].high < box[1].low,
            'The visits must be distinct and ordered.')
    F, J0 = equations(quarters, tuple(I.wrap(s) for s in center), inner)
    _, J = equations(quarters, box, inner)
    R = inverse([[x.midpoint() for x in row] for row in J0])
    defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(2))
               for j in range(2)] for i in range(2)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 100), 'The bitangent box is not a strong contraction.')
    offsets = [-sum(R[i][k]*F[k] for k in range(2))+
               sum(defect[i][j]*I(-radius, radius) for j in range(2)) for i in range(2)]
    require(all(-radius < x.low <= x.high < radius for x in offsets),
            'The bitangent map does not send its box into the interior.')
    # This proves existence and uniqueness by the contraction theorem.
    weight = Q(inner-6, 2)
    points = [evaluate(q, s, weight) for q, s in zip(quarters, box)]
    velocities = [evaluate(q, s, weight, 1) for q, s in zip(quarters, box)]
    require(dot(*velocities).low > 0, 'The certified tangents are not cooriented.')
    delta = tuple(x-y for x, y in zip(*points))
    distance = sqrt_interval(dot(delta, delta))
    require(distance.low > 500, 'The two points are not separately located.')
    # Distinct points and equal (theta,h) imply unequal slopes. Their
    # difference is the signed separation along the common tangent.
    return {'quarters': quarters, 'center': center, 'radius': radius, 'box': box,
            'norm': norm, 'separation': distance}


def check_evaluation():
    """Compare the two-variable Jacobian with rational central differences.

    The exact rational evaluations also compare zero-radius interval jets
    against the independently implemented frozen circle evaluator.
    """
    from certify_intersections import IntersectionCertificate
    count = 0
    for inner in (6, 8):
        solver = IntersectionCertificate(11, inner, 1)
        try:
            for quarter in range(4):
                for s in (Q(0), Q(1, 7), Q(1, 2), Q(1)):
                    position, _, raw = solver.evaluate(quarter, s)
                    z = evaluate(quarter, s, Q(inner-6, 2))
                    v = evaluate(quarter, s, Q(inner-6, 2), 1)
                    require(all(z[i].low == z[i].high == position[i] for i in range(2)),
                            'The rational position evaluators disagree.')
                    expected_v = (-Q(raw[1], raw[2]), Q(raw[0], raw[2]))
                    require(all(v[i].low == v[i].high == expected_v[i] for i in range(2)),
                            'The rational velocity evaluators disagree.')
                    count += 4
        finally:
            solver.evaluate.cache_clear()
        quarters, center = parameters(inner)
        _, J = equations(quarters, tuple(I.wrap(s) for s in center), inner)
        epsilon = Q(1, 10**8)
        for axis in range(2):
            plus, minus = list(center), list(center)
            plus[axis] += epsilon
            minus[axis] -= epsilon
            Fplus, _ = equations(quarters, tuple(I.wrap(s) for s in plus), inner)
            Fminus, _ = equations(quarters, tuple(I.wrap(s) for s in minus), inner)
            for row in range(2):
                difference = (Fplus[row].low-Fminus[row].low)/(2*epsilon)
                require(abs(difference-J[row][axis].low) < Q(1, 10000),
                        'The analytic bitangent Jacobian disagrees with central differences.')
                count += 1
    return count


def main():
    comparisons = check_evaluation()
    print(f'{comparisons} rational evaluator and Jacobian comparisons passed.')
    for inner in (6, 8):
        proof = certify(*parameters(inner), inner)
        require(proof['norm'] < Q(1, 10**7), 'The advertised contraction bound failed.')
        low, high = (571, 572) if inner == 6 else (546, 547)
        separation = proof['separation']
        require(low < separation.low <= separation.high < high,
                'The advertised point-separation enclosure failed.')
        print(f'11 / {inner}: one unique cooriented bitangent in the selected box; '
              f'{low} < separation < {high}; contraction norm < 1e-7.')
        quarters, center = parameters(inner)
        for bad_quarters, bad_center, radius in [
            (quarters, (center[0]+Q(1, 100), center[1]), Q(1, 10**11)),
            (quarters[::-1], center[::-1], Q(1, 10**11)),
            (quarters, center, Q(-1, 10**11)),
            ((quarters[0], quarters[0]), (center[0], center[0]), Q(1, 10**11))]:
            try:
                certify(bad_quarters, bad_center, inner, radius)
            except ValueError:
                pass
            else:
                raise ValueError('An invalid bitangent control was accepted.')
    print('Shifted, reversed, coincident-visit, and negative-radius controls rejected.')
    print('These are two selected examples, not a census of the conormal fronts.')


if __name__ == '__main__':
    main()
