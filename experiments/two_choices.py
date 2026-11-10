"""A strictly convex intercept law with two equally good insertions.

For h(p)=p^4/4+epsilon*p^2/2 on [-1,1], the maximum splits into
two exactly when 0<epsilon<1/2. The selected epsilon=1/8 has rational
maximizers +/-1/2. Exact controls, data, and a rounded standalone SVG.
Only the standard library; see two_choices.md.
"""

import argparse
from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

from blend_cusps import require
from parabolic_tradeoff import serialize
from shifted_parabolas import check, crossing, variance_area

HERE = Path(__file__).resolve().parent


def h(p, epsilon):
    return p**4/4+epsilon*p*p/2


def area_at(r, epsilon):
    require(type(r) is Q and -1 <= r <= 1 and type(epsilon) is Q and epsilon > 0,
            'Use a rational inserted slope in [-1,1] and a positive rational epsilon.')
    return (1-r*r)*(r*r+1+2*epsilon)**2/16


def optimum(epsilon):
    require(type(epsilon) is Q and epsilon > 0, 'Use a positive rational epsilon.')
    squared = max(Q(0), (1-2*epsilon)/3)
    maximum = (1-squared)*(squared+1+2*epsilon)**2/16
    return {"epsilon": epsilon, "optimal_slope_squared": squared,
            "maximum_area": maximum, "midpoint_area": (1+2*epsilon)**2/16,
            "number_of_maximizers": 2 if squared > 0 else 1}


def pocket(r, epsilon=Q(1, 8)):
    slopes = (Q(-1), r, Q(1))
    points = [(p, h(p, epsilon)) for p in slopes]
    vertices = [crossing(points[i], points[j]) for i, j in ((0, 1), (0, 2), (1, 2))]
    # Undoing the common shear turns U into X=U+Y^2/2.
    vertices = [(u+y*y/2, y) for u, y in vertices]
    branches = (slopes[0], slopes[2], slopes[1])
    primitive = lambda p, y: y**3/6-p*y*y/2+h(p, epsilon)*y
    integral = sum(primitive(p, vertices[(j+1) % 3][1])-primitive(p, vertices[j][1])
                   for j, p in enumerate(branches))
    require(integral == area_at(r, epsilon) == check(points),
            'Fresh clipping, a curved integral, and the insertion polynomial disagree.')
    return {"slope": r, "slopes": slopes, "intercepts": [h(p, epsilon) for p in slopes],
            "vertices": vertices, "branches": branches, "area": integral}


def record():
    rows = [pocket(r) for r in (Q(-1, 2), Q(0), Q(1, 2))]
    require(rows[0]['area'] == rows[2]['area'] == Q(27, 256)
            and rows[1]['area'] == Q(25, 256), 'The selected symmetric maximum has the wrong exact area.')
    return {"scope": "Three complete shifted parabolas X=Y^2/2-pY+h(p), outer labels -1 and 1.",
            "epsilon": Q(1, 8), "rows": rows,
            "relative_gain_over_midpoint": Q(2, 25),
            "parameter_examples": [optimum(e) for e in (Q(1, 8), Q(1, 2), Q(3, 4))]}


def controls():
    comparisons = clipped = 0
    for i in range(1, 49):
        epsilon = Q(i, 32)
        row = optimum(epsilon)
        z = row['optimal_slope_squared']
        require(0 <= z < 1, 'The selected maximum must be interior.')
        for j in range(101):
            r = Q(-1)+Q(j, 50)
            require(area_at(r, epsilon) <= row['maximum_area'],
                    'A rational insertion beats the exact claimed maximum.')
            # Independent secant-variance area also exercises the family
            # away from its stationary points, including negative labels.
            if 0 < j < 100:
                points = [(p, h(p, epsilon)) for p in (Q(-1), r, Q(1))]
                require(variance_area(points) == area_at(r, epsilon),
                        'The general variance formula misses the quartic insertion area.')
            comparisons += 1
        if epsilon < Q(1, 2):
            d = 1-2*epsilon
            require(row['maximum_area']-row['midpoint_area'] == d*d*(9-4*d)/432 > 0,
                    'The symmetry-breaking gain has the wrong sign or coefficient.')
        else:
            require(z == 0 and row['maximum_area'] == row['midpoint_area'],
                    'The midpoint must be the unique optimum at and above the threshold.')
    for epsilon in (Q(1, 8), Q(1, 2), Q(3, 4)):
        for r in (Q(-1, 2), Q(0), Q(1, 2)):
            pocket(r, epsilon)
            clipped += 1
    invalid = 0
    for args in ((Q(2), Q(1)), (Q(0), Q(0)), (Q(0), Q(-1)), (0, Q(1)), (Q(0), .125)):
        try:
            area_at(*args)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid twin-placement control was accepted.')
    return comparisons, clipped, invalid


