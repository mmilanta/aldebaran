"""Draw four equal-radius candidates and three spatial visits.

Run: python3 experiments/fold_shoulder_events_figure.py
Standard library only. Reads the finite certificates for display values.
The generated SVG and responsive reading page work without JavaScript.
All plotted geometry is numerical; repeat the separate rational proofs.
"""

import cmath
from fractions import Fraction as Q
from html import escape
import json
from math import atan, pi

from blend_cusps import require
from fold_contacts_figure import (BG, BLUE, GOLD, GREEN, HERE, INK, MUTED,
                                  PANEL, midpoint, number, orbit, path, text)

ROSE = '#edabb8'
COLORS = (BLUE, GOLD, GREEN, ROSE)
SCALE = Q(11, 40)


def geometry(event):
    d = event['folds']
    phi = midpoint(event['phase_over_pi'])*pi
    z = complex(*map(midpoint, event['position']))
    radial = event['fourth_visit']
    parameters = list(map(midpoint, radial['known_half_angle_parameters']))
    parameters.append(midpoint(radial['fourth_half_angle_parameter']))
    candidates = []
    for v in parameters:
        u = 2*atan(v)
        bracket = 245+140*cmath.exp(1j*u)+65*cmath.exp(1j*(phi-u))
        target = cmath.phase(z)-cmath.phase(bracket)
        k = round((d*target-u)/(2*pi))
        t = (u+2*pi*k)/d
        point = cmath.exp(1j*t)*bracket
        offset = d*cmath.phase(point/z)/(2*pi)
        require(abs(abs(bracket)-abs(z)) < 1e-7, 'An illustrated candidate leaves the common radius.')
        require(-.5-1e-10 <= offset <= .5+1e-10, 'An illustrated lift leaves its nearest sector.')
        candidates.append({'v': v, 'u': u, 'B': bracket, 'offset': offset})
    require(all(abs(c['offset']) < 1e-8 for c in candidates[:3]),
            'The three illustrated spatial visits do not align.')
    require(abs(candidates[3]['offset']) > .01, 'The illustrated fourth direction is unresolved.')
    return d, phi, z, candidates


def orbit_panel(event):
    d, phi, z, _ = geometry(event)
    rotation = z.conjugate()/abs(z)
    segments = 4096
    while SCALE*(245+140*(d+1)**2+65*(d-1)**2)*Q(44, 7*segments)**2/8+Q(1, 100000) >= Q(1, 200):
        segments *= 2
    points = []
    for k in range(segments+1):
        x, y = orbit(2*pi*k/segments, d, phi)
        p = complex(x, y)*rotation
        points.append((180+float(SCALE)*p.real, 162-float(SCALE)*p.imag))
    budget = SCALE*(245+140*(d+1)**2+65*(d-1)**2)*Q(44, 7*segments)**2/8+Q(1, 100000)
    require(budget < Q(1, 200), 'An orbit exceeds its 0.005 sheet-unit error budget.')
    mx = 180+float(SCALE)*abs(z)
    return ''.join([text(180, 25, 'One complete drawing', 22, INK, 'text-anchor="middle"'),
                    f'<g data-role="orbit-panel" data-folds="{d}" data-phase="{phi}" '
                    f'data-rotation="{-cmath.phase(z)}" data-scale="{SCALE}" data-segments="{segments}">',
                    path(points, BLUE, .65, 'data-role="orbit"'),
                    f'<circle cx="{number(mx)}" cy="162" r="6" fill="{INK}" stroke="{BG}" stroke-width="2"/>',
                    '</g>', text(180, 296, f'{d} rotated triple points · one marked', 17, MUTED,
                                'text-anchor="middle"')])


