"""Certify the detour lens's unique axis crossing; optionally draw the SVG.

Run: python3 experiments/arm_detour_lens.py [--figure]
Standard library only. Bernstein bounds cover each whole leg continuously.
The illustration uses independent floating-point complex Fourier sums.
"""

from fractions import Fraction as Q
from math import comb, hypot, log10, pi
from pathlib import Path
import argparse
import cmath

from arm_detour import BRIDGES
from blend_cusps import add, derivative, product, require, scale, value
from certify_intersections import IntersectionCertificate


def central_polynomial(endpoint):
    """y(pi+u) = sin(u) G(cos u), for even m and odd n."""
    m, n, length = endpoint
    require(m > 0 and n > 0 and m % 2 == 0 and n % 2 == 1,
            'The central-arc factorization needs even m and odd n.')
    U = [(Q(1),), (Q(0), Q(2))]
    for _ in range(2, max(m, n)):
        U.append(add(product((0, 2), U[-1]), scale(U[-2], -1)))
    return add((-length,), add(scale(U[m-1], 140), scale(U[n-1], 65)))


def bernstein(p, low, high):
    """Exact Bernstein coefficients on a closed rational interval."""
    require(low < high, 'A Bernstein interval must have positive width.')
    degree = len(p)-1
    # First substitute c = low + (high-low) x into the power expansion.
    powers = [sum(p[j]*comb(j, k)*low**(j-k)*(high-low)**k
                  for j in range(k, degree+1)) for k in range(degree+1)]
    # x^k = sum_{i=k}^degree C(i,k)/C(degree,k) B_i^degree(x).
    return tuple(sum(powers[k]*Q(comb(i, k), comb(degree, k))
                     for k in range(i+1)) for i in range(degree+1))


def certify_lens(first, second, max_depth=20):
    """Prove one simple G root in (0,1) for EVERY weight on this leg.

    Return the complete rectangle cover for independent inspection. Every
    root has G_c > 0; the endpoint signs therefore force exactly one root.
    No simplicity or fixed crossing count is claimed for the closed arc.
    """
    endpoints = [central_polynomial(first), central_polynomial(second)]
    require(all(value(p, 0) < 0 < value(p, 1) for p in endpoints),
            'The central crossing does not have the required endpoint signs.')
    cover = []

    def visit(cl, ch, al, ah, depth):
        edges = [add(scale(endpoints[0], 1-a), scale(endpoints[1], a)) for a in (al, ah)]
        coefficients = [b for p in edges for b in bernstein(p, cl, ch)]
        upper = max(coefficients)
        if upper < 0:
            cover.append({'cosine': (cl, ch), 'weight': (al, ah),
                          'reason': 'negative', 'bound': upper, 'depth': depth})
            return
        coefficients = [b for p in edges for b in bernstein(derivative(p), cl, ch)]
        lower = min(coefficients)
        if lower > 0:
            cover.append({'cosine': (cl, ch), 'weight': (al, ah),
                          'reason': 'increasing', 'bound': lower, 'depth': depth})
            return
        require(depth < max_depth, 'The central-arc cover needs a deeper partition.')
        if ch-cl >= ah-al:
            mid = (cl+ch)/2
            visit(cl, mid, al, ah, depth+1)
            visit(mid, ch, al, ah, depth+1)
        else:
            mid = (al+ah)/2
            visit(cl, ch, al, mid, depth+1)
            visit(cl, ch, mid, ah, depth+1)

    visit(Q(0), Q(1), Q(0), Q(1), 0)
    return cover


def check_algebra():
    require(bernstein((0, 1, -1), Q(0), Q(1)) == (0, Q(1, 2), 0),
            'The quadratic Bernstein conversion failed.')
    require(bernstein((7,), Q(-2), Q(3)) == (7,), 'The constant conversion failed.')
    checked = 0
    for endpoint in {e for bridge in BRIDGES for e in bridge}:
        m, n, length = endpoint
        p = central_polynomial(endpoint)
        curve = IntersectionCertificate(m, n, 1)
        try:
            for j in range(1, 17):
                s = Q(j, 16)
                c, sine = (1-s*s)/(1+s*s), 2*s/(1+s*s)
                # A separate exact unit-circle evaluator at t = pi + u.
                y = curve.evaluate(2, s)[0][1] - (length-245)*sine
                require(y == sine*value(p, c), 'The shifted sine polynomial is wrong.')
                checked += 1
        finally:
            curve.evaluate.cache_clear()
        for lo, hi in [(Q(0), Q(1)), (Q(1, 2), Q(7, 8)), (Q(-1), Q(2))]:
            coefficients = bernstein(p, lo, hi)
            d = len(coefficients)-1
            for j in range(9):
                x = Q(j, 8)
                reconstructed = sum(b*comb(d, i)*x**i*(1-x)**(d-i)
                                    for i, b in enumerate(coefficients))
                require(reconstructed == value(p, lo+(hi-lo)*x),
                        'The Bernstein basis does not reconstruct the polynomial.')
                checked += 1
    # Wrong parity and a first arm so long that the initial upward arc
    # disappears must not be silently certified.
    for first, second, expected in [((3, 3, 245), (4, 7, 300), 'even m'),
                                    ((2, 3, 600), (2, 3, 700), 'endpoint signs')]:
        try:
            certify_lens(first, second)
        except ValueError as error:
            require(expected in str(error), 'Unexpected negative-control error.')
        else:
            raise ValueError('An incompatible lens received a certificate.')
    print(f'{checked} exact factorization and Bernstein-identity checks passed.')


