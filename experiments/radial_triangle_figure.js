'use strict';

// Rounded drawing of three selected arcs at delta=0. Exact area bounds
// are produced separately by radial_triangle.py, without sampled paths.
const fs = require('node:fs'), path = require('node:path');
const Model = require('./positive_front_math.js');
const record = require('./radial_triangle.json');
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
  if (floors[0] !== floors[1] || floors[0] < 0n) throw new Error('An area decimal prefix is not certified.');
  return `${floors[0] / scale}.${String(floors[0] % scale).padStart(places, '0')}…`;
}
const row = record.examples.find(r => r.offset === 25);
if (!row || record.scaled_area_limit !== '3375/2048' || record.uniform_area_tail?.positive_area_deficit_upper !== '5/M^3') {
  throw new Error('Regenerate the rational pocket-area record first.');
}
const outer = middle(row.outer), circle = middle(row.circle), polar = middle(row.polar);
const offset = row.offset, colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
const n = x => x.toFixed(4);
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;');
const text = (x, y, s, size = 20, color = '#c7c7d4', extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${esc(s)}</text>`;
function point(theta, which) {
  const model = Model.local([1, 2, 1], ['triangle', 0], theta, .5);
  const h = model.heights[which], p = model.slopes[which];
  return [2 * offset * Math.sin(theta / 2) ** 2 + h * Math.cos(theta) - p * Math.sin(theta),
    -offset * Math.sin(theta) + h * Math.sin(theta) + p * Math.cos(theta)];
}
function arc(start, end, which, samples = 600) {
  return Array.from({ length: samples + 1 }, (_, i) => point(start + (end - start) * i / samples, which));
}
const boundary = [...arc(circle, outer, 0), ...arc(-outer, -circle, 2), ...arc(polar, -polar, 1)];
const curves = [arc(0, .125, 0), arc(-.06, .06, 1), arc(-.125, 0, 2)];
const corners = [point(circle, 0), point(outer, 0), point(-circle, 2)];
const height = 2 * corners[0][1];
const line = (points, map, close = false) => points.map((p, i) => {
  const [x, y] = map(p);
  return `${i ? 'L' : 'M'}${n(x)},${n(y)}`;
}).join('') + (close ? 'Z' : '');
const parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="920" viewBox="0 0 1200 920" role="img" aria-labelledby="title description">',
  '<title id="title">How much triangle is left?</title>',
  `<desc id="description">At the front triple moment, parameter zero, the three selected offset-25 plane arcs still enclose a thin curved pocket. The left panel uses equal physical coordinate scales: its width is about 0.07002 units and its height about ${height.toFixed(5)}. The right panel shows the same pocket after stretching horizontal distances by exactly 25; vertical distances are unchanged. The original area is about 0.0656428042557 square drawing units. Multiplying the area by distance tends to 3375 over 2048. For every real M at least 25, the area is below 3375/(2048M) by a positive amount less than 5/M cubed. Exact arc integrals and a uniform polynomial certificate are separate from these rounded paths. This is an isolated three-arc model, with no assertion that the full movie has an empty face here.</desc>`,
  '<rect width="1200" height="920" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(35, 65, 'How much triangle is left?', 48, '#f4f1e8'),
  text(35, 110, 'At the front’s triple, δ = 0, the three plane arcs still enclose a little pocket.', 23),
  text(35, 149, 'Gold and lilac: outer arcs · blue: middle circle · offset M = 25', 19, '#9999ae')];

function panel(origin, stretch, title, subtitle, id) {
  const map = p => [origin + (stretch === 1 ? 345 : 75) + 200 * stretch * p[0], 470 - 200 * p[1]];
  parts.push(`<rect x="${origin + 25}" y="180" width="550" height="540" rx="14" fill="#0b0e1a" stroke="#383b50"/>`,
    text(origin + 47, 220, title, 28, '#f4f1e8'), text(origin + 47, 255, subtitle, 18),
    `<defs><clipPath id="${id}"><rect x="${origin + 45}" y="275" width="510" height="395"/></clipPath></defs>`,
    `<g clip-path="url(#${id})">`,
    `<path d="${line(boundary, map, true)}" fill="#f4f1e8" fill-opacity=".12" data-role="pocket"/>`);
  curves.forEach((points, which) => parts.push(`<path d="${line(points, map)}" fill="none" stroke="${colors[which]}" stroke-width="2.2" data-role="arc"/>`));
  corners.forEach(p => {
    const [x, y] = map(p);
    parts.push(`<circle cx="${n(x)}" cy="${n(y)}" r="4" fill="#0b0e1a" stroke="#f4f1e8" stroke-width="1.5" data-role="crossing"/>`);
  });
  parts.push('</g>', text(origin + 300, 690, stretch === 1 ? 'Equal horizontal and vertical scales' : 'Same pocket · horizontal distances ×25', 19, '#c7c7d4', 'text-anchor="middle"'));
  return map;
}
const physical = panel(0, 1, 'The physical pocket', 'A narrow sliver, at its true proportions.', 'physical');
panel(600, 25, 'Stretch the horizontal direction', 'Vertical distances keep their original scale.', 'stretched');
const target = physical([middle(row.parameter), 0]);
parts.push(`<path d="M125,446H265L${n(target[0] - 6)},${n(target[1])}" fill="none" stroke="#9999ae" stroke-width="1.2"/>`,
  text(65, 402, 'Width ≈ 0.07002', 21, '#f4f1e8'),
  text(65, 431, `Height ≈ ${height.toFixed(5)}`, 20),
  text(65, 492, 'Curved area', 19),
  text(65, 523, decimalPrefix(row.area), 22, '#e8b66e'),
  text(660, 758, `M × area ≈ ${middle(row.scaled_area).toFixed(11)}`, 22, '#e8b66e'),
  text(35, 758, 'The pocket shrinks as the offset grows.', 26, '#f4f1e8'),
  text(35, 805, 'In the stretched coordinates, its boundaries approach three parabolas.', 22),
  text(35, 845, 'Integrating between them gives:  M × area → 3375/2048 = 1.64794921875.', 23),
  '<a href="radial_limit.md#the-triangle-left-at-the-front-triple">',
  text(35, 891, 'Every M ≥ 25:  0 < 3375/(2048M) − area < 5/M³.  Exact proof ↗', 19, '#e8b66e'),
  '</a></g></svg>');
fs.writeFileSync(path.join(__dirname, 'radial_triangle.svg'), parts.join('\n') + '\n');
console.log('Wrote radial_triangle.svg: the physical pocket and an explicitly stretched view.');
