'use strict';

// An illustration of certified words, not a new numerical extraction.
// Generate the record first: python3 experiments/normal_front_braid.py --write
// Then run: node experiments/normal_front_braid_figure.js
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const data = require('./normal_front_braid.json');
const blue = '#9fc7eb', gold = '#e8b66e', ink = '#f4f1e8', background = '#0b0e1a';
assert.equal(data.strands, 11);
assert.equal(data.conjugator.length, 195);
assert.deepEqual(data.endpoints.map(record => record.inner), [6, 8]);
assert.deepEqual(data.endpoints[0].alexander_coefficients, data.endpoints[1].alexander_coefficients);
const number = x => String(Math.round(x * 100) / 100);
const text = (x, y, value, size = 18, color = '#c7c7d4', extra = '') =>
  `<text x="${number(x)}" y="${number(y)}" font-size="${size}" fill="${color}" ${extra}>${value}</text>`;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1570" viewBox="0 0 1200 1570" role="img" aria-labelledby="title description">',
  '<title id="title">Two braid words, one knot</title>',
  '<desc id="description">Two positive eleven-strand braids, each with 106 crossings, read from the conormal fronts of rhythms 11 / 6 and 11 / 8. Gold follows one strand through each cut diagram. Join each bottom position to the top at that same position. An explicit conjugator proves that their ordinary closures are the same knot. Their complete degree-96 Alexander polynomials agree and have determinant 189. These diagrams show braid order, not geometric scale. No plane-curve homotopy is drawn.</desc>',
  '<rect width="1200" height="1570" fill="#101323"/>',
  '<g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(30, 58, 'Two braid words, one knot.', 40, ink, 'font-weight="650" letter-spacing="-1.5"'),
  text(30, 99, 'Eleven strands · 106 positive crossings each · one knot per closure', 21)];

for (const [column, record] of data.endpoints.entries()) {
  assert.equal(record.word.length, 106);
  assert.deepEqual([...record.initial].sort((a, b) => a - b), [...Array(11).keys()]);
  const offset = 30 + 590 * column, center = offset + 275;
  const x = position => center + 31 * (position - 5);
  const top = 210, step = 10.7, bottom = top + step * record.word.length;
  const color = label => label === 0 ? gold : blue;
  const labels = [...record.initial];
  const paths = new Map(labels.map((label, i) => [label, `M${number(x(i))},${top}`]));
  const bridges = [];
  const curve = (a, b, y) => `C${number(x(a))},${number(y + step * .45)} ` +
    `${number(x(b))},${number(y + step * .55)} ${number(x(b))},${number(y + step)}`;
  svg.push(`<rect x="${offset}" y="130" width="550" height="1290" rx="14" fill="${background}" stroke="#383b50"/>`,
    text(center, 168, `Rhythms 11 / ${record.inner}`, 24, ink, 'text-anchor="middle"'),
    text(center, 194, 'Start at the normal (3/5, 4/5)', 15, '#c7c7d4', 'text-anchor="middle"'));
  for (const [k, generator] of record.word.entries()) {
    assert.ok(Number.isInteger(generator) && generator >= 1 && generator < 11);
    const low = generator - 1, y = top + step * k;
    for (let position = 0; position < 11; position++) {
      const target = position === low ? low + 1 : position === low + 1 ? low : position;
      paths.set(labels[position], paths.get(labels[position]) +
        (target === position ? `L${number(x(position))},${number(y + step)}` : curve(position, target, y)));
    }
    bridges.push({ d: `M${number(x(low))},${number(y)}` + curve(low, low + 1, y), color: color(labels[low]) });
    [labels[low], labels[low + 1]] = [labels[low + 1], labels[low]];
    if ((k + 1) % 10 === 0 || k + 1 === 106) {
      svg.push(text(offset + 25, y + step + 4, String(k + 1), 12, '#9999ae'));
    }
  }
  assert.deepEqual(labels, record.initial.map(label => (label + 10) % 11));
  for (const [label, d] of paths) svg.push(`<path d="${d}" fill="none" stroke="${color(label)}" stroke-width="${label === 0 ? 2 : 1.4}"/>`);
  // The strand with larger front slope passes in front. These are all
  // positive generators; erase only a narrow strip beneath its bridge.
  for (const bridge of bridges) svg.push(`<path d="${bridge.d}" fill="none" stroke="${background}" stroke-width="6"/><path d="${bridge.d}" fill="none" stroke="${bridge.color}" stroke-width="1.6"/>`);
  for (let i = 0; i < 11; i++) {
    svg.push(text(x(i), top - 3, String(record.initial[i]), 11, color(record.initial[i]), 'text-anchor="middle"'),
      text(x(i), bottom + 20, String(labels[i]), 11, color(labels[i]), 'text-anchor="middle"'));
  }
  svg.push(text(center, 1396, 'Join bottom to top at matching positions.', 16, '#c7c7d4', 'text-anchor="middle"'));
}
svg.push(text(30, 1466, 'Same complete Alexander polynomial: degree 96, determinant 189.', 23, ink),
  text(30, 1506, 'Gold follows strand 0 through the cut. Labels follow normal turns; the closure joins all eleven.', 17),
  text(30, 1540, 'A 195-generator conjugator proves ordinary knot equivalence. Plane-curve routes remain separate.', 17),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'normal_front_braid.svg'), svg.join('\n') + '\n');
console.log('Wrote normal_front_braid.svg from both certified 106-generator words.');
