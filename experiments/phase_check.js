'use strict';

// Independent numerical checks of the browser geometry. Exact existence
// statements belong to phase_unfolding.py; these checks do not replace it.
const assert = require('node:assert/strict');
const M = require('./phase_math.js');
let checks = 0, maximumPositionError = 0;
function check(condition, message) { checks++; assert.ok(condition, message); }
function close(x, y, tolerance, message) {
  check(Math.abs(x - y) <= tolerance, `${message}: ${x} vs ${y}`);
}
const mul = ([a, b], [c, d]) => [a * c - b * d, a * d + b * c];
function pow(z, n) {
  if (n < 0) return pow([z[0], -z[1]], -n);
  let result = [1, 0];
  for (let j = 0; j < n; j++) result = mul(result, z);
  return result;
}
function independent(u, a, phase, order = 0, weightDerivative = false) {
  const t = Math.PI + u, w = [Math.cos(t), Math.sin(t)];
  const rotation = [Math.cos(phase), Math.sin(phase)];
  const terms = weightDerivative
    ? [[-140, 2], [140, 4], [-65, -3], [65, -7]]
    : [[300, 1], [140 * (1 - a), 2], [140 * a, 4], [65 * (1 - a), -3], [65 * a, -7]];
  const sum = [0, 0];
  for (const [radius, k] of terms) {
    let p = pow(w, k);
    if (k < 0) p = mul(p, rotation);
    for (let j = 0; j < order; j++) p = mul(p, [0, k]);
    sum[0] += radius * p[0]; sum[1] += radius * p[1];
  }
  return sum;
}

for (let j = 0; j <= 80; j++) {
  const u = -Math.PI + 2 * Math.PI * j / 80;
  for (let k = 0; k <= 16; k++) {
    const a = M.minimum + (M.maximum - M.minimum) * k / 16;
    for (const phase of [-.001, -.0001, 0, .0001, .001]) {
      for (let order = 0; order <= 3; order++) {
        for (const derivative of [false, true]) {
          const p = M.evaluate(u, a, phase, order, derivative);
          const q = independent(u, a, phase, order, derivative);
          const error = Math.hypot(p[0] - q[0], p[1] - q[1]);
          if (order === 0) maximumPositionError = Math.max(maximumPositionError, error);
          check(error < [2e-12, 1e-11, 7e-11, 5e-10][order], 'Complex-power geometry mismatch.');
        }
      }
      const p = M.evaluate(u, a, phase), q = M.evaluate(-u, a, -phase);
      close(p[0], q[0], 2e-12, 'Reflection x');
      close(p[1], -q[1], 2e-12, 'Reflection y');
    }
  }
}

function independentBranch(y, a, phase, sign, radius) {
  let lo = sign * radius - .15, hi = sign * radius + .15;
  check(independent(lo, a, phase)[1] > y && independent(hi, a, phase)[1] < y,
    'The independent height bracket failed.');
  for (let j = 0; j < 48; j++) {
    const mid = (lo + hi) / 2;
    if (independent(mid, a, phase)[1] > y) lo = mid;
    else hi = mid;
  }
  const u = (lo + hi) / 2;
  return { u, x: independent(u, a, phase)[0] };
}

for (let j = 0; j <= 10; j++) {
  const a = M.minimum + (M.maximum - M.minimum) * j / 10;
  const r = M.radius(a);
  for (const phase of [-.001, -.0003, 0, .0003, .001]) {
    for (let k = 0; k <= 16; k++) {
      const y = -32 + 4 * k;
      for (const sign of [-1, 1]) {
        const b = M.branch(y, a, phase, sign, r);
        const other = independentBranch(y, a, phase, sign, r);
        close(b.y, y, 5e-12, 'Height inversion');
        close(b.u, other.u, 2e-14, 'Independent branch time');
        close(b.x, other.x, 3e-12, 'Independent branch position');
      }
      const g = M.gap(y, a, phase, r), mirror = M.gap(-y, a, -phase, r);
      close(g.value, -mirror.value, 3e-12, 'Separation reflection');
      close(g.slope, mirror.slope, 3e-13, 'Slope reflection');
    }
  }
}