def figure(data):
    colors = {'white': '#f4f1e8', 'ink': '#c7c7d4', 'muted': '#aaaabd',
              'gold': '#e8b66e', 'blue': '#9fc7eb', 'green': '#a7d9bb'}
    n = lambda x: f'{float(x):.6f}'.rstrip('0').rstrip('.') or '0'
    xy = lambda p: ','.join(n(x) for x in p)
    text = lambda x, y, s, size=21, color='ink', extra='': (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{colors[color]}" {extra}>{escape(str(s))}</text>')
    epsilon = data['epsilon']
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1400" viewBox="0 0 1200 1400" role="group" aria-labelledby="title description">',
             '<title id="title">Two equally good places</title>',
             '<desc id="description">A strictly convex quartic intercept law has two global best insertions. Fix outer slope labels minus one and one, with intercept h(p)=p to the fourth over four plus p squared over sixteen. The midpoint slope zero encloses area 25 over 256. Either slope minus one half or plus one half encloses the larger area 27 over 256, an eight percent gain over the midpoint. Three panels show the complete pockets using identical coordinates and unit scales. The two best pockets are reflections. A graph of area against the inserted slope shows the equal peaks. The intercept second derivative is everywhere at least one eighth; strict convexity alone therefore does not imply a unique best insertion.</desc>',
             '<rect width="1200" height="1400" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 68, 'Two equally good places.', 49, 'white'),
             text(35, 113, 'Strictly convex intercepts can leave a choice.', 25),
             text(35, 155, 'Xₚ = Y²/2 − pY + h(p), with h(p) = p⁴/4 + p²/16. Outer labels: −1 and +1.', 23)]
    for i, row in enumerate(data['rows']):
        left, top, scale = 35+385*i, 204, 240
        origin, center = left+150, 452
        project = lambda p: (origin+scale*float(p[0]), center-scale*float(p[1]))
        def arc(p, low, high, move=True):
            p, low, high = float(p), float(low), float(high)
            X = lambda y: y*y/2-p*y+p**4/4+float(epsilon)*p*p/2
            a, b = (X(low), low), (X(high), high)
            c = (a[0]+(low-p)*(high-low)/2, (low+high)/2)
            return (f'M{xy(project(a))}' if move else '')+f'Q{xy(project(c))} {xy(project(b))}'
        vertices = row['vertices']
        d = ''.join(arc(p, vertices[j][1], vertices[(j+1) % 3][1], j == 0)
                    for j, p in enumerate(row['branches']))+'Z'
        color = 'blue' if i == 1 else 'green'
        parts += [f'<g data-twin-pocket="{i}" data-slope="{row["slope"]}" data-origin="{origin}" data-center="{center}" data-scale="{scale}">',
                  f'<rect x="{left}" y="{top}" width="360" height="482" rx="14" fill="#141829" stroke="#383b50"/>',
                  text(left+18, top+37, ['One best choice.', 'The midpoint.', 'Another best choice.'][i], 25, 'white'),
                  text(left+18, top+72, ['r = −1/2', 'r = 0', 'r = +1/2'][i], 23, color),
                  f'<defs><clipPath id="twin-{i}-clip"><rect x="{left+18}" y="{top+92}" width="324" height="300"/></clipPath></defs>',
                  f'<rect x="{left+18}" y="{top+92}" width="324" height="300" fill="#0b0e1a"/>',
                  f'<path d="M{left+18},{center}h324" stroke="#252b42"/>',
                  f'<g clip-path="url(#twin-{i}-clip)">',
                  f'<path d="{d}" fill="{colors[color]}" fill-opacity=".3" data-role="face"/>']
        for p in (Q(-1), Q(1)):
            parts += [f'<path d="{arc(p, Q(-3, 4), Q(3, 4))}" fill="none" stroke="{colors["gold"]}" stroke-width="2.2" data-role="branch" data-slope="{p}"/>']
        parts += [f'<path d="{arc(row["slope"], Q(-3, 4), Q(3, 4))}" fill="none" stroke="{colors[color]}" stroke-width="2.7" data-role="branch" data-slope="{row["slope"]}"/>']
        for vertex in vertices:
            x, y = project(vertex)
            parts += [f'<circle cx="{n(x)}" cy="{n(y)}" r="3.5" fill="{colors["white"]}"/>']
        parts += ['</g>', text(left+18, top+430, 'Area = '+str(row['area']), 25, 'white'),
                  text(left+18, top+464, 'A global maximum.' if i != 1 else 'A smaller pocket.', 20), '</g>']
    parts += [text(35, 735, 'Either best choice gains exactly 8% over the midpoint. Every panel uses the same unit scale.', 22),
              text(35, 777, 'The intercept is strictly convex throughout: h″(p) = 3p² + 1/8 > 0.', 24, 'white'),
              text(35, 819, 'Convexity proves the pocket formula. The shape of h decides where its maxima lie.', 22),
              text(35, 881, 'The best placement need not be unique.', 31, 'white')]
    x0, y0, sx, sy = 100, 1190, 500, Q(17, 2)
    parts += [f'<g data-twin-graph="area" data-origin="{x0},{y0}" data-scales="{sx},{sy}">',
              '<rect x="100" y="920" width="1000" height="270" fill="#0b0e1a" stroke="#383b50"/>']
    for r in (Q(-1), Q(-1, 2), Q(0), Q(1, 2), Q(1)):
        x = x0+sx*(r+1)
        parts += [f'<path d="M{x},920v270" stroke="#252b42"/>', text(x, 1225, r, 18, 'muted', 'text-anchor="middle"')]
    for value in (0, 8, 16, 24):
        y = y0-sy*value
        parts += [f'<path d="M100,{n(y)}h1000" stroke="#252b42"/>', text(85, n(y+6), value, 18, 'muted', 'text-anchor="end"')]
    samples = [(x0+sx*(r+1), y0-sy*256*area_at(r, epsilon))
               for r in (Q(-1)+Q(j, 250) for j in range(501))]
    parts += ['<path d="'+''.join(('M' if i == 0 else 'L')+xy(p) for i, p in enumerate(samples))
              +f'" fill="none" stroke="{colors["white"]}" stroke-width="2.8" data-role="area-curve"/>']
    for row in data['rows']:
        x, y = x0+sx*(row['slope']+1), y0-sy*256*row['area']
        color = 'blue' if row['slope'] == 0 else 'green'
        parts += [f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="{colors[color]}" stroke="#101323" stroke-width="2"/>']
    parts += [text(100, 908, 'Area × 256 ↑', 20), text(350, 946, '27', 21, 'green', 'text-anchor="middle"'),
              text(850, 946, '27', 21, 'green', 'text-anchor="middle"'), text(600, 1023, '25', 21, 'blue', 'text-anchor="middle"'),
              text(1100, 1266, 'Inserted slope r →', 20, 'ink', 'text-anchor="end"'), '</g>',
              text(35, 1308, 'Area = (1 − r²)(r² + 5/4)²/16. The exact global peaks occur at r² = 1/4.', 23),
              text(35, 1348, 'The graph uses different axis scales. Pocket arcs are quadratic; the sextic area graph is sampled.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/two_choices.md">',
              text(35, 1380, 'Follow the two-choice proof and its symmetry-breaking threshold ↗', 21, 'gold'), '</a>', '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save freshly checked exact data and the standalone SVG.')
    args = parser.parse_args()
    counts = controls()
    data = record()
    if args.write:
        (HERE/'two_choices.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
        (HERE/'two_choices.svg').write_text(figure(data))
    print(f'{counts[0]} exact insertion comparisons, {counts[1]} complete clipped/curved arrangements, and {counts[2]} invalid controls passed.')
    print('At epsilon=1/8, the two global maximizers are +/-1/2, with area 27/256; midpoint area is 25/256.')
    print('For epsilon>=1/2 the midpoint is the unique maximum. The written derivative proves the whole family.')


if __name__ == '__main__':
    main()
