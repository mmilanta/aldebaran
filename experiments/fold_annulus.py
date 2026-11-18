"""Rational radial ranges at every degree of the half-turn.

Run: python3 experiments/fold_annulus.py [--json | --figure]
The monotonicity proof for every real phase is in fold_annulus.md.
This calculator encloses both global extrema at all 181 slider settings.
Only the standard library is needed; no sampled extremum decides a bound.
"""

import argparse
from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

from blend_cusps import Interval as I, require
from fold_contacts import PI, round_interval
from phase_unfolding import sincos, sqrt_interval

A, B, R = 205, 75, 245
D = A*A-B*B
HERE = Path(__file__).resolve().parent


def square(x):
    """A true interval square, including intervals that straddle zero."""
    x = I.wrap(x)
    return I(0 if x.low <= 0 <= x.high else min(x.low*x.low, x.high*x.high),
             max(x.low*x.low, x.high*x.high))


def secular(q2, multiplier, maximum):
    return sum(a*a*x/square(multiplier-a*a if maximum else multiplier+a*a)
               for a, x in zip((A, B), q2))-1


def multiplier(q2, maximum):
    low = Q(A*A)+Q(1, 2**20) if maximum else Q(0)
    high = Q(A*A+A*R+1) if maximum else Q(A*R)
    require(secular(q2, low, maximum).low > 0,
            'The lower multiplier endpoint is not strictly below its root.')
    require(secular(q2, high, maximum).high < 0,
            'The upper multiplier endpoint is not strictly above its root.')
    for _ in range(80):
        mid = (low+high)/2
        sign = secular(q2, mid, maximum).sign()
        if sign > 0:
            low = mid
        else:
            high = mid
    result = I(low, high)
    require(secular(q2, low, maximum).low > 0
            and secular(q2, high, maximum).high < 0,
            'A final multiplier bracket lost its strict signs.')
    return result


def radial_bounds(degrees):
    require(type(degrees) is int and 0 <= degrees <= 180,
            'Use an integer degree from zero through 180.')
    if degrees == 0:
        return I.wrap(40), I.wrap(450)
    if degrees == 180:
        return I.wrap(170), sqrt_interval(I.wrap(Q(23155775, 208)), bits=100)
    sine, cosine = [round_interval(x, 36) for x in sincos(PI*Q(degrees, 360))]
    require(cosine.low > 0 and sine.low > 0, 'The half-phase left its open quadrant.')
    q2 = [R*R*square(x) for x in (cosine, sine)]
    bounds = []
    for maximum in (False, True):
        lam = multiplier(q2, maximum)
        r2 = square(lam)*sum(x/square(lam-a*a if maximum else lam+a*a)
                            for a, x in zip((A, B), q2))
        bounds.append(sqrt_interval(r2, bits=100))
    require(bounds[0].high < bounds[1].low, 'The annulus reversed.')
    return tuple(bounds)


def prove():
    require(R > A > B > 0 and B*R < D, 'The endpoint and multiplier cases changed.')
    require(A*A*(1+Q(R*R, D)) == Q(23155775, 208),
            'The symmetric farthest-point formula changed.')
    rows = [radial_bounds(degrees) for degrees in range(181)]
    require(all(a[0].high < b[0].low and a[1].low > b[1].high
                for a, b in zip(rows, rows[1:])),
            'The independent degree enclosures do not tighten strictly.')
    require(all(x.high-x.low < Q(1, 10**16) for row in rows for x in row),
            'An enclosure is wider than its advertised precision.')
    # Prove that each range has one unambiguous two-decimal rounding. This
    # audits the displayed values; all mathematical archive values stay rational.
    require(all((x.low*100+Q(1, 2))//1 == (x.high*100+Q(1, 2))//1
                for row in rows for x in row),
            'A radius straddles a two-decimal display rounding boundary.')
    return rows


def record(rows):
    return {'scope': 'Global radial extrema at each integer phase in degrees; fold-independent.',
            'radii': [{'degrees': degrees,
                       'inner': [str(r.low), str(r.high)],
                       'outer': [str(s.low), str(s.high)]}
                      for degrees, (r, s) in enumerate(rows)]}


