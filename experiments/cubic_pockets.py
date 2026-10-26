"""One cubic, two area laws: exact examples and a numerical common limit.

Run: python3 experiments/cubic_pockets.py [--figure]
Standard library only. The cubic formulas have a short algebraic proof in
cubic_pockets.md. Rational examples check the identities; numerical orbital
roots and quadrature check convergence, not certified area enclosures.
--figure also regenerates the standalone cubic.svg without plotting packages.
"""

import argparse
from fractions import Fraction as Q
from html import escape
from math import acos, cos, fsum, pi, sqrt
from pathlib import Path

from blend_cusps import require
from phase_area import bisect, integral
from phase_contact_probe import gap
from phase_unfolding import coefficients


TILT_SCALE = 2/(3*sqrt(3))


def model(v, mu, tau):
    return v**3-mu*v+TILT_SCALE*tau


def roots(mu, tau):
    """Independent trigonometric solution, for the three-real-root model."""
    if mu == 0 and tau == 0:
        return [0., 0., 0.]
    require(mu > 0 and abs(tau) <= mu**1.5+1e-14, 'Expected three real model roots.')
    if abs(mu**3-tau*tau) < 1e-14:
        s = (1 if tau > 0 else -1)*sqrt(mu/3)
        return sorted([-2*s, s, s])
    angle = acos(max(-1, min(1, -tau/mu**1.5)))/3
    return sorted(2*sqrt(mu/3)*cos(angle-2*pi*k/3) for k in range(3))


def areas(rr):
    return [abs(rr[2 if j == 0 else 0]-(rr[j]+rr[j+1])/2)
            * (rr[j+1]-rr[j])**3/6 for j in (0, 1)]


def exact_examples():
    count = 0
    for i in range(-8, 9):
        for j in range(-8, 9):
            rr = sorted([Q(i, 7), Q(j, 5), -Q(i, 7)-Q(j, 5)])
            mu = -sum(rr[k]*rr[(k+1) % 3] for k in range(3))
            nu = -rr[0]*rr[1]*rr[2]
            primitive = lambda v: v**4/4-mu*v*v/2+nu*v
            for k in (0, 1):
                a, b = rr[k:k+2]
                c = rr[2 if k == 0 else 0]
                signed = (c-(a+b)/2)*(b-a)**3/6
                require(signed == primitive(b)-primitive(a), 'Exact pocket identity failed.')
                require(abs(signed) == areas(rr)[k], 'Unsigned pocket identity failed.')
                count += 2
            require(all(v**3-mu*v+nu == 0 for v in rr), 'Vieta factorization failed.')
            count += 1
            lower, upper = areas(rr)
            middle = rr[1]
            require(lower+upper == mu*mu/2+3*mu*middle*middle/2-9*middle**4/4,
                    'The combined-area identity failed.')
            require(lower-upper == middle*(rr[2]-rr[0])**3/4,
                    'The pocket-imbalance identity failed.')
            count += 2
    # General rational tangency parameter s: q = (v-s)^2 (v+2s).
    for s in [Q(k, 11) for k in range(1, 25)]:
        mu, nu = 3*s*s, 2*s**3
        require(4*mu**3 == 27*nu*nu, 'Discriminant parametrization failed.')
        require(areas([-2*s, s, s]) == [27*s**4/4, 0], 'Surviving fold area failed.')
        require(areas([-s, -s, 2*s]) == [0, 27*s**4/4], 'Reflected fold area failed.')
        count += 3
    print(f'{count:,} exact rational example checks: pocket integrals, Vieta, area balance, fold areas and discriminant.')


