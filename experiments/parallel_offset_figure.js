'use strict';

// Plot certified offset locations and their analytically proved pair jumps.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const data = require('./parallel_offset_events.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const number = x => String(Math.round(x * 100) / 100);
const text = (x, y, content, size = 18, color = '#c7c7d4', extra = '') =>
  `<text x="${number(x)}" y="${number(y)}" font-size="${size}" fill="${color}" ${extra}>${content}</text>`;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="750" viewBox="0 0 1200 750" role="img" aria-labelledby="title description">',
  '<title id="title">The way out, and the way home</title>',
  '<desc id="description">Two step graphs count transverse crossing pairs along outward parallel offsets of the 11 / 6 and 11 / 8 curves. Each goes from forty to 106 by thirty-three inverse contact pairs at eighteen offset weights, including mirror partners at the same weight. Reversing the second leg gives thirty-three deaths. The middle of the positive-front construction avoids both types of touch, giving a generic route with sixty-six inverse touches and no direct ones. Values at contact weights are omitted. Horizontal positions are rounded from rational certificates.</desc>',
  '<rect width="1200" height="750" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(35, 61, 'The way out, and the way home.', 43, '#f4f1e8', 'font-weight="650" letter-spacing="-1.5"'),
  text(35, 103, 'Every outward inverse touch creates two crossings. None of them takes a pair away.', 21)];
for (const [column, endpoint] of data.endpoints.entries()) {
  const left = 30 + 590 * column, color = column ? '#9fc7eb' : '#e8b66e';
  const x = m => left + 65 + 455 * m / 170;
  const y = count => 570 - 4.5 * (count - 40);
  svg.push(`<rect x="${left}" y="140" width="550" height="515" rx="14" fill="#0b0e1a" stroke="#383b50"/>`,
    text(left + 275, 182, `Rhythms 11 / ${endpoint.inner}`, 26, '#f4f1e8', 'text-anchor="middle"'),
    text(left + 65, 222, 'Crossing pairs', 17));
  for (const count of [40, 60, 80, 100, 106]) {
    svg.push(`<path d="M${x(0)},${y(count)}H${x(170)}" stroke="#383b50" fill="none" stroke-dasharray="3 5"/>`,
      text(x(0) - 12, y(count) + 5, String(count), 16, '#c7c7d4', 'text-anchor="end"'));
  }
  for (const m of [0, 40, 80, 120, 160]) {
    svg.push(`<path d="M${number(x(m))},${y(40)}v7" stroke="#737b99"/>`,
      text(x(m), 597, String(m), 16, '#c7c7d4', 'text-anchor="middle"'));
  }
  svg.push(`<path d="M${x(0)},240V570H${x(170)}" stroke="#737b99" fill="none"/>`);
  let count = 40, d = `M${x(0)},${y(count)}`, contacts = 0;
  assert.equal(endpoint.ordered_weight_groups.length, 18);
  for (const group of endpoint.ordered_weight_groups) {
    const m = group.offset.map(rational).reduce((a, b) => a + b) / 2;
    assert.ok(m > 0 && m < 157);
    const jump = 2 * group.members.length;
    contacts += group.members.length;
    d += `H${number(x(m))}V${number(y(count + jump))}`;
    count += jump;
  }
  assert.equal(contacts, 33); assert.equal(count, 106);
  d += `H${x(170)}`;
  svg.push(`<path d="${d}" fill="none" stroke="${color}" stroke-width="2.6" stroke-linejoin="round"/>`,
    text(left + 275, 630, 'Outward distance offset M →', 18, '#c7c7d4', 'text-anchor="middle"'));
}
svg.push(text(35, 700, '33 births on the way out · 33 deaths on the way home · no touches in the middle', 23, '#f4f1e8'),
  text(35, 735, 'Away from contact weights. Mirror partners can occur together; each contact pair contributes its own jump.', 18),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'parallel_offset.svg'), svg.join('\n') + '\n');
console.log('Wrote parallel_offset.svg from 66 certified event pairs and their exact weight groups.');
