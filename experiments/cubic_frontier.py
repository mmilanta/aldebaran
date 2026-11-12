"""The complete four-curve cubic total/minimum frontier on [1,3].

Exact Bernstein bounds localize every relevant competitor to a rectangle
where total area is strictly concave. Positive constraint supports then
prove two complete branches, with one algebraic switch. Further curvature
signs select every linear-area price. Standard library only; see
cubic_frontier.md. Numerical samples are controls, not the proof.
"""

import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from math import comb
from pathlib import Path
from random import Random

from blend_cusps import (Interval as I, add, bound, isolate_roots,
                        product, remainder, require, scale, value)
from cubic_maximin import (at, constant, diff, enclose, face_polynomials,
                           optimum, plus, power, scaled, serialize, times)
from parabolic_balance import Quadratic
from shifted_maximin import check_arrangement, run_area
from shifted_parabolas import variance_area
from shifted_placement import partition, sqrt_bounds

HERE = Path(__file__).resolve().parent
BOX = ((Q(11, 8), Q(2)), (Q(23, 10), Q(14, 5)))
EQUAL_BOX = ((Q(163, 100), Q(183, 100)), (Q(49, 20), Q(131, 50)))
FIRST_BOX = ((Q(91, 50), Q(46, 25)), (Q(49, 20), Q(247, 100)))
SWITCH = tuple(map(Q, (28832, 24585, -12250, -7528, 148, 461, 52)))
F = tuple(Q(c, 9) for c in (-48, 40, 13, -4, -1))
SAMPLES = tuple(map(Q, ('1.828', '1.826', '1.825', '1.8', '1.75',
                        '1.7', '1.65', '1.631')))


def precision(bits):
    require(type(bits) is int and 48 <= bits <= 512,
            'Use an integer precision from 48 through 512 bits.')


class NeedMorePrecision(Exception):
    """A required strict inequality is not yet separated by rational boxes."""


def decided(condition, message):
    if not condition:
        raise NeedMorePrecision(message)


def bernstein_rectangle(p, box):
    """Exact tensor Bernstein coefficients after an affine rectangle map."""
    (xl, xh), (yl, yh) = box
    require(xl < xh and yl < yh and p, 'Use a nonempty polynomial and rectangle.')
    nx, ny = max(i for i, j in p), max(j for i, j in p)
    affine = {}
    for (i, j), c in p.items():
        for a in range(i+1):
            for b in range(j+1):
                affine[a, b] = affine.get((a, b), Q(0))+(
                    c*comb(i, a)*xl**(i-a)*(xh-xl)**a
                    *comb(j, b)*yl**(j-b)*(yh-yl)**b)
    return tuple(tuple(sum(c*Q(comb(i, a), comb(nx, a))*Q(comb(j, b), comb(ny, b))
                           for (a, b), c in affine.items() if a <= i and b <= j)
                       for j in range(ny+1)) for i in range(nx+1))


def positive_certificate(name, p, box):
    coefficients = bernstein_rectangle(p, box)
    require(all(c > 0 for row in coefficients for c in row),
            f'The continuous sign certificate failed: {name}.')
    return {'polynomial': name, 'rectangle': box,
            'bidegree': (len(coefficients)-1, len(coefficients[0])-1),
            'positive_coefficients': sum(map(len, coefficients)),
            'minimum_coefficient': min(c for row in coefficients for c in row),
            'coefficients': coefficients}


def substitute_numerator(p, numerator, denominator):
    """D^d p(x,N/D), so zero remainders prove exact algebraic identities."""
    degree = max(j for i, j in p)
    def raised(a, n):
        out = (Q(1),)
        for _ in range(n):
            out = product(out, a)
        return out
    out = (Q(0),)
    for (i, j), c in p.items():
        term = product(raised(numerator, j), raised(denominator, degree-j))
        out = add(out, (Q(0),)*i+scale(term, c))
    return out


