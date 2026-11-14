"""Draw the two complete phase-contact staircases and one opening lens.

Run: python3 experiments/fold_contacts_figure.py
Standard library only. Reads the archived certificate for approximate
display locations; repeat fold_contacts.py for a fresh mathematical proof.
The SVG and static HTML page have no external dependencies or scripts.
"""

from fractions import Fraction as Q
from html import escape
import json
from math import cos, hypot, pi, sin, sqrt
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SEGMENTS = 4096
INK = '#f4f1e8'
MUTED = '#c7c7d4'
GOLD = '#e8b66e'
BLUE = '#9fc7eb'
GREEN = '#a7d9bb'
BG = '#101323'
PANEL = '#0b0e1a'


def midpoint(a):
    return float((Q(a['low'])+Q(a['high']))/2)


def number(x):
    return f'{x:.5f}'.rstrip('0').rstrip('.') or '0'


def text(x, y, content, size=24, color=MUTED, extra=''):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>'
            f'{escape(str(content))}</text>')


def path(points, color=MUTED, width=1, extra='', close=False):
    data = 'M'+'L'.join(','.join(number(x) for x in p) for p in points)
    return (f'<path d="{data}{"Z" if close else ""}" fill="none" '
            f'stroke="{color}" stroke-width="{width}" {extra}/>')


def orbit(t, d, phase, order=0):
    result = [0., 0.]
    for r, k in ((245, 1), (140, d+1), (65, -(d-1))):
        angle = k*t+(phase if k < 0 else 0)+order*pi/2
        result[0] += r*k**order*cos(angle)
        result[1] += r*k**order*sin(angle)
    return result


def frame(event):
    times = [midpoint(t) for t in event['times']]
    phase = midpoint(event['phase_over_pi'])*pi
    center = orbit(times[0], 7, phase)
    v = orbit(times[0], 7, phase, 1)
    speed = hypot(*v)
    return times, phase, center, [v[0]/speed, v[1]/speed]


def branch(frame_data, phase, index, x):
    times, _, center, tangent = frame_data

    def local(p, vector=False):
        a, b = [p[j]-(0 if vector else center[j]) for j in range(2)]
        return tangent[0]*a+tangent[1]*b, -tangent[1]*a+tangent[0]*b

    t = times[index]
    for _ in range(10):
        p = local(orbit(t, 7, phase))
        v = local(orbit(t, 7, phase, 1), True)
        if abs(v[0]) < 400:
            raise ValueError('The illustrated branch left its local graph.')
        t -= (p[0]-x)/v[0]
    p = local(orbit(t, 7, phase))
    if abs(p[0]-x) > 1e-9 or abs(t-times[index]) > .02:
        raise ValueError('The illustrated graph inversion did not converge.')
    return p[1]


def bisect(fn, a, b):
    fa = fn(a)
    if fa*fn(b) > 0:
        raise ValueError('An illustrated crossing was not bracketed.')
    for _ in range(48):
        m = (a+b)/2
        fm = fn(m)
        if fa*fm > 0:
            a, fa = m, fm
        else:
            b = m
    return (a+b)/2


