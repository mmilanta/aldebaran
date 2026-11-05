'use strict';

// A drawing of the last certified 11 / 6 reflected triple, using rounded
// coordinates. The separate rational census decides completeness.
const fs = require('node:fs'), path = require('node:path');
const Census = require('./offset_leg_census.json'), Orbit = require('./weave_math.js');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = b => (rational(b[0]) + rational(b[1])) / 2;
const endpoint = Census.endpoints.find(e => e.inner === 6);
const event = endpoint.roots.filter(r => middle(r.point[1]) > 0)
  .sort((a, b) => middle(b.offset) - middle(a.offset))[0];
if (!event || event.strangeness_jump !== -1 || event.axis_event !== undefined) throw new Error('The final negative off-axis circle is missing.');
const radius = middle(event.offset), center = event.point.map(middle);
if (Math.abs(radius - 16172.76506281) > 1e-6 || endpoint.no_higher_meeting_from !== '16173') {
  throw new Error('The printed final-circle distance or tail bound needs updating.');
}
const times = event.root_box.map((b, i) => event.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(b)));
const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
const number = x => x.toFixed(4);
const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;');
const text = (x, y, s, size = 20, color = '#c7c7d4', extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${escape(s)}</text>`;
const mainScale = .55;
const main = p => [385 + mainScale * p[0], 430 - mainScale * p[1]];
const smallScale = 165 / radius;
const small = p => [980 + smallScale * (p[0] - center[0]), 430 - smallScale * (p[1] - center[1])];
function curve(map, start = 0, end = 2 * Math.PI, count = 4800) {
  return Array.from({ length: count + 1 }, (_, i) => {
    const p = map(Orbit.orbit(start + (end - start) * i / count, 0));
    return `${i ? 'L' : 'M'}${number(p[0])},${number(p[1])}`;
  }).join('');
}
const parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850" role="img" aria-labelledby="title description">',
  '<title id="title">The last circle is almost a line</title>',
  '<desc id="description">The final higher meeting on the whole 11 / 6 outward leg is a negative reflected pair at distance about 16172.76506. This drawing shows the member above the mirror axis. On the left, three colored visits of the original curve touch a very large circle, whose visible arc looks almost straight. Short dashed arrows point toward the distant center. On the right, the complete same circle makes the entire original drawing look tiny near its lower edge. Both views use equal horizontal and vertical scales, at different magnifications. The complete census proves no higher meeting at any distance at least 16173.</desc>',
  '<rect width="1200" height="850" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(35, 65, 'The last circle is almost a line.', 43, '#f4f1e8'),
  text(35, 108, 'The final reflected pair on 11 / 6 occurs at M ≈ 16,172.76506.', 22),
  '<rect x="25" y="146" width="737" height="596" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
  '<defs><clipPath id="original-clip"><rect x="26" y="147" width="735" height="594" rx="13"/></clipPath></defs>',
  text(47, 183, 'THE ORIGINAL DRAWING', 16, '#9999ae', 'letter-spacing="1.2"'),
  '<g clip-path="url(#original-clip)">',
  `<path d="${curve(main)}" fill="none" stroke="#69748d" stroke-width="1.15"/>`];
const pc = main(center);
parts.push(`<circle cx="${number(pc[0])}" cy="${number(pc[1])}" r="${number(mainScale * radius)}" fill="none" stroke="#f4f1e8" stroke-width="1.5" stroke-dasharray="8 6"/>`);
times.forEach((t, i) => {
  const original = Orbit.orbit(t, 0), p = main(original), v = Orbit.orbit(t, 0, 1);
  const speed = Math.hypot(...v), outward = [v[1] / speed, -v[0] / speed];
  const endpoint = main(original.map((x, j) => x + 72 * outward[j]));
  const dx = endpoint[0] - p[0], dy = endpoint[1] - p[1], length = Math.hypot(dx, dy), unit = [dx / length, dy / length];
  parts.push(`<path d="${curve(main, t - .021, t + .021, 100)}" fill="none" stroke="${colors[i]}" stroke-width="3"/>`,
    `<path d="M${number(p[0])},${number(p[1])}L${number(endpoint[0])},${number(endpoint[1])}" stroke="${colors[i]}" stroke-width="1.3" stroke-dasharray="4 4"/>`,
    `<path d="M${number(endpoint[0] - 8 * unit[0] - 4 * unit[1])},${number(endpoint[1] - 8 * unit[1] + 4 * unit[0])}L${number(endpoint[0])},${number(endpoint[1])}L${number(endpoint[0] - 8 * unit[0] + 4 * unit[1])},${number(endpoint[1] - 8 * unit[1] - 4 * unit[0])}" fill="none" stroke="${colors[i]}" stroke-width="1.6"/>`,
    `<circle cx="${number(p[0])}" cy="${number(p[1])}" r="4.5" fill="#0b0e1a" stroke="${colors[i]}" stroke-width="2"/>`,
    text(p[0] + 13, p[1] + 20, String(i + 1), 21, colors[i]));
});
parts.push('</g>',
  text(47, 704, 'The three marked visits touch this circle tangentially.', 19),
  text(798, 183, 'THE WHOLE CIRCLE', 16, '#9999ae', 'letter-spacing="1.2"'),
  '<circle cx="980" cy="430" r="165" fill="none" stroke="#f4f1e8" stroke-width="1.5"/>',
  '<circle cx="980" cy="430" r="3.5" fill="#f4f1e8"/>',
  text(980, 407, 'Center', 18, '#f4f1e8', 'text-anchor="middle"'),
  `<path d="${curve(small)}" fill="none" stroke="#e8b66e" stroke-width=".8"/>`);
const target = small([0, 0]);
parts.push(`<path d="M980,430L${number(target[0])},${number(target[1])}" stroke="#9999ae" stroke-width="1" stroke-dasharray="4 5"/>`,
  `<path d="M815,641H890L${number(target[0] - 9)},${number(target[1] + 5)}" fill="none" stroke="#e8b66e" stroke-width="1.2"/>`,
  text(800, 674, 'The entire original drawing', 19, '#e8b66e'),
  text(800, 710, 'Circle diameter ≈ 32,345.53 units', 18),
  text(35, 785, 'Dashed arrows on the left point toward the distant center. Moving one full radius brings all three visits there.', 20),
  text(35, 822, 'Equal horizontal and vertical scales within each view · different magnifications · no higher meeting for M ≥ 16,173', 18, '#9999ae'),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'offset_last_circle.svg'), parts.join('\n') + '\n');
console.log('Wrote offset_last_circle.svg from the final certified 11 / 6 circle.');
