"""Draw the complete phase-event timeline, from the local event records.

Run: python3 experiments/fold_movie_figure.py
Standard library only. Curves and diagram positions are numerical artwork;
fold_movie_census.py repeats the continuous rational proof independently.
"""

import json
from math import pi
import xml.etree.ElementTree as ET

from fold_contacts_figure import (BG, BLUE, GOLD, GREEN, HERE, INK, MUTED,
                                  PANEL, midpoint, number, orbit, path, text)

ROSE = '#edabb8'
NS = 'http://www.w3.org/2000/svg'


def events():
    contacts = json.loads((HERE/'fold_contacts.json').read_text())
    triples = json.loads((HERE/'fold_triples.json').read_text())
    rows = []
    for family in contacts['families']:
        for j, event in enumerate(family['events']):
            rows.append({'folds': family['folds'], 'phase': midpoint(event['phase_over_pi']),
                         'kind': 'touch', 'sign': 0, 'delta_pairs': 2*family['folds'],
                         'direct': event['direct']})
    for event in triples['events']:
        rows.append({'folds': event['folds'], 'phase': midpoint(event['phase_over_pi']),
                     'kind': 'triple', 'sign': event['passage_sign'], 'delta_pairs': 0})
    return sorted(rows, key=lambda row: (row['folds'], row['phase']))


def mark(x, y, event, radius=5):
    color = GOLD if event['kind'] == 'touch' else BLUE if event['sign'] > 0 else ROSE
    if event['kind'] == 'touch':
        return (f'<path d="M{number(x)},{number(y-radius)}l{radius},{radius}'
                f'l-{radius},{radius}l-{radius},-{radius}Z" fill="{color}"/>')
    result = f'<path d="M{number(x-radius)},{number(y)}h{2*radius}" stroke="{color}" stroke-width="2.4"/>'
    if event['sign'] > 0:
        result += f'<path d="M{number(x)},{number(y-radius)}v{2*radius}" stroke="{color}" stroke-width="2.4"/>'
    return result