def linear_price_polynomials():
    """Positive numerators make the raw-area price increase with minimum."""
    A, C, B = face_polynomials()
    T = plus(A, C, B)
    ax, ay, bx, by = diff(A, 0), diff(A, 1), diff(B, 0), diff(B, 1)
    J = plus(times(ax, by), scaled(times(ay, bx), -1))
    N = plus(times(bx, by), times(ax, ay), scaled(times(ax, by), -2))
    fx, fy = plus(ax, scaled(bx, -1)), plus(by, scaled(ay, -1))
    second = plus(times(plus(times(diff(N, 0), J), scaled(times(N, diff(J, 0)), -1)), fy),
                  times(plus(times(diff(N, 1), J), scaled(times(N, diff(J, 1)), -1)), fx))
    U, D = scaled(ax, -1), bx
    tyy, txy = diff(diff(T, 1), 1), diff(diff(T, 0), 1)
    first = plus(times(plus(times(diff(U, 0), D), scaled(times(U, diff(D, 0)), -1)), tyy),
                 scaled(times(plus(times(diff(U, 1), D), scaled(times(U, diff(D, 1)), -1)), txy), -1))
    return first, second


@lru_cache(maxsize=1)
def global_certificate():
    A, C, B = face_polynomials()
    T = plus(A, C, B)
    tx, ty = diff(T, 0), diff(T, 1)
    require(tx == diff(A, 0) and ty == diff(B, 1),
            'The two single-insertion total identities failed.')
    x, y = {(1, 0): Q(1)}, {(0, 1): Q(1)}
    ex = plus(scaled(power(x, 2), 4), scaled(times(x, y), -1),
              scaled(x, -1), scaled(power(y, 2), -1), constant(-1))
    ey = plus(power(x, 2), times(x, y), scaled(power(y, 2), -4),
              scaled(y, 3), constant(9))
    require(tx == scaled(times(plus(y, constant(-1)), plus(x, y, constant(1)), ex), Q(-1, 18))
            and ty == scaled(times(plus(constant(3), scaled(x, -1)),
                                   plus(x, y, constant(3)), ey), Q(1, 18)),
            'The insertion-gradient factorizations failed.')
    xx, yy, xy = diff(tx, 0), diff(ty, 1), diff(tx, 1)
    determinant = plus(times(xx, yy), scaled(times(xy, xy), -1))
    ax, ay, bx, by = diff(A, 0), diff(A, 1), diff(B, 0), diff(B, 1)
    J = plus(times(ax, by), scaled(times(ay, bx), -1))
    wa = times(by, plus(bx, scaled(ax, -1)))
    wb = times(ax, plus(ay, scaled(by, -1)))
    require(not plus(times(J, tx), times(wa, ax), times(wb, bx))
            and not plus(times(J, ty), times(wa, ay), times(wb, by)),
            'The continuous two-constraint support identities failed.')
    certificates = [positive_certificate('negative_total_hessian_xx', scaled(xx, -1), BOX),
                    positive_certificate('total_hessian_determinant', determinant, BOX),
                    positive_certificate('triangle_gradient_determinant', J, EQUAL_BOX),
                    positive_certificate('first_branch_C_minus_B', plus(C, scaled(B, -1)), FIRST_BOX)]
    require([c['positive_coefficients'] for c in certificates[:3]] == [12, 49, 64],
            'The main continuous certificates changed size.')
    first_price, second_price = linear_price_polynomials()
    certificates += [positive_certificate('first_branch_linear_price_derivative_numerator', first_price, FIRST_BOX),
                     positive_certificate('second_branch_linear_price_derivative_numerator', second_price, EQUAL_BOX)]
    require([c['positive_coefficients'] for c in certificates[-2:]] == [70, 196],
            'The linear-price certificates changed size.')
    # Any minimum >=1 has F(x)=A+C>=2 and F(y)=B+C>=2.
    # F increases up to (1+sqrt(11))/2 and decreases thereafter.
    localization = {'F_at_left_edge': value(F, BOX[0][0]),
                    'F_at_top_edge': value(F, BOX[1][1]),
                    'A_upper_if_y_at_most_23_over_10': Q(13, 10)**3*Q(28, 5)**2/72,
                    'B_upper_if_x_at_least_2': Q(8, 9)}
    require(localization['F_at_left_edge'] < 2 and localization['F_at_top_edge'] < 2
            and localization['A_upper_if_y_at_most_23_over_10'] < 1
            and localization['B_upper_if_x_at_least_2'] < 1,
            'A localization inequality failed.')
    # The switch is both a best right-hand insertion and F(x)=F(y).
    numerator, denominator = tuple(map(Q, (469, 163, -83, -21))), tuple(map(Q, (-115, 98, 25)))
    for p in (ey, plus(A, scaled(B, -1))):
        require(remainder(substitute_numerator(p, numerator, denominator), SWITCH) == (0,),
                'The switch polynomial misses a defining equation.')
    # Reinterpret the two polynomial variables as midpoint m and half-gap d.
    # F(m-d)-F(m+d) factors by d and a polynomial linear in d^2.
    m, d = x, y
    substituted = plus(*(scaled(times(power(plus(m, scaled(d, -1)), i),
                                     power(plus(m, d), j)), c)
                         for (i, j), c in plus(A, scaled(B, -1)).items()))
    midpoint_factor = scaled(times(d, plus(
        scaled(times(power(d, 2), plus(m, constant(1))), 2),
        scaled(power(m, 3), 2), scaled(power(m, 2), 6),
        scaled(m, -13), constant(-20))), Q(4, 9))
    require(substituted == midpoint_factor, 'The equal-triangle midpoint identity failed.')
    return {'localization': localization, 'continuous_signs': certificates,
            'switch_polynomial_ascending': SWITCH,
            'switch_y_numerator_ascending': numerator,
            'switch_y_denominator_ascending': denominator}


