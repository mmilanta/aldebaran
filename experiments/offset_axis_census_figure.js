'use strict';

// Illustration of a fresh rational axis census. Rounded normal positions
// show the geometry; the archived rational signs determine the sign bars.
const fs = require('node:fs'), path = require('node:path');
const Data = require('./offset_axis_census.json'), Orbit = require('./weave_math.js');
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

function times(event) {
  const upper = event.cosine_box.map(middle).reverse().map(Math.acos);
  return [...upper, 2 * Math.PI - upper[1], 2 * Math.PI - upper[0]];
}

function normals(event) {
  return times(event).map(t => {
    const v = Orbit.orbit(t, (event.inner - 6) / 2, 1), speed = Math.hypot(...v);
    return [-v[1] / speed, v[0] / speed];
  });
}

function figure() {
  const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1370" viewBox="0 0 1200 1370" role="img" aria-labelledby="title description">',
    '<title id="title">Every mirror meeting</title>',
    '<desc id="description">A complete atlas of the higher mirror-axis meetings on the unperturbed outward offset families. Rhythms 11 / 6 have eleven fourfolds; 11 / 8 have nine. Each card shows the four unit left normals in visit colors and the four certified triple signs in order 123, 124, 134, 234. Twelve circles have four negative signs, seven have two of each, and one has four positive signs. The all-positive circle is at outward distance 284.56257 on 11 / 6. All circles use the same equal coordinate scales. There are no ordinary axis triples and no axis meetings with six or more visits. Off-axis events remain unclassified.</desc>',
    '<rect width="1200" height="1370" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
    text(30, 62, 'Every mirror meeting.', 46, ink, 'font-weight="650" letter-spacing="-1.4"'),
    text(30, 105, 'Seven eligible arcs per drawing. Twenty circles where four visits come together.', 23),
    '<path d="M600,145V1145" stroke="#383b50"/>'];
  for (const [column, endpoint] of Data.endpoints.entries()) {
    const left = 30 + 600 * column;
    svg.push(text(left, 161, `11 / ${endpoint.inner}`, 31, ink),
      text(left + 150, 159, `${endpoint.events.length} fourfolds · all outward distances covered`, 18));
    endpoint.events.forEach((event, index) => {
      const x = left + 184 * (index % 3), y = 190 + 232 * Math.floor(index / 3);
      const cx = x + 85, cy = y + 65, radius = 43;
      const points = normals(event).map(n => [cx + radius * n[0], cy - radius * n[1]]);
      svg.push(`<g data-inner="${endpoint.inner}" data-event="${index}">`,
        `<rect x="${x}" y="${y}" width="170" height="218" rx="11" fill="#0b0e1a" stroke="#383b50"/>`,
        text(x + 12, y + 22, String(index + 1).padStart(2, '0'), 12, '#9999ae'),
        `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none" stroke="#737b99" stroke-width="1.3"/>`,
        `<path d="M${cx - radius - 7},${cy}H${cx + radius + 7}" stroke="#383b50" stroke-dasharray="2 5"/>`);
      points.forEach((p, i) => {
        const next = points[(i + 1) % 4];
        svg.push(`<path d="M${number(p[0])},${number(p[1])}L${number(next[0])},${number(next[1])}" stroke="${colors[i]}" stroke-opacity=".5" stroke-width="1.5"/>`);
      });
      points.forEach((p, i) => svg.push(`<circle cx="${number(p[0])}" cy="${number(p[1])}" r="3.2" fill="${colors[i]}"/>`));
      const offset = middle(event.offset).toFixed(5), center = middle(event.axis_center).toFixed(5).replace('-', '−');
      svg.push(text(cx, y + 132, `M ${offset}`, 18, ink, 'text-anchor="middle"'),
        text(cx, y + 156, `X ${center}`, 15, muted, 'text-anchor="middle"'));
      event.triples.forEach((triple, i) => {
        const positive = triple.strangeness_jump > 0, bx = x + 20 + 34 * i;
        svg.push(`<rect x="${bx}" y="${y + 173}" width="28" height="27" rx="4" fill="${positive ? gold : blue}"/>`,
          text(bx + 14, y + 192, positive ? '+' : '−', 21, '#101323', 'text-anchor="middle" font-weight="700"'));
      });
      svg.push('</g>');
    });
    svg.push(text(left, 1168, `${endpoint.positive_triples} positive · ${endpoint.negative_triples} negative`, 26, ink),
      text(left, 1202, `${endpoint.events.length * 4} local triples after small symmetry-breaking shifts`, 18));
  }
  svg.push('<rect x="630" y="886" width="538" height="218" rx="11" fill="#141829" stroke="#383b50"/>',
    text(650, 921, 'One sign comes from three directions.', 23, ink),
    text(650, 956, 'Read each triple of normals in orbit order.', 19),
    text(650, 987, 'Clockwise gives +1; counterclockwise gives −1.', 19),
    text(650, 1025, 'The four sign bars follow 123 · 124 · 134 · 234.', 18),
    text(650, 1060, 'Close marks may overlap. Signs use exact certificates.', 17),
    '<path d="M30,1231H1170" stroke="#383b50"/>',
    text(30, 1268, 'UNIT LEFT NORMALS', 13, muted, 'letter-spacing="1.5"'));
  colors.forEach((color, i) => svg.push(`<circle cx="${270 + 83 * i}" cy="1262" r="4" fill="${color}"/>`,
    text(283 + 83 * i, 1268, String(i + 1), 18, color)));
  svg.push(text(650, 1268, 'M = outward distance · X = center on the mirror axis', 18),
    text(30, 1306, 'Every circle uses equal coordinate scales. The sign counts refer to local generic resolutions of the fourfolds.', 19),
    text(30, 1340, 'Axis census for M ≥ 0. The later whole-leg census also closes the off-axis question.', 18),
    '</g></svg>');
  return svg.join('\n') + '\n';
}

if (require.main === module) {
  fs.writeFileSync(path.join(__dirname, 'offset_axis_census.svg'), figure());
  console.log('Wrote offset_axis_census.svg from the complete rational axis census.');
}
module.exports = { figure, times, normals };
