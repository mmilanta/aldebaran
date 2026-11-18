"""A line approaches its entire annulus as the fold count grows.

Run: python3 experiments/fold_band.py [--figure]
The elementary Hausdorff-distance bound is proved in fold_band.md.
Exact rational upper bounds and standard-library SVG illustrations.
"""

import argparse
from fractions import Fraction as Q
from html import escape
from math import cos, pi, sin
from pathlib import Path

from blend_cusps import Interval as I, require
from fold_contacts import PI
from phase_unfolding import sincos, sqrt_interval

HERE = Path(__file__).resolve().parent
MAXIMUM2 = Q(23155775, 208)
FOLDS = (14, 60, 240)
SCALE = Q(21, 50)


def cover_bound(d):
    require(type(d) is int and d >= 1, 'Use a positive integer fold count.')
    # Both factors are positive. Exact sine and square-root enclosures.
    sine, _ = sincos(PI/(2*d))
    require(sine.low > 0, 'The half-sector chord must be positive.')
    return 2*sqrt_interval(I.wrap(MAXIMUM2), bits=120)*sine


def prove():
    bounds = [cover_bound(d) for d in FOLDS]
    require(all(a.low > b.high for a, b in zip(bounds, bounds[1:])),
            'The illustrated covering radii do not decrease.')
    # One uniform drawing unit suffices for all phases at d >= 1414,
    # using sin(x) <= x and every phase's M <= 450.
    require(450*PI.high/1414 < 1, 'The uniform one-unit covering bound changed.')
    # At a half-turn, the smaller outer radius needs only 1049 folds.
    require((sqrt_interval(I.wrap(MAXIMUM2), bits=120)*PI/1049).high < 1,
            'The half-turn one-unit covering bound changed.')
    # The whole half-turn has annulus area at least pi*area_factor. A
    # 38/d tube around a curve of length <=2pi(320+205d) has smaller area,
    # since d>=1. This proves the uniform lower bound for Hausdorff distance.
    area_factor = MAXIMUM2-170**2
    require(area_factor == Q(17144575, 208)
            and 4*38*(320+205)+38**2 < area_factor,
            'The uniform 38/d lower bound lost its strict area gap.')
    return bounds


def figure(bounds):
    def number(x):
        return f'{float(x):.4f}'.rstrip('0').rstrip('.') or '0'
    def text(x, y, value, size=22, fill='#c7c7d4', extra=''):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title description">',
             '<title id="title">A line approaches a band</title>',
             '<desc id="description">Three complete orbital drawings at a half-turn starting angle share one scale. Fourteen, sixty, then two hundred forty folds become finer within the same annulus, whose inner radius is 170 and outer radius is about 333.66. Every point in that annulus is within the printed distance of its smooth curve. The rigorous distances are upper bounds, not measured largest gaps. The sampled drawings have chord and rounding error below 0.01 sheet units. The finite curves are still lines; no crossing count or whole-branch clearance is asserted.</desc>',
             '<rect width="1200" height="900" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(42, 72, 'A line approaches a band.', 49, '#f4f1e8'),
             text(42, 117, 'More folds. The same two radial edges.', 27),
             text(42, 164, 'One scale · lengths 245, 140, 65 · backward starting angle 180°', 23)]
    r = float(sqrt_interval(I.wrap(MAXIMUM2), bits=120).midpoint())
    for column, (d, bound) in enumerate(zip(FOLDS, bounds)):
        cx, cy = 210+390*column, 425
        cents = -((-bound.high*100)//1)
        rounded_up = f'{cents//100}.{int(cents%100):02}'
        # Exact second-derivative/chord bound, plus coordinate rounding.
        segments = 256*d
        error = SCALE*(245+140*(d+1)**2+65*(d-1)**2)*Q(44, 7*segments)**2/8+Q(1, 10000)
        require(error < Q(1, 100), 'An illustrated path exceeds its 0.01-unit sheet bound.')
        points = []
        for i in range(segments+1):
            t = 2*pi*i/segments
            x = 245*cos(t)+140*cos((d+1)*t)-65*cos((d-1)*t)
            y = 245*sin(t)+140*sin((d+1)*t)+65*sin((d-1)*t)
            points.append(number(cx+float(SCALE)*x)+','+number(cy-float(SCALE)*y))
        # A faint annulus remains the same in every panel. The ideal trace
        # lies inside it; finite stroke width may straddle its boundary.
        outer, inner = float(SCALE)*r, float(SCALE)*170
        parts += [text(cx, 246, f'{d} folds', 27, '#f4f1e8', 'text-anchor="middle"'),
                  f'<circle cx="{cx}" cy="{cy}" r="{number((outer+inner)/2)}" fill="none" stroke="#9fc7eb" stroke-opacity=".06" stroke-width="{number(outer-inner)}"/>',
                  f'<g data-role="band-orbit" data-folds="{d}" data-phase="pi" data-cx="{cx}" data-cy="{cy}" data-scale="{SCALE}" data-segments="{segments}"><path d="M{"L".join(points)}" fill="none" stroke="#9fc7eb" stroke-width=".65" stroke-linejoin="round"/></g>',
                  f'<circle cx="{cx}" cy="{cy}" r="{number(inner)}" fill="none" stroke="#e8b66e" stroke-opacity=".6" stroke-dasharray="3 5" stroke-width="1"/>',
                  f'<circle cx="{cx}" cy="{cy}" r="{number(outer)}" fill="none" stroke="#e8b66e" stroke-opacity=".6" stroke-dasharray="3 5" stroke-width="1"/>',
                  text(cx, 625, 'Every point in the band', 21, extra='text-anchor="middle"'),
                  text(cx, 655, f'is within {rounded_up} units*', 23, '#e8b66e', 'text-anchor="middle"')]
    parts += [text(42, 724, '*Rounded up: guaranteed bounds, not measured largest gaps.', 22),
              text(42, 765, 'At 1,049 folds, every band point is within one drawing unit of the line.', 22),
              text(42, 807, 'The distance is measured to the ideal line, before adding ink thickness.', 21),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_turn.html">',
              text(42, 862, 'Follow the ellipse inside the drawing ↗', 23, '#e8b66e'), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true', help='Regenerate the three complete drawings.')
    args = parser.parse_args()
    bounds = prove()
    for d, bound in zip(FOLDS, bounds):
        print(f'{d} folds: annulus distance bound 2 M sin(pi/(2d)) is approximately {float(bound.midpoint()):.10f}.')
    print('The rational upper bounds prove one-unit coverage at 1,049 half-turn folds, or 1,414 at every phase.')
    print('The tube-area bound also gives 38/d < Hausdorff distance throughout the half-turn; the order 1/d is sharp.')
    if args.figure:
        (HERE/'fold_band.svg').write_text(figure(bounds))


if __name__ == '__main__':
    main()