def insertion(a, b, bits):
    lo, hi = sqrt_bounds(17*a*a+2*a*b+17*b*b, bits+16)
    return (a+b+lo)/8, (a+b+hi)/8


def interval_polynomial(p, x, y):
    return I(*enclose(p, (x.low, x.high), (y.low, y.high)))


def pack(name, nodes, branch, multipliers=None):
    A, C, B = [enclose(p, nodes[1], nodes[2]) for p in face_polynomials()]
    return {'name': name, 'branch': branch, 'nodes': nodes, 'face_areas_A_C_B': (A, C, B),
            'smallest_area': (min(A[0], C[0], B[0]), min(A[1], C[1], B[1])),
            'total_area': (A[0]+C[0]+B[0], A[1]+C[1]+B[1]),
            'constraint_multipliers_A_B': multipliers}


@lru_cache(maxsize=None)
def endpoints(bits=96):
    precision(bits)
    proof = global_certificate()
    total = partition(3, bits=bits)
    best = optimum(bits)
    roots = isolate_roots(SWITCH, Q(73, 40), Q(913, 500), bits=bits)
    require(len(roots) == 1, 'The switch bracket must have exactly one simple root.')
    sx = I(*roots[0])
    sy = bound(proof['switch_y_numerator_ascending'], sx)/bound(proof['switch_y_denominator_ascending'], sx)
    rows = [pack('largest total', total['nodes'], 'start'),
            pack('two triangles first tie', [(Q(1), Q(1)), (sx.low, sx.high),
                                             (sy.low, sy.high), (Q(3), Q(3))], 'switch'),
            pack('largest minimum', best['nodes'], 'finish')]
    first, switch, last = rows
    require(last['nodes'][1][1] < switch['nodes'][1][0] < switch['nodes'][1][1] < first['nodes'][1][0]
            and switch['nodes'][2][1] < first['nodes'][2][0] < last['nodes'][2][0],
            'The endpoint order is incorrect.')
    require(first['smallest_area'][0] > 1
            and first['face_areas_A_C_B'][0][0] > first['face_areas_A_C_B'][2][1]
            and first['face_areas_A_C_B'][1][0] > first['face_areas_A_C_B'][2][1],
            'The total optimizer needs just B as its smallest face, above one.')
    require(switch['face_areas_A_C_B'][1][0] > max(a[1] for a in switch['face_areas_A_C_B'][::2]),
            'The switch quadrilateral must be inactive.')
    require(interval_polynomial(diff(face_polynomials()[0], 0), sx, sy).low > 0,
            'The switch must lie before the left insertion optimum.')
    for row in (first, switch):
        require(all(lo < node[0] <= node[1] < hi for node, (lo, hi) in zip(row['nodes'][1:3], FIRST_BOX)),
                'The first branch leaves its certified rectangle.')
    for row in (switch, last):
        require(all(lo < node[0] <= node[1] < hi for node, (lo, hi) in zip(row['nodes'][1:3], EQUAL_BOX)),
                'The equal-triangle branch leaves its certified rectangle.')
    return rows


