"""Draw the certified four-curve frontier and two complete arrangements.

The proof and rational enclosures live in cubic_frontier.py/json.
Graph samples and exported coordinates here are rounded illustrations.
Only the standard library is needed.
"""

from html import escape
import json
from math import sqrt
from pathlib import Path

from cubic_maximin_figure import COLORS, LETTERS, RUNS, geometry, midpoint

HERE = Path(__file__).resolve().parent


def areas(x, y):
    a = (x-1)*(y-x)*(y-1)*(1+x+y)**2/18
    b = (y-x)*(3-y)*(3-x)*(x+y+3)**2/18
    c = single(x)-a
    return a, c, b


def single(x):
    return (x-1)*(3-x)*(x+4)**2/9


def equal_y(x):
    lo, hi = 2.45, 2.62
    for _ in range(60):
        middle = (lo+hi)/2
        if single(middle) > single(x):
            lo = middle
        else:
            hi = middle
    return (lo+hi)/2


def figure():
    data = json.loads((HERE/'cubic_frontier.json').read_text())
    start, switch, finish = data['endpoints']
    middle = next(row for row in data['samples'] if midpoint(row['nodes'][1]) == 1.75)
    nodes = lambda row: [midpoint(box) for box in row['nodes']]
    x0, sigma, alpha = [nodes(row)[1] for row in (start, switch, finish)]
    first, second = [], []
    for i in range(201):
        x = x0+(sigma-x0)*i/200
        y = (x+3+sqrt(17*x*x+6*x+153))/8
        a, c, b = areas(x, y)
        first.append((b, a+c+b))
        x = sigma+(alpha-sigma)*i/200
        y = equal_y(x)
        a, c, b = areas(x, y)
        second.append((min(a, b), a+c+b))
    number = lambda x: f'{x:.7f}'.rstrip('0').rstrip('.') or '0'
    pair = lambda p: ','.join(number(x) for x in p)
    text = lambda x, y, s, size=21, color='ink', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{COLORS[color]}" {extra}>{escape(str(s))}</text>')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="2070" viewBox="0 0 1200 2070" role="group" aria-labelledby="title description">',
             '<title id="title">First one pocket. Then two.</title>',
             '<desc id="description">The complete efficient total-area and smallest-pocket frontier for four cubic-intercept parabolas with outer labels one and three has two branches. First only triangle B grows. At labels about 1.825622 and 2.459833, triangles A and B tie; both then grow together until all three pockets are equal. A full frontier graph and an explicitly enlarged first-branch graph use different axis scales. Two complete arrangements below share coordinates and unit scale: the switch, and first interior label seven quarters. Their area table and slope rulers show the change. The exact global proof uses rational sign certificates; the graph samples, coordinates, and decimal readouts in this drawing are rounded illustrations.</desc>',
             '<rect width="1200" height="2070" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 65, 'First one pocket. Then two.', 48, 'white'),
             text(35, 111, 'Every point gives the largest total for its smallest-pocket requirement.', 24),
             text(35, 153, 'Four curves: Xₚ = Y²/2 − pY + p³/3. Outer slope labels: 1 and 3.', 23),
             text(35, 204, 'B alone', 23, 'green'), text(190, 204, '→', 23),
             text(235, 204, 'A = B', 23, 'gold'), text(380, 204, '→', 23),
             text(425, 204, 'A = C = B', 23, 'white'),
             '<rect x="35" y="235" width="730" height="500" rx="14" fill="#141829" stroke="#383b50"/>',
             '<rect x="795" y="235" width="370" height="500" rx="14" fill="#141829" stroke="#383b50"/>',
             text(57, 274, 'The complete compromise.', 27, 'white'),
             text(817, 274, 'The short first branch.', 24, 'white'),
             text(817, 310, 'Enlarged on both axes.', 20),
             text(62, 313, 'Total area', 18, 'muted'),
             text(817, 350, 'Total area', 18, 'muted')]
    project = lambda p: (120+(p[0]-1.17)/.37*590, 635-(p[1]-4.54)/.32*300)
    for t in (4.55, 4.65, 4.75, 4.85):
        py = project((1.17, t))[1]
        parts += [f'<path d="M120,{number(py)}h590" stroke="#30354c"/>',
                  text(108, number(py+6), f'{t:.2f}', 18, 'muted', 'text-anchor="end"')]
    for s in (1.2, 1.3, 1.4, 1.5):
        px = project((s, 4.54))[0]
        parts += [f'<path d="M{number(px)},335v300" stroke="#30354c"/>',
                  text(number(px), 665, f'{s:.1f}', 18, 'muted', 'text-anchor="middle"')]
    path = lambda values, mapping: 'M'+'L'.join(pair(mapping(p)) for p in values)
    for values, color, branch in ((first, 'green', 'B'), (second, 'gold', 'A_B')):
        parts += [f'<path d="{path(values, project)}" fill="none" stroke="{COLORS[color]}" stroke-width="3" data-role="frontier" data-branch="{branch}"/>']
    for row, color in ((start, 'blue'), (switch, 'green'), (middle, 'gold'), (finish, 'white')):
        p = project((midpoint(row['smallest_area']), midpoint(row['total_area'])))
        parts += [f'<circle cx="{number(p[0])}" cy="{number(p[1])}" r="4.5" fill="{COLORS[color]}" data-role="frontier-point" data-name="{escape(row["name"])}"/>']
    parts += [text(167, 326, 'Largest total; switch just beside it.', 19),
              text(355, 425, 'Two triangles tie.', 22, 'gold'),
              text(451, 609, 'All three equal.', 22, 'white'),
              text(415, 708, 'Smallest-pocket area →', 21, 'muted', 'text-anchor="middle"')]
    # A separate inset is needed: the first branch loses only 0.000668% total.
    s0, s1 = first[0][0], first[-1][0]
    t0, t1 = first[0][1], first[-1][1]
    inset = lambda p: (850+(p[0]-s0)/(s1-s0)*265, 590-(p[1]-t1)/(t0-t1)*205)
    parts += [f'<path d="{path(first, inset)}" fill="none" stroke="{COLORS["green"]}" stroke-width="3" data-role="frontier-inset"/>']
    for label, p in (('Largest total', first[0]), ('Triangles tie', first[-1])):
        xx, yy = inset(p)
        parts += [f'<circle cx="{number(xx)}" cy="{number(yy)}" r="4.5" fill="{COLORS["green"]}"/>']
    parts += [text(861, 379, '4.842587', 18, 'muted'), text(845, 577, '4.842555', 18, 'muted'),
              text(850, 623, f'{s0:.6f}', 17, 'muted'),
              text(1115, 623, f'{s1:.6f}', 17, 'muted', 'text-anchor="end"'),
              text(850, 414, 'Largest total', 18), text(1115, 558, 'Triangles tie', 18, 'green', 'text-anchor="end"'),
              text(980, 665, 'Smallest area →', 20, 'muted', 'text-anchor="middle"'),
              text(817, 708, 'Axis spans differ from the full graph.', 17, 'muted'),
              text(35, 789, f'At the switch: +{100*(s1/s0-1):.2f}% minimum; −{100*(1-t1/t0):.6f}% total.', 27, 'white'),
              text(35, 831, 'Each percentage uses its own area at the largest-total placement as its baseline.', 21),
              text(35, 877, 'The second interior label first falls, then rises. Here are two stops along the way.', 23)]
    selected = (switch, middle)
    arrangements = [nodes(row) for row in selected]
    faces = [geometry(p) for p in arrangements]
    coords = []
    for slopes, polygons in zip(arrangements, faces):
        for vertices, branches in polygons:
            for k, branch in enumerate(branches):
                lo, hi = sorted((vertices[k][1], vertices[(k+1) % len(vertices)][1]))
                p = slopes[branch]
                for yy in (lo, hi, max(lo, min(hi, p))):
                    coords.append((yy*yy/2-p*yy+p**3/3, yy))
    xmin, xmax = min(p[0] for p in coords), max(p[0] for p in coords)
    ymin, ymax = min(p[1] for p in coords), max(p[1] for p in coords)
    unit = min(480/(xmax-xmin), 235/(ymax-ymin))
    for panel, (slopes, polygons, row) in enumerate(zip(arrangements, faces, selected)):
        left, top = 35+580*panel, 925
        origin, center = left+35-unit*xmin, top+254+unit*(ymax+ymin)/2
        project = lambda p: (origin+unit*p[0], center-unit*p[1])
        def arc(p, lo, hi, move=True):
            a, b = (lo*lo/2-p*lo+p**3/3, lo), (hi*hi/2-p*hi+p**3/3, hi)
            control = (a[0]+(lo-p)*(hi-lo)/2, (lo+hi)/2)
            return (f'M{pair(project(a))}' if move else '')+f'Q{pair(project(control))} {pair(project(b))}'
        parts += [f'<g data-arrangement="{panel}" data-slopes="{",".join(map(str, slopes))}" data-origin="{origin}" data-center="{center}" data-scale="{unit}">',
                  f'<rect x="{left}" y="{top}" width="550" height="514" rx="14" fill="#141829" stroke="#383b50"/>',
                  text(left+22, top+42, 'At the switch.' if panel == 0 else 'Farther along.', 29, 'white'),
                  text(left+22, top+80, 'A first catches B.' if panel == 0 else 'A and B grow together. C shrinks.', 21),
                  f'<rect x="{left+18}" y="{top+104}" width="514" height="300" fill="#0b0e1a"/>',
                  f'<defs><clipPath id="panel-{panel}"><rect x="{left+18}" y="{top+104}" width="514" height="300"/></clipPath></defs>',
                  f'<g clip-path="url(#panel-{panel})">']
        for p in slopes:
            parts += [f'<path d="{arc(p, ymin-.35, ymax+.35)}" fill="none" stroke="#555b78" stroke-width="1.4" data-role="branch" data-slope="{p}"/>']
        for k, (vertices, branches) in enumerate(polygons):
            d = ''.join(arc(slopes[branch], vertices[i][1], vertices[(i+1) % len(vertices)][1], i == 0)
                        for i, branch in enumerate(branches))+'Z'
            color = ('gold', 'blue', 'green')[k]
            parts += [f'<path d="{d}" fill="{COLORS[color]}" fill-opacity=".3" stroke="{COLORS[color]}" stroke-width="1.8" stroke-linejoin="round" data-role="face" data-run="{RUNS[k][0]},{RUNS[k][1]}" data-letter="{LETTERS[k]}"/>']
        for k, (vertices, branches) in enumerate(polygons):
            u = sum(v[0] for v in vertices)/len(vertices)
            yy = sum(v[1] for v in vertices)/len(vertices)
            xx, sy = project((u+yy*yy/2, yy))
            parts += [f'<circle cx="{number(xx)}" cy="{number(sy)}" r="11" fill="#101323"/>',
                      text(number(xx), number(sy+6), LETTERS[k], 17, ('gold', 'blue', 'green')[k], 'text-anchor="middle"')]
        parts += ['</g>', text(left+22, top+451, f'Total ≈ {midpoint(row["total_area"]):.9f}', 25, 'white'),
                  text(left+22, top+491, f'Smallest ≈ {midpoint(row["smallest_area"]):.9f}', 24), '</g>']
    parts += [text(35, 1486, 'Both complete arrangements share coordinates and unit scale.', 22)]
    for xx, label in ((55, 'Pocket'), (330, 'At the switch'), (770, 'Farther along')):
        parts += [text(xx, 1546, label, 22, 'muted')]
    for i, (letter, color) in enumerate(zip(LETTERS, ('gold', 'blue', 'green'))):
        yy = 1593+46*i
        parts += [text(55, yy, f'{letter} · '+('quadrilateral' if letter == 'C' else 'triangle'), 22, color)]
        for xx, row in zip((330, 770), selected):
            parts += [text(xx, yy, f'{midpoint(row["face_areas_A_C_B"][i]):.9f}', 24)]
    parts += [text(35, 1752, 'Keep the outer labels. Move both inner curves.', 28, 'white')]
    for i, slopes in enumerate(arrangements):
        yy, color = 1810+100*i, 'green' if i == 0 else 'gold'
        parts += [text(35, yy-24, 'At the switch' if i == 0 else 'Farther along', 20, color),
                  f'<path d="M120,{yy}h980" stroke="#555b78"/>']
        for k, p in enumerate(slopes):
            xx = 120+490*(p-1)
            parts += [f'<path d="M{number(xx)},{yy-9}v18" stroke="{COLORS[color]}" stroke-width="2" data-role="slope-tick"/>',
                      text(number(xx), yy+34, f'{p:.6f}' if k in (1, 2) else f'{p:g}', 19, color, 'text-anchor="middle"')]
    parts += [text(35, 1995, 'The proof covers every placement. The graph samples and printed decimals are rounded.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/cubic_frontier.md">',
              text(35, 2040, 'Follow both branches and the exact global certificate ↗', 22, 'gold'), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'cubic_frontier.svg').write_text(figure())
    print('Wrote the complete frontier, enlarged first branch, and two arrangements at one scale.')