def ellipse_panel(event):
    d, phi, z, candidates = geometry(event)
    scale, cx, cy = .28, 130, 162
    project = lambda p: (cx+scale*p.real, cy-scale*p.imag)
    points = []
    for k in range(1025):
        u = 2*pi*k/1024
        bracket = 245+140*cmath.exp(1j*u)+65*cmath.exp(1j*(phi-u))
        points.append(project(bracket))
    result = [text(180, 25, 'Four points at one radius', 22, INK, 'text-anchor="middle"'),
              f'<g data-role="ellipse-panel" data-folds="{d}" data-phase="{phi}">',
              f'<circle cx="{cx}" cy="{cy}" r="{number(scale*abs(z))}" fill="none" '
              'stroke="#70758f" stroke-width="1.3" stroke-dasharray="4 5"/>',
              path(points, MUTED, 1.4, 'data-role="ellipse"'),
              f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{MUTED}"/>']
    for j, (candidate, color) in enumerate(zip(candidates, COLORS)):
        x, y = project(candidate['B'])
        result += [f'<circle cx="{number(x)}" cy="{number(y)}" r="4" fill="{color}" '
                   f'stroke="{PANEL}" stroke-width="1" data-role="radius-point" data-visit="{j}" '
                   f'data-v="{candidate["v"]}"/>']
    result += ['</g>', text(180, 296, 'The dotted circle fixes the radius', 17, MUTED, 'text-anchor="middle"')]
    return ''.join(result)


def direction_panel(event):
    d, _, _, candidates = geometry(event)
    result = [text(180, 25, 'Three matching directions', 22, INK, 'text-anchor="middle"'),
              f'<g data-role="direction-panel" data-folds="{d}">',
              path(((205, 47), (205, 235)), '#70758f', 1.3, 'stroke-dasharray="4 5"')]
    for j, (candidate, color) in enumerate(zip(candidates, COLORS)):
        y = 76+43*j
        x = 205+250*candidate['offset']
        result += [text(25, y+6, 'ABCD'[j], 20, color),
                   path(((80, y), (330, y)), '#383b50', 1),
                   path(((205, y), (x, y)), color, 2),
                   f'<circle cx="{number(x)}" cy="{y}" r="5.5" fill="{color}" '
                   f'data-role="direction-point" data-visit="{j}" data-offset="{candidate["offset"]}"/>']
    result += [path(((80, 237), (330, 237)), MUTED, 1)]
    for x, label in ((80, '−½'), (205, '0'), (330, '+½')):
        result += [path(((x, 233), (x, 241)), MUTED, 1),
                   text(x, 263, label, 17, MUTED, 'text-anchor="middle"')]
    result += ['</g>', text(180, 296, 'Direction offset · in one fold sector', 17, MUTED,
                            'text-anchor="middle"')]
    return ''.join(result)


def panel_svg(content, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 310" '
            'width="360" height="310" role="img" aria-label="'+escape(label, quote=True)+'" '
            'font-family="ui-sans-serif,system-ui,sans-serif">'+content+'</svg>')


def figure(events):
    result = ['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="1320" '
              'viewBox="0 0 1260 1320" role="img" aria-labelledby="title desc" '
              'font-family="ui-sans-serif,system-ui,sans-serif">',
              '<title id="title">Four points. Three visits.</title>',
              '<desc id="desc">Three rows show selected negative ordinary triples at thirty, sixty, '
              'and one hundred twenty folds. Each full orbit has one triple marked. Four colored '
              'points lie on an offset ellipse and the same radius circle. The direction strip '
              'puts the nearest spatial lift of each point in one rotational sector: blue A, '
              'gold B, and green C align at zero, while pink D misses. Orbit drawings share a scale '
              'and are each rotated to place the selected meeting on the right. Ellipses share '
              'another scale. The strips measure fractions of a fold sector, not distances. '
              'These are numerical illustrations of separately certified selected events, not censuses.</desc>',
              f'<rect width="1260" height="1320" fill="{BG}"/>',
              text(30, 66, 'Four points. Three visits.', 47, INK),
              text(30, 111, 'Sharing a radius is only half the journey. The fourth point has the wrong direction.', 23)]
    for j, event in enumerate(events):
        top = 171+350*j
        d, phase = event['folds'], midpoint(event['phase_over_pi'])
        result += [text(30, top, f'{d} folds', 29, INK),
                   text(230, top, f'φ / π ≈ {phase:.13f} · selected negative triple', 22),
                   f'<g transform="translate(30,{top+20})">'+orbit_panel(event)+'</g>',
                   f'<g transform="translate(440,{top+20})">'+ellipse_panel(event)+'</g>',
                   f'<g transform="translate(850,{top+20})">'+direction_panel(event)+'</g>']
    result += [text(30, 1235, 'A, B, C: the three visits. D: the only remaining radius candidate. Exactly three meet.', 22),
               text(30, 1270, 'Selected batches only · numerical artwork · rational local proofs and whole-orbit fourth-visit exclusions', 20),
               '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_shoulder_events.html">',
               text(30, 1305, 'Follow the radius and the direction ↗', 22, GOLD), '</a></svg>']
    return '\n'.join(result)+'\n'


def page(events):
    sections = []
    labels = ('A full orbital drawing with one selected triple marked.',
              'Four colored points on the ellipse share a radius.',
              'Three directions align at zero; the fourth misses.')
    for event in events:
        d, phase = event['folds'], midpoint(event['phase_over_pi'])
        pictures = ''.join('<div class="picture">'+panel_svg(fn(event), label)+'</div>'
                           for fn, label in zip((orbit_panel, ellipse_panel, direction_panel), labels))
        sections.append(f'<section aria-labelledby="fold-{d}"><h2 id="fold-{d}">{d} folds</h2>'
                        f'<p class="phase">Selected phase ≈ {phase:.13f}π</p><div class="pictures">{pictures}</div></section>')
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101323">
  <meta name="description" content="Four points on an ellipse share a radius, but only three meet on the orbital drawing. Three certified local examples approach the radial shoulder.">
  <title>Aldebaran · Four points, three visits</title>
  <style>
    :root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; background: #101323; color: #f4f1e8; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    main { max-width: 80rem; margin: auto; padding: clamp(1.2rem, 4vw, 3rem); overflow-wrap: anywhere; }
    a { color: #e8b66e; text-underline-offset: .22em; }
    :focus-visible { outline: 3px solid #e8b66e; outline-offset: 5px; }
    nav, .save, .jump { display: flex; flex-wrap: wrap; gap: .8rem 2rem; }
    nav { justify-content: space-between; font-size: .85rem; margin-bottom: 3rem; }
    .eyebrow { color: #e8b66e; font-size: .75rem; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; }
    h1 { font-size: clamp(3.4rem, 8vw, 6.5rem); font-weight: 650; line-height: 1; letter-spacing: -.065em; margin: 1rem 0 1.5rem; }
    p { color: #c7c7d4; line-height: 1.8; max-width: 45rem; }
    .intro { font-size: 1.1rem; }
    .jump { border-block: 1px solid #383b50; padding-block: 1rem; margin-block: 2rem; font-size: .9rem; }
    section { margin-top: 3rem; }
    h2 { font-size: 1.7rem; line-height: 1.2; letter-spacing: -.03em; margin-bottom: .5rem; scroll-margin-top: 1rem; }
    .phase { margin-top: 0; font-variant-numeric: tabular-nums; font-size: .9rem; }
    .pictures { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
    .picture { min-width: 0; border: 1px solid #383b50; border-radius: .8rem; padding: .6rem; background: #0b0e1a; }
    svg { display: block; width: 100%; height: auto; }
    .legend { display: flex; flex-wrap: wrap; gap: .6rem 1.8rem; padding: 0; list-style: none; font-size: .9rem; color: #c7c7d4; }
    .legend span { display: inline-block; min-width: 1.5em; font-weight: 700; }
    .save { margin-block: 2rem; font-size: .9rem; }
    .reading { border-left: 2px solid #e8b66e; padding-left: 1.2rem; margin-top: 2rem; }
    .reading h2 { font-size: 1.3rem; }
    footer { border-top: 1px solid #383b50; margin-top: 3rem; padding-top: 1rem; color: #9999ae; line-height: 1.8; font-size: .85rem; }
    @media (max-width: 1050px) { .pictures { grid-template-columns: repeat(2, minmax(0, 1fr)); max-width: 48rem; } }
    @media (max-width: 680px) { .pictures { grid-template-columns: minmax(0, 1fr); max-width: 28rem; } }
    @media print { :root { color-scheme: light; background: white; color: #101323; } nav, .jump, .save { display: none; } p, a, footer { color: #101323; } .pictures { grid-template-columns: repeat(3, minmax(0, 1fr)); max-width: none; } .picture { background: #101323; } section { break-inside: avoid; } }
  </style>
</head>
<body>
  <main>
    <nav aria-label="Sketchbook navigation"><a href="index.html">← All studies</a><a href="fold_movie.html">Every meeting in the turn ↗</a></nav>
    <header>
      <div class="eyebrow">Radius and direction</div>
      <h1>Four points.<br>Three visits.</h1>
      <p class="intro">The ellipse offers four points at the same radius. Three return to the same place on the orbital drawing. The fourth passes in another direction.</p>
    </header>
    <p>Thirty, sixty, then one hundred twenty folds: three selected meetings creep toward the same radial shoulder. Each is a negative ordinary triple. At its exact location, three visits meet and a fourth is excluded.</p>
    <div class="jump" aria-label="Choose a fold count"><a href="#fold-30">30 folds ↓</a><a href="#fold-60">60 folds ↓</a><a href="#fold-120">120 folds ↓</a></div>
    <ul class="legend" aria-label="Candidate colors"><li><span style="color:#9fc7eb">A</span><span style="color:#e8b66e">B</span><span style="color:#a7d9bb">C</span>Three visits</li><li><span style="color:#edabb8">D</span>The remaining candidate</li></ul>
    <p>Read each row from left to right. The whole drawing marks one meeting. The ellipse shows four candidates at its radius. The direction strip follows each candidate to its nearest place within one fold sector. Three line up at zero; D misses.</p>
    '''+''.join(sections)+'''
    <p>Every full drawing uses one scale, rotated to put the selected meeting on the right. The ellipses use their own common scale. The strips measure fractions of a fold sector: a half-sector spans π/d radians. Those strips compare angles, rather than physical distances.</p>
    <div class="save"><a href="fold_shoulder_events.svg">Open the complete sheet ↗</a><a href="fold_shoulder_events.svg" download>Save the drawing ↓</a><a href="fold_shoulder.svg">See the petals before the turn ↗</a></div>
    <h2>One radius is only half the test</h2>
    <p>A point in the orbital drawing has both a radius and a direction. The ellipse's four candidates share the first. They usually do not share the second. At these selected phases, three agree on both; the fourth cannot.</p>
    <p>The radius equation is a quartic. Three known roots leave just one candidate. Its possible time direction would have to satisfy one more circle identity. Rational bounds prove it misses that identity in all three examples.</p>
    <h2>Closer to the shoulder</h2>
    <p>No three-or-more-visit meeting is possible through <strong>0.894940827171…π</strong>, at any positive fold count. These examples get closer as their folds grow. A separate analytic argument constructs meetings arbitrarily close from above, with phase excess proportional to 1/d².</p>
    <p>The finite examples certify <em>selected batches</em>, with thirty, sixty, or one hundred twenty rotated points each. They do not count every event at those fold counts, identify the first meeting, or supply a numerical cutoff for the analytic theorem. The drawings and printed phase locations are rounded illustrations.</p>
    <h2>Ordinary triples reach the same limit</h2>
    <p>A further analytic calculation proves that ordinary negative triples approach the shoulder too. For sufficiently large folds, all three selected pairs stay transverse, and a fourth branch cannot join at two consecutive fold counts. At least one of each pair therefore has an ordinary triple. There is no specified starting fold count.</p>
    <p>The meeting also gets flatter: its closest pair of tangent directions approaches parallel as 1/d³. <a href="fold_shoulder_tangents.md">Follow the tangent expansion and the fourth direction ↗</a>.</p>
    <aside class="reading">
      <h2>Follow the calculation</h2>
      <p><a href="fold_shoulder_events.md">Three finite local certificates ↗</a> · <a href="fold_shoulder_events.json">Their exact bounds ↗</a><br><a href="fold_radial.md">Why three visits have to wait ↗</a> · <a href="fold_shoulder.md">Meetings approach the shoulder ↗</a></p>
    </aside>
    <footer>Aldebaran · A little time, every day.<br><a href="index.html">All studies ↗</a> · <a href="../JOURNAL.md">Read the notebook ↗</a></footer>
  </main>
</body>
</html>
'''


def main():
    record = json.loads((HERE/'fold_shoulder_events.json').read_text())
    events = record['events']
    (HERE/'fold_shoulder_events.svg').write_text(figure(events))
    (HERE/'fold_shoulder_events.html').write_text(page(events))
    print('Wrote three radius/direction comparisons, a standalone sheet, and a responsive reading page.')


if __name__ == '__main__':
    main()