for (const a of [M.minimum, M.critical, M.maximum]) {
  for (const phase of [-.001, 0, .001]) {
    for (const y of [-24, -3, 0, 10, 25]) {
      const g = M.gap(y, a, phase);
      const dy = .001, da = 1e-5;
      close((M.gap(y + dy, a, phase).value - M.gap(y - dy, a, phase).value) / (2 * dy),
        g.slope, 2e-9, 'Height derivative');
      close((M.gap(y + dy, a, phase).slope - M.gap(y - dy, a, phase).slope) / (2 * dy),
        g.curvature, 1e-10, 'Height curvature');
      close((M.gap(y, a + da, phase).value - M.gap(y, a - da, phase).value) / (2 * da),
        g.weight, 2e-6, 'Weight derivative');
      close((M.gap(y, a + da, phase).slope - M.gap(y, a - da, phase).slope) / (2 * da),
        g.slopeWeight, 2e-7, 'Slope weight derivative');
    }
  }
}

for (let j = -100; j <= 100; j++) {
  const phase = j / 100000;
  const c = M.contact(phase), reflected = M.contact(-phase);
  const g = M.gap(c.height, c.weight, phase);
  close(g.value, 0, 1e-10, 'Contact position');
  close(g.slope, 0, 1e-11, 'Contact slope');
  close(c.height, -reflected.height, 1e-9, 'Contact reflection height');
  close(c.weight, reflected.weight, 1e-12, 'Contact reflection weight');
  for (const [offset, expected] of [[-.001, 1], [0, phase === 0 ? 1 : 2], [.001, 3]]) {
    const a = c.weight + offset, meetings = M.meetings(a, phase);
    check(meetings.length === expected, `Wrong meeting count at phase ${phase}, offset ${offset}.`);
    for (const meeting of meetings) {
      const residual = M.gap(meeting.height, a, phase);
      close(residual.value, 0, 2e-10, 'Meeting residual');
      check(Math.abs(meeting.height) <= 32, 'A marker left the height window.');
      if (meeting.kind === 'touch') close(residual.slope, 0, 1e-10, 'Touch slope');
      else if (meeting.kind === 'crossing') check(Math.abs(residual.slope) > 1e-7, 'A crossing is unresolved.');
    }
  }
}

for (const [phase, weight, height] of [[.001, .142248319367, 10.504076656],
  [-.001, .142248319367, -10.504076656], [.0001, .140093630361, 4.907289851],
  [-.0001, .140093630361, -4.907289851], [.00001, .139631799872, 2.280964329],
  [.000001, .139532411843, 1.059050717]]) {
  const c = M.contact(phase);
  close(c.weight, weight, 6e-13, 'Certified-example rounded weight');
  close(c.height, height, 6e-10, 'Certified-example rounded height');
}

let prior = Infinity;
for (const phase of [1e-3, 1e-4, 1e-5, 1e-6]) {
  const c = M.contact(phase);
  const error = Math.abs((c.weight - M.critical) / c.prediction - 1);
  check(error < prior && error < .006, 'The two-thirds asymptotic is not converging.');
  prior = error;
}

function distance(p, q) {
  const dx = q[0] - p[0], dy = q[1] - p[1], norm = dx * dx + dy * dy;
  const t = norm ? Math.max(0, Math.min(1, -(p[0] * dx + p[1] * dy) / norm)) : 0;
  return Math.hypot(p[0] + t * dx, p[1] + t * dy);
}
function turns(points, error) {
  let angle = 0;
  for (let j = 0; j < points.length - 1; j++) {
    const p = points[j], q = points[j + 1];
    check(distance(p, q) > error, 'An angle polygon lacks a smooth-curve clearance bound.');
    angle += Math.atan2(p[0] * q[1] - p[1] * q[0], p[0] * q[0] + p[1] * q[1]);
  }
  return angle / (2 * Math.PI);
}
for (const phase of [-.001, 0, .001]) {
  for (let j = 0; j <= 10; j++) {
    const a = M.minimum + (M.maximum - M.minimum) * j / 10;
    const steps = 4096, h = 2 * Math.PI / steps;
    for (const [order, expected] of [[0, 1], [1, 0]]) {
      const points = Array.from({ length: steps + 1 }, (_, k) => independent(-Math.PI + h * k, a, phase, order));
      const derivativeBound = 300 + 140 * ((1 - a) * 2 ** (order + 2) + a * 4 ** (order + 2)) +
        65 * ((1 - a) * 3 ** (order + 2) + a * 7 ** (order + 2));
      close(turns(points, derivativeBound * h * h / 8), expected, 1e-11, 'Smooth sampled turn count');
    }
  }
}

console.log(`${checks.toLocaleString('en-US')} geometry checks passed.`);
console.log(`Largest independent position discrepancy: ${maximumPositionError.toExponential(3)} drawing units.`);
console.log('All 201 phase settings give 1 / 2 / 3 local meetings across the contact (1 / 1 / 3 at zero phase).');
console.log('At 33 sampled orbits, cleared angle polygons give center winding +1 and tangent index 0.');
