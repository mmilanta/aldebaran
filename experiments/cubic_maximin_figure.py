"""Draw the four-curve total-area and smallest-pocket optima at one scale.

The mathematical certificate is cubic_maximin.py. This generator only
rounds saved rational enclosures to SVG coordinates and printed readouts.
"""

from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLORS = {'white': '#f4f1e8', 'ink': '#c7c7d4', 'muted': '#aaaabd',
          'gold': '#e8b66e', 'blue': '#9fc7eb', 'green': '#a7d9bb'}
RUNS = ((1, 1), (1, 2), (2, 2))
LETTERS = ('A', 'C', 'B')


def midpoint(box):
    return float(sum(map(Q, box))/2)


def geometry(slopes):
    points = [(p, p**3/3) for p in slopes]
    def crossing(i, j):
        a, b = points[i], points[j]
        y = (b[1]-a[1])/(b[0]-a[0])
        return a[1]-a[0]*y, y
    out = []
    for i, j in RUNS:
        pairs = ((i-1, i), (i-1, j+1), (i, j+1)) if i == j else (
            (i-1, j), (i-1, j+1), (i, j+1), (i, j))
        branches = (i-1, j+1, i) if i == j else (i-1, j+1, i, j)
        out.append(([crossing(a, b) for a, b in pairs], branches))
    return out


