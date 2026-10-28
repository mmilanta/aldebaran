"""Generate weave_data.js and weave.svg from fresh rational proofs.

Run: python3 experiments/weave_figure.py
Only the standard library is used. Figure coordinates are approximate.
The exact words and the complete two event-window proofs are independent
of the numerical geometry used to draw the three close-ups.
"""

import json
from math import pi

from rhythm_passages import HINTS, WINDOWS, HERE, certify_window, check_evaluation, orbit, snapshot


COLORS = ('#9fc7eb', '#e8b66e', '#d1b6ea')


def crossing(times, a, i, j):
    t, u = times[i], times[j]
    for _ in range(12):
        p, q, v, w = orbit(t, a), orbit(u, a), orbit(t, a, 1), orbit(u, a, 1)
        f = p-q
        d = v.imag*w.real-v.real*w.imag
        t -= (-w.imag*f.real+w.real*f.imag)/d
        u -= (-v.imag*f.real+v.real*f.imag)/d
    return t, u


def path(points, project, close=False):
    return 'M'+' L'.join(project(p) for p in points)+(' Z' if close else '')


def samples(start, end, count, a):
    return [orbit(start+(end-start)*j/count, a) for j in range(count+1)]


def still(records, events):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1120" viewBox="0 0 1200 1120" role="img" aria-labelledby="title desc">',
           '<title id="title">The same counts, a different weave</title>',
           '<desc id="desc">Rhythms 11/6 and 11/8 each have 40 crossings, 41 bounded regions, and tangent index 11, but strangeness 15 and 11. Three close-ups show the first triple passage, before, near the meeting, and after. Each passage has a reflected partner below the axis.</desc>',
           '<rect width="1200" height="1120" fill="#101323"/>',
           '<g font-family="system-ui, sans-serif" fill="#f4f1e8">',
           '<text x="40" y="62" font-size="36" font-weight="700">The same counts, a different weave</text>',
           '<text x="40" y="100" font-size="19" fill="#c7c7d4">40 crossings · 41 enclosed regions · 11 tangent turns</text>']
    for j, record in enumerate(records):
        cx, cy, scale = 305+590*j, 335, .43
        project = lambda p: f'{cx+scale*p.real:.5f},{cy-scale*p.imag:.5f}'
        svg.append(f'<rect x="{30+590*j}" y="130" width="550" height="440" rx="16" fill="#0b0e1a" stroke="#383b50"/>')
        svg.append(f'<path d="{path(samples(0, 2*pi, 4800, j), project)}" fill="none" stroke="{COLORS[j]}" stroke-width="1.3"/>')
        svg.append(f'<text x="{cx}" y="166" text-anchor="middle" font-size="23">11 / {6+2*j}</text>')
        svg.append(f'<text x="{cx}" y="543" text-anchor="middle" font-size="25">Strangeness  {record["strangeness"]}</text>')
    svg.extend(['<text x="40" y="616" font-size="23">Three branches pass through one another</text>',
                '<text x="40" y="650" font-size="18" fill="#c7c7d4">The first meeting, magnified at equal scales. Its local strangeness jump is −1.</text>'])
    event = events[0]
    for j, step in enumerate((-1, 0, 1)):
        cx, cy, scale = 210+390*j, 820, 62
        center = complex(*event['center'])
        project = lambda p: f'{cx+scale*(p-center).real:.5f},{cy-scale*(p-center).imag:.5f}'
        a, times = event['weight']+.003*step, event['times']
        svg.append(f'<defs><clipPath id="lens{j}"><rect x="{40+390*j}" y="685" width="340" height="285" rx="12"/></clipPath></defs>')
        svg.append(f'<rect x="{40+390*j}" y="685" width="340" height="285" rx="12" fill="#0b0e1a" stroke="#383b50"/>')
        svg.append(f'<g clip-path="url(#lens{j})">')
        if step:
            ab, bc, ac = [crossing(times, a, i, k) for i, k in ((0, 1), (1, 2), (0, 2))]
            points = (samples(ab[1], bc[0], 80, a)+samples(bc[1], ac[1], 80, a)+samples(ac[0], ab[0], 80, a))
            svg.append(f'<path d="{path(points, project, True)}" fill="#f4f1e8" fill-opacity=".2"/>')
        for t, color in zip(times, COLORS):
            svg.append(f'<path d="{path(samples(t-.014, t+.014, 160, a), project)}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        svg.append('</g>')
        svg.append(f'<text x="{cx}" y="1004" text-anchor="middle" font-size="20">{("Before", "Meeting (approx.)", "After")[j]}</text>')
    svg.extend(['<text x="40" y="1056" font-size="18" fill="#c7c7d4">Two reflected pairs of passages have individual jumps −1, totaling −4.</text>',
                '<text x="40" y="1092" font-size="15" fill="#9999ae">Exact endpoint integers and complete event counts in two short weight windows; rounded figure geometry.</text>',
                '</g></svg>'])
    (HERE/'weave.svg').write_text('\n'.join(svg)+'\n')


def generate():
    check_evaluation()
    records = [snapshot(a) for a in (0, 1)]
    require_counts = [(r['crossings'], r['tangent_index'], r['winding_regions']) for r in records]
    assert require_counts[0] == require_counts[1] == (40, 11, {1: 10, 2: 19, 3: 10, 4: 2})
    assert [r['strangeness'] for r in records] == [15, 11]
    events = []
    for i, hint in enumerate(HINTS):
        proofs, _ = certify_window(i)
        *times, weight = hint
        position = orbit(times[0], weight)
        events.append({'times': times, 'weight': weight,
                       'center': [position.real, position.imag], 'half_size': (2.2, 2.8)[i],
                       'window': [str(a) for a in WINDOWS[i]],
                       'weight_box': [str(x) for x in (proofs[0]['small']['box'][3].low,
                                                      proofs[0]['small']['box'][3].high)],
                       'jump_per_passage': -1})
    js = "'use strict';\n\n// Generated by weave_figure.py from fresh rational certificates.\n"
    js += '// Words and integers are exact; times, centers, and event weights only place drawings.\n'
    js += 'const WeaveData = '+json.dumps({'endpoints': records, 'events': events}, indent=2)+';\n\n'
    js += "if (typeof module !== 'undefined' && module.exports) module.exports = WeaveData;\n"
    (HERE/'weave_data.js').write_text(js)
    still(records, events)
    print('Wrote weave_data.js and weave.svg from fresh endpoint and event-window proofs.')


if __name__ == '__main__':
    generate()
