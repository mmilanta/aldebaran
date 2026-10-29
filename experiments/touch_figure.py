"""Generate touch_data.js and touch.svg, repeating fresh local certificates.

Run: python3 experiments/touch_figure.py
Standard library only. Figure coordinates and quadrature are numerical.
Rational boxes and fresh smooth snapshots are certified independently.
"""

import json
from fractions import Fraction as Q
from math import pi

from blend_cusps import require
from rhythm_passages import HERE, orbit
from rhythm_tangencies import (EXPECTED_COEFFICIENTS, HINTS, certify_event,
                               certify_isolation, check_evaluation, snapshots)


COLORS = ('#9fc7eb', '#e8b66e')


def frame(event, weight, t, order=0):
    z = orbit(t, weight, order)
    if order == 0:
        z -= complex(*event['center'])
    return z/complex(*event['tangent'])


def branch(event, weight, index, x):
    t = event['times'][index]
    for _ in range(9):
        t -= (frame(event, weight, t).real-x)/frame(event, weight, t, 1).real
    p = frame(event, weight, t)
    require(abs(p.real-x) < 1e-8 and abs(t-event['times'][index]) < .04,
            'A numerical branch left its selected chart.')
    return p, t


def gap(event, weight, x):
    return branch(event, weight, 0, x)[0].imag-branch(event, weight, 1, x)[0].imag


def bisect(fn, low, high):
    require(fn(low)*fn(high) < 0, 'A numerical root was not bracketed.')
    left = fn(low)
    for _ in range(42):
        mid = (low+high)/2
        if fn(mid)*left > 0:
            low = mid
        else:
            high = mid
    return (low+high)/2


def meetings(event, weight):
    if abs(weight-event['weight']) < 1e-14:
        return [0.]
    # The selected lenses' extrema stay close to the event; zero brackets
    # their two roots at all offsets used by this numerical check/figure.
    h = event['half_size']
    fn = lambda x: gap(event, weight, x)
    roots = [bisect(fn, lo, hi) for lo, hi in ((-h, 0), (0, h)) if fn(lo)*fn(hi) < 0]
    expected = 2 if (weight-event['weight'])*event['pocket_side'] > 0 else 0
    require(len(roots) == expected, 'A numerical crossing count changed.')
    return roots


def area(event, weight, roots, steps=128):
    if len(roots) != 2:
        return 0.
    low, high = roots
    h = (high-low)/steps
    return abs(h/3*sum((1 if j in (0, steps) else 4 if j % 2 else 2)*gap(event, weight, low+j*h)
                      for j in range(steps+1)))


def check_areas(events):
    for i, event in enumerate(events):
        previous = float('inf')
        for delta in (.003, .001, .0003, .0001, .00003, .00001, .000003):
            a = event['weight']+event['pocket_side']*delta
            roots = meetings(event, a)
            A = area(event, a, roots)
            refined = area(event, a, roots, 512)
            require(abs(A-refined) < 1e-8*A+1e-12, 'The numerical lens quadrature did not stabilize.')
            ratio = refined/(event['coefficient']*delta**1.5)
            require(abs(ratio-1) < previous and abs(ratio-1) < .02,
                    'A numerical area ratio did not approach its certified coefficient.')
            previous = abs(ratio-1)
            print(f'  Touch {i+1}, |delta|={delta:g}: A/(K |delta|^1.5) = {ratio:.9f}')
        require(previous < .00002, 'The smallest-offset area law is unresolved.')


def path(points, project, close=False):
    return 'M'+' L'.join(project(p) for p in points)+(' Z' if close else '')


def samples(low, high, count, fn):
    return [fn(low+(high-low)*j/count) for j in range(count+1)]


