"""A quadratic area law for the two new orbital triple passages.

Run: python3 experiments/triple_area.py
     python3 experiments/triple_area.py --figure
Standard library only. Fresh complete event-window proofs precede the
coefficient enclosures. The finite-offset area checks and figure are numerical.
See triple_area.md for the local theorem and its limits.
"""

import argparse
from fractions import Fraction as Q
from time import monotonic

from blend_cusps import Interval as I, require
from rhythm_passages import (Family, HINTS, HERE, RhythmBlend, WINDOWS,
                             certify_window, check_evaluation, orbit)
from weave_figure import crossing, samples


def cross(p, q):
    return p[0]*q[1]-p[1]*q[0]


def linear_data(velocities, motions):
    D = [cross(velocities[i], velocities[j]) for i, j in ((0, 1), (1, 2), (2, 0))]
    b = [cross(v, w) for v, w in zip(velocities, motions)]
    H = b[0]*D[1]+b[1]*D[2]+b[2]*D[0]
    return D, H


def coefficient(velocities, motions):
    """Area of the triangle cut out by the three lines W_i + span(V_i)."""
    D, H = linear_data(velocities, motions)
    product = D[0]*D[1]*D[2]
    if isinstance(product, I):
        H.sign()
        product *= product.sign()
    else:
        require(product != 0, 'The linearized branches must be pairwise transverse.')
        product = abs(product)
    return H*H/(2*product)


def linear_intersection(p, v, q, w):
    d = (q[0]-p[0], q[1]-p[1])
    along = cross(d, w)/cross(v, w)
    return tuple(x+along*y for x, y in zip(p, v))


def check_algebra():
    V = [(Q(1), Q(0)), (Q(0), Q(1)), (Q(1), Q(-1))]
    W = [(Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(2))]
    count = 0
    for a, b, c, d in ((a, b, c, d) for a in range(1, 4) for b in range(-2, 3)
                        for c in range(-1, 2) for d in range(1, 4) if a*d-b*c):
        transform = lambda p: (a*p[0]+b*p[1], c*p[0]+d*p[1])
        velocities, motions = [list(map(transform, vectors)) for vectors in (V, W)]
        for rescale in ((Q(1), Q(1), Q(1)), (Q(2), Q(-3), Q(5, 7))):
            vs = [tuple(s*x for x in v) for v, s in zip(velocities, rescale)]
            # Add both a common translating frame and branchwise tangential
            # motion. Neither changes the triangle area.
            ws = [tuple(w[axis]+Q(j+1, 3)*v[axis]+(Q(2, 3), Q(-4, 5))[axis]
                        for axis in range(2)) for j, (v, w) in enumerate(zip(vs, motions))]
            P = [linear_intersection(ws[i], vs[i], ws[j], vs[j]) for i, j in ((0, 1), (1, 2), (0, 2))]
            actual = abs(cross(tuple(x-y for x, y in zip(P[1], P[0])),
                               tuple(x-y for x, y in zip(P[2], P[0]))))/2
            require(coefficient(vs, ws) == actual == Q(abs(a*d-b*c), 2),
                    'The line formula disagrees with exact intersection area or coordinate covariance.')
            D, H = linear_data(vs, ws)
            axis = next(i for i in (0, 1) if vs[1][i])
            middle_time_difference = (P[1][axis]-P[0][axis])/vs[1][axis]
            require(middle_time_difference == -H/(D[0]*D[1]),
                    'The middle-branch order does not agree with the signed passage formula.')
            count += 1
    require(coefficient(V, [(Q(0), Q(0))]*3) == 0, 'An unsplit triple should have zero linear area.')
    try:
        coefficient([V[0]]*3, W)
    except ValueError:
        pass
    else:
        raise ValueError('Parallel lines were accepted as an ordinary triple.')
    print(f'{count} exact line-intersection / shoelace checks passed, plus degenerate controls.')


def certify_coefficient(index, proof):
    family = Family(*WINDOWS[index])
    radius = Q(1, 10**12)
    try:
        refined = family.triple_box(proof['parameters'], proof['center'], [radius]*4)
        require(all(A.low < B.low < B.high < A.high
                    for A, B in zip(proof['small']['box'], refined['box'])),
                'The area refinement left the certified event box.')
        curve = RhythmBlend(proof['center'][3])
        velocities, motions = [], []
        for quarter, s in proof['parameters']:
            v = curve.evaluate(quarter, s)[1]
            error = (89990+1820)*radius
            velocities.append([I(x-error, x+error) for x in v])
            motions.append([I(x-1820*radius, x+1820*radius)
                            for x in family.weight_derivative(quarter, s)])
        result = coefficient(velocities, motions)
        _, H = linear_data(velocities, motions)
        require(H.high < 0, 'The local branch formula does not give a negative passage.')
        expected = ((Q(1512205655, 100000), Q(1512205659, 100000)),
                    (Q(3441095224, 100000), Q(3441095230, 100000)))[index]
        require(expected[0] < result.low < result.high < expected[1],
                'The advertised quadratic area coefficient enclosure changed.')
        print(f'Passage {index+1}: {float(result.low):.8f} < K < {float(result.high):.8f} '
              '(rounded printout; rational inequalities passed); H < 0 gives jump -1.')
        return result
    finally:
        family.clear()


