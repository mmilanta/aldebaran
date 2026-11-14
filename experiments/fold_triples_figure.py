"""Draw one selected sevenfold triple before, near, and after its meeting.

Standard library only. The plotted geometry is numerical. Rational phase
bounds check that all three controls lie inside its fourth-branch cover.
"""

import cmath
from fractions import Fraction as Q
import json
from math import pi

from blend_cusps import Interval as I, require
from fold_contacts import HERE, angle
from fold_contacts_figure import GOLD, BLUE, GREEN, INK, MUTED, path, text, midpoint


def orbit(t, phase, order=0):
    return sum(r*(1j*k)**order*cmath.exp(1j*(k*t+(phase if k < 0 else 0)))
               for r, k in ((245, 1), (140, 8), (65, -6)))


def crossing(times, phase, i, j):
    t, s = times[i], times[j]
    for _ in range(10):
        f = orbit(t, phase)-orbit(s, phase)
        v, w = orbit(t, phase, 1), orbit(s, phase, 1)
        determinant = -v.real*w.imag+w.real*v.imag
        t -= (-w.imag*f.real+w.real*f.imag)/determinant
        s -= (v.real*f.imag-v.imag*f.real)/determinant
    require(abs(orbit(t, phase)-orbit(s, phase)) < 1e-9,
            'An illustrated pairwise crossing did not converge.')
    return t, s


def figure():
    event = json.loads((HERE/'fold_triples.json').read_text())['events'][0]
    times = list(map(midpoint, event['times']))
    phase = midpoint(event['phase_over_pi'])*pi
    origin = orbit(times[0], phase)
    disk_center = list(map(Q, event['isolation']['origin']))
    require(sum((abs(Q(v)-c)+Q(1, 20))**2
                for v, c in zip((origin.real, origin.imag), disk_center)) < 1,
            'A plotted viewing square leaves the certified isolation disk.')
    q = event['quarters'][3]
    p = event['root_image'][3]
    phase_root = angle(q, I(Q(p['low']), Q(p['high'])))
    window = event['isolation']['phase_chart']
    lower = angle(q, I.wrap(Q(window['low'])))
    upper = angle(q, I.wrap(Q(window['high'])))
    delta = Q(1, 10000)
    require(lower.high < phase_root.low-delta < phase_root.high+delta < upper.low,
            'The three plotted controls leave the fourth-branch exclusion window.')
    require(all(lower.high < Q(phase+offset) < upper.low
                for offset in (-float(delta), 0., float(delta))),
            'A floating-point display control leaves the certified phase window.')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" '
             'viewBox="0 0 1200 760" role="img" aria-labelledby="title description">',
             '<title id="title">The count stays. The order changes.</title>',
             '<desc id="description">Three equal-scale local orbital views show a selected '
             'sevenfold triple passage. Blue, gold, and green branches bound a small '
             'triangle before the meeting; meet approximately at one point; then enclose '
             'a triangle on the other side. Arrows follow increasing time. Each square '
             'spans 0.1 drawing units each way. The controls are a phase offset minus '
             '0.0001, approximately zero, and plus 0.0001 radians. They lie inside the '
             'certified fourth-branch exclusion window. There are 35 crossing pairs '
             'throughout this local window. This is one selected batch, not a complete '
             'triple census. Plotted geometry is numerical.</desc>',
             '<rect width="1200" height="760" fill="#101323"/>',
             '<g font-family="ui-sans-serif,system-ui,sans-serif">',
             text(40, 68, 'The count stays.', 45, INK),
             text(40, 121, 'The order changes.', 45, INK),
             text(40, 169, 'Three moving branches meet. A little triangle switches sides.', 25),
             text(40, 205, 'One selected sevenfold batch · 35 crossing pairs before and after', 23)]
    for j, offset in enumerate((-float(delta), 0., float(delta))):
        left, top, cx, cy, scale = 40+385*j, 280, 215+385*j, 455, 3500
        project = lambda z: (cx+scale*(z-origin).real, cy-scale*(z-origin).imag)
        parts += [text(cx, 258, ('Before', 'Meeting · approximate', 'After')[j], 24, INK,
                       'text-anchor="middle"'),
                  f'<rect x="{left}" y="{top}" width="350" height="350" rx="10" '
                  'fill="#0b0e1a" stroke="#383b50"/>',
                  f'<defs><clipPath id="clip-{j}"><rect x="{left}" y="{top}" width="350" '
                  'height="350" rx="10"/></clipPath></defs>',
                  f'<g clip-path="url(#clip-{j})" data-role="triple-panel" data-delta="{offset}">']
        ph = phase+offset
        if offset:
            ab, bc, ac = [crossing(times, ph, a, b) for a, b in ((0, 1), (1, 2), (0, 2))]
            boundary = []
            for a, b in ((ab[1], bc[0]), (bc[1], ac[1]), (ac[0], ab[0])):
                boundary += [project(orbit(a+(b-a)*k/128, ph)) for k in range(129)]
            parts.append(path(boundary, 'none', 0, 'style="fill:#f4f1e8;fill-opacity:.2"', close=True))
            points = [orbit(t, ph) for t in (ab[0], bc[0], ac[0])]
        else:
            points = [origin]
        for i, color in enumerate((BLUE, GOLD, GREEN)):
            coords = [project(orbit(times[i]+.0004*(k/512-.5), ph)) for k in range(513)]
            parts.append(path(coords, color, 2.4, f'data-role="branch" data-visit="{i}"'))
            t = times[i]+.000025
            point = project(orbit(t, ph))
            velocity = orbit(t, ph, 1)
            speed = abs(velocity)
            ux, uy = velocity.real/speed, -velocity.imag/speed
            arrow = [(point[0]-7*ux+5*uy, point[1]-7*uy-5*ux),
                     (point[0]+7*ux, point[1]+7*uy),
                     (point[0]-7*ux-5*uy, point[1]-7*uy+5*ux)]
            parts.append(path(arrow, color, 2.4))
        for point in points:
            x, y = project(point)
            parts.append(f'<circle cx="{x:.6f}" cy="{y:.6f}" r="4" fill="{INK}" '
                         'stroke="#0b0e1a" stroke-width="1.1"/>')
        parts += ['</g>', text(cx, 664, ('−0.0001 rad', '0 · rounded location', '+0.0001 rad')[j],
                              22, MUTED, 'text-anchor="middle"')]
    parts += [text(40, 709, 'Equal axes · each square spans 0.1 drawing units · seven rotated copies meet together', 22),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_triples.md">',
              text(40, 746, 'Four selected triple batches, their signs, and the open census ↗', 22, GOLD), '</a></g></svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'fold_triples.svg').write_text(figure())
    print('Wrote one selected triple; all three phase controls lie inside its fourth-branch window.')
