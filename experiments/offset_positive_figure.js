'use strict';

// A numerical illustration of the selected rational certificates. The right
// panel is a first-order resolution, not a finite-epsilon event certificate.
const fs = require('node:fs'), path = require('node:path');
const Data = require('./offset_positive.json'), Orbit = require('./weave_math.js');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
const number = x => {
  if (!Number.isFinite(x)) throw new RangeError('A figure coordinate must be finite.');
  return String(Math.round(x * 10000) / 10000);
};
const ink = '#f4f1e8', muted = '#c7c7d4', gold = '#e8b66e', blue = '#9fc7eb';
const colors = [gold, blue, '#d1b6ea', '#a7d9bb'];
const text = (x, y, content, size = 20, color = muted, extra = '') =>
  `<text x="${number(x)}" y="${number(y)}" font-size="${size}" fill="${color}" ${extra}>${content}</text>`;
const panel = (x, y, w, h) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="#0b0e1a" stroke="#383b50"/>`;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1290" viewBox="0 0 1200 1290" role="img" aria-labelledby="title description">',
  '<title id="title">Positive steps on an outward journey</title>',
  '<desc id="description">One selected fourfold on rhythms 11 / 6, near outward distance 284.56257, separates into four positive triple passages after small local normal shifts. The circle and original arcs use equal coordinate scales. The first-order event weights on the right are all distinct. Further selected certificates force at least eighteen positive passages on the 11 / 6 outward leg and ten on 11 / 8. Their net strangeness changes of minus 102 and minus 112 therefore require at least 120 and 122 negative passages. Adding the distant middle and reversing the second leg gives at least 992 triples, 494 positive and 498 negative. This is a lower bound for one sufficiently distant construction, not an exact count or a minimum over all routes. No numerical common-offset threshold is supplied.</desc>',
  '<rect width="1200" height="1290" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(30, 62, 'Positive steps on an outward journey.', 43, ink, 'font-weight="650" letter-spacing="-1.4"'),
  text(30, 103, 'A few passages raise the count. Other passages must bring it back down.', 23),
  panel(20, 135, 1160, 455)];

const event = Data.endpoints[0].fourfolds.find(e => e.triples.every(t => t.strangeness_jump === 1));
if (!event) throw new Error('The all-positive fourfold certificate is missing.');
const center = event.point.map(middle), radius = middle(event.offset);
const project = p => [272 + 157 * (p[0] - center[0]) / radius, 372 - 157 * p[1] / radius];
const d = points => points.map((p, i) => `${i ? 'L' : 'M'}${project(p).map(number).join(',')}`).join('');
svg.push(text(42, 177, 'One circle, four positive passages', 25, ink),
  text(42, 209, `Rhythms 11 / 6 · outward distance ${radius.toFixed(5)}`, 18),
  '<circle cx="272" cy="372" r="157" fill="none" stroke="#737b99" stroke-dasharray="5 7"/>',
  '<path d="M70,372H475" stroke="#383b50" stroke-dasharray="3 7"/>');
event.root_box.forEach((bounds, i) => {
  const t = event.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(bounds));
  const point = Orbit.orbit(t, 0), [x, y] = project(point);
  const arc = Array.from({ length: 121 }, (_, k) => Orbit.orbit(t + .035 * (k - 60) / 60, 0));
  const v = Orbit.orbit(t, 0, 1), speed = Math.hypot(...v), tangent = [v[0] / speed, -v[1] / speed];
  const tip = [x + 17 * tangent[0], y + 17 * tangent[1]];
  svg.push(`<path d="M272,372L${number(x)},${number(y)}" stroke="${colors[i]}" stroke-width="1" stroke-dasharray="3 5"/>`,
    `<path d="${d(arc)}" fill="none" stroke="${colors[i]}" stroke-width="3"/>`,
    `<circle cx="${number(x)}" cy="${number(y)}" r="4.5" fill="#0b0e1a" stroke="${colors[i]}" stroke-width="2"/>`,
    `<path d="M${number(tip[0] - 8 * tangent[0] + 4 * tangent[1])},${number(tip[1] - 8 * tangent[1] - 4 * tangent[0])}L${number(tip[0])},${number(tip[1])}L${number(tip[0] - 8 * tangent[0] - 4 * tangent[1])},${number(tip[1] - 8 * tangent[1] + 4 * tangent[0])}" fill="none" stroke="${colors[i]}" stroke-width="2"/>`);
  const away = [x - 272, y - 372], length = Math.hypot(...away);
  svg.push(text(x + 24 * away[0] / length, y + 24 * away[1] / length + 6,
    String(i + 1), 20, colors[i], 'text-anchor="middle"'));
});
svg.push('<circle cx="272" cy="372" r="3" fill="#f4f1e8"/>',
  text(42, 565, 'Original arcs · arrows follow travel · equal scales', 17),
  text(550, 209, 'After normal shifts 0, 1, 3, 7', 24, ink),
  text(550, 244, 'First-order model: M = M* + εd + O(ε²)', 18));
const px = weight => 770 + 320 * (weight + 100) / 160;
for (let lane = 0; lane < event.perturbed_order.length; lane++) {
  const triple = event.triples[event.perturbed_order[lane]], weight = middle(triple.first_order_weight);
  const y = 301 + 57 * lane;
  svg.push(`<path d="M770,${y}H1090" stroke="#383b50"/>`,
    `<circle cx="${number(px(weight))}" cy="${y}" r="6" fill="${gold}"/>`,
    text(550, y + 6, triple.visits.map(i => i + 1).join(' · ') + '    +1', 21, gold),
    text(px(weight), y + 25, weight.toFixed(2), 16, muted, 'text-anchor="middle"'));
}
svg.push(text(550, 535, 'Four different event weights · net St change +4', 20, ink),
  text(550, 566, 'Each row selects three of the four visits.', 17),
  panel(20, 610, 1160, 290),
  text(42, 651, 'What the selected local certificates force', 27, ink),
  text(42, 684, 'Eight fourfolds and five reflected ordinary pairs supply these positive passages.', 19));
for (const [i, endpoint] of Data.endpoints.entries()) {
  const y = 742 + 101 * i;
  const mixed = endpoint.fourfolds.filter(e => e.triples.filter(t => t.strangeness_jump > 0).length === 2).length;
  const allPositive = endpoint.fourfolds.length - mixed;
  svg.push(text(42, y, `11 / ${endpoint.inner}`, 28, ink),
    text(174, y, `≥ ${endpoint.positive_lower_bound} positive`, 25, gold),
    text(425, y, `≥ ${endpoint.negative_lower_bound} negative`, 25, blue),
    text(717, y, `net ${endpoint.inner === 6 ? '−102' : '−112'}`, 25, ink),
    text(963, y, `≥ ${endpoint.triple_lower_bound} triples`, 25, ink),
    text(174, y + 32, `${mixed} mixed fourfolds × 2${allPositive ? ' + one fourfold × 4' : ''} + ${endpoint.ordinary_triples.length / 2} reflected pairs × 2`, 18));
}
svg.push(panel(20, 920, 1160, 245),
  text(42, 962, 'Outward, across the middle, then home', 27, ink),
  text(42, 996, 'The second outward leg is reversed on the way home: its passage signs reverse too.', 19));
const stages = [
  { x: 42, label: 'OUTWARD 11 / 6', plus: '≥ 18', minus: '≥ 120' },
  { x: 356, label: 'DISTANT MIDDLE', plus: '354', minus: '368' },
  { x: 666, label: 'HOME TO 11 / 8', plus: '≥ 122', minus: '≥ 10' },
];
stages.forEach(stage => svg.push(text(stage.x, 1040, stage.label, 16),
  text(stage.x, 1080, stage.plus + ' positive', 25, gold), text(stage.x, 1120, stage.minus + ' negative', 25, blue)));
svg.push(text(985, 1039, 'TOTAL', 16),
  text(985, 1085, '≥ 992', 43, ink, 'font-weight="650"'),
  text(985, 1120, '≥494+ / ≥498−', 18),
  text(30, 1210, 'A lower bound for the sufficiently distant constructed route. The net signed change remains −4.', 21, ink),
  text(30, 1246, 'The later whole-leg census proves this bound is exact. No numerical middle-event threshold is supplied.', 18),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'offset_positive.svg'), svg.join('\n') + '\n');
console.log('Wrote offset_positive.svg from selected local certificates and separate radial-word inputs.');
