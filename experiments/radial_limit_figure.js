'use strict';

// Rounded illustrations of the analytic radial limit and the separately
// certified local time shift. The SVG does not supply proof decisions.
const fs = require('node:fs'), path = require('node:path');
const Model = require('./positive_front_math.js');
const record = require('./radial_limit.json');
const rational = s => {
  const [a, b = '1'] = s.split('/');
  return Number(a) / Number(b);
};
const middle = box => (rational(box[0]) + rational(box[1])) / 2;
function decimalPrefix(box, places = 11) {
  const scale = 10n ** BigInt(places);
  const floors = box.map(s => {
    const [a, b = '1'] = s.split('/');
    return BigInt(a) * scale / BigInt(b);
  });
  if (floors[0] !== floors[1] || floors[0] < 0n) throw new Error('A displayed decimal prefix is not certified.');
  return `${floors[0] / scale}.${String(floors[0] % scale).padStart(places, '0')}…`;
}
const local = record.examples.find(row => row.offset === 25);
if (!local || record.uniform_local_drift.positive_fifth_order_remainder_upper !== '40') {
  throw new Error('Regenerate the rational radial-limit record first.');
}
const delta = middle(local.parameter), colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
const first = rational(record.uniform_local_drift.first_coefficient);
const third = rational(record.uniform_local_drift.third_coefficient);
const n = x => x.toFixed(4);
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const text = (x, y, content, size = 20, color = '#c7c7d4', attributes = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${attributes}>${esc(content)}</text>`;
const route = x => Model.local([1, 2, 1], ['triangle', 0], x, .5);
function jet(theta, d, which) {
  const model = Model.local([1, 2, 1], ['triangle', 0], theta, .5 + 2 * d);
  return [model.heights[which], model.slopes[which]];
}
function deficit(alpha, d, which, offset = 25) {
  let lo = -1, hi = 1;
  for (let i = 0; i < 48; i++) {
    const theta = (lo + hi) / 2, [h, p] = jet(theta, d, which);
    if (theta - Math.atan2(p, offset - h) < alpha) lo = theta;
    else hi = theta;
  }
  const [h, p] = jet((lo + hi) / 2, d, which), u = offset - h;
  return h - p * p / (Math.hypot(u, p) + u);
}
function triple(offset) {
  let lo = 0, hi = .125;
  for (let i = 0; i < 50; i++) {
    const x = (lo + hi) / 2, model = route(x);
    const value = (model.heights[0] - offset) * Math.sin(x) + model.slopes[0] * Math.cos(x);
    if (value > 0) lo = x;
    else hi = x;
  }
  const x = (lo + hi) / 2, model = route(x);
  return model.heights[0] - model.slopes[0] * Math.tan(x / 2);
}
if (Math.abs(triple(25) - delta) > 1e-14) throw new Error('The illustrative local root misses its rational bracket.');
function line(points, close = false) {
  return points.map(([x, y], i) => `${i ? 'L' : 'M'}${n(x)},${n(y)}`).join('') + (close ? 'Z' : '');
}
const parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1120" viewBox="0 0 1200 1120" role="img" aria-labelledby="title description">',
  '<title id="title">The clock moves when the curve moves out</title>',
  '<desc id="description">Two graphs compare the same polar-angle coordinates at offset 25. Dashed curves are tangent-line heights; solid curves are radial deficits of the plane drawing. At the front triple, parameter zero, the solid curves form a triangle. They meet together later, at parameter about 0.07001970943. The three plane visits then have different normal angles, about 0.074448, zero, and minus 0.074448 radians. A lower graph shows distance times the triple parameter approaching 225 over 128. A narrow shaded band encloses the exact local value between a cubic approximation and that approximation plus 40 over distance to the fifth power, for every distance at least 25. Graph axes use different units. Rounded paths illustrate separate rational proofs; no whole-movie offset threshold is claimed.</desc>',
  '<rect width="1200" height="1120" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(35, 65, 'The clock moves when the curve moves out.', 44, '#f4f1e8'),
  text(35, 109, 'Compare the two pictures at the same polar angle. Their meetings happen at different times.', 21),
  '<path d="M36,143H72" stroke="#f4f1e8" stroke-width="2" stroke-dasharray="6 5"/>',
  text(83, 150, 'Tangent-line height h', 18),
  '<path d="M342,143H378" stroke="#f4f1e8" stroke-width="2.5"/>',
  text(389, 150, 'Plane radial deficit D = M − radius', 18),
  text(1165, 150, 'Local model · M = 25', 18, '#9999ae', 'text-anchor="end"')];

function panel(origin, d, title, subtitle, id) {
  const x = a => origin + 280 + a * 1600, y = h => 465 - h * 500;
  parts.push(`<rect x="${origin + 25}" y="176" width="550" height="480" rx="14" fill="#0b0e1a" stroke="#383b50"/>`,
    text(origin + 47, 215, title, 25, '#f4f1e8'), text(origin + 47, 248, subtitle, 18),
    `<defs><clipPath id="${id}"><rect x="${origin + 55}" y="270" width="490" height="310"/></clipPath></defs>`,
    `<path d="M${origin + 55},${y(0)}H${origin + 545}M${x(0)},270V580" fill="none" stroke="#42485f" stroke-dasharray="4 5"/>`,
    `<g clip-path="url(#${id})">`);
  for (let which = 0; which < 3; which++) {
    const dashed = [], solid = [];
    for (let i = 0; i <= 450; i++) {
      const alpha = -.16 + i * .32 / 450;
      dashed.push([x(alpha), y(jet(alpha, d, which)[0])]);
      solid.push([x(alpha), y(deficit(alpha, d, which))]);
    }
    parts.push(`<path d="${line(dashed)}" fill="none" stroke="${colors[which]}" stroke-width="1.5" stroke-opacity=".6" stroke-dasharray="6 5" data-role="front"/>`,
      `<path d="${line(solid)}" fill="none" stroke="${colors[which]}" stroke-width="2.5" data-role="deficit"/>`);
  }
  parts.push('</g>',
    `<circle cx="${x(0)}" cy="${y(d === 0 ? 0 : delta)}" r="6" fill="#0b0e1a" stroke="#f4f1e8" stroke-width="2" data-role="meeting"/>`,
    text(origin + 47, 290, 'Height', 16, '#9999ae'),
    text(x(-.1), 606, '−0.1', 16, '#9999ae', 'text-anchor="middle"'),
    text(x(0), 606, '0', 16, '#9999ae', 'text-anchor="middle"'),
    text(x(.1), 606, '+0.1', 16, '#9999ae', 'text-anchor="middle"'),
    text(x(0), 637, 'Polar angle α · radians', 18, '#c7c7d4', 'text-anchor="middle"'));
}
panel(0, 0, 'At the front’s triple', 'δ = 0 · the plane still has a small triangle', 'before');
panel(600, delta, 'At the plane’s triple', 'δ ≈ 0.07001970943 · three solid curves meet', 'after');
parts.push(text(35, 694, 'One polar direction, three normal directions:  +0.074448…    0    −0.074448… radians.', 21),
  text(35, 735, 'Multiply the meeting time by the distance.', 30, '#f4f1e8'),
  text(35, 771, 'Mδ approaches 225/128. The blue band is an exact bound; the gold path is numerical.', 19));

const x = inverse => 95 + inverse * 15500;
const y = scaled => 990 - (scaled - 1.749) * 16500;
parts.push('<rect x="25" y="793" width="735" height="232" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
  `<path d="M95,${y(first)}H715M95,813V990H715" fill="none" stroke="#737b99" stroke-width="1"/>`,
  text(109, y(first) - 10, '225/128', 16, '#c7c7d4'));
const lower = [], upper = [], actual = [];
for (let i = 0; i <= 400; i++) {
  const inverse = .04 * i / 400;
  const corrected = first + third * inverse * inverse;
  lower.push([x(inverse), y(corrected)]);
  upper.push([x(inverse), y(corrected + 40 * inverse ** 4)]);
  actual.push([x(inverse), y(i ? triple(1 / inverse) / inverse : first)]);
}
parts.push(`<path d="${line([...lower, ...upper.reverse()], true)}" fill="#9fc7eb" fill-opacity=".45" data-role="bound-band"/>`,
  `<path d="${line(lower)}" fill="none" stroke="#9fc7eb" stroke-width="1.2"/>`,
  `<path d="${line(actual)}" fill="none" stroke="#e8b66e" stroke-width="2.2" data-role="clock"/>`);
for (const [inverse, label] of [[0, '∞'], [.01, '100'], [.02, '50'], [.04, '25']]) {
  const v = inverse ? triple(1 / inverse) / inverse : first;
  parts.push(`<circle cx="${n(x(inverse))}" cy="${n(y(v))}" r="3.5" fill="#e8b66e"/>`,
    text(x(inverse), 1013, label, 16, '#c7c7d4', 'text-anchor="middle"'));
}
parts.push(text(376, 1050, 'Distance M · horizontal position is 1/M', 17, '#9999ae', 'text-anchor="middle"'),
  text(795, 822, 'CERTIFIED LOCAL TIMES', 17, '#9999ae', 'letter-spacing="1.2"'));
record.examples.forEach((row, i) => {
  parts.push(text(795, 863 + i * 38, `M = ${row.offset.toLocaleString('en-US')}`, 18),
    text(1160, 863 + i * 38, decimalPrefix(row.parameter), 19, '#e8b66e', 'text-anchor="end"'));
});
parts.push('<a href="radial_limit.md">',
  text(35, 1091, 'Every M ≥ 25:  δ = 225/(128M) − 151875/(32768M³) + R,  with 0 < R < 40/M⁵.  Proof ↗', 19),
  '</a></g></svg>');
fs.writeFileSync(path.join(__dirname, 'radial_limit.svg'), parts.join('\n') + '\n');
console.log('Wrote radial_limit.svg: same-angle graphs, shifted local triple, and a certified inverse-distance clock band.');
