'use strict';

// Two selected certified fourfolds and their first-order local resolutions.
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const Orbit = require('./weave_math.js'), Data = require('./offset_fourfold.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = pair => pair.map(rational).reduce((a, b) => a + b) / 2;
const number = x => String(Math.round(x * 10000) / 10000);
const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea', '#a7d9bb'];
const text = (x, y, content, size = 18, color = '#c7c7d4', extra = '') =>
  `<text x="${number(x)}" y="${number(y)}" font-size="${size}" fill="${color}" ${extra}>${content}</text>`;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1160" viewBox="0 0 1200 1160" role="img" aria-labelledby="title description">',
  '<title id="title">Four visits, two cancelling pairs</title>',
  '<desc id="description">Two selected outward-offset fourfold meetings, one on 11 / 6 at distance about 57.58865 and one on 11 / 8 at about 110.66889. Four original visits touch a circle centered on the mirror axis. Offsetting by its radius brings all four to one point. Small local normal shifts with coefficients zero, one, three, and seven separate four ordinary triple events, two positive and two negative, at the distinct first-order weights shown on the right. Whole-orbit rational covers exclude a fifth branch. Pictures and horizontal positions are numerical illustrations of separate rational certificates, not a census of the full offset families.</desc>',
  '<rect width="1200" height="1160" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(30, 61, 'Four visits, two cancelling pairs.', 43, '#f4f1e8', 'font-weight="650" letter-spacing="-1.5"'),
  text(30, 103, 'A small break of the mirror separates four triple passages. Their signed changes cancel.', 21)];
for (const [row, event] of Data.events.entries()) {
  const top = 135 + 470 * row, center = event.point.map(middle), radius = middle(event.offset);
  const times = event.center.map((s, i) => event.quarters[i] * Math.PI / 2 + 2 * Math.atan(rational(s)));
  const project = p => [265 + 160 * (p[0] - center[0]) / radius, top + 234 - 160 * p[1] / radius];
  const d = points => points.map((p, i) => `${i ? 'L' : 'M'}${project(p).map(number).join(',')}`).join('');
  svg.push(`<rect x="20" y="${top}" width="1160" height="444" rx="14" fill="#0b0e1a" stroke="#383b50"/>`,
    text(42, top + 38, `Rhythms 11 / ${event.inner} · radius ${radius.toFixed(5)}`, 23, '#f4f1e8'),
    `<circle cx="265" cy="${top + 234}" r="160" fill="none" stroke="#737b99" stroke-dasharray="5 7"/>`,
    `<path d="M60,${top + 234}H465" stroke="#383b50" stroke-dasharray="3 7"/>`);
  times.forEach((t, i) => {
    const point = Orbit.orbit(t, (event.inner - 6) / 2), [x, y] = project(point);
    const arc = Array.from({ length: 101 }, (_, k) => Orbit.orbit(t + .012 * (k - 50) / 50, (event.inner - 6) / 2));
    svg.push(`<path d="${d(arc)}" fill="none" stroke="${colors[i]}" stroke-width="3"/>`,
      `<path d="M265,${top + 234}L${number(x)},${number(y)}" fill="none" stroke="${colors[i]}" stroke-width="1.2" stroke-dasharray="3 5"/>`,
      `<circle cx="${number(x)}" cy="${number(y)}" r="4.5" fill="#0b0e1a" stroke="${colors[i]}" stroke-width="2"/>`);
    const direction = [point[0] - center[0], point[1]], length = Math.hypot(...direction);
    if (Math.abs(point[1]) < .08 * radius && (i === 0 || i === 3)) {
      const labelY = y + (i === 0 ? 31 : -20);
      svg.push(`<path d="M${number(x + 5)},${number(y)}L${number(x + 19)},${number(labelY - 7)}" fill="none" stroke="${colors[i]}" stroke-width="1"/>`,
        text(x + 28, labelY, String(i + 1), 19, colors[i], 'text-anchor="middle"'));
    } else {
      svg.push(text(x + 18 * direction[0] / length, y - 18 * direction[1] / length + 6,
        String(i + 1), 19, colors[i], 'text-anchor="middle"'));
    }
  });
  svg.push(`<circle cx="265" cy="${top + 234}" r="3" fill="#f4f1e8"/>`,
    text(42, top + 422, 'Four original visits · equal coordinate scales', 17));
  const weights = event.triples.map(t => middle(t.first_order_weight));
  const low = Math.min(...weights), high = Math.max(...weights), margin = .12 * (high - low);
  const x = value => 750 + 360 * (value - low + margin) / (high - low + 2 * margin);
  svg.push(text(560, top + 87, 'After normal shifts 0, 1, 3, 7', 23, '#f4f1e8'),
    text(560, top + 121, 'Horizontal position: d in M = M* + εd + O(ε²)', 17));
  event.perturbed_order.forEach((i, lane) => {
    const triple = event.triples[i];
    const positive = triple.strangeness_jump > 0, y = top + 171 + 52 * lane, color = positive ? '#e8b66e' : '#9fc7eb';
    svg.push(`<path d="M750,${y}H1110" stroke="#383b50" fill="none"/>`,
      `<circle cx="${number(x(weights[i]))}" cy="${y}" r="6" fill="${color}"/>`,
      text(560, y + 6, triple.visits.map(v => v + 1).join(' · ') + `   ${positive ? '+1' : '−1'}`, 19, color),
      text(x(weights[i]), y + 23, weights[i].toFixed(2), 15, '#c7c7d4', 'text-anchor="middle"'));
  });
  assert.deepEqual(event.triples.map(t => t.strangeness_jump).sort(), [-1, -1, 1, 1]);
  svg.push(text(560, top + 389, 'Two positive and two negative triples · net change zero', 18, '#f4f1e8'),
    text(560, top + 420, 'Each row names three visits and their strangeness jump.', 16));
}
svg.push(text(30, 1110, 'Selected higher meetings strengthen the outward lower bounds to 106 and 116 triple passages.', 21, '#f4f1e8'),
  text(30, 1143, 'These selected circles give a lower bound. The later whole-leg census counts exactly 992 on this distant route.', 18), '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'offset_fourfold.svg'), svg.join('\n') + '\n');
console.log('Wrote offset_fourfold.svg from two selected rational fourfold certificates.');
