'use strict';

// Geometric implementation checks for every native passage-slider setting.
// The exact smooth proofs live in rhythm_passages.py, independently of this.
const assert = require('node:assert/strict');
const M = require('./weave_math.js');
const D = require('./weave_data.js');
const S = require('./strangeness_math.js');
const W = require('./winding_math.js');
const archive = require('./strangeness_atlas.json');
let checks = 0, leastClearanceRatio = Infinity, largestResidual = 0;
function check(condition, message) { assert.ok(condition, message); checks++; }

const steps = 48000, endpoints = [W.orbit(11, 6, steps), W.orbit(11, 8, steps)];
const errorBound = (245 + 140 * 121 + 65 * 64) * (M.cycle / steps) ** 2 / 8 + 1e-8;
const polygon = new Float64Array(2 * steps);

for (let j = 0; j < D.endpoints.length; j++) {
  const record = D.endpoints[j];
  const saved = archive.verified.find(r => r.outer === 11 && r.inner === 6 + 2 * j);
  assert.deepEqual(record.word, saved.word); checks++;
  check(record.crossings === 40 && record.tangent_index === 11, 'Endpoint counts differ.');
  assert.deepEqual(record.winding_regions, { 1: 10, 2: 19, 3: 10, 4: 2 }); checks++;
  check(S.walk(record.word, 1).value === [15, 11][j], 'Endpoint strangeness differs.');
  const indices = S.walk(record.word, 1).rows;
  for (let label = 0; label < 40; label++) {
    const visits = record.word.flatMap(([v], k) => v === label ? [k] : []);
    const [a, b] = visits.map(k => record.display_times[k]);
    const p = S.orbit(a, 11, 6 + 2 * j), q = S.orbit(b, 11, 6 + 2 * j);
    check(Math.hypot(p[0] - q[0], p[1] - q[1]) < 1e-8, 'Rounded endpoint visits do not meet.');
    const va = S.velocity(a, 11, 6 + 2 * j), vb = S.velocity(b, 11, 6 + 2 * j);
    check(record.word[visits[0]][1] === -Math.sign(va[0] * vb[1] - va[1] * vb[0]),
      'An endpoint exponent disagrees with independent tangents.');
    const angles = [va, vb].flatMap(([x, y]) => {
      const angle = (Math.atan2(y, x) + M.cycle) % M.cycle;
      return [angle, (angle + Math.PI) % M.cycle];
    }).sort((x, y) => x - y);
    const sectors = angles.map((angle, k) => {
      const next = k === 3 ? angles[0] + M.cycle : angles[k + 1];
      const middle = (angle + next) / 2;
      const result = W.inspect(endpoints[j], p[0] + .03 * Math.cos(middle), p[1] + .03 * Math.sin(middle));
      check(result.distance > 10 * errorBound, 'An endpoint sector probe is too close.');
      return result.count;
    });
    const mean = sectors.reduce((sum, x) => sum + x, 0) / 4;
    check(indices[label].index === mean, 'An endpoint mean index disagrees with geometric winding.');
  }
}

for (const event of D.events) {
  for (let progress = -100; progress <= 100; progress++) {
    const upper = M.state(event, progress, false);
    for (let j = 0; j < polygon.length; j++) {
      polygon[j] = (1 - upper.weight) * endpoints[0][j] + upper.weight * endpoints[1][j];
    }
    for (const reflected of [false, true]) {
      const s = M.state(event, progress, reflected), triangle = M.triangle(s);
      check(Math.abs(s.weight - upper.weight) < 1e-15, 'Reflection changed the blend weight.');
      for (const t of s.times) {
        const p = M.orbit(t, s.weight), v = M.orbit(t, s.weight, 1);
        const ends = [S.orbit(t, 11, 6), S.orbit(t, 11, 8)];
        const velocities = [S.velocity(t, 11, 6), S.velocity(t, 11, 8)];
        for (let axis = 0; axis < 2; axis++) {
          check(Math.abs(p[axis] - ((1 - s.weight) * ends[0][axis] + s.weight * ends[1][axis])) < 1e-9,
            'The displayed geometry is not the affine blend.');
          check(Math.abs(v[axis] - ((1 - s.weight) * velocities[0][axis] + s.weight * velocities[1][axis])) < 1e-8,
            'A displayed arrow has the wrong derivative.');
        }
        check(Math.hypot(...v) >= 775, 'A numerical sample violates the exact speed bound.');
      }
      for (const [pair, crossing] of triangle.crossings.entries()) {
        const [a, b] = crossing.times.map(t => S.orbit(t, 11, 6).map((x, axis) =>
          (1 - s.weight) * x + s.weight * S.orbit(t, 11, 8)[axis]));
        const residual = Math.hypot(a[0] - b[0], a[1] - b[1]);
        largestResidual = Math.max(largestResidual, residual);
        check(residual < 1e-8, 'The lens marker does not lie on both branches.');
        check(crossing.point.every((x, axis) => Math.abs(x - s.center[axis]) < 1.2 * s.halfSize),
          'A selected crossing left the lens.');
        const [i, j] = [[0, 1], [1, 2], [0, 2]][pair];
        const ua = M.orbit(s.times[i], s.weight), ub = M.orbit(s.times[j], s.weight);
        const residualAtSeeds = Math.hypot(ua[0] - ub[0], ua[1] - ub[1]);
        if (progress !== 0) check(residualAtSeeds > 1e-4, 'A crossing marker did not move away from its event seed.');
      }
      if (progress !== 0) {
        const center = [0, 1].map(axis => triangle.crossings.reduce((sum, c) => sum + c.point[axis], 0) / 3);
        const result = W.inspect(polygon, ...center);
        leastClearanceRatio = Math.min(leastClearanceRatio, result.distance / errorBound);
        check(result.distance > 10 * errorBound, 'A triangle winding probe is too close to certify numerically.');
        check(result.count === (progress < 0 ? 2 : 1), 'The little triangle has an unexpected winding count.');
        const reflectedTriangle = M.triangle(M.state(event, progress, !reflected));
        for (const c of triangle.crossings) {
          check(reflectedTriangle.crossings.some(other =>
            Math.hypot(c.point[0] - other.point[0], c.point[1] + other.point[1]) < 1e-8),
          'The below-axis geometry is not the reflected drawing.');
        }
      } else {
        check(triangle.crossings.every(c => Math.hypot(c.point[0] - s.center[0], c.point[1] - s.center[1]) < 1e-7),
          'The rounded meeting does not bring its three markers together.');
      }
    }
  }
}
for (const progress of [-101, 101, NaN, Infinity]) {
  assert.throws(() => M.state(D.events[0], progress, false), RangeError); checks++;
}
console.log(`${checks} checks passed, including all 804 passage states and independent endpoint sector probes.`);
console.log(`Largest crossing residual ${largestResidual.toExponential(3)}; least triangle clearance / interpolation bound ${leastClearanceRatio.toFixed(1)}.`);