def check_common_limit(data):
    a0, A, C, B = [float(data[k].midpoint()) for k in ('weight', 'A_prime', 'C', 'B')]
    L = sqrt(-A/C)
    horizontal = 2*A*L
    phase_scale = -horizontal/B
    area_scale = horizontal*L
    print(f'L ≈ {L:.10f}; phase multiplier ≈ {phase_scale:.10f}; area multiplier ≈ {area_scale:.6f}.')
    print('Numerical orbital areas divided by the common cubic prediction (lower, upper):')
    for tau in (0, .5, .9, -.5, -.9):
        rr = roots(1, tau)
        model_areas = areas(rr)
        cuts = [rr[0]-.25, (rr[0]+rr[1])/2, (rr[1]+rr[2])/2, rr[2]+.25]
        previous = [float('inf')]*2
        errors = []
        for h in (.04, .02, .01, .005):
            weight = a0+h*h
            phase = phase_scale*h**3*TILT_SCALE*tau
            normalized = lambda v: -gap(L*h*v, weight, phase)[0]/(horizontal*h**3)
            actual_roots = [bisect(normalized, cuts[k], cuts[k+1]) for k in range(3)]
            ratios = []
            for k in (0, 1):
                low, high = actual_roots[k:k+2]
                area = abs(integral(normalized, low, high, 128))
                refined = abs(integral(normalized, low, high, 256))
                require(abs(area-refined) < 2e-9, 'The common-limit quadrature did not stabilize.')
                ratio = refined/model_areas[k]
                error = abs(ratio-1)
                require(error < previous[k] and error < .15,
                        'The orbital pocket did not approach the common cubic area.')
                previous[k] = error
                ratios.append(ratio)
            # Independently compare the separation on a compact height grid.
            discrepancy = max(abs(normalized(-1.4+2.8*j/40)-model(-1.4+2.8*j/40, 1, tau))
                              for j in range(41))
            errors.append(discrepancy)
            print(f'  tilt {tau:+.1f}, h={h:.3f}: {ratios[0]:.9f}, {ratios[1]:.9f}; '
                  f'max sampled gap error {discrepancy:.3g}.')
        require(all(3.5 < p/q < 4.5 for p, q in zip(errors, errors[1:])),
                'The sampled normalized gap error does not scale like h squared.')
        require(all(error < .002 for error in previous), 'The final area ratio is too far from one.')
    print('20 common-limit comparisons converge. These are numerical checks, not interval area bounds.')
    # The normalized mirror area 1/4 recovers yesterday's coefficient.
    require(abs(area_scale/4-float(data['mirror_pocket_coefficient'].midpoint())) < 1e-8,
            'The normalization lost the mirror coefficient.')


def check_fold_limit():
    prior = float('inf')
    for epsilon in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
        area = areas(roots(1+epsilon, 1))[1]
        ratio = area/(Q(4, 9)*epsilon**1.5)
        require(abs(ratio-1) < prior and abs(ratio-1) < .004, 'The model fold law failed.')
        prior = abs(ratio-1)
        print(f'  tilted model, epsilon={epsilon:.0e}: area/[(4/9) epsilon^1.5] ≈ {ratio:.9f}.')