def sample(x, bits=96):
    """Enclose an interior frontier point at an exact rational first label."""
    precision(bits)
    require(type(x) is Q, 'The first interior label must be an exact rational.')
    while True:
        try:
            return _sample_at_precision(x, bits)
        except NeedMorePrecision as error:
            if bits == 512:
                raise ValueError(f'{error} The calculator reached its 512-bit precision limit.') from None
            bits = min(512, bits+32)


def _sample_at_precision(x, bits):
    """Accept only decided exact predicates; the caller can refine boxes."""
    start, switch, finish = endpoints(bits)
    require(finish['nodes'][1][0] < x < start['nodes'][1][1],
            'Use a first label strictly between the maximin and total labels.')
    decided(finish['nodes'][1][1] < x < start['nodes'][1][0],
            'The label overlaps an endpoint enclosure.')
    decided(not switch['nodes'][1][0] <= x <= switch['nodes'][1][1],
            'The label overlaps the switch enclosure.')
    if x > switch['nodes'][1][1]:
        y = insertion(x, Q(3), bits)
        branch = 'B only'
    else:
        # F is strictly decreasing on this entire y bracket.
        low, high, target = Q(49, 20), Q(131, 50), value(F, x)
        require(value(F, low) > target > value(F, high), 'The equal-F root lost its bracket.')
        while high-low > Q(1, 1 << bits):
            middle = (low+high)/2
            v = value(F, middle)
            if v == target:
                low = high = middle
                break
            if v > target:
                low = middle
            else:
                high = middle
        y, branch = (low, high), 'A and B'
    xx, yy = I.wrap(x), I(*y)
    A, C, B = face_polynomials()
    ax, ay, bx, by = [interval_polynomial(p, xx, yy)
                       for p in (diff(A, 0), diff(A, 1), diff(B, 0), diff(B, 1))]
    if branch == 'B only':
        wa, wb = I.wrap(0), -ax/bx
        decided(wb.low > 0, 'A first-branch constraint multiplier has an undecided sign.')
    else:
        J = ax*by-ay*bx
        wa, wb = by*(bx-ax)/J, ax*(ay-by)/J
        decided(min(wa.low, wb.low, ax.low, -by.high, J.low) > 0,
                'An equal-triangle branch support has an undecided sign.')
    row = pack(f'x={x}', [(Q(1), Q(1)), (x, x), y, (Q(3), Q(3))], branch,
               ((wa.low, wa.high), (wb.low, wb.high)))
    areas = row['face_areas_A_C_B']
    decided(areas[1][0] > max(areas[0][1], areas[2][1])
            and row['smallest_area'][0] > 1, 'The active face ordering is undecided.')
    if branch == 'B only':
        decided(areas[0][0] > areas[2][1], 'The first branch triangle ordering is undecided.')
    else:
        require(max(areas[0][0], areas[2][0]) <= min(areas[0][1], areas[2][1]),
                'The equal triangles have disjoint area enclosures.')
    return dict(row, working_precision_bits=bits)


