'use strict';

// Numerical implementation controls, independent of the rational cover.
// Direct Fourier jets and actual curved, locally shifted branches audit
// every circle, sign, and first-order resolution. No numerical result here
// supplies a completeness predicate.
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const Data = require('./offset_axis_census.json'), Figure = require('./offset_axis_census_figure.js');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
let checks = 0, pointError = 0, signError = 0, weightError = 0, curvedError = 0;
function check(condition) { assert.ok(condition); checks++; }

function solve(A, b) {
  const a = A.map((row, i) => [...row, b[i]]), n = a.length;
  for (let k = 0; k < n; k++) {
    let pivot = k;
    for (let i = k + 1; i < n; i++) if (Math.abs(a[i][k]) > Math.abs(a[pivot][k])) pivot = i;
    [a[k], a[pivot]] = [a[pivot], a[k]];
    assert.ok(Math.abs(a[k][k]) > 1e-13);
    const scale = a[k][k];
    for (let j = k; j <= n; j++) a[k][j] /= scale;
    for (let i = 0; i < n; i++) if (i !== k) {
      const scale = a[i][k];
      for (let j = k; j <= n; j++) a[i][j] -= scale * a[k][j];
    }
  }
  return a.map(row => row[n]);
}

function jet(t, inner, offset = 0) {
  const point = [0, 0], v = [0, 0], a = [0, 0];
  for (const [radius, k] of [[245, 1], [140, 11], [65, -inner]]) {
    const c = Math.cos(k * t), s = Math.sin(k * t);
    point[0] += radius * c; point[1] += radius * s;
    v[0] -= radius * k * s; v[1] += radius * k * c;
    a[0] -= radius * k * k * c; a[1] -= radius * k * k * s;
  }
  const speed = Math.hypot(...v), normal = [-v[1] / speed, v[0] / speed];
  const factor = 1 + offset * cross(v, a) / speed ** 3;
  return { original: [...point], point: point.map((x, i) => x - offset * normal[i]),
    normal, velocity: v.map(x => factor * x), speed, factor };
}

function curvedTriple(event, times, indices, epsilon, model) {
  const ts = indices.map(i => times[i]), base = middle(event.offset);
  let offset = base + epsilon * model[2];
  for (let step = 0; step < 7; step++) {
    const samples = ts.map((t, k) => jet(t, event.inner, offset - epsilon * event.normal_shifts[indices[k]]));
    const F = [], J = [];
    for (const other of [1, 2]) for (const axis of [0, 1]) {
      F.push(samples[0].point[axis] - samples[other].point[axis]);
      J.push([samples[0].velocity[axis], other === 1 ? -samples[1].velocity[axis] : 0,
        other === 2 ? -samples[2].velocity[axis] : 0, samples[other].normal[axis] - samples[0].normal[axis]]);
    }
    const delta = solve(J, F);
    ts.forEach((_, i) => { ts[i] -= delta[i]; }); offset -= delta[3];
  }
  const samples = ts.map((t, k) => jet(t, event.inner, offset - epsilon * event.normal_shifts[indices[k]]));
  for (let i = 1; i < 3; i++) check(Math.hypot(...samples[0].point.map((x, axis) => x - samples[i].point[axis])) < 1e-8);
  ts.forEach((t, k) => check(Math.abs(t - times[indices[k]]) < 1e-3));
  const predicted = [middle(event.axis_center) + epsilon * model[0], epsilon * model[1], base + epsilon * model[2]];
  const error = Math.hypot(samples[0].point[0] - predicted[0], samples[0].point[1] - predicted[1], offset - predicted[2]);
  const relative = error / (epsilon * Math.hypot(...model));
  curvedError = Math.max(curvedError, relative); check(relative < 1e-3);
  const N = samples.map(s => s.normal), H = -cross(N[0], N[1]) - cross(N[1], N[2]) - cross(N[2], N[0]);
  return { offset, sign: Math.sign(H) };
}

