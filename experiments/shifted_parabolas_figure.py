"""Draw the exact midpoint and non-midpoint cubic-intercept pockets.

No external packages. The saved record retains rational/quadratic values;
only the SVG coordinates and decimal labels are rounded.
"""

import argparse
from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

from blend_cusps import require
from parabolic_balance import Quadratic
from parabolic_tradeoff import serialize
from shifted_parabolas import cubic_area

HERE = Path(__file__).resolve().parent


def pocket(r):
    slopes = (Q(1), r, Q(3))
    vertices = []
    for a, b in ((slopes[0], slopes[1]), (slopes[0], slopes[2]), (slopes[1], slopes[2])):
        y = (a*a+a*b+b*b)/3
        vertices.append((y*y/2-a*y+a**3/3, y))
    # Integrating X dY around the curved boundary independently of A(r).
    branches = (slopes[0], slopes[2], slopes[1])
    primitive = lambda p, y: y**3/6-p*y*y/2+p**3*y/3
    integral = sum(primitive(p, vertices[(i+1) % 3][1])-primitive(p, vertices[i][1])
                   for i, p in enumerate(branches))
    require(integral == cubic_area(r) > 0, "The exact curved boundary misses its pocket area.")
    for x, y in vertices:
        require(sum(x == y*y/2-p*y+p**3/3 for p in slopes) == 2,
                "A pocket vertex must be a transverse double meeting.")
    return {"inserted_slope": r, "slopes": slopes, "vertices": vertices,
            "branches": branches, "area": integral,
            "horizontal_shifts": [p**3/3-p*p/2 for p in slopes]}


def record():
    best = Quadratic(11, Q(1, 2), Q(1, 2))
    rows = (pocket(Q(2)), pocket(best))
    require(2*best*best-2*best-5 == 0 and rows[0]["area"] == 4
            and rows[1]["area"] == Quadratic(11, Q(-71, 36), Q(11, 6)),
            "The selected insertion must be the exact cubic maximum.")
    return {"scope": "Complete three-parabola arrangements X=Y^2/2-pY+p^3/3, outer slopes 1 and 3.",
            "rows": rows, "relative_gain": rows[1]["area"]/4-1}