def controls():
    proof = global_certificate()
    # Reconstruct every tensor Bernstein identity at independently chosen
    # rational points, then audit complete faces by polygon clipping.
    A, C, B = face_polynomials()
    T = plus(A, C, B)
    tx, ty = diff(T, 0), diff(T, 1)
    xx, yy, xy = diff(tx, 0), diff(ty, 1), diff(tx, 1)
    polys = (scaled(xx, -1), plus(times(xx, yy), scaled(times(xy, xy), -1)),
             plus(times(diff(A, 0), diff(B, 1)), scaled(times(diff(A, 1), diff(B, 0)), -1)),
             plus(C, scaled(B, -1)))+linear_price_polynomials()
    identities = 0
    random = Random(20261112)
    for p, certificate in zip(polys, proof['continuous_signs']):
        (xl, xh), (yl, yh) = certificate['rectangle']
        nx, ny = certificate['bidegree']
        for _ in range(16):
            u, v = Q(random.randrange(17), 16), Q(random.randrange(17), 16)
            reconstructed = sum(c*comb(nx, i)*u**i*(1-u)**(nx-i)
                                *comb(ny, j)*v**j*(1-v)**(ny-j)
                                for i, row in enumerate(certificate['coefficients']) for j, c in enumerate(row))
            require(reconstructed == at(p, xl+(xh-xl)*u, yl+(yh-yl)*v),
                    'A Bernstein identity does not reconstruct its original polynomial.')
            identities += 1
    rows = [sample(x) for x in SAMPLES]
    count = 0
    for row in rows:
        nodes = [sum(p)/2 for p in row['nodes']]
        points = [(p, p*p*p/3) for p in nodes]
        count += check_arrangement(points, lambda a, b: (2*a, 2*b))
        areas = [run_area(points, i, j)[0] for i, j in ((1, 1), (1, 2), (2, 2))]
        require(areas == [at(p, nodes[1], nodes[2]) for p in (A, C, B)]
                and sum(areas) == variance_area(points), 'A frontier sample misses a complete face or band.')
        require(all(lo <= area <= hi for area, (lo, hi) in zip(areas, row['face_areas_A_C_B'])),
                'A complete clipped face escapes its rational enclosure.')
    ordered = [endpoints()[0]]+rows[:2]+[endpoints()[1]]+rows[2:]+[endpoints()[2]]
    for first, second in zip(ordered, ordered[1:]):
        require(first['smallest_area'][1] < second['smallest_area'][0]
                and first['total_area'][0] > second['total_area'][1],
                'The recorded frontier samples are not strictly ordered.')
    for bits in (48, 64, 128, 192):
        for old, new in zip(endpoints(), endpoints(bits)):
            for a, b in zip(old['nodes'], new['nodes']):
                require(max(a[0], b[0]) <= min(a[1], b[1]), 'Endpoint precisions give disjoint root boxes.')
    # An exact radical point on the second branch, independent of bisection.
    radical = Quadratic(7, Q(0), Q(1))
    x, y = Q(17, 8)-7*radical/40, Q(17, 8)+7*radical/40
    exact = [at(p, x, y) for p in (A, C, B)]
    triangle, single = 288463*radical/512000, Q(2019241, 640000)
    require(exact == [triangle, single-triangle, triangle]
            and exact[1] > triangle
            and endpoints()[2]['nodes'][1][1] < x < endpoints()[1]['nodes'][1][0],
            'The exact radical example leaves the certified tied-triangle branch.')
    # These valid rationals are much closer to the special labels than
    # the default boxes can decide. Refinement must never infer a sign.
    total_fine, switch_fine, finish_fine = endpoints(256)
    delta = Q(1, 2**160)
    near_total, near_switch, near_finish = [sum(row['nodes'][1])/2
                                          for row in (total_fine, switch_fine, finish_fine)]
    close_inputs = (near_total-delta, near_switch+delta, near_switch-delta, near_finish+delta)
    close_rows = [sample(x) for x in close_inputs]
    require(all(row['working_precision_bits'] > 96 for row in close_rows)
            and [row['branch'] for row in close_rows] == ['B only', 'B only', 'A and B', 'A and B'],
            'A close valid rational failed to refine or received the wrong branch.')
    invalid = 0
    for call in (lambda: sample(Q(1)), lambda: sample(Q(2)), lambda: sample(1.75),
                 lambda: endpoints(True), lambda: endpoints(47), lambda: endpoints(513),
                 lambda: positive_certificate('negative control', constant(-1), BOX),
                 lambda: sample(near_total+delta), lambda: sample(near_finish-delta)):
        try:
            call()
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid control was accepted.')
    # A rational inside the final switch box cannot be decided at this
    # resource limit. Reject explicitly, rather than guessing its side.
    cap_input = sum(endpoints(512)[1]['nodes'][1])/2
    try:
        sample(cap_input, bits=512)
    except ValueError as error:
        require('512-bit precision limit' in str(error), 'An unresolved input lost its precision-limit explanation.')
        invalid += 1
    else:
        raise ValueError('An undecided switch input was accepted at the precision cap.')
    return {'Bernstein_identity_controls': identities, 'complete_arrangements': len(rows),
            'clipped_faces': count, 'endpoint_precisions': 5, 'exact_radical_examples': 1,
            'close_rational_refinements': len(close_rows), 'rejected_controls': invalid}


