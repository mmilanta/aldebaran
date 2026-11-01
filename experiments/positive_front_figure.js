'use strict';

// A still of one checked local move. No browser or external packages.
const fs = require('node:fs');
const path = require('node:path');
const M = require('./positive_front_math.js');
const data = require('./positive_front_data.js');
const states = M.replay(data);
const at = data.moves.findIndex(move => move[0] === 'triangle');
const word = [...states[at]], move = data.moves[at];
const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
const n = x => String(Math.round(x * 100) / 100);
const text = (x, y, value, size = 18, color = '#c7c7d4', extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${value}</text>`;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-labelledby="title description">',
  '<title id="title">A knot, one move at a time</title>',
  '<desc id="description">Before, during, and after a three-strand move in the conormal graph. At halfway the three graph heights agree, with slopes 15/8, zero, and minus 15/8. The reconstructed original points stay distinct on one tangent line. The full checked sequence has 6,367 moves between the positive eleven-strand endpoint braids, each with 106 crossings. Graph axes have different units; the local point diagram uses equal coordinate scales.</desc>',
  '<rect width="1200" height="800" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(40, 60, 'A knot, one move at a time.', 43, '#f4f1e8', 'font-weight="650" letter-spacing="-1.5"'),
  text(40, 101, 'Three strands can meet in the tangent-line graph while their original points stay apart.', 21)];
for (const [column, progress] of [0, .5, 1].entries()) {
  const left = 40 + column * 380;
  const xMap = x => left + 30 + 300 * (x + 1) / 2;
  const yMap = h => 320 - 123 * h;
  svg.push(`<rect x="${left}" y="135" width="360" height="370" rx="12" fill="#0b0e1a" stroke="#383b50"/>`,
    text(left + 180, 172, ['Before', 'Halfway', 'After'][column], 24, '#f4f1e8', 'text-anchor="middle"'),
    `<path d="M${xMap(0)},190V455M${left + 20},455H${left + 340}" fill="none" stroke="#737b99" stroke-dasharray="4 6"/>`);
  for (let strand = 0; strand < 3; strand++) {
    const points = Array.from({ length: 301 }, (_, k) => {
      const x = -1 + k / 150, h = M.local(word, move, x, progress).heights[strand];
      return `${k ? 'L' : 'M'}${n(xMap(x))},${n(yMap(h))}`;
    });
    svg.push(`<path d="${points.join('')}" fill="none" stroke="${colors[strand]}" stroke-width="2.7"/>`);
  }
  const model = M.local(word, move, 0, progress);
  for (let strand = 2; strand >= 0; strand--) {
    const previous = model.heights.slice(0, strand).filter(h => Math.abs(h - model.heights[strand]) < 1e-10).length;
    svg.push(`<circle cx="${xMap(0)}" cy="${n(yMap(model.heights[strand]))}" r="${5 + 3 * previous}" fill="none" stroke="${colors[strand]}" stroke-width="2"/>`);
  }
  svg.push(text(left + 180, 486, 'Normal direction →', 17, '#c7c7d4', 'text-anchor="middle"'));
}
svg.push('<rect x="40" y="530" width="1120" height="170" rx="12" fill="#0b0e1a" stroke="#383b50"/>',
  text(65, 571, 'One line, three places.', 29, '#f4f1e8'),
  text(65, 609, 'At halfway, distance agrees. The three slopes do not.', 20),
  text(65, 646, 'Slope places each point along its tangent line.', 19),
  text(65, 677, 'Local reconstruction · common distance offset 25 · equal x/y scales', 16));
const middle = M.local(word, move, 0, .5), points = M.points(middle);
svg.push('<path d="M930,543V689" stroke="#9999ae" stroke-dasharray="5 6" fill="none"/>');
for (let i = 0; i < 3; i++) {
  const x = 930 + 31 * (points[i][0] + 25), y = 616 - 31 * points[i][1];
  svg.push(`<circle cx="${n(x)}" cy="${n(y)}" r="6" fill="${colors[i]}"/>`,
    `<path d="M${n(x + 17)},${n(y - 11)}v22m-4,-5l4,5l4,-5" stroke="${colors[i]}" stroke-width="1.8" fill="none"/>`);
}
svg.push(text(40, 740, '6,367 checked moves: 5,450 independent swaps · 722 three-strand moves · 195 cut moves', 20, '#f4f1e8'),
  text(40, 777, 'A positive-front route between the endpoint words. The full plane event list is not counted.', 18),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'positive_front.svg'), svg.join('\n') + '\n');
console.log('Wrote positive_front.svg from the checked movie and polynomial local models.');
