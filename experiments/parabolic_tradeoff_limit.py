"""A uniform scaling limit for the even-count pocket compromise.

Relative minimum gain is order m^-2; relative total loss is order m^-4.
Exact controls check the rescaled cubic curves, a quadratic limit,
uniform common-parameter errors, and finite endpoint enclosures.
Only the standard library; see parabolic_tradeoff_limit.md.
"""

import argparse
from fractions import Fraction as Q
from html import escape
import json
from pathlib import Path

from blend_cusps import require
from parabolic_balance import Quadratic
from parabolic_pockets import area, bounded_faces
from parabolic_tradeoff import bezier, endpoint, serialize

HERE = Path(__file__).resolve().parent


def scaled(size, v):
    require(type(size) is int and size >= 6 and size % 2 == 0
            and type(v) in (Q, Quadratic) and v >= 0,
            "Use an even slope count at least six and an exact nonnegative parameter.")
    m = size-1
    r = Q(1, m*m)
    D = 3-2*(1-3*r)*v-3*(r-r*r)*v*v
    require(D >= 0, "The scaled parameter is beyond the efficient interval.")
    return (3*v*v+2*r*v**3,
            3*v-v*v+r*v*v*(3-v)+r*r*v**3)


def end_certificate(size):
    m = size-1
    r = Q(1, m*m)
    v = m*m*endpoint(size)
    lo, hi = Q(3, 2), Q(3, 2)*(1+r)
    D = lambda z: 3-2*(1-3*r)*z-3*(r-r*r)*z*z
    require(D(v) == 0 and D(lo) == Q(9, 4)*r*(1+3*r) > 0,
            "The stationary scaled endpoint misses the lower bracket.")
    require(D(hi) == Q(3, 4)*r*(-1+3*r+9*r*r+9*r**3) < 0
            and lo < v < hi <= Q(39, 25),
            "The stationary scaled endpoint misses the upper bracket.")
    x, y = scaled(size, v)
    require(0 < x-Q(27, 4) < 22*r and 0 < y-Q(9, 4) < 4*r,
            "An endpoint escapes the all-count scaled remainder bounds.")
    require(y >= Q(9, 4)+Q(27, 8)*r*(1+r),
            "The final minimum is smaller than the common-window endpoint.")
    return {"slopes": size, "gaps": m, "parameter_end": v,
            "scaled_end": (x, y), "relative_loss": x/m**4, "relative_gain": y/(m*m)}


def curve_record(size):
    m = size-1
    B0, S0 = Q(8, 3)*(1-Q(1, m*m)), Q(16, m**3)
    controls = tuple(((B0-p[0])*m**4/B0, (p[1]-S0)*m*m/S0) for p in bezier(size))
    end = end_certificate(size)
    for step in range(37):
        t = Q(step, 36)
        actual = tuple((1-t)**3*controls[0][i]+3*t*(1-t)**2*controls[1][i]
                       +3*t*t*(1-t)*controls[2][i]+t**3*controls[3][i] for i in (0, 1))
        require(actual == scaled(size, end["parameter_end"]*t),
                "The rescaled cubic misses its area coordinates.")
    return {**end, "bezier": controls}


def controls(maximum):
    endpoints = uniform = clipped = 0
    # These are audits of the written all-count bounds, not their proof.
    for size in range(6, maximum+1, 2):
        end_certificate(size)
        endpoints += 1
        m = size-1
        r = Q(1, m*m)
        for step in range(37):
            v = Q(step, 24)  # The common window 0 <= v <= 3/2.
            x, y = scaled(size, v)
            require(0 <= x-3*v*v <= Q(27, 4)*r
                    and 0 <= y-(3*v-v*v) <= Q(27, 8)*r*(1+r),
                    "A common-window point escapes the uniform rational error bounds.")
            # Independent substitution into the unscaled gap objectives.
            u = v/(m*m)
            a, b = Q(4, m)*(1-(m-1)*u), Q(4, m)*(1+(m+1)*u)
            B, S = (64-Q(size, 2)*a**3-(Q(size, 2)-1)*b**3)/24, a*b*(a+b)/8
            B0, S0 = Q(8, 3)*(1-r), Q(16, m**3)
            require(x == (B0-B)*m**4/B0 and y == (S-S0)*m*m/S0,
                    "The normalized gain/loss units disagree with the gap areas.")
            uniform += 1
        if size <= 10:
            for v in (Q(0), Q(3, 2)):
                u = v/(m*m)
                a, b = Q(4, m)*(1-(m-1)*u), Q(4, m)*(1+(m+1)*u)
                slopes = [Q(-2)]
                for i in range(m):
                    slopes.append(slopes[-1]+(a if i % 2 == 0 else b))
                areas = [area(polygon) for polygon in bounded_faces(slopes)]
                B0, S0 = Q(8, 3)*(1-r), Q(16, m**3)
                x, y = scaled(size, v)
                require((B0-sum(areas))*m**4/B0 == x and (min(areas)-S0)*m*m/S0 == y,
                        "Fresh clipped faces miss the scaled objectives.")
                clipped += 1
    invalid = 0
    for size, v in ((4, Q(0)), (7, Q(0)), (True, Q(0)), (6, -.1), (6, Q(-1)), (6, Q(2))):
        try:
            scaled(size, v)
        except ValueError:
            invalid += 1
        else:
            raise ValueError("An invalid scaling problem was accepted.")
    return endpoints, uniform, clipped, invalid