def record():
    return {'scope': 'Complete efficient total-area/smallest-area frontier and unique linear-area and proportional-growth priced maxima for four complete cubic-intercept parabolas, outer labels 1 and 3.',
            'equation': 'X_p(Y)=Y^2/2-pY+p^3/3',
            'parameter_direction': 'First interior label x decreases from total optimum to maximin.',
            'branches': ['B only: y is the best insertion between x and 3.',
                         'A and B: F(x)=F(y), with y above (1+sqrt(11))/2.'],
            'endpoints': endpoints(), 'samples': [sample(x) for x in SAMPLES],
            'exact_radical_example': {
                'representation': 'Each pair (a,b) means a+b*sqrt(7).',
                'nodes': [(Q(1), Q(0)), (Q(17, 8), Q(-7, 40)),
                          (Q(17, 8), Q(7, 40)), (Q(3), Q(0))],
                'face_areas_A_C_B': [(Q(0), Q(288463, 512000)),
                                     (Q(2019241, 640000), Q(-288463, 512000)),
                                     (Q(0), Q(288463, 512000))]},
            'global_certificate': global_certificate()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate exact rational endpoints, samples, and continuous sign certificates.')
    parser.add_argument('--x', type=Q, help='Enclose an interior frontier point at this exact rational first label.')
    args = parser.parse_args()
    query = sample(args.x) if args.x is not None else None
    counts = controls()
    data = record()
    if args.write:
        (HERE/'cubic_frontier.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    print('Complete two-branch frontier: strict total concavity on the localized competitor rectangle.')
    print('Linear-area price proof: 70 + 196 positive Bernstein coefficients; unique optimum at every nonnegative price.')
    print(', '.join(f'{v} {k.replace("_", " ")}' for k, v in counts.items())+'.')
    for row in data['endpoints']+([query] if query is not None else []):
        mid = lambda pair: float(sum(pair)/2)
        print(f'{row["name"]}: x={mid(row["nodes"][1]):.12f}, y={mid(row["nodes"][2]):.12f}; '
              f'min={mid(row["smallest_area"]):.12f}, total={mid(row["total_area"]):.12f}.')
    print('The continuous certificates and positive supports prove the frontier; samples only audit implementation.')


if __name__ == '__main__':
    main()