def position(t, first, second, weight):
    """Independent complex implementation, for illustration only."""
    w = cmath.exp(1j*t)
    def endpoint(pair):
        m, n, length = pair
        return length*w + 140*w**m + 65*w**-n
    z = (1-weight)*endpoint(first)+weight*endpoint(second)
    return z.real, z.imag


def central_radius(first, second, weight):
    lo, hi = 0, pi/2
    for _ in range(52):
        mid = (lo+hi)/2
        if position(pi+mid, first, second, weight)[1] > 0:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def velocity(t, first, second, weight):
    w = cmath.exp(1j*t)
    def endpoint(pair):
        m, n, length = pair
        return 1j*(length*w + 140*m*w**m - 65*n*w**-n)
    v = (1-weight)*endpoint(first)+weight*endpoint(second)
    return v.real, v.imag


def draw_figure(destination):
    """Five stills per detour, each row with a fixed scale, and two lenses."""
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1120" viewBox="0 0 1400 1120" role="img" aria-labelledby="title description">
<title id="title">Room to keep moving</title>
<desc id="description">Two three-leg detours connect rhythms 2 / 3 to 4 / 7, and 4 / 7 to 6 / 11. The first arm grows to 300 or 700, stays long during the blend, then returns to 245. Five stills show each route at one scale. Gold arcs around halfway through the orbit are magnified below; they can cross themselves. Every drawing has zero net tangent turns and winds once around its center.</desc>
<style>
text { font: 16px ui-sans-serif, system-ui, sans-serif; fill: #c7c7d4; }
.title { font-size: 30px; font-weight: 600; fill: #f4f1e8; }
.label { font-size: 20px; fill: #e8b66e; }
.small { font-size: 14px; fill: #9999ae; }
.outline { fill: none; stroke: #9999ae; stroke-width: 1; }
.gold { fill: none; stroke: #e8b66e; stroke-width: 1.8; }
</style>
<rect width="1400" height="1120" rx="20" fill="#101323"/>
<text x="30" y="46" class="title">Room to keep moving</text>
<text x="1370" y="43" text-anchor="end" class="small">ALDEBARAN · TWO DETOURS</text>
<text x="30" y="78">Lengthen the first arm · blend with it held long · bring it home.</text>''']

    def sampled(fn, start, end, steps):
        return [fn(start+(end-start)*j/steps) for j in range(steps+1)]

    def path(points, transform):
        return ' '.join(f'{"L" if j else "M"}{x:.3f} {y:.3f}'
                        for j, (x, y) in enumerate(map(transform, points)))

    def circle(point, transform, fill, stroke, radius=3):
        x, y = transform(point)
        return f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius}" fill="{fill}" stroke="{stroke}"/>'

    def arrow(fn, first, second, weight, t, transform, length=11):
        x, y = transform(fn(t))
        vx, vy = velocity(t, first, second, weight)
        speed = hypot(vx, vy)
        dx, dy = vx/speed, -vy/speed
        tx, ty = x+length*dx/2, y+length*dy/2
        wing = length*.35
        d = (f'M{x-length*dx/2:.3f} {y-length*dy/2:.3f}L{tx:.3f} {ty:.3f} '
             f'M{tx-wing*dx+wing*.65*dy:.3f} {ty-wing*dy-wing*.65*dx:.3f}'
             f'L{tx:.3f} {ty:.3f}L{tx-wing*dx-wing*.65*dy:.3f} {ty-wing*dy+wing*.65*dx:.3f}')
        return f'<path d="{d}" fill="none" stroke="#f4f1e8" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'

    titles = ['Start', 'Arm out', 'Halfway blend', 'New drawing', 'Home']
    for row, bridge in enumerate(BRIDGES):
        long = bridge[1][2]
        top = 114+345*row
        start_pair, end_pair = bridge[0][:2], bridge[-1][:2]
        svg.append(f'<text x="30" y="{top}" class="label">{start_pair[0]} / {start_pair[1]} → {end_pair[0]} / {end_pair[1]} · first arm out to {long}</text>')
        svg.append(f'<text x="1370" y="{top}" text-anchor="end" class="small">0 net direction turns · +1 around the center</text>')
        stills = [(bridge[0], bridge[0], 0), (bridge[1], bridge[1], 0),
                  (bridge[1], bridge[2], .5), (bridge[2], bridge[2], 0),
                  (bridge[3], bridge[3], 0)]
        for col, (first, second, a) in enumerate(stills):
            cx, cy = 150+275*col, top+176
            factor = 109/(long+205)
            transform = lambda p: (cx+factor*p[0], cy-factor*p[1])
            fn = lambda t: position(t, first, second, a)
            radius = central_radius(first, second, a)
            svg.append(f'<rect x="{cx-123}" y="{top+21}" width="246" height="296" rx="12" fill="#0b0e1a" stroke="#383b50"/>')
            svg.append(f'<text x="{cx}" y="{top+47}" text-anchor="middle">{titles[col]}</text>')
            svg.append(f'<text x="{cx}" y="{top+70}" text-anchor="middle" class="small">First arm {first[2]}</text>')
            svg.append(f'<path class="outline" d="{path(sampled(fn, 0, 2*pi, 2400), transform)}"/>')
            svg.append(f'<path class="gold" d="{path(sampled(fn, pi-radius, pi+radius, 360), transform)}"/>')
            for fraction in [.08, .24, .39, .61, .76, .92]:
                svg.append(arrow(fn, first, second, a, 2*pi*fraction, transform))
            svg.append(circle(fn(pi), transform, '#e8b66e', '#0b0e1a', 2.5))
            svg.append(f'<path d="M{cx-3} {cy}h6 M{cx} {cy-3}v6" stroke="#747889"/>')
            svg.append(f'<path d="M{cx-101} {top+296}v-4h{100*factor:.3f}v4" fill="none" stroke="#9999ae"/>')
            svg.append(f'<text x="{cx-101}" y="{top+310}" class="small">100 units</text>')

        first, second = bridge[1:3]
        fn = lambda t: position(t, first, second, .5)
        radius = central_radius(first, second, .5)
        context = sampled(fn, pi-1.18*radius, pi+1.18*radius, 600)
        xs, ys = zip(*context)
        factor = min(250/(max(xs)-min(xs)), 145/(max(ys)-min(ys)))
        midx, midy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
        left = 30+700*row
        transform = lambda p: (left+150+factor*(p[0]-midx), 950-factor*(p[1]-midy))
        svg.append(f'<rect x="{left}" y="826" width="640" height="258" rx="12" fill="#0b0e1a" stroke="#383b50"/>')
        svg.append(f'<text x="{left+24}" y="857" class="label">The halfway blend, closer</text>')
        svg.append(f'<path class="outline" d="{path(context, transform)}"/>')
        svg.append(f'<path class="gold" d="{path(sampled(fn, pi-radius, pi+radius, 480), transform)}"/>')
        for t in [pi-.48*radius, pi+.48*radius]:
            svg.append(arrow(fn, first, second, .5, t, transform, 14))
        svg.append(circle(fn(pi), transform, '#e8b66e', '#0b0e1a', 3))
        svg.append(circle(fn(pi-radius), transform, '#0b0e1a', '#f4f1e8', 3))
        magnitude = 10**int(log10(60/factor)//1)
        units = max(x*magnitude for x in (1, 2, 5) if x*magnitude <= 60/factor)
        svg.append(f'<path d="M{left+24} 1044v-4h{units*factor:.3f}v4" fill="none" stroke="#9999ae"/>')
        svg.append(f'<text x="{left+24}" y="1066" class="small">{units:g} drawing units</text>')
        for j, line in enumerate([f'First arm {long}. Blend 50%.',
                                  'Gold: near the orbit’s halfway point.',
                                  'Hollow circle: the arc’s ends meet.',
                                  'The arc can also cross itself.',
                                  'Both axes use the same scale.']):
            svg.append(f'<text x="{left+310}" y="{903+30*j}" class="small">{line}</text>')
    svg.append('<text x="30" y="1109" class="small">Full drawings share one scale within each row. Lenses fit independently. The exact speed certificates cover the complete routes.</text>\n</svg>\n')
    destination.write_text('\n'.join(svg))
    print(f'Wrote {destination.name}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true', help='Regenerate the standalone SVG.')
    args = parser.parse_args()
    check_algebra()
    total = 0
    for bridge in BRIDGES:
        for first, second in zip(bridge, bridge[1:]):
            cover = certify_lens(first, second)
            total += len(cover)
            print(f'{first} → {second}: {len(cover)} rectangles, '
                  f'deepest split {max(r["depth"] for r in cover)}; one simple cosine root.')
    print(f'All six continuous legs certified with {total} rectangles. The lens follows one continuous arc.')
    if args.figure:
        draw_figure(Path(__file__).with_name('arm_detour.svg'))


if __name__ == '__main__':
    main()
