'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const M = require('./four_visits_math.js'), V = require('./four_visits_view.js'), Data = require('./four_visits_data.js');
const Record = require('./offset_positive.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
let checks = 0, largestAreaError = 0;
const check = condition => { assert.ok(condition); checks++; };
const near = (a, b, tolerance = 1e-9) => check(Math.abs(a - b) < tolerance);
const source = fs.readFileSync(require.resolve('./four_visits_math.js'), 'utf8');
function variant(data) {
  const context = { module: { exports: {} }, require: () => data };
  vm.runInNewContext(source, context); return context.module.exports;
}
const shifted = variant({ ...Data, shifts: Data.shifts.map(x => x + 7) });
const rotated = variant({ ...Data, normals: Data.normals.map(([x, y]) => [-y, x]) });
const certificate = Record.endpoints[0].fourfolds.find(e => e.triples.every(t => t.strangeness_jump === 1));
M.events.forEach((event, index) => {
  const archived = certificate.triples.find(t => t.visits.every((v, i) => v === event.indices[i]));
  near(event.weight, middle(archived.first_order_weight));
  near(shifted.events[index].weight, event.weight + 7);
  near(rotated.events[index].weight, event.weight);
  near(rotated.events[index].coefficient, event.coefficient);
  for (let progress = -100; progress <= 100; progress++) {
    const state = M.state(index, progress), shiftedState = shifted.state(index, progress), rotatedState = rotated.state(index, progress);
    const extra = [0, 1, 2, 3].find(i => !event.indices.includes(i));
    const sides = [];
    state.crossings.forEach((crossing, k) => {
      crossing.visits.forEach(i => near(M.dot(M.normals[i], crossing.point), M.shifts[i] - state.weight));
      const [x, y] = V.project(crossing.point, event);
      check(x >= 57 && x <= 543 && y >= 57 && y <= 543);
      sides.push(M.dot(M.normals[extra], crossing.point) - M.shifts[extra] + state.weight);
      shiftedState.crossings[k].point.forEach((v, i) => near(v, crossing.point[i]));
      near(rotatedState.crossings[k].point[0], -crossing.point[1]);
      near(rotatedState.crossings[k].point[1], crossing.point[0]);
    });
    check(sides.every(x => x > 1e-8) || sides.every(x => x < -1e-8));
    const ps = state.crossings.map(c => c.point.map((x, i) => x - event.center[i]));
    const area = Math.abs(ps.reduce((sum, p, i) => sum + M.cross(p, ps[(i + 1) % 3]), 0)) / 2;
    const error = Math.abs(area - state.area);
    largestAreaError = Math.max(largestAreaError, error); check(error < 1e-10);
    if (progress === 0) { check(state.area === 0); check(state.crossings.every(c => c.point.every((x, i) => x === event.center[i]))); }
    const svg = V.lens(state); check(!/NaN|Infinity|undefined/.test(svg));
  }
});
for (const args of [[-1, 0], [4, 0], [.5, 0], [0, -101], [0, 101], [0, .5], [NaN, 0], [0, Infinity], [true, 0]]) {
  assert.throws(() => M.state(...args), RangeError); checks++;
}
assert.throws(() => variant({ ...Data, normals: Data.normals.map(([x, y]) => [x, -y]) }), /positive sign/); checks++;
console.log(`${checks} local-model checks passed: every slider position, certified first-order weights, line equations, triangle faces and areas, equal-scale framing, translation and rotation controls, and rejected invalid inputs.`);
console.log(`Largest triangle-area discrepancy ${largestAreaError.toExponential(3)} model square units.`);