def family_panel(d, x, rows):
    relevant = [row for row in rows if row['folds'] == d]
    result = [f'<g data-role="family-panel" data-folds="{d}" transform="translate({x},190)">',
              f'<rect width="540" height="860" rx="18" fill="{PANEL}" stroke="#383b50"/>',
              text(30, 45, f'{d} folds', 31, INK),
              text(30, 77, 'The same lengths. A different weave.', 21)]
    for j, phase in enumerate((0, pi)):
        cx, cy, scale = 145+250*j, 220, .215
        result.append(f'<g data-role="orbit-panel" data-folds="{d}" data-phase="{phase}" data-cx="{cx}" data-cy="{cy}" data-scale="{scale}">')
        points = []
        for k in range(4097):
            px, py = orbit(2*pi*k/4096, d, phase)
            points.append((cx+scale*px, cy-scale*py))
        result.append(path(points, BLUE if j == 0 else GREEN, .9,
                           'data-role="orbit" stroke-linejoin="round"'))
        result.append(text(cx, 340, 'At zero' if j == 0 else 'At a half turn', 21, MUTED,
                           'text-anchor="middle"'))
        pairs = (7, 35) if d == 7 else (70, 126)
        result.append(text(cx, 372, f'{pairs[j]} pairs · St {d*(j+1)}', 22, INK,
                           'text-anchor="middle"'))
        result.append('</g>')
    result.extend([text(30, 420, 'The complete half-turn', 24, INK),
                   path(((80, 455), (490, 455)), '#70758f', 1.4),
                   '<rect x="449" y="442" width="41" height="26" fill="none" stroke="#858aa5"/>'])
    for row in relevant:
        result.append(mark(80+410*row['phase'], 455, row, 4))
    result.extend([text(80, 490, '0', 19, MUTED, 'text-anchor="middle"'),
                   text(490, 490, 'π', 19, MUTED, 'text-anchor="middle"'),
                   text(30, 525, 'The last tenth, enlarged', 24, INK)])
    xp = lambda p: 80+410*(p-.9)/.1
    for role, start, maximum, base, height, color, label in (
            ('pairs', 7 if d == 7 else 70, 40 if d == 7 else 140, 650, 85, GOLD, 'Pairs'),
            ('strangeness', d, 18 if d == 7 else 35, 800, 85, BLUE, 'St')):
        minimum = 50 if d == 14 and role == 'pairs' else 0
        yp = lambda value: base-height*(value-minimum)/(maximum-minimum)
        value = start
        for row in relevant:
            if row['phase'] < .9:
                value += row['delta_pairs'] if role == 'pairs' else d*row['sign']
        initial = value
        points, previous = [], .9
        result.append(text(30, base-height-10, label, 23, color))
        ticks = (21, 35) if role == 'pairs' and d == 7 else (70, 98, 126) if role == 'pairs' else (7, 14) if d == 7 else (14, 28)
        for tick in ticks:
            y = yp(tick)
            result.append(path(((80, y), (490, y)), '#33394f', .8))
            result.append(text(68, y+7, tick, 19, MUTED, 'text-anchor="end"'))
        for row in relevant:
            if row['phase'] < .9:
                continue
            p = row['phase']
            points.extend(((xp(previous), yp(value)), (xp(p), yp(value))))
            delta = row['delta_pairs'] if role == 'pairs' else d*row['sign']
            if delta:
                result.append(path(((xp(p), yp(value)), (xp(p), yp(value+delta))), color, 1.1,
                                   'stroke-dasharray="3 4"'))
            if role == 'pairs' and row['kind'] == 'touch':
                result.append(mark(xp(p), yp(value+delta/2), row, 5))
            elif role == 'strangeness' and row['kind'] == 'triple':
                result.append(mark(xp(p), yp(value+delta/2), row, 5))
            value += delta
            previous = p
        points.extend(((xp(previous), yp(value)), (xp(1), yp(value))))
        # Separate subpaths keep vertical transitions out of the plateaux.
        data = ''.join(f'M{number(a[0])},{number(a[1])}L{number(b[0])},{number(b[1])}'
                       for a, b in zip(points[::2], points[1::2]))
        result.append(f'<path d="{data}" fill="none" stroke="{color}" stroke-width="2.8" '
                      f'data-role="{role}-steps" data-folds="{d}" data-initial="{initial}" data-final="{value}"/>')
        for p, lab in ((.9, '.90π'), (.95, '.95π'), (1, 'π')):
            result.append(text(xp(p), base+27, lab, 19, MUTED, 'text-anchor="middle"'))
    result.append('</g>')
    return '\n'.join(result)


def diagram(rows):
    parts = [f'<svg xmlns="{NS}" width="1160" height="1190" viewBox="0 0 1160 1190" role="img" '
             'aria-labelledby="title desc" font-family="ui-sans-serif,system-ui,sans-serif">',
             '<title id="title">Every meeting in the turn</title>',
             '<desc id="desc">Complete event timelines for seven and fourteen folds. The crossing-pair counts rise at touches. '
             'Strangeness rises at positive triples and falls at a negative triple. Seven folds have exactly seven positive '
             'triple passages. Fourteen folds have twenty-eight positive and fourteen negative. Four endpoint drawings use one scale.</desc>',
             f'<rect width="1160" height="1190" fill="{BG}"/>',
             text(30, 52, 'ALDEBARAN · A COMPLETE HALF-TURN', 19, GOLD, 'letter-spacing="3"'),
             text(30, 112, 'Every meeting in the turn.', 50, INK),
             text(30, 154, 'Touches change the count. Triples change the order.', 26)]
    parts.extend(family_panel(d, x, rows) for d, x in ((7, 25), (14, 595)))
    for x, event, label in ((45, {'kind': 'touch'}, 'Touch'),
                            (250, {'kind': 'triple', 'sign': 1}, 'Positive triple'),
                            (590, {'kind': 'triple', 'sign': -1}, 'Negative triple')):
        parts.append(mark(x, 1090, event, 7))
        parts.append(text(x+20, 1098, label, 23))
    parts.extend([text(30, 1140, 'Lines show values between events; dashed jumps connect the neighboring values.', 21),
                  text(30, 1172, 'Each marker is one rotational batch. Curves and event locations are numerical illustrations.', 20), '</svg>'])
    return '\n'.join(parts)+'\n'


