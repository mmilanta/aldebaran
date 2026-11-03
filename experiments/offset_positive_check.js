'use strict';

// Independent numerical controls for the selected ordinary events. Exact
// contractions, passage signs, and branch exclusions live in the Python proof.
const assert = require('node:assert/strict'), Data = require('./offset_positive.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
let checks = 0, pointError = 0, velocityError = 0, unfoldingError = 0;
function check(value) { assert.ok(value); checks++; }

function jet(t, inner, offset) {
  const p = [0, 0], v = [0, 0], a = [0, 0];
  for (const [radius, k] of [[245, 1], [140, 11], [65, -inner]]) {
    const c = Math.cos(k * t), s = Math.sin(k * t);
    p[0] += radius * c; p[1] += radius * s;
    v[0] -= radius * k * s; v[1] += radius * k * c;
    a[0] -= radius * k * k * c; a[1] -= radius * k * k * s;
  }
  const speed = Math.hypot(...v), normal = [-v[1] / speed, v[0] / speed];
  return { point: p.map((x, i) => x - offset * normal[i]), normal,
    velocity: v.map(x => (1 + offset * cross(v, a) / speed ** 3) * x) };
}

function determinant(A) {
  if (A.length === 1) return A[0][0];
  return A[0].reduce((sum, x, j) => sum + (-1) ** j * x * determinant(A.slice(1).map(row => row.filter((_, k) => k !== j))), 0);
}

function intersection(a, b, inner, offset) {
  for (let step = 0; step < 8; step++) {
    const p = jet(a, inner, offset), q = jet(b, inner, offset), delta = p.point.map((x, i) => x - q.point[i]);
    const d = cross(p.velocity, q.velocity);
    check(Math.abs(d) > 1);
    a -= cross(delta, q.velocity) / d;
    b -= cross(delta, p.velocity) / d;
  }
  const p = jet(a, inner, offset), q = jet(b, inner, offset);
  check(Math.hypot(...p.point.map((x, i) => x - q.point[i])) < 1e-7);
  return [a, b];
}

for (const endpoint of Data.endpoints) {
  const events = endpoint.ordinary_triples;
  check(events.length === (endpoint.inner === 6 ? 6 : 4));
  events.forEach((event, index) => {
    const ts = event.root_box.map((bounds, i) => event.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(bounds)));
    const offset = middle(event.offset), origin = event.point.map(middle);
    const samples = ts.map(t => jet(t, endpoint.inner, offset));
    samples.forEach((p, i) => {
      const error = Math.hypot(...p.point.map((x, axis) => x - origin[axis]));
      pointError = Math.max(pointError, error); check(error < 1e-6);
      const h = 2e-6;
      const values = [-2, -1, 1, 2].map(k => jet(ts[i] + k * h, endpoint.inner, offset).point);
      const difference = [0, 1].map(axis => (values[0][axis] - 8 * values[1][axis] + 8 * values[2][axis] - values[3][axis]) / (12 * h));
      const relative = Math.hypot(...difference.map((x, axis) => x - p.velocity[axis])) / Math.hypot(...p.velocity);
      velocityError = Math.max(velocityError, relative); check(relative < 1e-8);
    });
    const normals = samples.map(p => p.normal);
    const H = -cross(normals[0], normals[1]) - cross(normals[1], normals[2]) - cross(normals[2], normals[0]);
    const error = Math.abs(H - middle(event.normalized_unfolding));
    unfoldingError = Math.max(unfoldingError, error); check(error < 1e-12); check(H > 0);
    // Normalize away positive speed factors to audit the four-variable
    // equal-offset-point determinant without the circumcenter equations.
    const tangent = samples.map(p => { const s = Math.hypot(...p.velocity); return p.velocity.map(x => x / s); });
    const G = [];
    for (const other of [1, 2]) for (const axis of [0, 1]) G.push([tangent[0][axis],
      other === 1 ? -tangent[1][axis] : 0, other === 2 ? -tangent[2][axis] : 0,
      normals[other][axis] - normals[0][axis]]);
    check(Math.abs(determinant(G) + H) < 1e-12);
    check(determinant(G) < 0);
    // Pairwise crossings exchange their order on the middle visit. The
    // sign formula is independently checked against actual curved branches.
    for (const delta of [-.01, -.003, .003, .01]) {
      const ab = intersection(ts[0], ts[1], endpoint.inner, offset + delta);
      const bc = intersection(ts[1], ts[2], endpoint.inner, offset + delta);
      const actual = ab[1] - bc[0];
      const D01 = cross(samples[0].velocity, samples[1].velocity);
      const D12 = cross(samples[1].velocity, samples[2].velocity);
      const speeds = samples.map(s => Math.hypot(...s.velocity));
      const predicted = H * speeds.reduce((a, b) => a * b, 1) * delta / (D01 * D12);
      check(Math.sign(actual) === Math.sign(predicted));
      check(Math.abs(actual / predicted - 1) < .005);
    }
    if (index % 2 === 0) {
      const reflected = events[index + 1], opposite = reflected.point.map(middle);
      check(Math.abs(offset - middle(reflected.offset)) < 1e-8);
      check(Math.hypot(origin[0] - opposite[0], origin[1] + opposite[1]) < 1e-8);
      check(origin[1] > 0 && opposite[1] < 0);
    }
  });
  const positive = endpoint.fourfolds.reduce((sum, e) => sum + e.triples.filter(t => t.strangeness_jump > 0).length, 0) + events.length;
  check(positive === endpoint.positive_lower_bound);
  check(endpoint.negative_lower_bound - positive === (endpoint.inner === 6 ? 102 : 112));
  check(positive + endpoint.negative_lower_bound === endpoint.triple_lower_bound);
}
check(Data.full_route_positive_lower_bound === 494);
check(Data.full_route_negative_lower_bound === 498);
check(Data.full_route_triple_lower_bound === 992);
console.log(`${checks} independent numerical geometry, velocity, unfolding, curved crossing-order, reflection, and count checks passed.`);
console.log(`Largest point error ${pointError.toExponential(3)}, relative velocity error ${velocityError.toExponential(3)}, unfolding error ${unfoldingError.toExponential(3)}.`);