def record():
    limit = ((Q(0), Q(0)), (Q(0), Q(9, 4)), (Q(27, 4), Q(9, 4)))
    for step in range(37):
        t = Q(step, 36)
        point = tuple((1-t)**2*limit[0][i]+2*t*(1-t)*limit[1][i]+t*t*limit[2][i] for i in (0, 1))
        v = Q(3, 2)*t
        require(point == (3*v*v, 3*v-v*v) and (point[0]+3*point[1])**2 == 27*point[0],
                "The exact quadratic misses the limiting frontier.")
    return {"scope": "Complete exact limit-parabola arrangements; a limit in slope count, not finite orbital offset.",
            "horizontal": "m^4 * relative total-area loss", "vertical": "m^2 * relative smallest-area gain",
            "parameter": "v=m^2*(b-a)/(2L)", "common_window": (Q(0), Q(3, 2)),
            "curves": [curve_record(size) for size in (6, 10, 20)], "limit_quadratic": limit,
            "table": [end_certificate(size) for size in (6, 10, 20, 100)]}


def figure(data):
    color = {"white": "#f4f1e8", "ink": "#c7c7d4", "muted": "#aaaabd"}
    colors = ("#e8b66e", "#9fc7eb", "#a7d9bb")
    number = lambda x: f"{float(x):.6f}".rstrip("0").rstrip(".") or "0"
    text = lambda x, y, s, size=21, fill=color["ink"], extra="": f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(str(s))}</text>'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1450" viewBox="0 0 1200 1450" role="group" aria-labelledby="title description">',
             '<title id="title">The advantage fades twice</title>',
             '<desc id="description">Every even-count efficient pocket arrangement alternates short and long slope gaps. With m gaps, the relative smallest-area gain is order one over m squared, while relative total-area loss is order one over m to the fourth. Rescaling those two measures brings the six-, ten-, and twenty-slope efficient curves close to one universal quadratic arc. Its parameter v runs from zero to three halves, with coordinates three v squared and three v minus v squared. The endpoint is 27 over 4 horizontally and nine over 4 vertically. A table gives the actual unscaled percentage changes at four maximin endpoints. Each percentage uses its own equal-gap area as baseline. These are exact complete limit-parabola arrangements and a limit in slope count, not an outward-offset estimate for orbital curves.</desc>',
             '<rect width="1200" height="1450" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(35, 65, 'The advantage fades twice.', 47, color['white']),
             text(35, 110, 'The smallest pockets gain less. The relative cost in total area fades faster.', 23),
             text(35, 151, 'Rescale both changes to see one common curve emerge.', 23)]
    for i, size in enumerate((6, 10, 20)):
        left = 45+270*i
        parts += [f'<path d="M{left},198h32" stroke="{colors[i]}" stroke-width="3"/>', text(left+45, 205, f'{size} slopes', 21)]
    parts += ['<path d="M900,198h32" stroke="#f4f1e8" stroke-width="3" stroke-dasharray="6 5"/>', text(945, 205, 'Limit', 21)]
    plot = {"x": 110, "y": 290, "w": 1000, "h": 510, "sx": 125, "sy": 200}
    project = lambda p: (plot['x']+plot['sx']*float(p[0]), plot['y']+plot['h']-plot['sy']*float(p[1]))
    pair = lambda p: ','.join(number(x) for x in project(p))
    parts += [f'<g data-scaled-plot="frontier" data-left="110" data-bottom="800" data-x-scale="125" data-y-scale="200">',
              '<rect x="110" y="290" width="1000" height="510" fill="#0b0e1a" stroke="#383b50"/>']
    for x in (0, 2, 4, 6, 8):
        sx = plot['x']+125*x
        parts += [f'<path d="M{sx},290v510" stroke="#252b42"/>', text(sx, 832, x, 18, color['muted'], 'text-anchor="middle"')]
    for y in (0, 1, 2, Q(9, 4)):
        sy = plot['y']+plot['h']-200*float(y)
        parts += [f'<path d="M110,{number(sy)}h1000" stroke="#252b42"/>', text(95, number(sy+6), '9/4' if y == Q(9, 4) else y, 18, color['muted'], 'text-anchor="end"')]
    for row, stroke in zip(data['curves'], colors):
        c = row['bezier']
        parts += [f'<path d="M{pair(c[0])}C{pair(c[1])} {pair(c[2])} {pair(c[3])}" fill="none" stroke="{stroke}" stroke-width="2.5" data-slopes="{row["slopes"]}"/>']
        x, y = project(c[-1])
        parts += [f'<circle cx="{number(x)}" cy="{number(y)}" r="4.8" fill="{stroke}" stroke="#101323" stroke-width="1.5"/>']
    c = data['limit_quadratic']
    parts += [f'<path d="M{pair(c[0])}Q{pair(c[1])} {pair(c[2])}" fill="none" stroke="#f4f1e8" stroke-width="2.5" stroke-dasharray="6 5" data-role="limit"/>',
              text(110, 265, 'm² × relative smallest-area gain ↑', 20),
              text(1110, 876, 'm⁴ × relative total-area loss →', 20, color['ink'], 'text-anchor="end"'), '</g>',
              text(35, 940, 'At the largest possible minimum:', 29, color['white'])]
    for x, label in ((55, 'Slopes'), (295, 'Minimum gain'), (615, 'Total loss'), (920, 'Gaps m')):
        parts += [text(x, 995, label, 21, color['muted'])]
    for i, row in enumerate(data['table']):
        y = 1040+46*i
        gain, loss = float(row['relative_gain'])*100, float(row['relative_loss'])*100
        loss_label = f'{loss:.6f}%' if row['slopes'] < 100 else f'{loss:.8f}%'
        parts += [text(55, y, row['slopes'], 23, color['white']), text(295, y, f'+{gain:.6f}%', 23),
                  text(615, y, f'−{loss_label}', 23), text(920, y, row['gaps'], 23)]
    parts += [text(35, 1255, 'Gain and loss use different baselines: their own equal-gap minimum and total.', 22, color['white']),
              text(35, 1297, 'The graph rescales relative changes, not absolute pocket areas. Axis scales differ.', 21),
              text(35, 1338, 'Limit: X = 3v², Y = 3v − v², 0 ≤ v ≤ 3/2. End: (27/4, 9/4).', 23),
              text(35, 1377, 'Uniform rational error bounds and finite endpoint bounds accompany the limit.', 20, color['muted']),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/parabolic_tradeoff_limit.md">',
              text(35, 1420, 'Follow the scaling calculation and its bounds ↗', 21, '#e8b66e'), '</a>', '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-slopes', type=int, default=100, help='Largest even count to audit (at least 10).')
    parser.add_argument('--write', action='store_true', help='Regenerate the exact scaling record.')
    parser.add_argument('--figure', action='store_true', help='Regenerate the standalone rounded SVG.')
    args = parser.parse_args()
    require(args.max_slopes >= 10, 'Check through at least ten slopes.')
    counts = controls(args.max_slopes)
    data = record()
    if args.write:
        (HERE/'parabolic_tradeoff_limit.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    if args.figure:
        (HERE/'parabolic_tradeoff_limit.svg').write_text(figure(data))
    print(f'{counts[0]} exact endpoint enclosures, {counts[1]} uniform common-window controls,')
    print(f'{counts[2]} independent clipped arrangements, and {counts[3]} invalid controls passed.')
    print('111 exact finite-cubic and 37 limit-quadratic matches passed.')
    for row in data['table']:
        print(f"{row['slopes']} slopes: minimum gain {100*float(row['relative_gain']):.9f}%; total loss {100*float(row['relative_loss']):.9f}%.")
    print('The all-count bounds are the written polynomial inequalities, not the finite count table.')


if __name__ == '__main__':
    main()