def figure(data):
    colors = {"white": "#f4f1e8", "ink": "#c7c7d4", "muted": "#aaaabd",
              "gold": "#e8b66e", "blue": "#9fc7eb", "green": "#a7d9bb"}
    n = lambda x: f"{float(x):.6f}".rstrip("0").rstrip(".") or "0"
    xy = lambda p: ','.join(n(x) for x in p)
    text = lambda x, y, s, size=21, color="ink", extra="": (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{colors[color]}" {extra}>{escape(str(s))}</text>')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1370" viewBox="0 0 1200 1370" role="group" aria-labelledby="title description">',
             '<title id="title">A midpoint moves</title>',
             '<desc id="description">Two three-parabola arrangements share the outer slope labels one and three and the cubic intercept law h(p)=p cubed over three. All parabolas have the same shape. At the midpoint slope two the pocket has area four. Moving that slope to (one plus square root of eleven) over two, about 2.158312, makes the unique largest pocket, with area (66 square root of eleven minus 71) over 36, about 4.108257. This gains about 2.7064 percent. The drawing panels use identical unit scales and coordinates. A graph below plots pocket area against the inserted slope with different axis scales. This shifted family differs from the earlier quadratic-intercept model.</desc>',
             '<rect width="1200" height="1370" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 68, 'A midpoint moves.', 51, "white"),
             text(35, 114, 'Slide the parabolas sideways. The best new curve follows.', 25),
             text(35, 155, 'Xₚ = Y²/2 − pY + p³/3 · outer slope labels 1 and 3 stay fixed.', 23)]

    for i, row in enumerate(data['rows']):
        left, top, scale = 35+580*i, 202, 41
        origin, center = left+28, 672
        project = lambda p: (origin+scale*float(p[0]), center-scale*float(p[1]))
        def arc(p, low, high, move=True):
            p, low, high = float(p), float(low), float(high)
            X = lambda y: y*y/2-p*y+p**3/3
            a, b = (X(low), low), (X(high), high)
            c = (a[0]+(low-p)*(high-low)/2, (low+high)/2)
            return (f'M{xy(project(a))}' if move else '')+f'Q{xy(project(c))} {xy(project(b))}'
        vertices = row['vertices']
        d = ''.join(arc(p, vertices[j][1], vertices[(j+1) % 3][1], j == 0)
                    for j, p in enumerate(row['branches']))+'Z'
        parts += [f'<g data-pocket="{i}" data-origin="{origin}" data-center="{center}" data-scale="{scale}">',
                  f'<rect x="{left}" y="{top}" width="550" height="484" rx="14" fill="#141829" stroke="#383b50"/>',
                  text(left+22, top+40, 'Choose the midpoint.' if i == 0 else 'Choose the largest pocket.', 27, "white"),
                  text(left+22, top+75, 'r = 2' if i == 0 else 'r* = (1 + √11)/2 ≈ 2.158312', 22, "blue" if i == 0 else "green"),
                  f'<defs><clipPath id="pocket-{i}-clip"><rect x="{left+18}" y="{top+96}" width="514" height="290"/></clipPath></defs>',
                  f'<rect x="{left+18}" y="{top+96}" width="514" height="290" fill="#0b0e1a"/>']
        for y in (2, 4, 6, 8):
            screen = project((0, y))[1]
            parts += [f'<path d="M{left+18},{n(screen)}h514" stroke="#252b42"/>',
                      text(left+23, n(screen-5), y, 14, "muted")]
        parts += [f'<g clip-path="url(#pocket-{i}-clip)">',
                  f'<path d="{d}" fill="{colors["blue" if i == 0 else "green"]}" fill-opacity=".3" data-role="face"/>']
        for p in (Q(1), Q(3)):
            parts += [f'<path d="{arc(p, Q(7, 4), Q(35, 4))}" fill="none" stroke="{colors["gold"]}" stroke-width="2.4" data-role="outer" data-slope="{p}"/>']
        if i == 1:
            parts += [f'<path d="{arc(Q(2), Q(7, 4), Q(35, 4))}" fill="none" stroke="{colors["blue"]}" stroke-width="1.6" stroke-dasharray="5 5" data-role="midpoint-reference"/>']
        parts += [f'<path d="{arc(row["inserted_slope"], Q(7, 4), Q(35, 4))}" fill="none" stroke="{colors["blue" if i == 0 else "green"]}" stroke-width="2.8" data-role="inserted"/>']
        for vertex in vertices:
            x, y = project(vertex)
            parts += [f'<circle cx="{n(x)}" cy="{n(y)}" r="3.5" fill="{colors["white"]}"/>']
        parts += ['</g>', text(left+22, top+426, 'Area = 4' if i == 0 else 'Area = (66√11 − 71)/36', 25, "white"),
                  text(left+22, top+462, 'Equal slope gaps 1 : 1.' if i == 0 else 'About 4.108257 · a gain of 2.7064%.', 21), '</g>']

    parts += [text(35, 735, 'Same coordinates, same unit scale in both panels. Gold: the fixed outer curves.', 22),
              text(35, 772, 'The dashed blue curve keeps the old midpoint visible in the right panel.', 22),
              text(35, 822, 'Each curve slides by p³/3 − p²/2 from the earlier quadratic-intercept family.', 22),
              text(35, 879, 'Which inserted slope leaves the most room?', 30, "white")]
    # The area graph is sampled from its exact rational quartic.
    x0, y0, sx, sy = 100, 1195, 500, 60
    parts += [f'<g data-area-plot="cubic-intercepts" data-origin="{x0},{y0}" data-scales="{sx},{sy}">',
              '<rect x="100" y="915" width="1000" height="280" fill="#0b0e1a" stroke="#383b50"/>']
    for r in (Q(1), Q(3, 2), Q(2), Q(5, 2), Q(3)):
        x = x0+sx*(r-1)
        parts += [f'<path d="M{x},915v280" stroke="#252b42"/>', text(x, 1225, r, 18, "muted", 'text-anchor="middle"')]
    for a in (0, 2, 4):
        y = y0-sy*a
        parts += [f'<path d="M100,{y}h1000" stroke="#252b42"/>', text(85, y+6, a, 18, "muted", 'text-anchor="end"')]
    # A(r)=(-r^4-4r^3+13r^2+40r-48)/9. SVG has no native quartic
    # command, so rational samples draw the graph; pocket arcs above are exact
    # quadratics. The exact area formula remains in the record and note.
    samples = [(x0+sx*float(r-1), y0-sy*float(cubic_area(r)))
               for r in (Q(1)+Q(j, 250) for j in range(501))]
    parts += ['<path d="'+''.join(('M' if i == 0 else 'L')+xy(p) for i, p in enumerate(samples))
              +f'" fill="none" stroke="{colors["white"]}" stroke-width="2.7" data-role="area-curve"/>']
    for row, color in zip(data['rows'], ("blue", "green")):
        x, y = x0+sx*float(row['inserted_slope']-1), y0-sy*float(row['area'])
        parts += [f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="{colors[color]}" stroke="#101323" stroke-width="2"/>']
    parts += [text(580, 1060, 'Midpoint · 4', 20, "blue", 'text-anchor="end"'),
              text(710, 935, 'Maximum · 4.108257…', 20, "green"),
              text(100, 905, 'Pocket area ↑', 19), text(1100, 1265, 'Inserted slope r →', 20, "ink", 'text-anchor="end"'),
              '</g>', text(35, 1310, 'The area graph uses different axis scales. Its unique interior peak solves 2r² − 2r − 5 = 0.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/shifted_parabolas.md">',
              text(35, 1350, 'Follow the shifted-intercept calculation ↗', 21, "gold"), '</a>', '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save the exact data and rounded standalone SVG.')
    args = parser.parse_args()
    data = record()
    drawing = figure(data)
    if args.write:
        (HERE/'shifted_parabolas.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
        (HERE/'shifted_parabolas.svg').write_text(drawing)
    print('Two exact curved pocket integrals and six exact transverse vertices agree with the cubic maximum.')
    print('Only the standalone SVG and decimal labels are rounded; the saved quadratic data stay exact.')


if __name__ == '__main__':
    main()
