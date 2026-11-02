'use strict';

// Numerical checks of the explicit small generic resolutions. The rational
// certificates and the implicit-function argument are separate.
const assert = require('node:assert/strict');
const Orbit = require('./weave_math.js'), Data = require('./offset_fourfold.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = pair => pair.map(rational).reduce((a, b) => a + b) / 2;
const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
let checks = 0;
const check = condition => { assert.ok(condition); checks++; };

function jet(t, inner, offset) {
  const a = (inner - 6) / 2, p = Orbit.orbit(t, a), v = Orbit.orbit(t, a, 1), w = Orbit.orbit(t, a, 2);
  const speed = Math.hypot(...v), normal = [-v[1] / speed, v[0] / speed], curvature = cross(v, w) / speed ** 3;
  return { point: p.map((x, i) => x - offset * normal[i]), normal,
    velocity: v.map(x => (1 + offset * curvature) * x) };
}

function solve(matrix, vector) {
  const A = matrix.map((row, i) => [...row, vector[i]]), size = vector.length;
  for (let i = 0; i < size; i++) {
    let at = i;
    for (let j = i + 1; j < size; j++) if (Math.abs(A[j][i]) > Math.abs(A[at][i])) at = j;
    check(Math.abs(A[at][i]) > 1e-8);
    [A[i], A[at]] = [A[at], A[i]];
    for (let j = i + 1; j < size; j++) {
      const factor = A[j][i] / A[i][i];
      for (let k = i; k <= size; k++) A[j][k] -= factor * A[i][k];
    }
  }
  const out = Array(size).fill(0);
  for (let i = size - 1; i >= 0; i--) {
    out[i] = (A[i][size] - A[i].slice(i + 1, size).reduce((sum, x, j) => sum + x * out[i + j + 1], 0)) / A[i][i];
  }
  return out;
}

for (const event of Data.events) {
  const times = event.root_box.map((bounds, i) => event.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(bounds)));
  const offset = middle(event.offset), point = event.point.map(middle);
  times.forEach(t => check(Math.hypot(...jet(t, event.inner, offset).point.map((x, i) => x - point[i])) < 1e-6));
  const previous = Array(4).fill(Infinity);
  for (const epsilon of [.001, .0003, .0001, .00003]) {
    const actualWeights = [];
    event.triples.forEach((triple, at) => {
      const predicted = middle(triple.first_order_weight);
      const state = triple.visits.map(i => times[i]);
      state.push(offset + epsilon * predicted);
      for (let step = 0; step < 10; step++) {
        const samples = triple.visits.map((i, k) => jet(state[k], event.inner, state[3] - epsilon * event.normal_shifts[i]));
        const F = [], J = [];
        for (const other of [1, 2]) for (const axis of [0, 1]) {
          F.push(samples[0].point[axis] - samples[other].point[axis]);
          J.push([samples[0].velocity[axis], other === 1 ? -samples[1].velocity[axis] : 0,
            other === 2 ? -samples[2].velocity[axis] : 0, samples[other].normal[axis] - samples[0].normal[axis]]);
        }
        const change = solve(J, F);
        change.forEach((x, i) => state[i] -= x);
      }
      const samples = triple.visits.map((i, k) => jet(state[k], event.inner, state[3] - epsilon * event.normal_shifts[i]));
      samples.forEach((sample, k) => {
        check(Math.hypot(...sample.point.map((x, i) => x - samples[0].point[i])) < 1e-7);
        check(Math.abs(state[k] - times[triple.visits[k]]) < .001);
      });
      const H = -cross(samples[0].normal, samples[1].normal)
        - cross(samples[1].normal, samples[2].normal) - cross(samples[2].normal, samples[0].normal);
      check(Math.sign(H) === triple.strangeness_jump);
      const actual = (state[3] - offset) / epsilon, error = Math.abs(actual - predicted);
      check(error < previous[at]); previous[at] = error; actualWeights.push(actual);
    });
    check(actualWeights.map((d, i) => [d, i]).sort((a, b) => a[0] - b[0]).every((entry, i) => entry[1] === event.perturbed_order[i]));
  }
  check(previous.every((error, i) => error / Math.max(1, Math.abs(middle(event.triples[i].first_order_weight))) < .0002));
  console.log(`11/${event.inner}: all four triple weights converge from the actual curved perturbation; final coefficient errors ${previous.map(x => x.toExponential(3)).join(', ')}.`);
}
console.log(`${checks} numerical resolution checks passed. These accompany the rational local proofs; they are not a global event census.`);
