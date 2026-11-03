'use strict';
const fs = require('node:fs'), path = require('node:path');
const Data = require('./offset_positive.json'), Orbit = require('./weave_math.js');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
const event = Data.endpoints[0].fourfolds.find(e => e.triples.every(t => t.strangeness_jump === 1));
if (!event) throw new Error('The all-positive fourfold record is missing.');
const times = event.root_box.map((bounds, i) => event.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(bounds)));
const normals = times.map(t => { const v = Orbit.orbit(t, 0, 1), speed = Math.hypot(...v); return [-v[1] / speed, v[0] / speed]; });
const data = { scope: 'Rounded first-order model of one certified fourfold; no finite perturbation threshold.',
  normals, shifts: event.normal_shifts, triples: event.triples.map(t => t.visits),
  offset: middle(event.offset) };
fs.writeFileSync(path.join(__dirname, 'four_visits_data.js'), `'use strict';\nconst FourVisitsData = ${JSON.stringify(data, null, 2)};\nif (typeof module !== 'undefined' && module.exports) module.exports = FourVisitsData;\n`);
const M = require('./four_visits_math.js'), V = require('./four_visits_view.js');
const parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1650" viewBox="0 0 1200 1650" role="img" aria-labelledby="title description">',
  '<title id="title">Four signs agree</title><desc id="description">Four rows show the four first-order triple passages of one orbital fourfold. Each row has a before, meeting, and after panel at equal scales. A triangle changes sides and contributes a positive passage. The model consists of straight local branches after normal shifts zero, one, three, and seven; it is not a finite-offset orbital simulation.</desc>',
  '<rect width="1200" height="1650" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  '<style>.still text {font-size:28px}</style>',
  V.text(30, 61, 'Four signs agree.', 43, '#f4f1e8'),
  V.text(30, 103, 'One fourfold separates into four positive triples. Follow its first-order lines.', 22)];
M.events.forEach((event, index) => {
  const top = 130 + 365 * index;
  parts.push(V.text(30, top + 24, `Visits ${event.indices.map(i => i + 1).join(' · ')}    d ≈ ${event.weight.toFixed(5)}    sign +1`, 24, '#e8b66e'));
  [-70, 0, 70].forEach((progress, column) => {
    const x = 30 + 390 * column, y = top + 40, clip = `still-clip-${index}-${column}`;
    parts.push(`<svg class="still" x="${x}" y="${y}" width="360" height="300" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet">`,
      '<rect width="600" height="600" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
      `<defs><clipPath id="${clip}"><rect x="57" y="57" width="486" height="486"/></clipPath></defs>`,
      V.lens(M.state(index, progress), clip), '</svg>');
  });
});
parts.push(V.text(30, 1620, 'Straight local model · same scale before and after each meeting · no numerical orbital perturbation size asserted', 18), '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'four_visits.svg'), parts.join('\n') + '\n');
console.log('Wrote rounded model data and four_visits.svg from the selected rational fourfold record.');