const inventory = { 0: 0, 2: 0, 4: 0 };
for (const endpoint of Data.endpoints) {
  check(endpoint.events.length === (endpoint.inner === 6 ? 11 : 9));
  check(endpoint.eligible_arcs.length === 7);
  const stats = endpoint.cover;
  check(stats.projective_exclusions + stats.mean_value_exclusions + stats.root_leaves === 21 + stats.bisections);
  let positives = 0, negatives = 0;
  for (const [index, event] of endpoint.events.entries()) {
    if (index) check(rational(endpoint.events[index - 1].offset[1]) < rational(event.offset[0]));
    check(rational(event.contraction_norm_upper) < 1);
    const times = Figure.times(event), offset = middle(event.offset), center = middle(event.axis_center);
    check(times.every((t, i) => t > 0 && t < 2 * Math.PI && (!i || times[i - 1] < t)));
    const samples = times.map(t => jet(t, event.inner, offset)), normals = Figure.normals(event);
    samples.forEach((sample, i) => {
      const error = Math.hypot(sample.point[0] - center, sample.point[1]);
      pointError = Math.max(pointError, error); check(error < 1e-7);
      check(Math.abs(Math.hypot(sample.original[0] - center, sample.original[1]) - offset) < 1e-7);
      check(Math.hypot(...sample.normal.map((n, axis) => n - normals[i][axis])) < 1e-12);
      check(Math.abs(Math.hypot(...normals[i]) - 1) < 1e-14);
      check(sample.speed >= 775 && sample.factor > 1);
    });
    for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) check(Math.abs(cross(normals[i], normals[j])) > 1e-5);
    const models = event.triples.map(triple => {
      const [a, b, c] = triple.visits.map(i => normals[i]);
      const H = -cross(a, b) - cross(b, c) - cross(c, a);
      const area2 = cross([b[0] - a[0], b[1] - a[1]], [c[0] - a[0], c[1] - a[1]]);
      check(Math.abs(H + area2) < 2e-15);
      const error = Math.abs(H - middle(triple.normalized_unfolding));
      signError = Math.max(signError, error); check(error < 1e-12);
      check(Math.sign(H) === triple.strangeness_jump);
      if (H > 0) positives++; else negatives++;
      const model = solve(triple.visits.map(i => [...normals[i], 1]), triple.visits.map(i => event.normal_shifts[i]));
      const relative = Math.abs(model[2] - middle(triple.first_order_weight)) / (1 + Math.abs(model[2]));
      weightError = Math.max(weightError, relative); check(relative < 1e-10);
      return model;
    });
    const scale = Math.max(1, ...models.map(m => Math.hypot(...m)));
    for (const delta of [1e-3, 3e-4, 1e-4]) {
      const meetings = event.triples.map((triple, k) => curvedTriple(event, times, triple.visits, delta / scale, models[k]));
      event.triples.forEach((triple, i) => check(meetings[i].sign === triple.strangeness_jump));
      event.perturbed_order.slice(1).forEach((current, i) => check(meetings[event.perturbed_order[i]].offset < meetings[current].offset));
    }
    inventory[event.positive_triples]++;
    check(event.positive_triples + event.negative_triples === 4);
  }
  check(positives === endpoint.positive_triples && negatives === endpoint.negative_triples);
  check(positives === (endpoint.inner === 6 ? 12 : 6));
  check(negatives === (endpoint.inner === 6 ? 32 : 30));
}
check(inventory[0] === 12 && inventory[2] === 7 && inventory[4] === 1);
check(Figure.figure() === fs.readFileSync(path.join(__dirname, 'offset_axis_census.svg'), 'utf8'));
console.log(`${checks} independent Fourier, circle, normal, tangent, orientation, first-order, curved-resolution, cover-arithmetic, and figure checks passed.`);
console.log(`Largest meeting error ${pointError.toExponential(3)}, sign error ${signError.toExponential(3)}, relative weight error ${weightError.toExponential(3)}, relative curved-model error ${curvedError.toExponential(3)}.`);
