'use strict';

// Numerical implementation checks, separate from rhythm_tangencies.py's
// rational proofs. No browser dependency and no external packages.
const assert = require('node:assert/strict');
const M = require('./touch_math.js'), D = require('./touch_data.js');
let checks = 0, largestResidual = 0, largestAreaError = 0;
const near = (a, b, tolerance, message) => {
  assert.ok(Math.abs(a - b) <= tolerance, `${message}: ${a} vs ${b}`); checks++;
};
const mul = ([x, y], [u, v]) => [x * u - y * v, x * v + y * u];

// Independent complex-power evaluator: no per-frequency angles or phase
// shifts from the implementation under test.
function independent(t, a, order) {
  const w = [Math.cos(t), Math.sin(t)], powers = [[1, 0]];
  for (let k = 1; k <= 11; k++) powers.push(mul(powers[k - 1], w));
  const sum = [0, 0];
  for (const [r, k] of [[245, 1], [140, 11], [65 * (1 - a), -6], [65 * a, -8]]) {
    let p = [...powers[Math.abs(k)]];
    if (k < 0) p[1] = -p[1];
    for (let j = 0; j < order; j++) p = [-k * p[1], k * p[0]];
    for (let j = 0; j < 2; j++) sum[j] += r * p[j];
  }
  return sum;
}

for (let j = 0; j <= 256; j++) {
  const t = M.cycle * j / 256;
  for (const a of [0, .10386013617856, .32297509657704, .39371013549163, .5, .86394091539713, 1]) {
    for (let order = 0; order <= 2; order++) {
      const actual = M.orbit(t, a, order), expected = independent(t, a, order);
      for (let axis = 0; axis < 2; axis++) {
        near(actual[axis], expected[axis], [2e-11, 3e-10, 3e-9][order], 'Independent Fourier evaluation');
        near(actual[axis], (1 - a) * independent(t, 0, order)[axis] + a * independent(t, 1, order)[axis],
          [2e-11, 3e-10, 3e-9][order], 'Independent affine endpoint mixture');
      }
    }
  }
}

function polygonArea(points) {
  const origin = points[0];
  const shifted = points.map(([x, y]) => [x - origin[0], y - origin[1]]);
  return Math.abs(shifted.reduce((sum, [x, y], j) => {
    const [u, v] = shifted[(j + 1) % shifted.length];
    return sum + x * v - y * u;
  }, 0)) / 2;
}

let states = 0, lenses = 0;
for (const event of D.events) {
  for (let progress = -100; progress <= 100; progress++) {
    const upper = M.state(event, progress), upperRoots = M.meetings(upper);
    for (const reflected of [false, true]) {
      const s = M.state(event, progress, reflected), roots = M.meetings(s);
      near(Math.hypot(...s.tangent), 1, 1e-14, 'Unit common-tangent frame');
      for (const x of [-event.half_size, -.5 * event.half_size, 0, .5 * event.half_size, event.half_size]) {
        const first = M.branch(s, 0, x), second = M.branch(s, 1, x);
        for (const b of [first, second]) {
          const p = independent(b.t, s.weight, 0), local = M.local(s, p);
          near(local[0], x, 2e-10, 'Independent graph inversion');
          near(local[1], b.y, 2e-10, 'Independent normal coordinate');
          assert.ok(Math.abs(b.t - s.times[b === first ? 0 : 1]) < .04); checks++;
        }
        assert.equal(first.direction === second.direction, event.direct); checks++;
        const mirroredGap = M.gap(upper, x).value;
        near(first.y - second.y, mirroredGap, 5e-11, 'Reflection preserves the reordered gap');
        const g = M.gap(s, x);
        const g0 = M.gap(M.state(event, 0, reflected), 0);
        assert.ok(g.curvature * g0.curvature > 0, 'The sampled gap curvature changes sign'); checks++;
      }
      assert.equal(roots.length, progress === 0 ? 1 : Math.sign(progress) === event.pocket_side ? 2 : 0); checks++;
      assert.equal(roots.length, upperRoots.length); checks++;
      for (let k = 0; k < roots.length; k++) {
        near(roots[k], upperRoots[k], 3e-8, 'Reflected crossing coordinate');
        if (progress === 0) continue;
        const first = M.branch(s, 0, roots[k]), second = M.branch(s, 1, roots[k]);
        const p = independent(first.t, s.weight, 0), q = independent(second.t, s.weight, 0);
        const residual = Math.hypot(p[0] - q[0], p[1] - q[1]);
        largestResidual = Math.max(largestResidual, residual);
        assert.ok(residual < 1e-8, 'An independent crossing residual is too large'); checks++;
      }
      const A = M.area(s, roots);
      if (roots.length === 2) {
        assert.ok(A > 0); checks++;
        const refined = M.area(s, roots, 256);
        near(A, refined, 1e-8 * A + 1e-12, 'Quadrature refinement');
        // Integrate the actual planar boundary independently by shoelace;
        // its error is O(1/N^2), unlike the gap's Simpson quadrature.
        const points = [
          ...M.samples(roots[0], roots[1], 256, x => M.branch(s, 0, x).point),
          ...M.samples(roots[1], roots[0], 256, x => M.branch(s, 1, x).point)
        ];
        const polygon = polygonArea(points), error = Math.abs(polygon / A - 1);
        largestAreaError = Math.max(largestAreaError, error);
        assert.ok(error < 2e-5, 'Physical boundary and graph quadrature disagree'); checks++;
        lenses++;
      } else { assert.equal(A, 0); checks++; }
      states++;
    }
  }
  let previous = Infinity;
  for (const delta of [.003, .001, .0003, .0001, .00003, .00001, .000003]) {
    const s = M.state(event, 100 * event.pocket_side * delta / event.range);
    const A = M.area(s, M.meetings(s), 256);
    const error = Math.abs(A / (event.coefficient * delta ** 1.5) - 1);
    assert.ok(error < previous && error < .02, 'The three-halves law did not converge'); checks++;
    previous = error;
  }
  assert.ok(previous < .00002); checks++;
}

for (const bad of [NaN, Infinity, -101, 101]) {
  assert.throws(() => M.state(D.events[0], bad), RangeError); checks++;
}
for (const steps of [0, -2, 3, 2.5]) {
  const s = M.state(D.events[0], -100);
  assert.throws(() => M.area(s, M.meetings(s), steps), RangeError); checks++;
}
assert.throws(() => M.bisect(x => x * x + 1, -1, 1), RangeError); checks++;
console.log(`${checks.toLocaleString('en-US')} numerical checks passed across ${states} states and ${lenses} lenses.`);
console.log(`Largest independent crossing residual: ${largestResidual.toExponential(3)} drawing units.`);
console.log(`Largest relative physical-boundary / quadrature difference: ${largestAreaError.toExponential(3)}.`);
console.log('Rational event, isolation, and limiting coefficient proofs run separately in rhythm_tangencies.py.');
