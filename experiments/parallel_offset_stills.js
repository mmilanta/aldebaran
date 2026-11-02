'use strict';

// Regenerate the standalone illustrated sheet, using only Node.
const fs = require('node:fs'), path = require('node:path');
const Model = require('./parallel_offset_math.js'), View = require('./parallel_offset_view.js');
const Data = require('./parallel_offset_data.js');
const text = View.text;
const panels = [View.circle(), View.lens(Model.state(-100)), View.lens(Model.state(0)), View.lens(Model.state(100))];
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1420" viewBox="0 0 1200 1420" role="img" aria-labelledby="title description">',
  '<title id="title">Three visits, one circle</title>',
  '<desc id="description">A circle touches three visits of the 11 / 6 curve. At an outward distance equal to its radius, about 10.17122, those visits meet at the center. Three equal-scale close-ups show a triangle before, at, and after this ordinary triple passage. A whole-orbit rational cover and a four-variable uniqueness proof certify exactly one triple and no touch inside the viewing square throughout the displayed interval. This is one selected local window, not an event census for the whole curve. The drawing uses rounded coordinates.</desc>',
  '<rect width="1200" height="1420" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(30, 61, 'Three visits, one circle.', '#f4f1e8', 43, 'font-weight="650" letter-spacing="-1.5"'),
  text(30, 103, 'Move outward along the normals. One tangent circle becomes one triple meeting.', '#c7c7d4', 21)];
panels.forEach((body, i) => {
  const x = 20 + 590 * (i % 2), y = 132 + 590 * Math.floor(i / 2);
  svg.push(`<rect x="${x}" y="${y}" width="570" height="570" rx="14" fill="#0b0e1a" stroke="#383b50"/>`,
    `<svg x="${x}" y="${y}" width="570" height="570" viewBox="0 0 600 600">`,
    `<defs><clipPath id="clip-${i}"><rect x="46" y="46" width="508" height="508"/></clipPath></defs>`,
    body.replaceAll(/<(path|circle) /g, `<$1 clip-path="url(#clip-${i})" `), '</svg>');
});
svg.push(text(30, 1355, `Meeting distance ${Data.offset.toFixed(8)} · gold, blue, and lilac follow three visits of one orbit.`, '#f4f1e8', 21),
  text(30, 1391, 'The close-ups share a fixed 2 × 2 square. The circle view has its own equal-axis magnification.', '#c7c7d4', 18),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'parallel_offset_triptych.svg'), svg.join('\n') + '\n');
console.log('Wrote parallel_offset_triptych.svg from the separately certified selected meeting.');
