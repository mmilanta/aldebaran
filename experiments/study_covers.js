'use strict';

// Regenerate the gallery's small, numerical illustrations with:
//   node experiments/study_covers.js
// No browser or external packages. These are previews, not certificates.
const fs = require('node:fs');
const path = require('node:path');
const Blend = require('./blend_math.js');
const Detour = require('./arm_detour_math.js');
const Phase = require('./phase_math.js');
const Cubic = require('./cubic_math.js');
const Lobes = require('./two_lobes_math.js');
const Winding = require('./winding_math.js');
const Weave = require('./weave_math.js');
const WeaveData = require('./weave_data.js');
const Touch = require('./touch_math.js');
const TouchData = require('./touch_data.js');
const StrangenessData = require('./strangeness_data.js');
const Strangeness = require('./strangeness_math.js');

const blue = '#9fc7eb', gold = '#e8b66e', white = '#f4f1e8', muted = '#555b78';
const cycle = 2 * Math.PI;
const output = path.join(__dirname, 'covers');
const number = x => {
  if (!Number.isFinite(x)) throw new RangeError('A preview coordinate is not finite.');
  return String(Math.round(x * 10) / 10);
};
const samples = (fn, low = 0, high = cycle, count = 4096) =>
  Array.from({ length: count + 1 }, (_, i) => fn(low + (high - low) * i / count));
const map = (points, x, y, scale) => points.map(p => [x + scale * p[0], y - scale * p[1]]);

// Remove subpixel vertices. Always retain the endpoints, including closure.
function simplify(points, tolerance = .12) {
  const keep = new Set([0, points.length - 1]), pending = [[0, points.length - 1]];
  while (pending.length) {
    const [first, last] = pending.pop(), a = points[first], b = points[last];
    const dx = b[0] - a[0], dy = b[1] - a[1], norm = dx * dx + dy * dy;
    let best = tolerance * tolerance, split;
    for (let i = first + 1; i < last; i++) {
      const p = points[i];
      const u = norm ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / norm)) : 0;
      const d = (p[0] - a[0] - u * dx) ** 2 + (p[1] - a[1] - u * dy) ** 2;
      if (d > best) { best = d; split = i; }
    }
    if (split !== undefined) {
      keep.add(split);
      pending.push([first, split], [split, last]);
    }
  }
  return [...keep].sort((a, b) => a - b).map(i => points[i]);
}

const commands = points => simplify(points).map((p, i) =>
  `${i ? 'L' : 'M'}${number(p[0])},${number(p[1])}`).join('');
const line = (points, color = gold, width = 2, extra = '') =>
  `<path d="${commands(points)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" ${extra}/>`;
const fill = (points, color) =>
  `<path d="${commands(points)}Z" fill="${color}" fill-opacity=".18"/>`;
const dot = ([x, y], color = white, radius = 3.5) =>
  `<circle cx="${number(x)}" cy="${number(y)}" r="${radius}" fill="${color}" stroke="#0b0e1a" stroke-width="1.5"/>`;
const orbit = (m, n, t, length = 245) =>
  [length * Math.cos(t) + 140 * Math.cos(m * t) + 65 * Math.cos(n * t),
    length * Math.sin(t) + 140 * Math.sin(m * t) - 65 * Math.sin(n * t)];
const text = (x, y, value, color = white) =>
  `<text x="${x}" y="${y}" fill="${color}" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="22">${value}</text>`;

function write(name, title, description, body) {
  const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400" role="img" aria-labelledby="title description">\n<title id="title">${escape(title)}</title>\n<desc id="description">${escape(description)}</desc>\n<rect width="640" height="400" fill="#0b0e1a"/>\n${body}\n</svg>\n`;
  fs.writeFileSync(path.join(output, `${name}.svg`), svg);
}