def figure():
    data = json.loads((HERE/'cubic_maximin.json').read_text())
    total, best = data['total_optimizer'], data['maximin']
    arrangements = [[midpoint(p) for p in row['nodes']] for row in (total, best)]
    faces = [geometry(p) for p in arrangements]
    # Bounds include the true quadratic extrema of every complete face arc.
    coords = []
    for slopes, polygons in zip(arrangements, faces):
        for vertices, branches in polygons:
            for k, branch in enumerate(branches):
                lo, hi = sorted((vertices[k][1], vertices[(k+1) % len(vertices)][1]))
                p = slopes[branch]
                for y in (lo, hi, max(lo, min(hi, p))):
                    coords.append((y*y/2-p*y+p**3/3, y))
    xmin, xmax = min(p[0] for p in coords), max(p[0] for p in coords)
    ymin, ymax = min(p[1] for p in coords), max(p[1] for p in coords)
    scale = min(480/(xmax-xmin), 235/(ymax-ymin))
    number = lambda x: f'{x:.7f}'.rstrip('0').rstrip('.') or '0'
    pair = lambda p: ','.join(number(x) for x in p)
    text = lambda x, y, s, size=21, color='ink', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{COLORS[color]}" {extra}>{escape(str(s))}</text>')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1510" viewBox="0 0 1200 1510" role="group" aria-labelledby="title description">',
             '<title id="title">Three pockets, the same room</title>',
             '<desc id="description">Four parabolas with cubic intercepts and fixed outer slope labels one and three make three bounded pockets: triangles A and B and quadrilateral C. Two complete arrangements use the same coordinates and unit scale. The unique largest-total placement has total area about 4.842587 and smallest area about 1.175535. The unique largest-minimum placement makes all three areas about 1.521008, at total about 4.563023. Its interior labels are about 1.630620 and 2.611245. The smallest pocket grows about 29.39 percent, while total area falls about 5.77 percent, each relative to the largest-total arrangement and its respective area baseline. A table compares every pocket; two slope rulers show which curves moved. An exact cubic equation and global concavity certificate prove the finite four-curve result. These coordinates and printed decimals are rounded.</desc>',
             '<rect width="1200" height="1510" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 65, 'Three pockets, the same room.', 47, 'white'),
             text(35, 111, 'Give the smallest one more room by equalizing all three.', 25),
             text(35, 153, 'Four curves: Xₚ = Y²/2 − pY + p³/3. Outer slope labels: 1 and 3.', 23)]
    for panel, (slopes, polygons, row) in enumerate(zip(arrangements, faces, (total, best))):
        left, top = 35+580*panel, 200
        origin = left+35-scale*xmin
        center = top+254+scale*(ymax+ymin)/2
        project = lambda p: (origin+scale*p[0], center-scale*p[1])
        X = lambda p, y: y*y/2-p*y+p**3/3
        def arc(p, low, high, move=True):
            a, b = (X(p, low), low), (X(p, high), high)
            control = (a[0]+(low-p)*(high-low)/2, (low+high)/2)
            return (f'M{pair(project(a))}' if move else '')+f'Q{pair(project(control))} {pair(project(b))}'
        parts += [f'<g data-arrangement="{panel}" data-slopes="{",".join(str(x) for x in slopes)}" data-origin="{origin}" data-center="{center}" data-scale="{scale}">',
                  f'<rect x="{left}" y="{top}" width="550" height="514" rx="14" fill="#141829" stroke="#383b50"/>',
                  text(left+22, top+42, 'The largest total.' if panel == 0 else 'The largest minimum.', 29, 'white'),
                  text(left+22, top+80, 'Keep as much area as possible.' if panel == 0 else 'Every pocket has the same area.', 21),
                  f'<rect x="{left+18}" y="{top+104}" width="514" height="300" fill="#0b0e1a"/>',
                  f'<defs><clipPath id="panel-{panel}"><rect x="{left+18}" y="{top+104}" width="514" height="300"/></clipPath></defs>',
                  f'<g clip-path="url(#panel-{panel})">']
        for p in slopes:
            parts += [f'<path d="{arc(p, ymin-.35, ymax+.35)}" fill="none" stroke="#555b78" stroke-width="1.4" data-role="branch" data-slope="{p}"/>']
        for k, (vertices, branches) in enumerate(polygons):
            path = ''.join(arc(slopes[branch], vertices[i][1], vertices[(i+1) % len(vertices)][1], i == 0)
                           for i, branch in enumerate(branches))+'Z'
            color = ('gold', 'blue', 'green')[k]
            parts += [f'<path d="{path}" fill="{COLORS[color]}" fill-opacity=".3" stroke="{COLORS[color]}" stroke-width="1.8" stroke-linejoin="round" data-role="face" data-run="{RUNS[k][0]},{RUNS[k][1]}" data-letter="{LETTERS[k]}"/>']
        for k, (vertices, branches) in enumerate(polygons):
            u = sum(v[0] for v in vertices)/len(vertices)
            y = sum(v[1] for v in vertices)/len(vertices)
            x, sy = project((u+y*y/2, y))
            parts += [f'<circle cx="{number(x)}" cy="{number(sy)}" r="11" fill="#101323"/>',
                      text(number(x), number(sy+6), LETTERS[k], 17, ('gold', 'blue', 'green')[k], 'text-anchor="middle"')]
        total_area = midpoint(row['total_area'])
        min_area = min(map(midpoint, row['face_areas'])) if panel == 0 else midpoint(row['smallest_area'])
        parts += ['</g>', text(left+22, top+451, f'Total ≈ {total_area:.9f}', 25, 'white'),
                  text(left+22, top+491, f'Smallest ≈ {min_area:.9f}', 24), '</g>']
    smallest = midpoint(best['smallest_area'])
    gain = 100*(smallest/min(map(midpoint, total['face_areas']))-1)
    cost = 100*(1-midpoint(best['total_area'])/midpoint(total['total_area']))
    parts += [text(35, 761, f'Smallest area: +{gain:.2f}%. Total area: −{cost:.2f}%.', 28, 'white'),
              text(35, 802, 'Each change uses its own area at the largest-total placement as its baseline.', 21),
              text(35, 841, 'Both drawings share coordinates and unit scale. All three complete pockets are shaded.', 21)]
    for x, label, color in ((55, 'Pocket', 'muted'), (330, 'Largest total', 'muted'), (770, 'Largest minimum', 'muted')):
        parts += [text(x, 904, label, 22, color)]
    for i, (letter, color, box) in enumerate(zip(LETTERS, ('gold', 'blue', 'green'), total['face_areas'])):
        y = 953+46*i
        parts += [text(55, y, f'{letter} · '+('quadrilateral' if letter == 'C' else 'triangle'), 22, color),
                  text(330, y, f'{midpoint(box):.9f}', 24), text(770, y, f'{smallest:.9f}', 24, 'white')]
    parts += [text(35, 1122, 'The outer labels stay put. Move both interior curves.', 29, 'white')]
    for i, slopes in enumerate(arrangements):
        y, color = 1190+100*i, 'blue' if i == 0 else 'green'
        parts += [text(35, y-24, 'Largest total' if i == 0 else 'Largest minimum', 20, color),
                  f'<path d="M120,{y}h980" stroke="#555b78"/>']
        for k, p in enumerate(slopes):
            x = 120+490*(p-1)
            parts += [f'<path d="M{number(x)},{y-9}v18" stroke="{COLORS[color]}" stroke-width="2" data-role="slope-tick"/>',
                      text(number(x), y+34, f'{p:.6f}' if k in (1, 2) else f'{p:g}', 19, color, 'text-anchor="middle"')]
    parts += [text(35, 1383, 'A cubic equation selects this unique finite maximum. The proof covers all placements.', 22),
              text(35, 1424, 'The saved area and node bounds are rational. These coordinates and decimals are rounded.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/cubic_maximin.md">',
              text(35, 1473, 'Follow the exact four-curve proof and its global certificate ↗', 22, 'gold'),
              '</a></g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'cubic_maximin.svg').write_text(figure())
    print('Wrote the complete four-curve comparison with shared coordinates and unit scale.')
