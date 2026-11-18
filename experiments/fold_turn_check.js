'use strict';

// Independent three-frequency geometry, critical-point search, discrete Fourier
// areas, and exact Python radius enclosures. No browser or third-party packages.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const math = require('./fold_turn_math.js');
const cycle = 2 * Math.PI;
let comparisons = 0;
function close(a, b, tolerance = 1e-8) {
  comparisons++;
  assert.ok(Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) < tolerance,
    `${a} differs from ${b} by ${Math.abs(a - b)}`);
}
const original = (t, d, phase) => [
  245 * Math.cos(t) + 140 * Math.cos((d + 1) * t) + 65 * Math.cos(phase - (d - 1) * t),
  245 * Math.sin(t) + 140 * Math.sin((d + 1) * t) + 65 * Math.sin(phase - (d - 1) * t)];

for (const d of math.folds) {
  for (let degrees = 0; degrees <= 180; degrees++) {
    const phase = degrees * Math.PI / 180;
    const range = math.radialRange(phase);
    for (let i = 0; i <= 96; i++) {
      const t = cycle * i / 97;
      const expected = original(t, d, phase), actual = math.position(t, d, phase);
      actual.forEach((v, j) => close(v, expected[j]));
      const { fixed, turning } = math.joints(t, d, phase);
      turning[3].forEach((v, j) => close(v, expected[j]));
      close(Math.hypot(...fixed[3]), Math.hypot(...expected));
      for (const points of [fixed, turning]) {
        for (let j = 1; j <= 3; j++) {
          close(Math.hypot(points[j][0] - points[j - 1][0], points[j][1] - points[j - 1][1]), [245, 140, 65][j - 1]);
        }
      }
      const next = original(t + cycle / d, d, phase);
      const angle = cycle / d;
      close(next[0], expected[0] * Math.cos(angle) - expected[1] * Math.sin(angle));
      close(next[1], expected[0] * Math.sin(angle) + expected[1] * Math.cos(angle));
      const radius = Math.hypot(...expected);
      assert.ok(radius >= range[0] - 1e-8 && radius <= range[1] + 1e-8);
    }
  }
}

// Check actual serialized paths against the original equation, including
// their chord midpoints. The 22/7 bound also covers every untested phase.
let vertices = 0;
for (const d of math.folds) {
  const count = math.segmentCount(d);
  const theoretical = (245 + 140 * (d + 1) ** 2 + 65 * (d - 1) ** 2) * (44 / (7 * count)) ** 2 / 8 + Math.SQRT2 * .00005;
  assert.ok(theoretical < .02);
  for (const phase of [0, Math.PI / 2, Math.PI]) {
    for (const repeat of [false, true]) {
      const points = math.orbitPath(d, phase, repeat).slice(1).split('L').map(s => s.split(',').map(Number));
      const segments = repeat ? Math.ceil(count / d) : count;
      const end = repeat ? cycle / d : cycle;
      assert.equal(points.length, segments + 1);
      for (let i = 0; i <= segments; i++) {
        const p = original(end * i / segments, d, phase);
        close(points[i][0], p[0], .000051);
        close(points[i][1], -p[1], .000051);
        vertices++;
        if (i > 0) {
          const mid = original(end * (i - .5) / segments, d, phase);
          assert.ok(Math.hypot((points[i - 1][0] + points[i][0]) / 2 - mid[0],
            (points[i - 1][1] + points[i][1]) / 2 + mid[1]) < .02);
        }
      }
    }
  }
}

