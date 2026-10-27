"""Certify one isolated negative triple passage on the first arm detour.

Run: python3 experiments/triple_passage.py
     python3 experiments/triple_passage.py --figure
Standard library only. The proof covers every time and every weight in
[0.4641, 0.4642], not just its two endpoint drawings. See triple_passage.md.
The original intersection certificate remains unchanged.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from fractions import Fraction as Q
from functools import lru_cache
import io
from math import inf, lcm, nextafter, pi
from time import monotonic

from arm_detour_events import events
from arm_detour_lens import central_radius, certify_lens
from blend_cusps import Interval as I, require
from certify_intersections import IntersectionCertificate
from phase_contact_probe import orbit
from phase_unfolding import FIRST, SECOND, evaluate, sincos
from strangeness import HERE, audit_word, certified_word, from_faces


WEIGHT = I(Q(4641, 10000), Q(2321, 5000))
ROOM = (I(-229, -221), I(-1, 1))
CHARTS = [(Q(-52, 100), Q(-49, 100)), (Q(-1, 100), Q(1, 100)),
          (Q(49, 100), Q(52, 100))]
ZERO = I.wrap(0)
PARTITION = 4096


class DetourCurve(IntersectionCertificate):
    """The rational-circle evaluation for the R=300, 2/3 -> 4/7 leg.

    Reuse the original arc cover and contraction methods, with position,
    derivatives, and analytic bounds appropriate to these five Fourier terms.
    m/n are only progress labels here; no call to the original graph method
    is needed. Initial vertical velocity is 385+20a > 0 on this leg.
    """
    def __init__(self, weight, partition=PARTITION):
        require(isinstance(weight, (int, Q)) and 0 <= weight <= 1, 'Use an exact detour weight in [0,1].')
        super().__init__(4, 7, partition)
        self.weight = Q(weight)
        a = self.weight
        self.terms = [(k, Q(r)) for k, r in
                      [(1, 300), (2, 140*(1-a)), (4, 140*a),
                       (-3, 65*(1-a)), (-7, 65*a)] if r]
        self.M = sum(abs(r)*k*k for k, r in self.terms)
        self.V = sum(abs(r*k) for k, r in self.terms)
        self.L2 = 4*self.M+2*self.V
        self.degree = max(abs(k) for k, r in self.terms)
        self.common = lcm(*(r.denominator for k, r in self.terms))
        self.integer_terms = [(k, int(r*self.common)) for k, r in self.terms]

    @lru_cache(maxsize=8192)
    def evaluate(self, quarter, s):
        a, b = s.numerator, s.denominator
        w = b*b-a*a, 2*a*b
        for _ in range(quarter):
            w = -w[1], w[0]
        D = b*b+a*a
        powers, denominators = [(1, 0)], [1]
        for _ in range(self.degree):
            x, y = powers[-1]
            powers.append((x*w[0]-y*w[1], x*w[1]+y*w[0]))
            denominators.append(denominators[-1]*D)
        x = y = vx = vy = 0
        for k, radius in self.integer_terms:
            xx, yy = powers[abs(k)]
            if k < 0:
                yy = -yy
            scale = radius*denominators[self.degree-abs(k)]
            x += scale*xx
            y += scale*yy
            vx += k*scale*xx
            vy += k*scale*yy
        denominator = self.common*denominators[-1]
        factor = Q(2*b*b, D)
        return ((Q(x, denominator), Q(y, denominator)),
                (-Q(vy, denominator)*factor, Q(vx, denominator)*factor),
                (vx, vy, denominator))

    def numerical(self, quarter, s):
        w = (1j**quarter)*complex(1-s*s, 2*s)/(1+s*s)
        z = sum(float(r)*w**k for k, r in self.terms)
        v = sum(1j*k*float(r)*w**k for k, r in self.terms)*2/(1+s*s)
        return z, v


def check_evaluation():
    """Compare with the frozen evaluator and with affine endpoint mixing."""
    count = 0
    ends = [DetourCurve(Q(a)) for a in (0, 1)]
    originals = [IntersectionCertificate(m, n, 1) for m, n in ((2, 3), (4, 7))]
    try:
        for quarter in range(4):
            for s in (Q(0), Q(1, 7), Q(2, 3), Q(1)):
                w = ((1-s*s)/(1+s*s), 2*s/(1+s*s))
                for _ in range(quarter):
                    w = -w[1], w[0]
                factor = 2/(1+s*s)
                for original, end in zip(originals, ends):
                    p, v, raw = original.evaluate(quarter, s)
                    actual = end.evaluate(quarter, s)
                    expected = ((p[0]+55*w[0], p[1]+55*w[1]),
                                (v[0]-55*w[1]*factor, v[1]+55*w[0]*factor))
                    require(actual[:2] == expected, 'Detour endpoint position or derivative differs.')
                    require(tuple(Q(x, actual[2][2]) for x in actual[2][:2]) ==
                            (Q(raw[0], raw[2])+55*w[0], Q(raw[1], raw[2])+55*w[1]),
                            'Detour endpoint raw velocity differs.')
                    count += 6
                for weight in (Q(1, 3), WEIGHT.low, WEIGHT.high):
                    mixed = DetourCurve(weight)
                    result = mixed.evaluate(quarter, s)
                    first, second = [end.evaluate(quarter, s) for end in ends]
                    for row in range(2):
                        require(result[row] == tuple((1-weight)*x+weight*y for x, y in zip(first[row], second[row])),
                                'Affine position/derivative evaluation differs.')
                    require(tuple(Q(x, result[2][2]) for x in result[2][:2]) ==
                            tuple((1-weight)*Q(x, first[2][2])+weight*Q(y, second[2][2])
                                  for x, y in zip(first[2][:2], second[2][:2])),
                            'Affine raw-velocity evaluation differs.')
                    count += 6
    finally:
        DetourCurve.evaluate.cache_clear()
        IntersectionCertificate.evaluate.cache_clear()
    print(f'{count} exact evaluator comparisons passed.')


def separation(point, room=ROOM):
    return max(max(w.low-v.high, v.low-w.high) for v, w in zip(point, room))


def cover(low, high, predicate, order=0, depth=0):
    point = evaluate(I(low, high), WEIGHT, ZERO, order)
    margin = predicate(point)
    if margin > 0:
        return [(low, high, margin)]
    require(depth < 18, 'A triple-room interval is unresolved.')
    middle = (low+high)/2
    return (cover(low, middle, predicate, order, depth+1) +
            cover(middle, high, predicate, order, depth+1))


def checked_cover(low, high, predicate, order=0):
    arcs = cover(low, high, predicate, order)
    require(arcs[0][0] == low and arcs[-1][1] == high and
            all(a[1] == b[0] for a, b in zip(arcs, arcs[1:])), 'A room cover has a gap.')
    require(all(a < b and predicate(evaluate(I(a, b), WEIGHT, ZERO, order)) > 0
                for a, b, _ in arcs), 'An accepted room leaf failed re-evaluation.')
    return arcs


def certify_charts():
    """Three complete height graphs, separated slopes, and no extra room visits."""
    pi_upper = 4*sum(Q((-1)**k, 2*k+1) for k in range(21))
    require(pi_upper < Q(16, 5), 'The room cover misses part of the orbit.')
    outside = [(Q(-16, 5), CHARTS[0][0]), (CHARTS[0][1], CHARTS[1][0]),
               (CHARTS[1][1], CHARTS[2][0]), (CHARTS[2][1], Q(16, 5))]
    excluded = [arc for low, high in outside for arc in checked_cover(low, high, separation)]
    slopes, contained = [], []
    for j, (low, high) in enumerate(CHARTS):
        upward = j == 1
        velocity = evaluate(I(low, high), WEIGHT, ZERO, 1)
        require(velocity[1].low > 0 if upward else velocity[1].high < 0,
                'A selected chart is not height-monotone.')
        slopes.append(velocity[0]/velocity[1])
        bottom, top = [evaluate(I.wrap(t), WEIGHT, ZERO)[1] for t in (low, high)]
        require(bottom.high < -1 and top.low > 1 if upward else top.high < -1 and bottom.low > 1,
                'A selected chart does not span the full height window.')
        predicate = lambda p: min(p[0].low-ROOM[0].low, ROOM[0].high-p[0].high)
        contained.extend(checked_cover(low, high, predicate))
    require(slopes[0].high < slopes[1].low and slopes[1].high < slopes[2].low,
            'The three graph slopes are not strictly separated.')
    for slope, (low, high) in zip(slopes, [(Q(-57, 100), Q(-26, 100)),
                                         (Q(-9, 100), Q(9, 100)),
                                         (Q(26, 100), Q(57, 100))]):
        require(low < slope.low <= slope.high < high, 'An advertised slope enclosure failed.')
    # Each pair's difference is strictly monotone on its full common height
    # domain. Opposite orders at these two heights give exactly one meeting.
    seeds = ['-0.503206152', '-0.002349478', '0.507329385']
    radius = Q(1, 10000)
    for height in (-1, 1):
        positions = []
        for j in range(3):
            center = Q(seeds[j]) if height < 0 else -Q(seeds[2-j])
            low, high = center-radius, center+radius
            require(CHARTS[j][0] < low < high < CHARTS[j][1], 'A height bracket left its time chart.')
            first, last = [evaluate(I.wrap(t), WEIGHT, ZERO)[1] for t in (low, high)]
            require(first.high < height < last.low if j == 1 else last.high < height < first.low,
                    'A proposed endpoint-height bracket failed.')
            positions.append(evaluate(I(low, high), WEIGHT, ZERO)[0])
        order = positions if height > 0 else list(reversed(positions))
        require(all(a.high < b.low for a, b in zip(order, order[1:])),
                'The graph order at an endpoint height is unresolved.')
    print(f'{len(excluded)} arcs exclude every other visit from the triple room; '
          f'{len(contained)} contain the selected charts horizontally.')
    print('All three charts span [-1,1] in height, with disjoint slope intervals:')
    for slope in slopes:
        print(f'  {float(slope.low):+.6f} .. {float(slope.high):+.6f} (printed approximations)')
    print('At height -1 the order is later, halfway, earlier; at +1 it reverses.')
    return slopes


def chart_of(domain):
    """Place an entire rational-circle arc strictly inside a selected chart."""
    quarter, low, high = domain
    def circle(s):
        x, y = (1-s*s)/(1+s*s), 2*s/(1+s*s)
        for _ in range(quarter):
            x, y = -y, x
        return -x, -y  # exp(iu), for t=pi+u
    first, last = circle(low), circle(high)
    c49 = sincos(I.wrap(Q(49, 100)))[1]
    c52 = sincos(I.wrap(Q(52, 100)))[1]
    s01 = sincos(I.wrap(Q(1, 100)))[0]
    if (quarter in (1, 2) and c52.high < min(first[0], last[0]) and
            max(first[0], last[0]) < c49.low):
        return 0 if quarter == 1 else 2
    if (quarter in (1, 2) and min(first[0], last[0]) > 0 and
            max(abs(first[1]), abs(last[1])) < s01.low):
        return 1
    return None


def certify_complete_family():
    """Every possible crossing, for every weight, belongs to chart pairs.

    The bucket cover follows the original certificate, expanding its boxes
    by 410*weight_radius. Velocity varies by at most 1490*weight_radius.
    All predicate decisions and outward-rounding checks are rational.
    """
    middle, radius = WEIGHT.midpoint(), (WEIGHT.high-WEIGHT.low)/2
    curve = DetourCurve(middle)
    M = (300+140*(1-WEIGHT.low)*4+140*WEIGHT.high*16 +
         65*(1-WEIGHT.low)*9+65*WEIGHT.high*49)
    position_error, velocity_error = 410*radius, 1490*radius
    K, N = curve.K, 4*curve.K
    grid, buckets, stats = [], defaultdict(list), Counter()
    try:
        for i in range(N):
            quarter, k = divmod(i, K)
            domain = quarter, Q(k, K), Q(k+1, K)
            vx, vy, D = curve.evaluate(quarter, domain[1])[2]
            require(Q(vx*vx+vy*vy, D*D) > (2*M/K+velocity_error)**2,
                    'A uniform arc may contain a stationary point; use a finer partition.')
            raw = curve.bounds(domain)
            raw = (raw[0]-position_error, raw[1]+position_error,
                   raw[2]-position_error, raw[3]+position_error)
            box = tuple(nextafter(float(v), -inf if j % 2 == 0 else inf) for j, v in enumerate(raw))
            require(all(Q(v) <= r if j % 2 == 0 else Q(v) >= r
                        for j, (v, r) in enumerate(zip(box, raw))), 'An outward arc box is not outward.')
            grid.append((domain, box))
            visited = set()
            for x in range(raw[0]//8, raw[1]//8+1):
                for y in range(raw[2]//8, raw[3]//8+1):
                    for j in buckets[x, y]:
                        if j in visited:
                            continue
                        visited.add(j)
                        other = grid[j][1]
                        if (box[1] < other[0] or other[1] < box[0] or
                                box[3] < other[2] or other[3] < box[2]):
                            continue
                        difference = min(i-j, N-(i-j))
                        first = j if i-j <= N//2 else i
                        q0, s0, _ = grid[first][0]
                        vx, vy, D = curve.evaluate(q0, s0)[2]
                        if Q(vx*vx+vy*vy, D*D) > (2*M*(difference+1)/K+velocity_error)**2:
                            stats['monotone'] += 1
                            continue
                        a, b = chart_of(grid[j][0]), chart_of(domain)
                        require(a is not None and b is not None and a != b,
                                ('An unclassified possible crossing remains.', grid[j][0], domain))
                        stats[f'charts {min(a,b)} / {max(a,b)}'] += 1
                    buckets[x, y].append(i)
    finally:
        curve.evaluate.cache_clear()
    print(f'All {N} rational arcs are regular throughout the weight interval.')
    print('Uniform crossing cover:', dict(stats))
    return stats


def certify_event():
    certify_lens(FIRST, SECOND)
    record, = events(FIRST, SECOND, 'three visits')
    require(WEIGHT.low < record['weight'].low <= record['weight'].high < WEIGHT.high,
            'The isolated event is outside the certified weight interval.')
    c49 = sincos(I.wrap(Q(49, 100)))[1]
    c52 = sincos(I.wrap(Q(52, 100)))[1]
    require(c52.high < record['cosine'].low <= record['cosine'].high < c49.low,
            'The selected event times are outside the certified charts.')
    require(record['jacobian_sign'] == -1, 'The triple moves in an unexpected direction.')
    # End graphs are reflections and their difference is strictly monotone,
    # so they meet only at y=0. The middle chart has x(0)=-225 exactly.
    require(evaluate(ZERO, I.wrap(WEIGHT.midpoint()), ZERO) == (I.wrap(-225), ZERO) and
            evaluate(ZERO, WEIGHT, ZERO, 0, True) == (ZERO, ZERO), 'The halfway visit moved.')
    print(f'Exactly one triple passage: a ≈ {float(record["weight"].midpoint()):.15f}, at (-225,0).')
    return record


def certify_endpoints():
    records = []
    for weight, expected in [(WEIGHT.low, (0, {-1: 1, 0: 2, 1: 1})),
                             (WEIGHT.high, (-1, {0: 2, 1: 1, 2: 1}))]:
        curve = DetourCurve(weight)
        try:
            with redirect_stdout(io.StringIO()):
                curve.run()
                curve.refine()
            require(len(curve.refined) == 3, 'An endpoint has more than the three predicted crossings.')
            word, times, points = certified_word(curve)
            faces = from_faces(word, 2*(len(word)-1)+1)
            result = audit_word(word, 1, faces)
            require((result.value, faces.face_counts) == expected and faces.tangent_index == 0,
                    'An endpoint has unexpected strangeness or regions.')
            records.append((weight, result.value, word))
            print(f'Endpoint {weight}: three crossings, St={result.value}, '
                  f'bounded winding counts {faces.face_counts}; word {word}.')
        finally:
            curve.evaluate.cache_clear()
    require(records[1][1]-records[0][1] == -1, 'The triple passage has the wrong invariant jump.')
    return records


def checks():
    # Strict wall predicates must reject included and boundary points.
    require(separation((I.wrap(-225), ZERO)) < 0, 'An interior point was falsely excluded.')
    require(separation((I.wrap(-229), ZERO)) == 0, 'A wall point was falsely strictly excluded.')
    require(chart_of((0, Q(0), Q(1, 1000))) is None, 'A far-away arc was assigned to a triple chart.')
    require(chart_of((2, Q(0), Q(1, 1000))) == 1, 'The halfway chart does not include pi.')
    for weight in (Q(-1, 10), Q(11, 10), .5):
        try:
            DetourCurve(weight)
        except ValueError:
            pass
        else:
            raise ValueError('An unsupported proof weight was accepted.')


def graph_x(height, weight, chart):
    """Uncertified height inversion, used ONLY to draw the SVG."""
    radius = central_radius(FIRST, SECOND, weight)
    u = (-radius, 0, radius)[chart]
    for _ in range(12):
        t = pi+u
        u -= (orbit(t, 0, weight, 0).imag-height)/orbit(t, 1, weight, 0).imag
    point = orbit(pi+u, 0, weight, 0)
    require(abs(point.imag-height) < 1e-9 and float(CHARTS[chart][0]) < u < float(CHARTS[chart][1]),
            'A drawing-only height solve left its chart.')
    return point.real, u


def figure(event):
    """Three stills with equal coordinate scales and an actual-branch triangle."""
    weights = [float(WEIGHT.low), float(event['weight'].midpoint()), float(WEIGHT.high)]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="770" viewBox="0 0 1200 770" role="img" aria-labelledby="title description">',
           '<title id="title">A triangle switches sides at a negative triple passage</title>',
           '<desc id="description">Three magnified stills at weights 0.4641, approximately 0.464144224361, and 0.4642. Two downward-traveled outer branches and an upward-traveled halfway branch form a little clockwise triangle before meeting. A counterclockwise triangle opens on the other side. Its winding count changes from minus one to plus two, while strangeness changes from zero to minus one.</desc>',
           '<rect width="1200" height="770" fill="#101323"/>',
           '<g font-family="system-ui, sans-serif" fill="#f4f1e8">',
           '<text x="40" y="63" font-size="35" font-weight="700">A triangle switches sides</text>',
           '<text x="40" y="104" font-size="18" fill="#c7c7d4">Three branches keep moving. Their little triangle turns through one negative triple meeting.</text>']
    colors = ['#9fc7eb', '#f4f1e8', '#e8b66e']
    for panel, weight in enumerate(weights):
        left, cx, cy, scale = 30+390*panel, 210+390*panel, 365, 13750
        def point(x, y):
            return f'{cx+scale*(x+225):.5f},{cy-scale*y:.5f}'
        def path(chart, low, high, steps=240):
            return [point(graph_x(low+(high-low)*k/steps, weight, chart)[0],
                          low+(high-low)*k/steps) for k in range(steps+1)]
        svg.extend([f'<rect x="{left}" y="140" width="360" height="445" rx="16" fill="#0b0e1a" stroke="#383b50"/>',
                    f'<text x="{cx}" y="177" font-size="19" text-anchor="middle">a '+('≈' if panel == 1 else '=')+f' {weight:.12f}'.rstrip('0')+'</text>',
                    f'<defs><clipPath id="clip{panel}"><rect x="{left+15}" y="200" width="330" height="330"/></clipPath></defs>',
                    f'<g clip-path="url(#clip{panel})">',
                    f'<path d="M{cx} 200V530 M{left+15} {cy}H{left+345}" fill="none" stroke="#383b50" stroke-dasharray="3 6"/>'])
        if panel != 1:
            low, high = -.02, .02
            def gap(y):
                return graph_x(y, weight, 0)[0]-graph_x(y, weight, 1)[0]
            require(gap(low) > 0 and gap(high) < 0, 'The drawing triangle was not bracketed.')
            for _ in range(55):
                mid = (low+high)/2
                if gap(mid) > 0:
                    low = mid
                else:
                    high = mid
            height = (low+high)/2
            outline = path(0, height, 0, 80)+path(2, 0, -height, 80)+path(1, -height, height, 160)
            svg.append('<path d="M'+' L'.join(outline)+' Z" fill="'+('#9fc7eb' if panel == 0 else '#e8b66e')+'" fill-opacity=".4"/>')
        for chart, color in enumerate(colors):
            svg.append('<path d="M'+' L'.join(path(chart, -.013, .013))+'" fill="none" stroke="'+color+'" stroke-width="1.8"/>')
            y = .009
            x, u = graph_x(y, weight, chart)
            v = orbit(pi+u, 1, weight, 0)
            length = abs(v)
            dx, dy = v.real/length, -v.imag/length
            px, py = cx+scale*(x+225), cy-scale*y
            a, b = (px-10*dx, py-10*dy), (px+10*dx, py+10*dy)
            wing1 = b[0]-7*dx-4*dy, b[1]-7*dy+4*dx
            wing2 = b[0]-7*dx+4*dy, b[1]-7*dy-4*dx
            coords = lambda p: f'{p[0]:.5f},{p[1]:.5f}'
            svg.append(f'<path d="M{coords(a)} L{coords(b)} M{coords(wing1)} L{coords(b)} L{coords(wing2)}" fill="none" stroke="{color}" stroke-width="2.3"/>')
        svg.append('</g>')
        text = ['Triangle count −1', 'Three visits at (−225, 0)', 'Triangle count +2'][panel]
        svg.extend([f'<text x="{cx}" y="555" font-size="19" text-anchor="middle">{text}</text>',
                    f'<text x="{cx}" y="580" font-size="16" text-anchor="middle" fill="#c7c7d4">'+
                    ['Strangeness 0', 'The tracing points stay regular', 'Strangeness −1'][panel]+'</text>'])
    svg.extend(['<text x="40" y="630" font-size="18" fill="#c7c7d4">Blue and gold: the earlier and later visits. White: the halfway visit. Arrows follow travel.</text>',
                '<text x="40" y="665" font-size="18" fill="#c7c7d4">Every panel uses the same equal scales: 0.012 units from the horizontal axis to the window’s top.</text>',
                '<text x="40" y="700" font-size="18" fill="#c7c7d4">All crossings belong to these three branches throughout 0.4641 ≤ a ≤ 0.4642.</text>',
                '<text x="40" y="741" font-size="15" fill="#9999ae">Rounded numerical geometry; exact rational family cover, endpoint words, and invariant values are checked separately.</text>',
                '</g></svg>'])
    target = HERE/'triple_passage.svg'
    target.write_text('\n'.join(svg)+'\n')
    print('Wrote', target.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true', help='Also regenerate the SVG close-up.')
    args = parser.parse_args()
    start = monotonic()
    checks()
    check_evaluation()
    certify_charts()
    certify_complete_family()
    record = certify_event()
    certify_endpoints()
    print(f'The entire interval contains one ordinary negative triple event and no other curve events '
          f'({monotonic()-start:.2f}s). This does not classify the rest of the detour.')
    if args.figure:
        figure(record)


if __name__ == '__main__':
    main()
