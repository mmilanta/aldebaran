'use strict';

// Numerical implementation checks accompany the separate rational proofs.
const assert = require('node:assert/strict');
const Model = require('./parallel_offset_math.js'), Data = require('./parallel_offset_data.js');
const View = require('./parallel_offset_view.js');
const proof = require('./parallel_offset_triple.json');
let checks = 0, largestDerivativeError = 0, largestAreaError = 0;
const check = condition => { assert.ok(condition); checks++; };
const close = (a, b, allowance) => check(Math.abs(a - b) <= allowance);
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const slots = proof.event.viewer_window.isolation.slots;

// Direct Fourier formulas, independent of the imported orbit implementation.
function original(t, derivative = false) {
  return derivative
    ? [-245 * Math.sin(t) - 1540 * Math.sin(11 * t) - 390 * Math.sin(6 * t),
      245 * Math.cos(t) + 1540 * Math.cos(11 * t) - 390 * Math.cos(6 * t)]
    : [245 * Math.cos(t) + 140 * Math.cos(11 * t) + 65 * Math.cos(6 * t),
      245 * Math.sin(t) + 140 * Math.sin(11 * t) - 65 * Math.sin(6 * t)];
}
function shifted(t, offset) {
  const p = original(t), v = original(t, true), speed = Math.hypot(...v);
  return [p[0] + offset * v[1] / speed, p[1] - offset * v[0] / speed];
}

for (let k = 0; k <= 2048; k++) {
  const t = Model.cycle * k / 2048, p = original(t), v = original(t, true);
  for (const offset of [0, Data.offset, 1000]) {
    const jet = Model.jet(t, offset), q = shifted(t, offset);
    check(jet.curvature > 0);
    close(Math.hypot(...jet.normal), 1, 5e-15);
    close(jet.normal[0] * v[0] + jet.normal[1] * v[1], 0, 2e-10);
    close(Math.hypot(...jet.point.map((x, i) => x - p[i])), offset, 2e-10);
    jet.point.forEach((x, i) => close(x, q[i], 2e-10));
    const h = 2e-6, left = shifted(t - h, offset), right = shifted(t + h, offset);
    const farLeft = shifted(t - 2 * h, offset), farRight = shifted(t + 2 * h, offset);
    jet.velocity.forEach((x, i) => {
      const derivative = (farLeft[i] - 8 * left[i] + 8 * right[i] - farRight[i]) / (12 * h);
      const error = Math.abs(derivative - x);
      largestDerivativeError = Math.max(largestDerivativeError, error);
      check(error < 4e-5);
    });
  }
}

Data.times.forEach((t, branch) => {
  const jet = Model.jet(t), r = jet.original.map((v, i) => v - Data.point[i]);
  close(Math.hypot(...r), Data.offset, 1e-8);
  close(r[0] * jet.velocity[0] + r[1] * jet.velocity[1], 0, 1e-5);
  check(r[0] * jet.normal[0] + r[1] * jet.normal[1] > 0);
  close(Math.hypot(...Model.jet(t, Data.offset).point.map((v, i) => v - Data.point[i])), 0, 1e-8);
  close(rational(proof.event.center[branch]), Math.tan((t - proof.event.quarters[branch] * Math.PI / 2) / 2), 5e-15);
});

for (let progress = -100; progress <= 100; progress++) {
  const state = Model.state(progress), triangle = Model.triangle(state);
  check(state.offset >= rational(proof.event.viewer_window.offset[0])
    && state.offset <= rational(proof.event.viewer_window.offset[1]));
  for (const crossing of triangle.crossings) {
    crossing.times.forEach((t, at) => {
      const branch = crossing.branches[at], slot = slots[branch];
      const s = Math.tan((t - slot.quarter * Math.PI / 2) / 2);
      check(s > rational(slot.low) && s < rational(slot.high));
      const independent = shifted(t, state.offset);
      independent.forEach((x, i) => close(x, crossing.point[i], 1e-8));
    });
    crossing.point.forEach((x, i) => check(Math.abs(x - state.center[i]) < 1));
  }
  // Independent polygon area, with 256 samples on each actual curved edge.
  const polygon = triangle.edges.flatMap(edge => Array.from({ length: 256 }, (_, k) =>
    shifted(edge.start + (edge.end - edge.start) * k / 256, state.offset).map((x, i) => x - state.center[i])));
  const area = Math.abs(polygon.reduce((sum, p, k) => {
    const next = polygon[(k + 1) % polygon.length];
    return sum + p[0] * next[1] - p[1] * next[0];
  }, 0)) / 2;
  largestAreaError = Math.max(largestAreaError, Math.abs(area - triangle.area));
  close(area, triangle.area, 2e-8);
  if (progress !== 0) check(triangle.area > 0);
  else check(triangle.crossings.every(c => Math.hypot(...c.point.map((x, i) => x - state.center[i])) < 1e-8));
  check(!/NaN|Infinity|undefined/.test(View.lens(state)));
}

for (const fn of [() => Model.state(-101), () => Model.state(101), () => Model.state(NaN),
  () => Model.jet(0, -1), () => Model.jet(Infinity, 1), () => Model.jet(0, NaN),
  () => Model.intersection(Model.state(0), 1, 1), () => Model.intersection(Model.state(0), -1, 1),
  () => Model.intersection(Model.state(0), 0, 3), () => Model.intersection(Model.state(0), 0, 1.5),
  () => Model.sample(0, 1, 0, 1), () => Model.circle(3)]) {
  assert.throws(fn, RangeError); checks++;
}
check(!/NaN|Infinity|undefined/.test(View.circle()));
console.log(`${checks} checks pass: independent Fourier geometry, all slider positions, certified slots, offset derivatives, curved triangle area, and invalid controls.`);
console.log(`Largest velocity difference: ${largestDerivativeError}; largest independent area difference: ${largestAreaError}.`);