def diagram(record):
    seven, fourteen = record['families']
    events7, events14 = seven['events'], fourteen['events']
    phases7 = [midpoint(e['phase_over_pi']) for e in events7]
    phases14 = [midpoint(e['phase_over_pi']) for e in events14]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1760" '
        'viewBox="0 0 1200 1760" role="img" aria-labelledby="title description">',
        '<title id="title">The folds stay. The crossings change.</title>',
        '<desc id="description">Three equal-scale sevenfold orbital drawings have 7, 21, and 35 '
        'crossing pairs at backward-arm phases zero, 0.65 pi, and pi. A complete staircase '
        'has seven simultaneous quadratic touches at phase 0.341592 pi, then seven more '
        'at 0.951536 pi. The fourteenfold staircase rises from 70 to 98 to 126 pairs, '
        'at phases 0.914297 pi and 0.962912 pi; its axis shows only the last eleven percent '
        'of the half-turn. Three enlarged separation graphs show the first sevenfold '
        'gap before, near, and after its touch. Two zeros enclose a newly opened lens. '
        'The graph axes have different scales. The contact census is certified; plotted '
        'geometry is numerical. Pair counts include three pairs at a triple visit.</desc>',
        f'<rect width="1200" height="1760" fill="{BG}"/>',
        '<g font-family="ui-sans-serif,system-ui,sans-serif">',
        text(40, 69, 'The folds stay.', 48, INK),
        text(40, 124, 'The crossings change.', 48, INK),
        text(40, 172, 'Turn the backward arm from zero to a half turn. Keep all three lengths.', 25),
    ]
    for column, (phase, pairs, color) in enumerate(((0, 7, BLUE), (.65*pi, 21, GOLD), (pi, 35, GREEN))):
        left, cx, cy, scale = 40+385*column, 215+385*column, 414, .35
        parts += [f'<g data-role="orbit-panel" data-folds="7" data-phase="{phase}" '
                  f'data-cx="{cx}" data-cy="{cy}" data-scale="{scale}">',
                  f'<rect x="{left}" y="220" width="350" height="390" rx="14" '
                  f'fill="{PANEL}" stroke="#383b50"/>',
                  text(cx, 251, f'{pairs} crossing pairs', 26, color, 'text-anchor="middle"')]
        points = []
        for j in range(SEGMENTS+1):
            x, y = orbit(2*pi*j/SEGMENTS, 7, phase)
            points.append((cx+scale*x, cy-scale*y))
        # Same rigorous interpolation estimate as the phase-variation sheet.
        error = Q(7, 20)*(245+140*8**2+65*6**2)*Q(44, 7*SEGMENTS)**2/8+Q(1, 100000)
        if error >= Q(1, 200):
            raise ValueError('The illustrated orbital error exceeds 0.005 sheet units.')
        parts += [path(points, color, .95, 'data-role="orbit" stroke-linejoin="round"'),
                  f'<circle cx="{cx}" cy="{cy}" r="1.7" fill="{MUTED}"/>',
                  text(cx, 582, ('At the start', '0.65 of the half-turn', 'At a half turn')[column], 23,
                       MUTED, 'text-anchor="middle"'), '</g>']

    parts += [text(40, 666, 'Seven folds · two batches of seven touches', 29, INK),
              text(40, 703, 'Each batch adds fourteen transverse crossing pairs.', 23)]

    def staircase(d, phases, counts, ybase, lower):
        # A full sevenfold phase axis; an explicitly cropped fourteenfold axis.
        xmap = lambda f: 100+1020*(f-lower)/(1-lower)
        levels = [ybase-34*j for j in range(3)]
        colors = (BLUE, GOLD, GREEN)
        cuts = [lower]+phases+[1]
        result = [f'<path d="M100,{ybase+29}H1120" stroke="#555b78" fill="none"/>']
        for j in range(3):
            a, b = xmap(cuts[j]), xmap(cuts[j+1])
            result += [f'<path d="M{number(a)},{levels[j]}H{number(b)}" fill="none" '
                       f'stroke="{colors[j]}" stroke-width="5" data-role="step" '
                       f'data-folds="{d}" data-pairs="{counts[j]}"/>',
                       text((a+b)/2, levels[j]-14, str(counts[j]), 24, colors[j], 'text-anchor="middle"')]
            if j < 2:
                result += [f'<path d="M{number(b)},{levels[j]}V{levels[j+1]}" '
                           'stroke="#9999ae" stroke-width="2" stroke-dasharray="4 4"/>',
                           f'<circle cx="{number(b)}" cy="{levels[j+1]}" r="5" fill="{INK}"/>',
                           text(b, ybase+79, f'{phases[j]:.6f}', 22, MUTED, 'text-anchor="middle"')]
        result += [text(100, ybase+51, str(lower), 22, MUTED, 'text-anchor="middle"'),
                   text(1120, ybase+51, '1', 22, MUTED, 'text-anchor="middle"')]
        return result

    parts += staircase(7, phases7, seven['crossing_pairs'], 808, 0)
    parts += [text(40, 924, 'Fourteen folds · two batches of fourteen touches', 29, INK),
              text(40, 961, 'The count stays 70 through 0.89. Enlarge the last part of the turn:', 23)]
    parts += staircase(14, phases14, fourteen['crossing_pairs'], 1066, .89)
    parts += [text(600, 1178, 'Both horizontal axes: fraction of a half turn, φ / π', 22,
                   MUTED, 'text-anchor="middle"'),
              text(40, 1231, 'Subtract two branches. Watch a lens open.', 29, INK),
              text(40, 1270, 'First sevenfold touch · along-tangent range ±4 · normal range −0.12 to +0.36', 22),
              text(40, 1304, 'The normal scale is enlarged. These are selected-branch separation graphs.', 22)]
    fd = frame(events7[0])
    critical = fd[1]
    states = []
    for column, delta in enumerate((-.006, 0, .006)):
        left, cx = 40+385*column, 215+385*column
        xmap = lambda x: cx+34*x
        ymap = lambda y: 1519-420*y
        phase = critical+delta
        gap = lambda x: branch(fd, phase, 0, x)-branch(fd, phase, 1, x)
        roots = [] if delta < 0 else [0] if delta == 0 else [bisect(gap, -4, 0), bisect(gap, 0, 4)]
        parts += [f'<g data-role="gap-panel" data-phase-offset="{delta}" data-cx="{cx}">',
                  f'<rect x="{left}" y="1340" width="350" height="245" rx="14" '
                  f'fill="{PANEL}" stroke="#383b50"/>',
                  text(cx, 1380, ('Before', 'Touch · approximate', 'After')[column], 23, INK,
                       'text-anchor="middle"'),
                  f'<path d="M{cx-145},1519H{cx+145}" stroke="#555b78" fill="none"/>']
        points = [(xmap(-4+8*j/320), ymap(gap(-4+8*j/320))) for j in range(321)]
        if len(roots) == 2:
            a, b = roots
            fill = [(xmap(a), ymap(0))]+[(xmap(a+(b-a)*j/100), ymap(gap(a+(b-a)*j/100)))
                                                   for j in range(101)]+[(xmap(b), ymap(0))]
            parts.append(path(fill, 'none', 0, f'style="fill:{INK};fill-opacity:.2"', close=True))
        parts.append(path(points, (BLUE, GOLD, GREEN)[column], 2.6, 'data-role="gap"'))
        for root in roots:
            parts.append(f'<circle cx="{number(xmap(root))}" cy="1519" r="4.5" '
                         f'fill="{INK}" data-role="meeting" data-root="{root}"/>')
        parts += [text(cx-136, 1564, '−4', 21, MUTED, 'text-anchor="middle"'),
                  text(cx, 1564, '0', 21, MUTED, 'text-anchor="middle"'),
                  text(cx+136, 1564, '+4', 21, MUTED, 'text-anchor="middle"'), '</g>']
        states.append({'phase_offset': delta, 'roots': roots})
    parts += [text(40, 1633, 'At the touch the gap kisses zero. Just after, two zeros bound a little lens.', 23),
              text(40, 1673, 'All seven rotated copies do this together. Both tracing points keep moving.', 23),
              '<a href="https://mmilanta.github.io/aldebaran/experiments/fold_contacts.html">',
              text(40, 1725, 'Read the complete contact census and its scope ↗', 23, GOLD), '</a></g></svg>']
    return '\n'.join(parts)+'\n', states