def figure():
    """Write accessible, deterministic SVG with exact cubic Bezier curves."""
    bg, panel = '#101323', '#0b0e1a'
    gold, blue, ink, muted = '#e8b66e', '#9fc7eb', '#f4f1e8', '#c7c7d4'
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" '
           'viewBox="0 0 1200 760" role="img" aria-labelledby="title description">',
           '<title id="title">One cubic, two area laws</title>',
           '<desc id="description">Three graphs of the cubic separation against height: '
           'a cubic contact at opening zero and tilt zero; two equal pockets at opening one '
           'and tilt zero; and one surviving pocket at a quadratic touch at opening one '
           'and tilt one. The lower parameter map has a cusp separating one crossing from three. '
           'This is the leading model of two orbital branches, with independent normalized axis scales.</desc>',
           f'<rect width="1200" height="760" fill="{bg}"/>',
           '<g font-family="ui-sans-serif, system-ui, sans-serif">']

    def text(x, y, content, size=17, color=muted, anchor='start'):
        out.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
                   f'text-anchor="{anchor}">{escape(content)}</text>')

    def path(d, stroke='none', fill='none', width=1.5, extra=''):
        out.append(f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{width}" {extra}/>')

    def pair(p):
        return ' '.join(f'{v:.5f}' for v in p)

    text(50, 55, 'One cubic, two area laws', 32, ink)
    text(50, 90, 'A leading model: q(v) = v³ − μv + 2τ/(3√3). Shading measures area between the graph and zero.')
    for j, (mu, tau, title) in enumerate([(0, 0, 'A cubic contact'), (1, 0, 'Equal pockets'), (1, 1, 'A tilted touch')]):
        x0, y0, sx, sy = 220+380*j, 300, 95, 94
        map_point = lambda q, v: (x0+sx*q, y0-sy*v)

        def cubic(low, high):
            span = (high-low)/3
            a, b = model(low, mu, tau), model(high, mu, tau)
            pts = [(a, low), (a+span*(3*low*low-mu), low+span),
                   (b-span*(3*high*high-mu), high-span), (b, high)]
            pp = [pair(map_point(*p)) for p in pts]
            return f'M{pp[0]} C{pp[1]} {pp[2]} {pp[3]}'

        text(x0, 127, title, 21, gold, 'middle')
        text(x0, 151, f'Opening {mu} · tilt {tau}', 16, muted, 'middle')
        out.append(f'<rect x="{x0-155}" y="170" width="310" height="265" rx="10" fill="{panel}"/>')
        out.append(f'<clipPath id="clip-{j}"><rect x="{x0-150}" y="175" width="300" height="255"/></clipPath>')
        path(f'M{x0-150} 300H{x0+150} M{x0} 175V430', '#74788e', width=1)
        rr = roots(mu, tau)
        out.append(f'<g clip-path="url(#clip-{j})">')
        for k in (0, 1):
            low, high = rr[k:k+2]
            d = cubic(low, high)+f' L{pair(map_point(0, high))} L{pair(map_point(0, low))} Z'
            path(d, fill=blue if k == 0 else gold, extra='fill-opacity=".35"')
        path(cubic(-1.65, 1.65), ink, width=2.3)
        for v in sorted(set(rr)):
            x, y = map_point(0, v)
            touching = rr.count(v) > 1
            out.append(f'<circle cx="{x:.5f}" cy="{y:.5f}" r="{6 if touching else 4}" '
                       f'fill="{panel if touching else ink}" stroke="{ink}" stroke-width="1.5"/>')
        out.append('</g>')
        for v in (-1, 0, 1):
            text(x0-161, y0-sy*v+5, str(v).replace('-', '−'), 14, muted, 'end')
        for q in (-1, 0, 1):
            text(x0+sx*q, 453, str(q).replace('-', '−'), 14, muted, 'middle')
        text(x0, 480, 'Separation q →', 16, muted, 'middle')
        text(x0-145, 194, 'Height v ↑', 14)
        aa = areas(rr)
        text(x0, 512, f'Lower {aa[0]:.2f} · upper {aa[1]:.2f}', 17, ink, 'middle')

    text(50, 563, 'Two routes through a parameter map', 22, ink)
    text(50, 602, 'Mirror: tilt zero, opening μ > 0.', 18, blue)
    text(50, 629, 'Each pocket has area μ²/4.', 18)
    text(50, 672, 'Tilt +1: increase opening from 1 to 1 + ε.', 18, gold)
    text(50, 699, 'The new upper pocket has area ∼ (4/9) ε³⁄².', 18)
    plane = lambda mu, tau: (780+190*mu, 635-52*tau)
    t = 1.5**1.5
    controls = [plane(mu, tau) for mu, tau in [(1.5, -t), (-.5, t), (-.5, -t), (1.5, t)]]
    d = f'M{pair(controls[0])} C{pair(controls[1])} {pair(controls[2])} {pair(controls[3])}'
    path(d+' Z', fill=gold, extra='fill-opacity=".12"')
    path('M720 635H1090 M780 535V735', '#74788e', width=1)
    path('M720 583H1090', blue, width=1, extra='stroke-dasharray="5 5"')
    path(d, gold)
    for mu, tau in [(0, 0), (1, 0), (1, 1)]:
        x, y = plane(mu, tau)
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{ink}"/>')
    text(998, 660, '3 crossings', 14, ink)
    text(828, 555, '1 crossing', 14)
    text(1085, 628, 'μ →', 15)
    text(756, 550, 'τ ↑', 15)
    text(50, 741, 'Normalized units, separate axis scales. The full orbital drawing has higher-order corrections.', 15)
    out.extend(['</g>', '</svg>'])
    destination = Path(__file__).with_name('cubic.svg')
    destination.write_text('\n'.join(out)+'\n')
    print('Wrote', destination.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true')
    args = parser.parse_args()
    exact_examples()
    check_fold_limit()
    check_common_limit(coefficients())
    if args.figure:
        figure()


if __name__ == '__main__':
    main()