function main() {
  fs.mkdirSync(output, { recursive: true });

  const garden = samples(t => orbit(7, 13, t));
  const joints = [[0, 0], [245, 0], [385, 0], [450, 0]];
  write('001', 'Three circles make a garden',
    'The complete 7 / 13 drawing. A pale line shows the three arms at the start of their orbit.',
    line(map(garden, 320, 200, .41), blue, 1.6) +
    line(map(samples(t => orbit(7, 13, t), .35, 2.3, 1200), 320, 200, .41), gold, 2.2) +
    line(map(joints, 320, 200, .41), muted, 1.3) + map(joints, 320, 200, .41).map(p => dot(p, white, 2.5)).join(''));

  const tip = (t, r) => [-2 * (245 * Math.sin(t / 2) ** 2 +
    140 * Math.sin(4 * t) ** 2 + r * Math.sin(10.5 * t) ** 2),
  245 * Math.sin(t) + 140 * Math.sin(8 * t) - r * Math.sin(21 * t)];
  write('002', 'The birth of a loop',
    'Needle’s tip at inner length 70, in gold, compared with its cusp at length 65, in dashed blue. Both axes have the same scale.',
    line(map(samples(t => tip(t, 65), -.05, .05, 1000), 568, 200, 10.5), blue, 1.7, 'stroke-dasharray="5 6"') +
    line(map(samples(t => tip(t, 70), -.05, .05, 1000), 568, 200, 10.5), gold, 2.5) + dot([568, 200]));

  const backwards = Winding.orbit(2, 25);
  const backwardsPoints = Array.from({ length: backwards.length / 2 }, (_, i) => [backwards[2 * i], backwards[2 * i + 1]]);
  backwardsPoints.push(backwardsPoints[0]);
  // Find a readable negative-count probe, and check its smooth-curve clearance.
  let probe;
  for (let x = -220; x <= -60; x += 4) {
    for (let y = -20; y <= 20; y += 4) {
      const p = Winding.inspect(backwards, x, y);
      if (p.count === -7 && (!probe || p.distance > probe.distance)) probe = { x, y, ...p };
    }
  }
  if (!probe || probe.distance <= 10 * Winding.errorBound(2, 25)) throw new Error('The negative probe is unresolved.');
  const negative = map([[probe.x, probe.y]], 320, 200, .41)[0];
  write('003', 'A region can count backwards',
    'Rhythms 2 / 25. One point has winding count minus seven; the center counts plus one. The labels are independently checked against the sampled curve and its interpolation allowance.',
    line(map(backwardsPoints, 320, 200, .41), blue, 1.5) +
    dot(negative, gold, 5) + text(negative[0], negative[1] + 32, '−7', gold) + dot([320, 200]) + text(320, 232, '+1'));
  if (Winding.inspect(backwards, 0, 0).count !== 1) throw new Error('Unexpected center count.');

  const little = samples(Lobes.position, Lobes.crossingTime, cycle - Lobes.crossingTime, 1000);
  write('004', 'Two lobes, two ways to turn',
    'The 2 / 3 drawing and an enlarged view of its small clockwise lobe. Each individual view has equal coordinate scales.',
    line(map(samples(Lobes.position), 180, 200, .42), blue, 2) +
    line(map(little, 180, 200, .42), gold, 2.5) +
    '<path d="M375,60V340" stroke="#383b50"/>' +
    fill(map(little, 810, 200, 2.1), gold) + line(map(little, 810, 200, 2.1), gold, 2.5) +
    dot(map([Lobes.position(Lobes.crossingTime)], 810, 200, 2.1)[0]));

  write('005', 'Two routes between two zeros',
    'The straight blend, blue, and the logarithmic route, gold, at the same weight 0.35. Each drawing has the same scale.',
    line(map(samples(t => Blend.position(t, .35)), 145, 200, .29), blue, 2.2) +
    line(map(samples(t => Blend.regularPosition(t, .35)), 465, 200, .29), gold, 2.2) +
    '<path d="M320,60V340" stroke="#383b50"/>');

  const states = [0, 1.5, 3].map(p => Detour.state(0, p));
  write('006', 'Room to keep moving',
    'Three drawings on the first arm detour: its beginning, the middle of its longer-arm blend, and its end. All share one scale.',
    states.map((s, i) => line(map(samples(t => Detour.position(t, s)), 95 + 212 * i, 200, .215),
      i === 1 ? gold : blue, 1.8)).join(''));

  const phase = .001, contact = Phase.contact(phase), weight = contact.weight + .001;
  const currentGap = samples(y => [Phase.gap(y, weight, phase).value, y], -32, 32, 800);
  const mirrorGap = samples(y => [Phase.gap(y, weight, 0).value, y], -32, 32, 800);
  const gapMap = points => points.map(([x, y]) => [320 + 110 * x, 200 - 5 * y]);
  write('007', 'A small turn breaks the mirror',
    'A branch-separation graph: gold follows a small phase turn, dashed blue keeps the mirror. Horizontal separation is magnified relative to height. Dots mark meetings on the zero line.',
    '<path d="M320,30V370M70,200H570" stroke="#383b50"/>' +
    line(gapMap(mirrorGap), blue, 1.8, 'stroke-dasharray="5 6"') + line(gapMap(currentGap), gold, 2.5) +
    Phase.meetings(weight, phase).map(p => dot([320, 200 - 5 * p.height])).join(''));

  const cubic = samples(v => [Cubic.value(v, 1, 0), v], -1.5, 1.5, 600);
  const cubicMap = points => points.map(([x, v]) => [320 + 100 * x, 200 - 110 * v]);
  write('008', 'One cubic, two area laws',
    'The normalized cubic at opening one and tilt zero. Two equal pockets lie between it and the vertical zero line; separation and height have different scales.',
    '<path d="M320,25V375M80,200H560" stroke="#555b78"/>' +
    [[-1, 0, blue], [0, 1, gold]].map(([low, high, color]) =>
      fill(cubicMap(samples(v => [Cubic.value(v, 1, 0), v], low, high, 200)), color)).join('') +
    line(cubicMap(cubic), white, 2.4) + [-1, 0, 1].map(v => dot([320, 200 - 110 * v])).join(''));

  const crossingCurve = StrangenessData[1];
  const crossingState = Strangeness.state(crossingCurve, 0);
  write('009', 'Where the crossing remembers',
    'The 4 / 7 drawing. Blue rings and gold squares mark its seven crossing visits; a white point chooses the start of the orbit.',
    line(map(samples(t => orbit(4, 7, t)), 300, 200, .43), '#9999ae', 1.8) +
    crossingState.rows.map(row => {
      const visit = crossingCurve.word.findIndex(([label]) => label === row.label);
      const [x, y] = map([crossingCurve.display_points[visit]], 300, 200, .43)[0];
      return row.weight < 0 ? `<rect x="${number(x - 4)}" y="${number(y - 4)}" width="8" height="8" fill="#0b0e1a" stroke="${gold}" stroke-width="2"/>`
        : `<circle cx="${number(x)}" cy="${number(y)}" r="4.5" fill="#0b0e1a" stroke="${blue}" stroke-width="2"/>`;
    }).join('') + dot(map([orbit(4, 7, crossingState.time)], 300, 200, .43)[0]));

  const event = WeaveData.events[0], scene = Weave.state(event, -100, false);
  const triangle = Weave.triangle(scene);
  const trianglePoints = triangle.edges.flatMap(edge => Weave.points(edge.start, edge.end, 80, scene.weight));
  const closeMap = points => points.map(p => [365 + 200 * (p[0] - scene.center[0]), 170 - 200 * (p[1] - scene.center[1])]);
  write('010', 'The same counts, a different weave',
    'Three branches just before the first triple passage. They enclose a small pale triangle. Both axes have the same scale.',
    fill(closeMap(trianglePoints), white) + scene.times.map((t, i) =>
      line(closeMap(Weave.points(t - .009, t + .009, 300, scene.weight)), [blue, gold, white][i], 2.3)).join('') +
    triangle.crossings.map(p => dot(closeMap([p.point])[0])).join(''));

  const touch = Touch.state(TouchData.events[0], -100);
  const roots = Touch.meetings(touch);
  const edge = (index, low, high) => samples(x => [x, Touch.branch(touch, index, x).y], low, high, 600);
  const lens = [...edge(0, ...roots), ...edge(1, roots[1], roots[0])];
  write('011', 'Two ways to touch',
    'Two branches enclose a pale lens before the first direct touch. Its ends are crossings. Both axes have the same scale.',
    fill(map(lens, 320, 200, 23), white) + [0, 1].map(i => line(map(edge(i, -13.5, 13.5), 320, 200, 23), i ? gold : blue, 2.5)).join('') +
    roots.map(x => dot(map([[x, Touch.branch(touch, 0, x).y]], 320, 200, 23)[0])).join(''));

  console.log('Wrote eleven study covers; the negative-count probe has smooth-curve clearance.');
}

main();
