"""Six drawings beyond the sliders, with the original three arm lengths.

Run: python3 experiments/fold_shoulder_figure.py
Standard library only. The selected phases are numerical picture choices,
not finite-event certificates for the analytic large-fold theorem.
"""

from fractions import Fraction as Q
from math import pi

from blend_cusps import require
from fold_contacts_figure import BG, BLUE, GOLD, HERE, INK, orbit, path, text

SEGMENTS = 16384
SCALE = Q(7, 20)
CHOICES = ((14, Q(973358851456924, 10**15)),
           (30, Q(914957492737127, 10**15)),
           (60, Q(900248531005621, 10**15)))


def figure():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="1000" viewBox="0 0 1260 1000" '
             'role="img" aria-labelledby="title desc" font-family="ui-sans-serif,system-ui,sans-serif">',
             '<title id="title">Beyond the sliders</title>',
             '<desc id="desc">Six curves use the original lengths 245, 140, and 65. '
             'Columns have fourteen, thirty, and sixty folds. The top row starts at zero phase, '
             'giving finer and finer petals; the bottom row turns the backward arm near the radial shoulder, '
             'giving overlapping rings. All six use one scale. These are numerical drawings at rounded '
             'phase choices, not new finite-event certificates. Chord and vertex errors stay below '
             '0.005 sheet units. The link below opens the analytic three-visit approach.</desc>',
             f'<rect width="1260" height="1000" fill="{BG}"/>',
             text(30, 53, 'Beyond the sliders', 42, INK),
             text(30, 91, 'The original three lengths. More folds, finer threads. Numerical drawings.', 23)]
    for j, (d, selected) in enumerate(CHOICES):
        error = SCALE*(245+140*(d+1)**2+65*(d-1)**2)*Q(44, 7*SEGMENTS)**2/8+Q(1, 100000)
        require(error < Q(1, 200), 'A drawing exceeds its chord/rounding error budget.')
        for row, phase in enumerate((Q(0), selected)):
            cx, cy = 210+420*j, 310+405*row
            phi = float(phase)*pi
            points = []
            for k in range(SEGMENTS+1):
                x, y = orbit(2*pi*k/SEGMENTS, d, phi)
                points.append((cx+float(SCALE)*x, cy-float(SCALE)*y))
            parts += [f'<g data-role="orbit-panel" data-folds="{d}" data-phase-ratio="{phase}" '
                      f'data-cx="{cx}" data-cy="{cy}" data-scale="{SCALE}">',
                      path(points, BLUE if row == 0 else GOLD, .48, 'data-role="orbit"'),
                      text(cx, cy+187, f'{d} folds · {float(phase):.6f}π', 22, INK, 'text-anchor="middle"'), '</g>']
    parts += ['<a href="https://mmilanta.github.io/aldebaran/experiments/fold_shoulder.md">',
              text(30, 969, 'Three visits approach the shoulder: follow the analytic calculation ↗', 23, GOLD),
              '</a></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'fold_shoulder.svg').write_text(figure())
    print('Wrote six larger-fold drawings at one scale; geometric error budgets are below 0.005 sheet units.')
