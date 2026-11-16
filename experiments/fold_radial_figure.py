"""Draw two/four radial preimages and the shoulder that separates them.

Run: python3 experiments/fold_radial_figure.py
Standard library only. The exact circle counts are repeated first;
rounded paths are illustrations, separate from the rational proof.
"""

from math import atan, atan2, cos, pi, sin, sqrt

from fold_contacts_figure import (BG, BLUE, GOLD, GREEN, HERE, INK, MUTED,
                                  PANEL, number, path, text)
from fold_radial import A, B, D, R, prove


def ellipse(theta, phase):
    c, s = cos(phase/2), sin(phase/2)
    return R+A*c*cos(theta)-B*s*sin(theta), A*s*cos(theta)+B*c*sin(theta)


def radius(theta, phase):
    x, y = ellipse(theta, phase)
    return sqrt(x*x+y*y)


def intersections(phase, level):
    """Numerical suggestions for already-counted circle intersections."""
    result = []
    for k in range(4096):
        low, high = 2*pi*k/4096, 2*pi*(k+1)/4096
        f = radius(low, phase)-level
        if f*(radius(high, phase)-level) < 0:
            for _ in range(55):
                middle = (low+high)/2
                fm = radius(middle, phase)-level
                if f*fm < 0:
                    high = middle
                else:
                    low, f = middle, fm
            result.append((low+high)/2)
    return result


def circle_panel(left, phase, count, color):
    ox, oy, scale = 220, 240, .45
    points = [ellipse(2*pi*k/4096, phase) for k in range(4097)]
    hits = intersections(phase, 321)
    if len(hits) != count:
        raise ValueError('The numerical artwork disagrees with its exact circle count.')
    parts = [f'<g data-role="radial-panel" data-phase="{phase}" data-count="{count}" transform="translate({left},190)">',
             f'<rect width="540" height="440" rx="18" fill="{PANEL}" stroke="#383b50"/>',
             text(25, 43, f'{count} ellipse points at one radius', 27, INK),
             text(25, 78, f'Phase ≈ {phase/pi:.5f}π', 22, color),
             f'<circle cx="{ox}" cy="{oy}" r="{321*scale}" fill="none" stroke="#747c9b" stroke-width="1.4"/>',
             f'<path d="M{ox-5},{oy}h10M{ox},{oy-5}v10" stroke="{MUTED}" stroke-width="1.5"/>',
             path([(ox+scale*x, oy-scale*y) for x, y in points], color, 2,
                  'data-role="ellipse"'),
             f'<circle cx="{ox+scale*R}" cy="{oy}" r="2.7" fill="{color}"/>']
    for theta in hits:
        x, y = ellipse(theta, phase)
        parts.append(f'<circle data-role="radial-hit" data-theta="{theta}" cx="{number(ox+scale*x)}" '
                     f'cy="{number(oy-scale*y)}" r="4" fill="{INK}" stroke="{BG}" stroke-width="1.6"/>')
    parts += [text(25, 415, 'Same radius: 321. Same scale.', 21), '</g>']
    return parts


def figure():
    record = prove()
    c = record['cos_phase']
    # The certified cosine interval is much narrower than drawing precision.
    from math import acos
    threshold = acos(float((c.low+c.high)/2))
    before, after = 4*atan(4/5), 4*atan(19/20)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="1120" viewBox="0 0 1160 1120" '
             'role="img" aria-labelledby="title desc" font-family="ui-sans-serif,system-ui,sans-serif">',
             '<title id="title">Why the triangles wait</title>',
             '<desc id="desc">Two tilted ellipses meet the same origin-centered circle of radius 321. '
             'The earlier ellipse has two intersections and the later ellipse has four. '
             'A radial close-up shows a flat shoulder appearing at phase 0.89494082717179 pi. '
             'Before and at that threshold every positive fold count has at most two visits to a point. '
             'Four ellipse points at one radius do not assert four visits to one spatial point. '
             'Circle counts are exact; the paths and marked positions are numerical illustrations.</desc>',
             f'<rect width="1160" height="1120" fill="{BG}"/>',
             text(30, 48, 'ALDEBARAN · THE ELLIPSE INSIDE THE TURN', 19, GOLD, 'letter-spacing="2"'),
             text(30, 107, 'Why the triangles wait.', 50, INK),
             text(30, 151, 'A third visit needs a third ellipse point at the same radius.', 26)]
    parts += circle_panel(25, before, 2, BLUE)
    parts += circle_panel(595, after, 4, GREEN)
    parts += [text(30, 682, 'A shoulder makes room for two more points', 30, INK),
              text(30, 718, 'Radius along one piece of the ellipse. The rest lies outside this close-up.', 22)]
    x0, y0, width, height = 100, 1010, 1010, 235
    x = lambda theta: x0+width*(theta-pi)/(pi/2)
    y = lambda r: y0-height*(r-290)/50
    for r in (290, 300, 310, 320, 330, 340):
        parts += [path(((x0, y(r)), (x0+width, y(r))), '#33394f', .8),
                  text(x0-15, y(r)+7, r, 19, MUTED, 'text-anchor="end"')]
    for t, label in ((pi, 'π'), (1.25*pi, '1.25π'), (1.5*pi, '1.5π')):
        parts.append(text(x(t), y0+30, label, 20, MUTED, 'text-anchor="middle"'))
    parts.append(text(35, 755, 'Radius', 20, MUTED))
    parts.append(f'<defs><clipPath id="radial-plot"><rect x="{x0}" y="{y0-height}" '
                 f'width="{width}" height="{height}"/></clipPath></defs><g clip-path="url(#radial-plot)">')
    for phase, color in ((before, BLUE), (threshold, GOLD), (after, GREEN)):
        points = [(x(t), y(radius(t, phase))) for t in (pi+pi/2*k/2048 for k in range(2049))]
        parts.append(path(points, color, 2.4, f'data-role="radial-profile" data-phase="{phase}"'))
    parts.append('</g>')
    theta = atan2(-(B*R*sin(threshold/2)/D)**(1/3),
                  -(A*R*cos(threshold/2)/D)**(1/3)) % (2*pi)
    cx, cy = x(theta), y(radius(theta, threshold))
    parts += [f'<circle cx="{number(cx)}" cy="{number(cy)}" r="4.5" fill="{GOLD}"/>',
              path(((cx, cy-10), (cx, 790), (cx+95, 790)), GOLD, 1),
              text(cx+105, 797, 'At the threshold: a flat shoulder', 22, GOLD),
              text(30, 1090, 'The radial obstruction ends at 0.894940827171…π, for every positive fold count.', 23, INK), '</svg>']
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    (HERE/'fold_radial.svg').write_text(figure())
    print('Drew the certified two/four circle examples and the radial shoulder; standard library only.')
