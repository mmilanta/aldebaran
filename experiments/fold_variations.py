"""A quiet sheet: seven and fourteen folds, with three backward-arm phases.

Every panel uses the original arm lengths and one common scale. Only the
backward arm's initial angle changes. The usual gcd rotation identity is
independent of that phase. Standard library only; no website runtime code.
"""

from fractions import Fraction as Q
from html import escape
from math import cos, gcd, pi, sin
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEGMENTS = 4096
SCALE = Q(9, 25)
PAIRS = ((8, 6), (15, 13))
PHASES = (0, pi/2, pi)
COLORS = ('#9fc7eb', '#e8b66e', '#a7d9bb')


def point(t, outer, inner, phase):
    return (245*cos(t)+140*cos(outer*t)+65*cos(-inner*t+phase),
            245*sin(t)+140*sin(outer*t)+65*sin(-inner*t+phase))


def figure():
    s = Q(-735, 1456)
    if (Q(102050)-36750*s-36400*s*s != Q(23155775, 208)
            or -36750-72800*s != 0):
        raise ValueError('The stated half-turn radial maximum changed.')
    number = lambda v: f'{v:.4f}'.rstrip('0').rstrip('.') or '0'
    text = lambda x, y, value, size=23, color='#c7c7d4', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1280" viewBox="0 0 1200 1280" role="group" aria-labelledby="title description">',
             '<title id="title">Keep the folds. Turn one arm.</title>',
             '<desc id="description">Six orbital line drawings share one scale and the original arm lengths 245, 140, and 65. The upper row uses rhythms eight and six, giving seven rotational folds. The lower row uses fifteen and thirteen, giving fourteen folds. In each row, the backward arm starts at zero, a quarter turn, and a half turn. The petal shapes change while their rotational fold counts stay fixed. The three phases are blue, gold, and green. Small center marks locate the origin. The curves are sampled illustrations with geometric position error less than 0.005 sheet units, including rounded coordinates. Links at the bottom open the original zero-phase drawings.</desc>',
             '<rect width="1200" height="1280" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 66, 'Keep the folds. Turn one arm.', 49, '#f4f1e8'),
             text(35, 113, 'The rhythms stay. Change where the backward arm begins.', 27),
             text(35, 157, 'The same scale and arm lengths. Seven folds above, fourteen below.', 23)]
    for column, label in enumerate(('At the start', 'A quarter turn', 'A half turn')):
        parts.append(text(215+385*column, 217, label, 25, COLORS[column], 'text-anchor="middle"'))
    for row, (outer, inner) in enumerate(PAIRS):
        fold = gcd(outer-1, inner+1)
        top, cy = 285+445*row, 465+445*row
        parts.append(text(35, top-23, f'{"Seven" if fold == 7 else "Fourteen"} folds · rhythms {outer} / {inner}', 26, '#f4f1e8'))
        # The chord interpolation error is at most max|z''| dt^2/8.
        # pi < 22/7 and vertex rounding contributes less than 1/10000.
        error = SCALE*(245+140*outer**2+65*inner**2)*Q(44, 7*SEGMENTS)**2/8+Q(1, 10000)
        if error >= Q(1, 200):
            raise ValueError('The drawing no longer meets its sampling-error bound.')
        for column, phase in enumerate(PHASES):
            left, cx = 35+385*column, 215+385*column
            coords = []
            for i in range(SEGMENTS+1):
                x, y = point(2*pi*i/SEGMENTS, outer, inner, phase)
                coords.append(number(cx+float(SCALE)*x)+','+number(cy-float(SCALE)*y))
            parts += [f'<g data-role="orbit-panel" data-outer="{outer}" data-inner="{inner}" data-fold="{fold}" data-phase="{phase}" data-scale="{float(SCALE)}" data-cx="{cx}" data-cy="{cy}">',
                      f'<rect x="{left}" y="{top}" width="360" height="360" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
                      f'<path d="M{"L".join(coords)}" fill="none" stroke="{COLORS[column]}" stroke-width=".85" stroke-linecap="round" stroke-linejoin="round" data-role="orbit"/>',
                      f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="#aaaabd"/>', '</g>']
    parts += [text(35, 1141, 'The same three arm lengths: 245, 140, 65. Only one starting angle changes.', 23),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_variations.md">',
              text(35, 1183, 'From petals to a ring: follow the little ellipse inside the turn ↗', 22, '#e8b66e'), '</a>',
              '<a href="https://mmilanta.github.io/aldebaran/?outer=8&amp;inner=6">',
              text(35, 1240, 'Draw the original sevenfold curve ↗', 23, '#e8b66e'), '</a>',
              '<a href="https://mmilanta.github.io/aldebaran/?outer=15&amp;inner=13">',
              text(625, 1240, 'Draw the original fourteenfold curve ↗', 23, '#e8b66e'), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'fold_variations.svg').write_text(figure())
    print('Wrote six drawings at one scale; all sampling errors are below 0.005 sheet units.')
    print('Exact half-turn radius range: 170 through sqrt(23155775/208).')