def figure(rows):
    def number(x):
        return f'{float(x):.4f}'.rstrip('0').rstrip('.') or '0'
    def text(x, y, value, size=22, fill='#c7c7d4', extra=''):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'
    def path(points):
        return ''.join(('M' if i == 0 else 'L')+number(x)+','+number(y)
                       for i, (x, y) in enumerate(points))
    # The curve locations come from rational enclosures at integer degrees.
    # Straight segments between them illustrate, rather than enclose, the graph.
    inner = [(90+5*degree, 650-float(r.midpoint())) for degree, (r, s) in enumerate(rows)]
    outer = [(90+5*degree, 650-float(s.midpoint())) for degree, (r, s) in enumerate(rows)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="850" viewBox="0 0 1100 850" role="img" aria-labelledby="title description">',
             '<title id="title">The annulus tightens</title>',
             '<desc id="description">A radial graph of the entire half-turn. The innermost radius rises strictly from 40 to 170; the outermost falls strictly from 450 to about 333.66. All positive integer fold counts have this same radial range. Blue marks the outer edge and gold the inner edge. The horizontal axis measures the backward arm’s starting angle from zero to 180 degrees; the vertical axis measures drawing units. Lines join rationally enclosed values at integer degrees and are illustrations of the analytic monotonicity proof.</desc>',
             '<rect width="1100" height="850" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(60, 70, 'The annulus tightens.', 49, '#f4f1e8'),
             text(60, 115, 'The same radial reach, at every fold count.', 25),
             text(90, 167, 'Distance from the center · drawing units', 20)]
    for radius in (0, 100, 200, 300, 400, 450):
        y = 650-radius
        parts += [f'<path d="M90,{y}H990" stroke="#383b50"/>',
                  text(74, y+7, radius, 19, extra='text-anchor="end"')]
    parts += [f'<path d="{path(outer)}{path(inner[::-1]).replace("M", "L", 1)}Z" fill="#9fc7eb" fill-opacity=".09"/>',
              f'<path d="{path(outer)}" fill="none" stroke="#9fc7eb" stroke-width="3"/>',
              f'<path d="{path(inner)}" fill="none" stroke="#e8b66e" stroke-width="3"/>']
    for degree in (0, 45, 90, 135, 180):
        x = 90+5*degree
        parts += [f'<path d="M{x},650v9" stroke="#c7c7d4"/>',
                  text(x, 689, str(degree)+'°', 20, extra='text-anchor="middle"')]
    for y, label, color in ((205, '450', '#9fc7eb'), (610, '40', '#e8b66e')):
        parts.append(text(104, y+27 if label == '450' else y-12, label, 21, color))
    parts += [text(610, 225, 'Outermost', 21, '#9fc7eb'),
              text(610, 580, 'Innermost', 21, '#e8b66e'),
              text(976, 304, '≈333.66', 21, '#9fc7eb', 'text-anchor="end"'),
              text(976, 515, '170', 21, '#e8b66e', 'text-anchor="end"'),
              text(540, 734, 'Backward arm’s starting angle', 21, extra='text-anchor="middle"'),
              text(60, 785, 'The inner edge moves out. The outer edge moves in.', 24, '#f4f1e8'),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_turn.html">',
              text(60, 826, 'Turn the arm and follow a repeat ↗', 21, '#e8b66e'), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='Print exact rational bounds for independent checks.')
    parser.add_argument('--figure', action='store_true', help='Regenerate the standalone radial graph.')
    args = parser.parse_args()
    rows = prove()
    if args.figure:
        (HERE/'fold_annulus.svg').write_text(figure(rows))
    if args.json:
        print(json.dumps(record(rows)))
    else:
        print('All 181 degree settings have rational inner/outer radius enclosures narrower than 1e-16.')
        print('Their annuli tighten strictly, and every two-decimal radius display is unambiguous.')
        for degree in (0, 45, 90, 135, 180):
            r, s = rows[degree]
            print(f'{degree:3} degrees: {float(r.midpoint()):.10f} through {float(s.midpoint()):.10f}')


if __name__ == '__main__':
    main()