def curved_area(index, delta, count=128):
    if delta == 0:
        return 0.
    *times, critical = HINTS[index]
    a = critical+delta
    ab, bc, ac = [crossing(times, a, i, j) for i, j in ((0, 1), (1, 2), (0, 2))]
    points = (samples(ab[1], bc[0], count, a)+samples(bc[1], ac[1], count, a)
              + samples(ac[0], ab[0], count, a))
    origin = orbit(times[0], critical)
    points = [p-origin for p in points]  # avoid subtracting large global areas
    return abs(sum((p.conjugate()*q).imag for p, q in zip(points, points[1:]+points[:1])))/2


def numerical_checks(index, enclosure):
    K = float(enclosure.midpoint())
    previous = [float('inf'), float('inf')]
    for delta in (.003, .001, .0003, .0001, .00003, .00001):
        ratios = []
        for j, sign in enumerate((-1, 1)):
            area = curved_area(index, sign*delta)
            ratio = area/(K*delta*delta)
            require(abs(ratio-1) < previous[j], 'The sampled quadratic-area limit did not improve.')
            previous[j] = abs(ratio-1)
            finer = curved_area(index, sign*delta, 512)
            require(abs(area-finer) < 1e-6*area, 'The numerical area needs finer sampling.')
            ratios.append(ratio)
        print(f'  |delta|={delta:g}: A/(K delta^2) = {ratios[0]:.9f} before, {ratios[1]:.9f} after')
    require(max(previous) < .00011, 'The smallest-offset area ratio is unresolved.')


def figure(coefficients):
    """Plot the finite-offset ratio; no figure predicate enters a proof."""
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">',
           '<title id="title">A triple triangle grows quadratically</title>',
           '<desc id="desc">Two plots show the triangle area divided by squared weight offset. Both approach a finite positive coefficient at the triple event: about 15122.05657 for the first passage and 34410.95227 for the second.</desc>',
           '<rect width="1200" height="650" fill="#101323"/>',
           '<g font-family="system-ui, sans-serif" fill="#f4f1e8">',
           '<text x="40" y="62" font-size="34" font-weight="700">A triple triangle grows quadratically</text>',
           '<text x="40" y="103" font-size="19" fill="#c7c7d4">Area divided by squared distance from the meeting approaches the same limit on either side.</text>']
    for j, enclosure in enumerate(coefficients):
        left, top, width, height = 90+590*j, 205, 450, 295
        K = float(enclosure.midpoint())
        spread = (160., 1300.)[j]
        project = lambda delta, ratio: (left+width*(delta+.003)/.006,
                                       top+height*(K+spread-ratio)/(2*spread))
        svg.append(f'<text x="{left}" y="166" font-size="24">Passage {j+1}</text>')
        svg.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="#0b0e1a" stroke="#383b50"/>')
        for level in (-1, 0, 1):
            y = project(0, K+spread*level)[1]
            svg.append(f'<text x="{left-12}" y="{y+5}" text-anchor="end" font-size="15" fill="#c7c7d4">{K+spread*level:.0f}</text>')
        for delta in (-.003, 0, .003):
            x = project(delta, K)[0]
            svg.append(f'<text x="{x}" y="{top+height+30}" text-anchor="middle" font-size="16" fill="#c7c7d4">{delta:+.3f}</text>')
        x0, y0 = project(0, K)
        svg.append(f'<path d="M{left},{y0} H{left+width}" fill="none" stroke="#e8b66e" stroke-width="1.5" stroke-dasharray="6 5"/>')
        svg.append(f'<path d="M{x0},{top} V{top+height}" fill="none" stroke="#555b78" stroke-width="1"/>')
        coordinates = []
        for k in range(161):
            delta = .003*(k-80)/80
            ratio = K if k == 80 else curved_area(j, delta)/delta**2
            x, y = project(delta, ratio)
            coordinates.append(f'{x:.5f},{y:.5f}')
        svg.append('<path d="M'+' L'.join(coordinates)+'" fill="none" stroke="#9fc7eb" stroke-width="2.4"/>')
        svg.append(f'<circle cx="{x0}" cy="{y0}" r="4.5" fill="#e8b66e"/>')
        svg.append(f'<text x="{left+width/2}" y="{top+height+65}" text-anchor="middle" font-size="18">Signed weight offset δ</text>')
        svg.append(f'<text x="{left}" y="190" font-size="15" fill="#c7c7d4">Area / δ²</text>')
    svg.extend(['<text x="40" y="606" font-size="17" fill="#c7c7d4">Blue: sampled curved triangles. Dashed gold: the certified limiting coefficient K.</text>',
                '<text x="40" y="635" font-size="15" fill="#9999ae">The blue curves are numerical. Rational event boxes separately enclose both limiting coefficients.</text>',
                '</g></svg>'])
    (HERE/'triple_area.svg').write_text('\n'.join(svg)+'\n')
    print('Wrote triple_area.svg (numerical paths, independently certified limiting coefficients).')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true', help='Regenerate the area-ratio SVG.')
    args = parser.parse_args()
    start = monotonic()
    check_algebra()
    check_evaluation()
    coefficients = []
    for index in range(2):
        proofs, _ = certify_window(index)
        enclosure = certify_coefficient(index, proofs[0])
        reflected = certify_coefficient(index, proofs[1])
        require(max(enclosure.low, reflected.low) < min(enclosure.high, reflected.high),
                'The reflected coefficient enclosures do not overlap.')
        numerical_checks(index, enclosure)
        coefficients.append(enclosure)
    if args.figure:
        figure(coefficients)
    print(f'Quadratic coefficients certified; finite-offset numerical checks passed in {monotonic()-start:.2f}s.')


if __name__ == '__main__':
    main()
