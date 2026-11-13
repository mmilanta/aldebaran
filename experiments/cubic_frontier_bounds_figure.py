"""Draw finite error bands for the short cubic-frontier branch.

The shaded bands are the uniform rational inequalities proved in
cubic_frontier_bounds.py. Central traces and curve coordinates are rounded
illustrations. No numerical subtraction of nearly equal total areas is used.
Standard library only; regenerate after running the certificate.
"""

from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

from cubic_frontier_bounds import models
from cubic_maximin_figure import COLORS, LETTERS, RUNS, geometry

HERE = Path(__file__).resolve().parent


def rounded_value(polynomial, epsilon):
    value = 0.0
    for coefficient in reversed(polynomial.c):
        if hasattr(coefficient, 'low'):
            coefficient = (coefficient.low+coefficient.high)/2
        value = value*epsilon+float(coefficient)
    return value


def figure():
    data = json.loads((HERE/'cubic_frontier_bounds.json').read_text())
    require_scope = data['root_polynomial_degree'] == 16 and len(data['uniform_root_tubes']) == 32
    if not require_scope:
        raise ValueError('Regenerate the rational certificate before drawing it.')
    _, total, _, gain, cost, *_ = models()
    number = lambda v: f'{v:.8f}'.rstrip('0').rstrip('.') or '0'
    pair = lambda point: ','.join(number(v) for v in point)
    text = lambda x, y, value, size=22, color='ink', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{COLORS[color]}" {extra}>{escape(str(value))}</text>')
    path = lambda points, project: 'M'+'L'.join(pair(project(p)) for p in points)
    epsilon = [i/2000 for i in range(201)]
    traces = [[], [], []]
    for e in epsilon:
        b, t = rounded_value(total['B'], e), rounded_value(total['T'], e)
        dg, dc = rounded_value(gain, e), rounded_value(cost, e)
        traces[0].append((e, dg/b/(8/27)))
        traces[1].append((e, dc/t/(16/2187)))
        traces[2].append((e, dc*b*b/(t*dg*dg)))
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600" role="group" aria-labelledby="title description">',
             '<title id="title">A limit with a ruler</title>',
             '<desc id="description">Four parabolas with cubic intercepts trade total area for a larger smallest pocket. For span parameter epsilon between zero and one tenth, finite rational bounds enclose the first step until the two triangles tie. A left graph divides the actual cubic gain and sixth-order cost by their leading predictions; gold and blue bands enclose their correction factors. A right graph magnifies the ratio of cost to squared gain: it lies between one twelfth minus epsilon squared over twenty and one twelfth minus epsilon squared over twenty-five. All bands hold continuously. Central traces and decimals are rounded illustrations. At outer labels three and four, the minimum gains about 0.025216 percent for a total-area cost of about 0.0000005271 percent. Below, all three complete pockets at the first triangle tie have been straightened and rescaled by one common area-preserving change of coordinates. This certifies spans with endpoint ratio at most four thirds; the general positive-span frontier remains a separate question.</desc>',
             '<rect width="1200" height="1600" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 66, 'A limit with a ruler.', 49, 'white'),
             text(35, 111, 'A tiny first improvement, now with finite error bounds.', 27),
             text(35, 156, 'Four curves. First grow the smaller triangle until both triangles tie.', 23),
             text(35, 200, 'ε = (b − a)/(b + 2a).   Here: 0 &lt; ε ≤ 1/10, or 1 &lt; b/a ≤ 4/3.'.replace('&lt;', '<'), 23, 'gold'),
             '<rect x="35" y="237" width="670" height="505" rx="14" fill="#141829" stroke="#383b50"/>',
             '<rect x="730" y="237" width="435" height="505" rx="14" fill="#141829" stroke="#383b50"/>',
             text(57, 279, 'How close are the leading laws?', 28, 'white'),
             text(57, 315, 'Actual value ÷ leading prediction', 20, 'muted'),
             text(752, 279, 'The ratio stays closer.', 28, 'white'),
             text(752, 315, 'Total cost ÷ minimum gain²', 20, 'muted')]
    left = lambda point: (119+point[0]*5290, 635-(point[1]-.68)/.34*265)
    right = lambda point: (821+point[0]*3030, 635-(point[1]-.08275)/.00063*265)
    for tick in (.7, .8, .9, 1.0):
        yy = left((0, tick))[1]
        parts += [f'<path d="M119,{number(yy)}h529" stroke="#30354c"/>',
                  text(106, number(yy+6), f'{tick:.1f}', 19, 'muted', 'text-anchor="end"')]
    for tick in (.0828, .0830, .0832):
        yy = right((0, tick))[1]
        parts += [f'<path d="M821,{number(yy)}h303" stroke="#30354c"/>',
                  text(808, number(yy+6), f'{tick:.4f}', 17, 'muted', 'text-anchor="end"')]
    for mapping, width in ((left, 529), (right, 303)):
        for tick in (0, .05, .1):
            xx = mapping((tick, 0))[0]
            parts += [f'<path d="M{number(xx)},370v265" stroke="#30354c"/>',
                      text(number(xx), 667, f'{tick:g}', 18, 'muted', 'text-anchor="middle"')]
    for name, color, lo, hi in (
        ('gain', 'gold', lambda e: 1-1.5*e-e*e/5, lambda e: 1-1.5*e+e*e/5),
        ('cost', 'blue', lambda e: 1-3*e+e*e, lambda e: 1-3*e+3*e*e)):
        points = [(e, lo(e)) for e in epsilon]+[(e, hi(e)) for e in reversed(epsilon)]
        parts += [f'<path d="{path(points, left)}Z" fill="{COLORS[color]}" fill-opacity=".23" data-role="certified-band" data-quantity="{name}"/>']
    ratio_points = [(e, 1/12-e*e/20) for e in epsilon]+[(e, 1/12-e*e/25) for e in reversed(epsilon)]
    parts += [f'<path d="{path(ratio_points, right)}Z" fill="{COLORS["green"]}" fill-opacity=".3" data-role="certified-band" data-quantity="ratio"/>']
    for points, color, project, name in zip(traces, ('gold', 'blue', 'green'), (left, left, right), ('gain', 'cost', 'ratio')):
        parts += [f'<path d="{path(points, project)}" fill="none" stroke="{COLORS[color]}" stroke-width="2.7" data-role="central-trace" data-quantity="{name}"/>']
    yy = right((0, 1/12))[1]
    parts += [f'<path d="M821,{number(yy)}h303" stroke="#aaaabd" stroke-dasharray="5 6"/>',
              text(1105, number(yy-12), '1/12', 19, 'muted', 'text-anchor="end"'),
              text(119, 349, 'Gain / [(8/27) ε³]', 18, 'gold'),
              text(380, 349, 'Cost / [(16/2187) ε⁶]', 18, 'blue'),
              text(390, 709, 'Span parameter ε →', 21, 'muted', 'text-anchor="middle"'),
              text(970, 709, 'Span parameter ε →', 21, 'muted', 'text-anchor="middle"'),
              text(35, 791, 'Shaded bands are proved for every ε. The central traces are rounded illustrations.', 22),
              text(35, 834, '1/12 − ε²/20 < cost/gain² < 1/12 − ε²/25', 29, 'green'),
              text(35, 891, 'At ε = 1/10: outer labels 3 and 4.', 31, 'white'),
              '<rect x="35" y="920" width="550" height="126" rx="12" fill="#141829" stroke="#383b50"/>',
              '<rect x="615" y="920" width="550" height="126" rx="12" fill="#141829" stroke="#383b50"/>',
              text(57, 957, 'Smallest-pocket gain', 22, 'gold'),
              text(57, 1008, '+0.025216%', 39, 'white'),
              text(637, 957, 'Total-area cost', 22, 'blue'),
              text(637, 1008, '−0.0000005271%', 39, 'white'),
              text(35, 1084, 'Each percentage uses its own area at the largest-total placement as its baseline.', 21)]
    # The usual row slide straightens every parabola, preserving area.
    # The common affine map (u,Y) -> (2(u+3.5Y-h(3.5)), (Y-37/3)/2)
    # also has determinant one and makes the pockets easier to read.
    slopes = [3.0]+[3+sum(float(Q(c))*.1**i for i, c in enumerate(data['root_polynomials']['switch'][key]))
                    for key in ('x', 'y')]+[4.0]
    faces = geometry(slopes)
    transform = lambda p: (2*(p[0]+3.5*p[1]-3.5**3/3), (p[1]-37/3)/2)
    coordinates = [transform(p) for vertices, _ in faces for p in vertices]
    xmin, xmax = min(p[0] for p in coordinates), max(p[0] for p in coordinates)
    ymin, ymax = min(p[1] for p in coordinates), max(p[1] for p in coordinates)
    unit = min(610/(xmax-xmin), 310/(ymax-ymin))
    origin, center = 70-unit*xmin, 1290+unit*(ymax+ymin)/2
    project = lambda point: (origin+unit*point[0], center-unit*point[1])
    parts += ['<rect x="35" y="1114" width="670" height="354" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
              f'<g data-role="arrangement" data-coordinates="area-preserving-straightened" data-slopes="{",".join(map(str, slopes))}" data-scale="{unit}" data-origin="{origin}" data-center="{center}">']
    for i, (vertices, branches) in enumerate(faces):
        d = path([transform(p) for p in vertices], project)+'Z'
        color = ('gold', 'blue', 'green')[i]
        parts += [f'<path d="{d}" fill="{COLORS[color]}" fill-opacity=".3" stroke="{COLORS[color]}" stroke-width="1.8" data-role="face" data-letter="{LETTERS[i]}" data-run="{RUNS[i][0]},{RUNS[i][1]}"/>']
        u, yy = [sum(v[k] for v in vertices)/len(vertices) for k in (0, 1)]
        xx, sy = project(transform((u, yy)))
        parts += [f'<circle cx="{number(xx)}" cy="{number(sy)}" r="11" fill="#101323"/>',
                  text(number(xx), number(sy+6), LETTERS[i], 17, color, 'text-anchor="middle"')]
    parts += ['</g>', text(735, 1159, 'At the first tie.', 29, 'white'),
              text(735, 1205, 'The gold and green triangles', 21),
              text(735, 1240, 'have the same area.', 21),
              text(735, 1293, 'The blue quadrilateral is larger.', 21, 'blue'),
              text(735, 1346, 'Straightened and rescaled.', 21),
              text(735, 1381, 'One change preserves all areas.', 21),
              text(35, 1515, 'The complete two-stage frontier is proved on this span range. These errors concern its first step.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/cubic_frontier_bounds.md">',
              text(35, 1563, 'Follow the finite bounds and the uniform frontier proof ↗', 23, 'gold'), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'cubic_frontier_bounds.svg').write_text(figure())
    print('Wrote three continuous error bands, rounded traces, and all three complete curve faces.')