def page(record, svg):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root = ET.fromstring(svg)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    orbit_panels, gap_panels = [], []

    def fragment(group, viewbox, height, description):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="350" '
                f'height="{height}" viewBox="{viewbox}" role="img" '
                f'aria-label="{escape(description, quote=True)}" '
                'font-family="ui-sans-serif,system-ui,sans-serif">'
                +ET.tostring(group, encoding='unicode')+'</svg>')

    for j, group in enumerate(root.findall('.//s:g[@data-role="orbit-panel"]', ns)):
        description = (f'Sevenfold orbital drawing with {(7, 21, 35)[j]} crossing pairs. '
                       +('Zero backward-arm starting phase.', 'Starting phase 0.65 pi.',
                         'Starting phase pi.')[j]+' All three drawings use the same scale.')
        orbit_panels.append('<figure class="mini">'+fragment(group, f'{40+385*j} 220 350 390',
                                                             390, description)+'</figure>')
    for j, group in enumerate(root.findall('.//s:g[@data-role="gap-panel"]', ns)):
        description = ('Selected-branch separation '+('before', 'approximately at', 'after')[j]
                       +' the first sevenfold touch. '
                       +('The gap stays above zero.', 'The gap touches zero.',
                         'Two zeros bound a newly opened lens.')[j]
                       +' Along-tangent range minus 4 to plus 4 drawing units. Normal scale enlarged.')
        gap_panels.append('<figure class="mini">'+fragment(group, f'{40+385*j} 1340 350 245',
                                                           245, description)+'</figure>')
    rows = []
    for family in record['families']:
        for j, event in enumerate(family['events']):
            before, after = family['crossing_pairs'][j:j+2]
            phase = midpoint(event['phase_over_pi'])
            direction = 'Opposite' if not event['direct'] else 'Same'
            rows.append(f'<tr><th scope="row">{family["folds"]} · {"first" if j == 0 else "second"}</th>'
                        f'<td>{phase:.6f}</td><td>{direction}</td><td>{before} → {after}</td></tr>')
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101323">
  <meta name="description" content="Keep seven or fourteen rotational folds while one arm turns. A complete calculation finds the two batches of touches that change the crossing pairs.">
  <title>Aldebaran · The folds stay. The crossings change.</title>
  <style>
    :root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; background: #101323; color: #f4f1e8; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    main { max-width: 76rem; margin: auto; padding: clamp(1.2rem, 4vw, 3rem); overflow-wrap: anywhere; }
    a { color: #e8b66e; text-underline-offset: .2em; }
    :focus-visible { outline: 3px solid #e8b66e; outline-offset: 4px; }
    nav { display: flex; flex-wrap: wrap; gap: .8rem 2rem; justify-content: space-between; font-size: .85rem; margin-bottom: 3rem; }
    .eyebrow { color: #e8b66e; font-size: .75rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
    h1 { font-size: clamp(2.5rem, 7vw, 5.5rem); line-height: 1.05; letter-spacing: -.05em; max-width: 16ch; margin: 1rem 0 1.5rem; }
    h2 { font-size: clamp(1.6rem, 4vw, 2.3rem); letter-spacing: -.03em; margin: 2.5rem 0 1rem; }
    p { max-width: 48rem; color: #c7c7d4; line-height: 1.8; }
    .intro { font-size: 1.1rem; max-width: 42rem; }
    figure { margin: 2rem 0; }
    .drawings { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin: 2rem 0 1rem; }
    .mini { min-width: 0; margin: 0; }
    .mini svg { width: 100%; height: auto; display: block; }
    img { display: block; width: 100%; height: auto; border: 1px solid #383b50; border-radius: .8rem; }
    figcaption { font-size: .9rem; color: #c7c7d4; line-height: 1.8; margin-top: .8rem; max-width: 49rem; }
    .save { display: flex; flex-wrap: wrap; gap: .8rem 1.6rem; margin: 1rem 0; }
    table { width: 100%; max-width: 55rem; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .95rem; }
    caption { text-align: left; color: #c7c7d4; line-height: 1.7; margin-bottom: 1rem; }
    th, td { text-align: left; padding: .9rem .65rem; border-bottom: 1px solid #383b50; overflow-wrap: anywhere; }
    th { font-weight: 600; }
    td { color: #c7c7d4; }
    .reading { border-left: 2px solid #e8b66e; padding-left: 1.2rem; margin-top: 2rem; }
    footer { border-top: 1px solid #383b50; padding-top: 1rem; margin-top: 3rem; font-size: .85rem; color: #9999ae; line-height: 1.8; }
    @media (max-width: 640px) { .drawings { grid-template-columns: minmax(0, 1fr); max-width: 25rem; } }
    @media (max-width: 560px) { table { font-size: .8rem; } th, td { padding: .8rem .3rem; } }
    @media print { :root { color-scheme: light; background: white; color: #101323; } nav, .save { display: none; } p, td, caption, figcaption, a { color: #101323; } }
  </style>
</head>
<body>
  <main>
    <nav aria-label="Sketchbook navigation"><a href="index.html">← All studies</a><a href="../index.html">Make a drawing ↗</a></nav>
    <header>
      <div class="eyebrow">A turn through the folds</div>
      <h1>The folds stay.<br>The crossings change.</h1>
      <p class="intro">Keep the rhythms. Turn where the backward arm begins. Seven petals become a ring; little lenses open along the way. The point keeps moving, and the drawing keeps all seven folds.</p>
    </header>
    <p>There are just two moments when branches touch during this half-turn. Each happens in seven rotated places at once, adding fourteen crossing pairs. The count rises from <strong>7 to 21 to 35</strong>. Fourteen folds have two moments too, both near the end: <strong>70 to 98 to 126</strong>.</p>
    <div class="drawings" role="group" aria-label="Three sevenfold drawings at one scale">'''+''.join(orbit_panels)+'''</div>
    <p>The three drawings share one scale and arm lengths 245, 140, and 65.</p>
    <div class="save"><a href="fold_contacts.svg">Open both contact staircases ↗</a><a href="fold_contacts.svg" download>Save the complete drawing sheet ↓</a><a href="fold_variations.svg">See all six phase variations ↗</a></div>
    <h2>Four batches of touches</h2>
    <p>The first sevenfold touch brings opposing travel directions together. The other three bring matching directions together. Each opens a lens, and each branch has a nonzero velocity throughout the whole turn.</p>
    <table>
      <caption>All contact phases for these two half-turns. Phase is a fraction of π radians; printed locations are rounded.</caption>
      <thead><tr><th scope="col">Folds · batch</th><th scope="col">Phase / π</th><th scope="col">Travel directions</th><th scope="col">Pairs before → after</th></tr></thead>
      <tbody>'''+''.join(rows)+'''</tbody>
    </table>
    <h2>Subtract two branches</h2>
    <p>The opening is thin. Subtract one branch from the other, then enlarge the normal scale. At the touch the gap kisses zero. Just after, two zeros enclose a little lens. All seven rotated copies do this together.</p>
    <div class="drawings" role="group" aria-label="The selected gap before, near, and after the first sevenfold touch">'''+''.join(gap_panels)+'''</div>
    <p>The graph axes have different scales. Each horizontal axis runs from −4 to +4 drawing units along the common tangent; normal separation runs from −0.12 to +0.36. A zero means the branches meet.</p>
    <h2>A pair is a pair of visits</h2>
    <p>Three visits can meet at one point. That point counts as three pairs, one for each choice of two visits. The calculation counts all tangencies between two visits; it does not locate all triple passages or count every winding region through the turn. At each certified touch, a separate whole-orbit calculation rules out a third branch.</p>
    <p>The small graph shows the selected sevenfold branches at a phase offset of −0.006, approximately zero, and +0.006 radians from their first touch. It is a numerical illustration. Its wider window is separate from the small disk used to prove that the exact contact has only two branches.</p>
    <aside class="reading">
      <h2>Two visits make a triangle</h2>
      <p>Subtract the two visits and factor out their common turn. The three remaining vectors must close into a triangle. Its side lengths depend only on the separation of the visits. That turns the complete tangency question into one polynomial in one variable.</p>
      <p><a href="fold_contacts.md">Follow the proof, exceptions, and area law ↗</a> · <a href="fold_contacts.py">Repeat the standard-library calculation ↗</a> · <a href="fold_contacts.json">Read the rational proof record ↗</a></p>
      <p>The earlier <a href="fold_variations.md">ellipse inside a turn</a> explains why the folds, tangent turns, and signed area stay fixed. The older interactive <a href="touch.html">Two ways to touch</a> explores a different orbital family.</p>
    </aside>
    <footer>Aldebaran · A little time, every day.<br><a href="index.html">All studies ↗</a> · <a href="../JOURNAL.md">Read the notebook ↗</a></footer>
  </main>
</body>
</html>
'''


def main():
    record = json.loads((HERE/'fold_contacts.json').read_text())
    svg, states = diagram(record)
    (HERE/'fold_contacts.svg').write_text(svg)
    (HERE/'fold_contacts.html').write_text(page(record, svg))
    print('Wrote the complete contact staircases and three sevenfold separation graphs.')
    print('Numerical gap roots:', states)


if __name__ == '__main__':
    main()
