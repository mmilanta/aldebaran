'use strict';

// Standalone numerical illustration. Node standard library only.
// Regenerate with: node experiments/normal_front_figure.js
const fs = require('node:fs');
const path = require('node:path');
const M = require('./normal_front_math.js');
const gold = '#e8b66e', lilac = '#d1b6ea', blue = '#9fc7eb', white = '#f4f1e8';
const example = M.sharedTangent(6, 0, 6, 102 * Math.PI / 180, 103 * Math.PI / 180);
const visits = Array.from({ length: 11 }, (_, i) => M.visit(example.beta, i, 6));
const whole = ([x, y]) => [305 + .52 * x, 420 - .52 * y];
const graph = ([beta, h]) => [660 + 510 * beta / M.cycle, 420 - .44 * h];
const number = x => String(Math.round(x * 100) / 100);
const line = (points, project, color, width = 1.5, extra = '') =>
  `<path d="M${points.map(p => project(p).map(number).join(',')).join('L')}" fill="none" stroke="${color}" stroke-width="${width}" ${extra}/>`;
const dot = ([x, y], color, r, fill = '#0b0e1a') => `<circle cx="${number(x)}" cy="${number(y)}" r="${r}" fill="${fill}" stroke="${color}" stroke-width="2"/>`;
const text = (x, y, value, size = 18, color = '#c7c7d4', extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${value}</text>`;
const v = visits[0], [nx, ny] = v.normal;
const svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="870" viewBox="0 0 1240 870" role="img" aria-labelledby="title description">',
  '<title id="title">One direction, eleven places</title>',
  '<desc id="description">Rhythms 11 / 6 have eleven places with any one left-normal direction. Gold visit 1 and lilac visit 7 share an oriented tangent line while remaining far apart. Their dots meet in a graph of normal direction and signed tangent-line distance, with different slopes. The graph edges join cyclically. Numerical illustration, not a census of shared tangents.</desc>',
  '<rect width="1240" height="870" fill="#101323"/>',
  '<g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(30, 58, 'One direction, eleven places.', 40, white, 'font-weight="650" letter-spacing="-1.5"'),
  text(30, 100, 'A shared tangent line, seen twice in direction and distance.', 21),
  '<rect x="30" y="140" width="550" height="550" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
  '<rect x="610" y="140" width="600" height="550" rx="14" fill="#0b0e1a" stroke="#383b50"/>',
  '<defs><clipPath id="orbit-clip"><rect x="45" y="180" width="520" height="480"/></clipPath><clipPath id="graph-clip"><rect x="660" y="215" width="510" height="410"/></clipPath></defs>',
  text(50, 174, 'The original drawing · 11 / 6', 19),
  text(635, 174, 'Direction and signed distance', 19),
  '<g clip-path="url(#orbit-clip)">',
  line([[-500, 0], [500, 0]], whole, '#282d43', 1),
  line([[0, -500], [0, 500]], whole, '#282d43', 1),
  line(Array.from({ length: 3001 }, (_, i) => M.orbit(M.cycle * i / 3000, 6)), whole, '#737b99', 1.25),
  line([[v.point[0] - 1000 * ny, v.point[1] + 1000 * nx],
    [v.point[0] + 1000 * ny, v.point[1] - 1000 * nx]], whole, gold, 1.8, 'stroke-dasharray="7 7"'),
  line([[0, 0], v.normal.map(n => n * v.distance)], whole, gold, 3)];
for (const i of [...Array(11).keys()].filter(i => i !== 0 && i !== 6).concat(0, 6)) {
  const visit = visits[i], color = i === 0 ? gold : i === 6 ? lilac : blue;
  const [x, y] = whole(visit.point), length = i === 0 || i === 6 ? 31 : 20;
  const tip = [x + length * nx, y - length * ny];
  svg.push(`<path d="M${number(x)},${number(y)}L${tip.map(number)}M${number(tip[0] - 6 * nx + 4 * ny)},${number(tip[1] + 6 * ny + 4 * nx)}L${tip.map(number)}L${number(tip[0] - 6 * nx - 4 * ny)},${number(tip[1] + 6 * ny - 4 * nx)}" fill="none" stroke="${color}" stroke-width="1.8"/>`);
  svg.push(dot([x, y], color, i === 0 || i === 6 ? 6 : 3.5));
}
svg.push('</g>', dot(whole([0, 0]), white, 2));
for (const h of [-450, 0, 450]) {
  const y = graph([0, h])[1];
  svg.push(line([[0, h], [M.cycle, h]], graph, '#282d43', 1),
    text(649, y + 5, String(h).replace('-', '−'), 15, '#c7c7d4', 'text-anchor="end"'));
}
svg.push('<g clip-path="url(#graph-clip)">');
const fronts = M.front(6);
for (const i of [...Array(11).keys()].filter(i => i !== 0 && i !== 6).concat(0, 6)) {
  svg.push(line(fronts[i], graph, i === 0 ? gold : i === 6 ? lilac : blue,
    i === 0 || i === 6 ? 2.6 : 1.2, `opacity="${i === 0 || i === 6 ? 1 : .5}"`));
}
svg.push(line([[example.beta, -450], [example.beta, 450]], graph, '#c7c7d4', 1, 'stroke-dasharray="4 6"'));
for (const i of [...Array(11).keys()].filter(i => i !== 0 && i !== 6).concat(0, 6)) {
  svg.push(dot(graph([example.beta, visits[i].distance]), i === 0 ? gold : i === 6 ? lilac : blue,
    i === 0 ? 5 : i === 6 ? 8 : 3, i === 6 ? 'none' : '#0b0e1a'));
}
svg.push('</g>');
for (const [i, label] of ['180°', '270°', '0°', '90°', '180°'].entries()) {
  const x = graph([i * M.cycle / 4, 0])[0];
  svg.push(text(x, 651, label, 15, '#c7c7d4', 'text-anchor="middle"'));
}
svg.push(text(915, 678, 'Normal direction · edges join', 16, '#c7c7d4', 'text-anchor="middle"'),
  text(30, 737, `One line touches visits 1 and 7, ${Math.hypot(...v.point.map((x, i) => x - visits[6].point[i])).toFixed(2)} drawing units apart.`, 23, white),
  text(30, 778, `Same normal: ${(180 + example.beta * 180 / Math.PI).toFixed(2)}°. Same signed distance: ${v.distance.toFixed(2).replace('-', '−')}. Different slopes: ${v.slope.toFixed(2)} and ${visits[6].slope.toFixed(2)}.`, 19),
  text(30, 824, 'The original drawing has equal coordinate scales. The graph uses angle and distance; its axes differ.', 17),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'normal_front.svg'), svg.join('\n') + '\n');
console.log('Wrote normal_front.svg: one numerical shared-tangent example, eleven strands.');