def still(events):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1060" viewBox="0 0 1200 1060" role="img" aria-labelledby="title desc">',
           '<title id="title">Two ways to touch</title>',
           '<desc id="desc">Two rows of equal-scale close-ups. In the first, two branches travel in the same direction and erase a little lens. In the second, opposite directions open a lens. White dots mark crossings. Arrows give actual travel direction.</desc>',
           '<rect width="1200" height="1060" fill="#101323"/>',
           '<g font-family="system-ui, sans-serif" fill="#f4f1e8">',
           '<text x="40" y="64" font-size="38" font-weight="700">Two ways to touch</text>',
           '<text x="40" y="104" font-size="19" fill="#c7c7d4">A little space closes or opens between two regular, moving branches.</text>']
    for row, event in enumerate(events[:2]):
        top = 180+410*row
        svg.append(f'<text x="40" y="{top-28}" font-size="23">{("Direct touch · same travel direction · lens closes", "Inverse touch · opposite directions · lens opens")[row]}</text>')
        for column, step in enumerate((-1, 0, 1)):
            left, cx, cy = 40+390*column, 210+390*column, top+142
            scale = 145/event['half_size']
            project = lambda p: f'{cx+scale*p.real:.5f},{cy-scale*p.imag:.5f}'
            a = event['weight']+.003*step
            clip = f'clip{row}{column}'
            svg.extend([f'<defs><clipPath id="{clip}"><rect x="{left}" y="{top}" width="340" height="285" rx="12"/></clipPath></defs>',
                        f'<rect x="{left}" y="{top}" width="340" height="285" rx="12" fill="#0b0e1a" stroke="#383b50"/>',
                        f'<g clip-path="url(#{clip})">'])
            roots = meetings(event, a)
            if len(roots) == 2:
                boundary = (samples(roots[0], roots[1], 128, lambda x: branch(event, a, 0, x)[0])
                            +samples(roots[1], roots[0], 128, lambda x: branch(event, a, 1, x)[0]))
                svg.append(f'<path d="{path(boundary, project, True)}" fill="#f4f1e8" fill-opacity=".22"/>')
            for index, color in enumerate(COLORS):
                points = samples(-event['half_size']*1.2, event['half_size']*1.2, 360,
                                 lambda x: branch(event, a, index, x)[0])
                svg.append(f'<path d="{path(points, project)}" fill="none" stroke="{color}" stroke-width="2.6"/>')
                p, t = branch(event, a, index, (-.88 if index == 0 else .88)*event['half_size'])
                v = frame(event, a, t, 1)
                direction = complex(v.real, -v.imag)/abs(v)
                center = complex(cx+scale*p.real, cy-scale*p.imag)
                wing = 5j*direction
                arrow = [center-6*direction+wing, center+7*direction, center-6*direction-wing]
                svg.append(f'<path d="{path(arrow, lambda z: f"{z.real:.5f},{z.imag:.5f}")}" fill="none" stroke="{color}" stroke-width="2.6"/>')
            for root in roots:
                p, _ = branch(event, a, 0, root)
                svg.append(f'<circle cx="{cx+scale*p.real:.5f}" cy="{cy-scale*p.imag:.5f}" r="{5 if step == 0 else 4}" fill="#f4f1e8" stroke="#0b0e1a" stroke-width="1.4"/>')
            svg.extend(['</g>', f'<text x="{cx}" y="{top+319}" text-anchor="middle" font-size="21">{("Before", "Touch (approx.)", "After")[column]}</text>'])
    svg.extend(['<text x="40" y="964" font-size="20">Opening ∝ |weight offset| · length ∝ √|weight offset| · area ∝ |weight offset|³ᐟ²</text>',
                '<text x="40" y="1002" font-size="17" fill="#c7c7d4">Blue: earlier visit. Gold: later visit. Each row has equal coordinate scales and a fixed common-tangent frame.</text>',
                '<text x="40" y="1032" font-size="15" fill="#9999ae">Numerical drawings. Separate rational boxes certify eight selected touches and their local area coefficients.</text>',
                '</g></svg>'])
    (HERE/'touch.svg').write_text('\n'.join(svg)+'\n')


def generate():
    check_evaluation()
    records = snapshots()
    events = []
    for index, (t, u, weight) in enumerate(HINTS):
        proofs = [certify_event(index, reflected) for reflected in (False, True)]
        for proof in proofs:
            certify_isolation(index, proof)
        proof = proofs[0]
        p, v = orbit(t, weight), orbit(t, weight, 1)
        tangent = v/abs(v)
        events.append({'times': [t, u], 'weight': weight, 'center': [p.real, p.imag],
                       'tangent': [tangent.real, tangent.imag], 'range': .003,
                       'half_size': (18, 8, 10, 10)[index], 'gap_limit': (2, 1, 2, 1)[index],
                       'coefficient': float(proof['coefficient'].midpoint()),
                       'coefficient_box': [str(Q(x, 100)) for x in EXPECTED_COEFFICIENTS[index]],
                       'weight_box': [str(x) for x in (proof['box'][2].low, proof['box'][2].high)],
                       'pocket_side': proof['pocket_side'], 'direct': proof['direct'],
                       'nearby_snapshots': [{k: r[k] for k in ('weight', 'crossings', 'strangeness', 'J_plus', 'J_minus')}
                                            for r in records[index]]})
    check_areas(events)
    js = "'use strict';\n\n// Generated by touch_figure.py, with fresh local rational certificates and smooth snapshots.\n"
    js += '// Event locations and drawing coordinates are rounded; rational boxes are separate.\n'
    js += 'const TouchData = '+json.dumps({'events': events}, indent=2)+';\n\n'
    js += "if (typeof module !== 'undefined' && module.exports) module.exports = TouchData;\n"
    (HERE/'touch_data.js').write_text(js)
    still(events)
    print('Wrote touch_data.js and touch.svg. Local certificates and numerical area checks passed.')


if __name__ == '__main__':
    generate()