// A distinct numerical algorithm finds every radial stationary point by
// derivative signs. This is a cross-check, separate from the rational proof.
for (let degrees = 0; degrees <= 180; degrees++) {
  const phase = degrees * Math.PI / 180, psi = phase / 2;
  const radial = theta => {
    const c = Math.cos(theta), s = Math.sin(theta);
    return Math.hypot(245 + 205 * c * Math.cos(psi) - 75 * s * Math.sin(psi),
      205 * c * Math.sin(psi) + 75 * s * Math.cos(psi));
  };
  const derivative = theta => -36400 * Math.sin(theta) * Math.cos(theta) -
    50225 * Math.cos(psi) * Math.sin(theta) - 18375 * Math.sin(psi) * Math.cos(theta);
  const candidates = [];
  for (let i = 0; i < 2048; i++) {
    let lo = cycle * i / 2048, hi = cycle * (i + 1) / 2048;
    if (Math.abs(derivative(lo)) < 1e-7) candidates.push(lo);
    if (derivative(lo) * derivative(hi) >= 0) continue;
    let sign = Math.sign(derivative(lo));
    for (let k = 0; k < 55; k++) {
      const mid = (lo + hi) / 2;
      if (Math.sign(derivative(mid)) === sign) lo = mid;
      else hi = mid;
    }
    candidates.push((lo + hi) / 2);
  }
  assert.ok(candidates.length >= 2);
  const distances = candidates.map(radial);
  const range = math.radialRange(phase);
  close(range[0], Math.min(...distances));
  close(range[1], Math.max(...distances));
}

// Shoelace areas have an independent exact discrete Fourier expression.
// Test that phase changes do not alter them, including the high-fold weave.
for (const d of math.folds) {
  const count = 8192, step = cycle / count;
  const expected = count / 2 * (245 ** 2 * Math.sin(step) +
    140 ** 2 * Math.sin((d + 1) * step) - 65 ** 2 * Math.sin((d - 1) * step));
  for (const phase of [0, .713, Math.PI]) {
    let sum = 0, correction = 0;
    let previous = original(0, d, phase);
    for (let i = 1; i <= count; i++) {
      const current = original(i * step, d, phase);
      const term = (previous[0] * current[1] - previous[1] * current[0]) / 2 - correction;
      const next = sum + term;
      correction = (next - sum) - term;
      sum = next;
      previous = current;
    }
    close(sum, expected, 1e-6);
  }
}

// Read exact rationals; round to cents with integer arithmetic, independently
// of both Python's floating display and JavaScript's bisection.
const archive = JSON.parse(execFileSync('python3', [path.join(__dirname, 'fold_annulus.py'), '--json'], { encoding: 'utf8' }));
const cents = s => {
  const [a, b = 1n] = s.split('/').map(BigInt);
  return (200n * a + b) / (2n * b);
};
assert.equal(archive.radii.length, 181);
for (const row of archive.radii) {
  const actual = math.radialRange(row.degrees * Math.PI / 180);
  for (const [j, key] of ['inner', 'outer'].entries()) {
    const [low, high] = row[key].map(cents);
    assert.equal(low, high);
    assert.equal(actual[j].toFixed(2), `${low / 100n}.${String(low % 100n).padStart(2, '0')}`);
  }
}

for (const search of ['', '?utm_source=sketchbook', '?unknown=1']) assert.deepEqual(math.parse(search), math.defaults);
assert.deepEqual(math.parse('?folds=60&phase=180&trace=1000'), { folds: 60, phase: 180, trace: 1000 });
assert.deepEqual(math.parse('?phase=0'), { ...math.defaults, phase: 0 });
for (const search of ['folds=13', 'folds=7&folds=14', 'phase=181', 'phase=-1', 'phase=',
  'phase=1.5', 'phase=1e2', 'trace=1001', 'trace=NaN', 'trace=1&trace=1', 'folds=60&phase=bad', 'phase=%20']) {
  assert.deepEqual(math.parse(`?${search}`), math.defaults);
}
for (const d of math.folds) {
  const state = { folds: d, phase: 173, trace: 832 };
  assert.deepEqual(math.parse(math.query(state)), state);
  const svg = math.drawing(d, 180);
  assert.ok(svg.includes(`${d} folds`) && !/NaN|Infinity|undefined/.test(svg));
  assert.ok(!svg.includes('orbit-point'));
}
console.log(`${comparisons.toLocaleString('en-US')} independent coordinate/length/area comparisons passed.`);
console.log(`${vertices.toLocaleString('en-US')} serialized vertices and all their chord midpoints passed the .02-unit bound.`);
console.log('All 362 radial displays agree with exact rational enclosures; independent extrema and link checks passed.');