def page(rows, svg):
    ET.register_namespace('', NS)
    root = ET.fromstring(svg)
    panels = []
    for group in root.findall(f'{{{NS}}}g[@data-role="family-panel"]'):
        d = group.attrib['data-folds']
        group.attrib.pop('transform')
        panels.append(f'<figure><svg xmlns="{NS}" viewBox="0 0 540 860" width="540" height="860" role="img" '
                      f'aria-label="{d} folds: endpoint drawings, the complete half-turn, and an enlarged final tenth showing crossing pairs and strangeness." '
                      'font-family="ui-sans-serif,system-ui,sans-serif">'
                      +ET.tostring(group, encoding='unicode')+'</svg></figure>')
    table = []
    values = {7: 7, 14: 14}
    for row in rows:
        d = row['folds']
        before = values[d]
        values[d] += d*row['sign']
        label = 'Touch' if row['kind'] == 'touch' else 'Positive triple' if row['sign'] > 0 else 'Negative triple'
        table.append(f'<tr><th scope="row">{d}</th><td>{row["phase"]:.6f}</td><td>{label}</td><td>{before} → {values[d]}</td></tr>')
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101323">
  <meta name="description" content="A complete phase-event census for seven and fourteen folds: every touch, every triple passage, and two ways to count what changes.">
  <title>Aldebaran · Every meeting in the turn</title>
  <style>
    :root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; background: #101323; color: #f4f1e8; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    main { max-width: 76rem; margin: auto; padding: clamp(1.2rem, 4vw, 3rem); overflow-wrap: anywhere; }
    a { color: #e8b66e; text-underline-offset: .2em; }
    :focus-visible { outline: 3px solid #e8b66e; outline-offset: 4px; }
    nav, .save { display: flex; flex-wrap: wrap; gap: .8rem 2rem; justify-content: space-between; }
    nav { font-size: .85rem; margin-bottom: 3rem; }
    .eyebrow { color: #e8b66e; font-size: .75rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
    h1 { font-size: clamp(2.5rem, 7vw, 5.5rem); line-height: 1.05; letter-spacing: -.05em; max-width: 14ch; margin: 1rem 0 1.5rem; }
    h2 { font-size: clamp(1.6rem, 4vw, 2.3rem); letter-spacing: -.03em; margin: 2.5rem 0 1rem; }
    p { max-width: 48rem; color: #c7c7d4; line-height: 1.8; }
    .intro { font-size: 1.1rem; max-width: 42rem; }
    .panels { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; margin: 2rem 0; }
    figure { min-width: 0; margin: 0; }
    svg { width: 100%; height: auto; display: block; }
    .save { justify-content: flex-start; }
    table { width: 100%; max-width: 48rem; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .95rem; }
    caption { text-align: left; color: #c7c7d4; line-height: 1.7; margin-bottom: 1rem; }
    th, td { text-align: left; padding: .9rem .65rem; border-bottom: 1px solid #383b50; overflow-wrap: anywhere; }
    th { font-weight: 600; }
    td { color: #c7c7d4; }
    .reading { border-left: 2px solid #e8b66e; padding-left: 1.2rem; margin-top: 2rem; }
    footer { border-top: 1px solid #383b50; padding-top: 1rem; margin-top: 3rem; font-size: .85rem; color: #9999ae; line-height: 1.8; }
    @media (max-width: 740px) { .panels { grid-template-columns: minmax(0, 1fr); max-width: 35rem; } }
    @media (max-width: 560px) { table { font-size: .8rem; } th, td { padding: .8rem .3rem; } }
    @media print { :root { color-scheme: light; background: white; color: #101323; } nav, .save { display: none; } p, td, caption, a { color: #101323; } }
  </style>
</head>
<body>
  <main>
    <nav aria-label="Sketchbook navigation"><a href="index.html">← All studies</a><a href="../index.html">Make a drawing ↗</a></nav>
    <header>
      <div class="eyebrow">A complete half-turn</div>
      <h1>Every meeting in the turn.</h1>
      <p class="intro">A touch opens a lens. A triple sends a triangle through itself. Follow the backward arm through a half-turn: every one of those meetings is now accounted for.</p>
    </header>
    <p>Seven folds have two batches of touches and one batch of positive triples. Fourteen folds have two batches of touches and three batches of triples: positive, negative, positive. Every batch happens in seven or fourteen rotated places at once.</p>
    <div class="panels" role="group" aria-label="The complete sevenfold and fourteenfold timelines">'''+''.join(panels)+'''</div>
    <p>The gold diamonds mark touches; a blue plus marks a positive triple, and a pink minus a negative one. The top strip follows the whole half-turn. Each graph below enlarges its final tenth. All four orbital drawings share one scale.</p>
    <div class="save"><a href="fold_movie.svg">Open the complete sheet ↗</a><a href="fold_movie.svg" download>Save the drawing ↓</a><a href="fold_triples.svg">Magnify one changing triangle ↗</a></div>
    <h2>Two counts tell different stories</h2>
    <p>A touch changes the number of crossing pairs: <strong>7 → 21 → 35</strong> for seven folds, <strong>70 → 98 → 126</strong> for fourteen. A triple leaves those pairs in place and changes their order.</p>
    <p><a href="strangeness.html">Strangeness</a>, abbreviated St, remembers that order. Positive triples add one at each meeting point; negative triples subtract one. For fourteen folds it rises from 14 to 28, returns to 14, then rises to 28 again. The number of pairs stays at 126 during that last down-and-up.</p>
    <p>The lines show values between event phases. At a touch, the tangent pairs give a pair count halfway between the neighboring plateaux. Strangeness is shown only for regular drawings between the events.</p>
    <table>
      <caption>Every event batch on these two half-turns. Printed phase locations are rounded; each row contains as many meeting points as there are folds.</caption>
      <thead><tr><th scope="col">Folds</th><th scope="col">Phase / π</th><th scope="col">Meeting</th><th scope="col">St before → after</th></tr></thead>
      <tbody>'''+''.join(table)+'''</tbody>
    </table>
    <h2>No room for another meeting</h2>
    <p>The earlier calculation found <a href="fold_contacts.html">every touch</a> and proved how many crossing pairs exist between them. Small moving charts now account for every one of those pairs across closed phase intervals. Checking which charts can share visits rules out any additional triple.</p>
    <p>The result is exact: <strong>seven positive triples</strong> for seven folds; <strong>twenty-eight positive and fourteen negative</strong> for fourteen. The half-turn endpoints have freshly certified crossing words too. The result concerns these two families and their fixed arm lengths.</p>
    <h2>Why the triangles wait</h2>
    <p>The ellipse supplies a reason for those late meetings. For <em>every</em> positive fold count, there can be at most two visits per point through phase <strong>0.894940827171…π</strong>. Then its radial profile gains a flat shoulder. <a href="fold_radial.svg">See two ellipse points become four at the same radius ↗</a>, or <a href="fold_radial.md">read the short calculation ↗</a>. Sharing a radius alone does not make a spatial crossing.</p>
    <aside class="reading">
      <h2>Follow the count</h2>
      <p><a href="fold_movie.md">Read the continuous proof and its scope ↗</a> · <a href="fold_movie_census.py">Repeat the standard-library certificate ↗</a> · <a href="fold_movie.json">Read the exact partition and endpoint words ↗</a></p>
      <p>The <a href="fold_variations.md">ellipse inside a turn</a> explains why speed stays positive. The <a href="fold_triples.md">local triangle calculation</a> explains each passage’s sign and quadratic area law. Reflection supplies the rest of a full starting-angle turn.</p>
    </aside>
    <footer>Aldebaran · A little time, every day.<br><a href="index.html">All studies ↗</a> · <a href="../JOURNAL.md">Read the notebook ↗</a></footer>
  </main>
</body>
</html>
'''


def main():
    rows = events()
    svg = diagram(rows)
    (HERE/'fold_movie.svg').write_text(svg)
    (HERE/'fold_movie.html').write_text(page(rows, svg))
    print('Wrote four endpoint drawings and two complete event timelines; no runtime dependencies.')


if __name__ == '__main__':
    main()
