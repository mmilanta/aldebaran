"""A still comparison of equal gaps, density quantiles, and finite placement.

Uses the proved rational enclosures in shifted_placement.json. Coordinates
and printed decimals are rounded; this program makes no proof decisions.
"""

from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def figure():
    source = json.loads((HERE/'shifted_placement.json').read_text())
    row = next(r for r in source['rows'] if r['gaps'] == 4)
    middle = lambda pair: float((Q(pair[0])+Q(pair[1]))/2)
    optimal = [middle(p) for p in row['nodes']]
    density = [middle(p) for p in row['density_nodes']]
    equal = [1, 1.5, 2, 2.5, 3]
    colors = {'white': '#f4f1e8', 'ink': '#c7c7d4', 'muted': '#aaaabd',
              'gold': '#e8b66e', 'blue': '#9fc7eb', 'green': '#a7d9bb'}
    n = lambda x: f'{x:.6f}'.rstrip('0').rstrip('.') or '0'
    xy = lambda p: ','.join(n(x) for x in p)
    text = lambda x, y, s, size=21, color='ink', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{colors[color]}" {extra}>{escape(str(s))}</text>')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1630" viewBox="0 0 1200 1630" role="group" aria-labelledby="title description">',
             '<title id="title">Put more curves where the intercept bends</title>',
             '<desc id="description">Five parabolas with cubic intercepts share outer slopes one and three. Equal slope gaps give total bounded area 5.0625. The unique finite optimum uses interior labels about 1.650241, 2.162146, and 2.603607, giving area about 5.097122 and decreasing gaps. Both arrangement panels use identical coordinates and unit scale. Three slope rulers compare equal spacing, the asymptotic density quantiles, and the finite optimum. A table resolves the small differences between the latter two. This is a total-area optimum, not a smallest-pocket theorem, and applies to the cubic intercept family.</desc>',
             '<rect width="1200" height="1630" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 65, 'Put more curves where the intercept bends.', 43, 'white'),
             text(35, 111, 'Five parabolas. Six pockets. One unique largest total.', 25),
             text(35, 153, 'Cubic intercepts: Xₚ = Y²/2 − pY + p³/3. The outer labels stay at 1 and 3.', 23)]
    for i, slopes in enumerate((equal, optimal)):
        left, top, scale = 35+580*i, 202, 29
        origin, center = left+28, 620
        project = lambda p: (origin+scale*p[0], center-scale*p[1])
        def arc(p, low, high, move=True):
            X = lambda y: y*y/2-p*y+p**3/3
            a, b = (X(low), low), (X(high), high)
            c = (a[0]+(low-p)*(high-low)/2, (low+high)/2)
            return (f'M{xy(project(a))}' if move else '')+f'Q{xy(project(c))} {xy(project(b))}'
        secants = [(a*a+a*b+b*b)/3 for a, b in zip(slopes, slopes[1:])]
        mean = 13/3
        # Inner edge goes upwards; outer edge returns downwards.
        inner = ''.join(arc(slopes[j+1], a, b, j == 0)
                        for j, (a, b) in enumerate(zip(secants, secants[1:])))
        outer = arc(slopes[-1], secants[-1], mean, False)+arc(slopes[0], mean, secants[0], False)
        band = inner+outer+'Z'
        total = 81/16 if i == 0 else middle(row['area'])
        parts += [f'<g data-arrangement="{i}" data-slopes="{",".join(str(p) for p in slopes)}" data-origin="{origin}" data-center="{center}" data-scale="{scale}">',
                  f'<rect x="{left}" y="{top}" width="550" height="484" rx="14" fill="#141829" stroke="#383b50"/>',
                  text(left+22, top+40, 'Equal slope gaps.' if i == 0 else 'The finite optimum.', 28, 'white'),
                  text(left+22, top+75, '1, 1.5, 2, 2.5, 3' if i == 0 else 'Gaps decrease toward the right.', 21, 'blue' if i == 0 else 'green'),
                  f'<defs><clipPath id="arrangement-{i}-clip"><rect x="{left+18}" y="{top+96}" width="514" height="290"/></clipPath></defs>',
                  f'<rect x="{left+18}" y="{top+96}" width="514" height="290" fill="#0b0e1a"/>',
                  f'<g clip-path="url(#arrangement-{i}-clip)">',
                  f'<path d="{band}" fill="{colors["blue" if i == 0 else "green"]}" fill-opacity=".3" data-role="band"/>']
        for j, p in enumerate(slopes):
            color = colors['gold' if j in (0, len(slopes)-1) else 'blue' if i == 0 else 'green']
            parts += [f'<path d="{arc(p, 1, 10)}" fill="none" stroke="{color}" stroke-width="{2.4 if j in (0, len(slopes)-1) else 1.9}" data-role="branch" data-slope="{p}"/>']
        parts += ['</g>', text(left+22, top+426, f'Total ≈ {total:.9f}' if i else 'Total = 81/16 = 5.0625', 25, 'white'),
                  text(left+22, top+462, 'All six bounded pockets are shaded.', 21), '</g>']
    gain = (middle(row['area'])/(81/16)-1)*100
    parts += [text(35, 733, f'The optimized total gains about {gain:.4f}%. Both panels use identical unit scales.', 22),
              text(35, 770, 'This maximizes the whole band; it does not maximize the smallest pocket.', 22),
              text(35, 833, 'Three ways to place the same five slopes.', 31, 'white')]
    for j, (nodes, label, color) in enumerate(((equal, 'Equal gaps', 'blue'),
                                              (density, 'Asymptotic density', 'gold'),
                                              (optimal, 'Finite optimum', 'green'))):
        y = 930+112*j
        parts += [text(35, y-30, label, 22, color),
                  f'<path d="M100,{y}h1000" stroke="#555b78" stroke-width="1.5"/>']
        for k, p in enumerate(nodes):
            x = 100+500*(p-1)
            parts += [f'<path d="M{n(x)},{y-9}v18" stroke="{colors[color]}" stroke-width="2" data-role="slope-tick"/>',
                      f'<circle cx="{n(x)}" cy="{y}" r="4" fill="{colors[color]}"/>']
            if j == 0 or k in (0, 4):
                parts += [text(n(x), y+35, f'{p:g}', 18, 'muted', 'text-anchor="middle"')]
    parts += [text(35, 1240, 'Density and finite placement almost agree. The table resolves the difference:', 22),
              text(35, 1295, 'Interior label', 20, 'muted'), text(300, 1295, 'Equal gaps', 20, 'blue'),
              text(540, 1295, 'Density quantile', 20, 'gold'), text(850, 1295, 'Finite optimum', 20, 'green')]
    for j in range(1, 4):
        y = 1345+46*(j-1)
        parts += [text(35, y, j, 23), text(300, y, f'{equal[j]:g}', 23),
                  text(540, y, f'{density[j]:.9f}', 23), text(850, y, f'{optimal[j]:.9f}', 23, 'white')]
    parts += [text(35, 1500, 'An increasing ratio recurrence selects the unique finite optimum for every count.', 22),
              text(35, 1541, 'The saved node and area bounds are rational. These coordinates and decimals are rounded.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/shifted_placement.md">',
              text(35, 1592, 'Follow the finite-placement proof and its exact enclosures ↗', 22, 'gold'), '</a>', '</g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'shifted_placement.svg').write_text(figure())
    print('Wrote the rounded finite-placement comparison from the saved rational node and area enclosures.')
