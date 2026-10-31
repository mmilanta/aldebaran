'use strict';

// Numerical implementation checks, independent of the analytic argument.
// Run: node experiments/normal_front_check.js (standard library only).
const assert = require('node:assert/strict');
const M = require('./normal_front_math.js');
let checks = 0, largestAngleError = 0, largestSlopeError = 0, largestReconstructionError = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };
const close = (x, y, tolerance, message) => check(Math.abs(x - y) < tolerance, message);
const independent = (t, n, order) => {
  // Different derivative implementation: multiply complex coefficients by ik.
  let x = 0, y = 0;
  for (const [radius, frequency] of [[245, 1], [140, 11], [65, -n]]) {
    let real = radius * Math.cos(frequency * t), imag = radius * Math.sin(frequency * t);
    for (let i = 0; i < order; i++) [real, imag] = [-frequency * imag, frequency * real];
    x += real; y += imag;
  }
  return [x, y];
};

// Exact integer arithmetic verifies the displayed uniform inequalities.
const crossBound = 1540n * 16940n - 1540n * 4405n - 765n * 16940n - 765n * 4405n;
assert.equal(crossBound, 2974975n); checks++;
assert.equal(crossBound * 212521n, 118999n * 2305n ** 2n); checks++;
check(1540n - 765n === 775n && 1540n - 765n > 0n, 'The velocity disk must miss zero.');

for (const inner of [6, 8]) {
  const strands = M.front(inner, 360);
  for (let branch = 0; branch < 11; branch++) {
    const right = M.visit(M.cycle, branch, inner), left = M.visit(0, (branch + 1) % 11, inner);
    close(right.distance, left.distance, 2e-10, 'A strand has the wrong distance at the seam.');
    close(right.slope, left.slope, 2e-10, 'A strand has the wrong slope at the seam.');
    for (let axis = 0; axis < 2; axis++) close(right.point[axis], left.point[axis], 2e-10,
      'The graph seam failed to rejoin the original curve.');
    for (let step = 0; step <= 720; step++) {
      const beta = step * M.cycle / 720, visit = M.visit(beta, branch, inner);
      const q = independent(visit.t, inner, 0), v = independent(visit.t, inner, 1);
      const a = independent(visit.t, inner, 2), speed = Math.hypot(...v);
      const det = v[0] * a[1] - v[1] * a[0], thetaRate = det / speed ** 2;
      check(speed >= 775 - 1e-8 && speed <= 2305 + 1e-8, 'A sample violates the proven speed bounds.');
      check(det >= 2974975 - 1e-6 && thetaRate >= 118999 / 212521,
        'A sample violates the proven curvature bound.');
      const normal = [-v[1] / speed, v[0] / speed];
      const angleError = Math.hypot(...normal.map((x, axis) => x - visit.normal[axis]));
      largestAngleError = Math.max(largestAngleError, angleError);
      check(angleError < 2e-12, 'The inverse angle selected a different normal.');
      close(M.normalTurn(visit.t, inner), beta + branch * M.cycle, 2e-12, 'The unwrapped angle is wrong.');
      close(visit.distance, q[0] * normal[0] + q[1] * normal[1], 1e-9,
        'The signed line distance disagrees with an independent normal.');
      const reconstructed = [visit.distance * normal[0] - visit.slope * normal[1],
        visit.distance * normal[1] + visit.slope * normal[0]];
      const error = Math.hypot(...q.map((x, axis) => x - reconstructed[axis]));
      largestReconstructionError = Math.max(largestReconstructionError, error);
      check(error < 1e-9, 'Distance and slope do not recover the original point.');
      if (step % 2 === 0) close(strands[branch][step / 2][1], visit.distance, 1e-12,
        'A cached front sample disagrees with its visit.');
      if (step > 0 && step < 720) {
        const h = 1e-4;
        const derivative = delta => (M.visit(beta + delta, branch, inner).distance -
          M.visit(beta - delta, branch, inner).distance) / (2 * delta);
        const slope = (4 * derivative(h / 2) - derivative(h)) / 3;
        const slopeError = Math.abs(slope - visit.slope);
        largestSlopeError = Math.max(largestSlopeError, slopeError);
        check(slopeError < 2e-7, 'The analytic front slope differs from independent finite differences.');
      }
    }
  }
  const example = M.sharedTangent(inner, 0, 6, (inner === 6 ? 102 : 95) * Math.PI / 180,
    (inner === 6 ? 103 : 96) * Math.PI / 180);
  const [first, second] = example.visits;
  close(first.distance, second.distance, 1e-9, 'The selected tangent lines do not coincide.');
  const separation = Math.hypot(...first.point.map((x, i) => x - second.point[i]));
  check(separation > 500, 'The two points should remain visibly far apart.');
  close(Math.abs(first.slope - second.slope), separation, 1e-9,
    'Slope difference must equal point separation on a shared tangent line.');
  const along = first.point.map((x, i) => x - second.point[i]);
  close(along[0] * first.normal[0] + along[1] * first.normal[1], 0, 1e-9,
    'The shared line is not perpendicular to the common normal.');
  // Reflection t -> 2pi-t sends beta -> 2pi-beta and branch -> 10-branch.
  for (let step = 1; step < 360; step++) {
    const beta = step * M.cycle / 360;
    for (let branch = 0; branch < 11; branch++) {
      const a = M.visit(beta, branch, inner), b = M.visit(M.cycle - beta, 10 - branch, inner);
      close(a.point[0], b.point[0], 1e-9, 'Reflection changed the horizontal coordinate.');
      close(a.point[1], -b.point[1], 1e-9, 'Reflection did not reverse the vertical coordinate.');
      close(a.distance, b.distance, 1e-9, 'Reflection changed the signed distance.');
      close(a.slope, -b.slope, 1e-9, 'Reflection did not reverse the slope.');
    }
  }
}

for (const inner of [5, 7, 9, '6', NaN]) {
  assert.throws(() => M.front(inner), RangeError); checks++;
}
for (const beta of [-1e-9, M.cycle + 1e-9, NaN, Infinity]) {
  assert.throws(() => M.visit(beta, 0, 6), RangeError); checks++;
}
for (const branch of [-1, 11, .5, NaN]) {
  assert.throws(() => M.visit(0, branch, 6), RangeError); checks++;
}
for (const turn of [-1e-9, 11 * M.cycle + 1e-9, NaN, Infinity]) {
  assert.throws(() => M.timeAt(turn, 6), RangeError); checks++;
}
for (const steps of [0, 3, 4097, 12.5]) {
  assert.throws(() => M.front(6, steps), RangeError); checks++;
}
assert.throws(() => M.sharedTangent(6, 0, 0, 1, 2), RangeError); checks++;
assert.throws(() => M.sharedTangent(6, 0, 6, 0, .001), RangeError); checks++;
assert.throws(() => M.sharedTangent(6, 0, 6, 2, 1), RangeError); checks++;
console.log(`${checks} implementation checks passed, including 15,862 visits, every seam, reflection, and shared-line examples.`);
console.log(`Largest errors: normal ${largestAngleError.toExponential(3)}, slope ${largestSlopeError.toExponential(3)}, reconstruction ${largestReconstructionError.toExponential(3)}.`);
