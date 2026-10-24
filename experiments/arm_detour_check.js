'use strict';

// Independent numerical checks of the browser geometry. Exact whole-family
// guarantees are supplied by arm_detour.py and arm_detour_lens.py.
const assert = require('node:assert/strict');
const M = require('./arm_detour_math.js');
let checks = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };
const distance = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1]);
const cross = (p, q) => p[0] * q[1] - p[1] * q[0];
const dot = (p, q) => p[0] * q[0] + p[1] * q[1];
const multiply = ([x, y], [u, v]) => [x * u - y * v, x * v + y * u];

function endpoint(t, pair, length, derivative) {
  // Build integer powers of one unit vector, rather than evaluating each
  // multiple-angle cosine/sine as the browser implementation does.
  const w = [Math.cos(t), Math.sin(t)], powers = [[1, 0]];
  for (let j = 1; j <= Math.max(...pair); j++) powers.push(multiply(powers.at(-1), w));
  const [m, n] = pair;
  if (!derivative) return [length * w[0] + 140 * powers[m][0] + 65 * powers[n][0],
    length * w[1] + 140 * powers[m][1] - 65 * powers[n][1]];
  return [-length * w[1] - 140 * m * powers[m][1] - 65 * n * powers[n][1],
    length * w[0] + 140 * m * powers[m][0] - 65 * n * powers[n][0]];
}

function independentState(bridgeIndex, p) {
  const bridge = M.bridges[bridgeIndex];
  const a = Math.max(0, Math.min(1, p - 1));
  const length = 245 + (bridge.length - 245) * Math.min(p, 1, 3 - p);
  return { length, a, first: bridge.first, second: bridge.second };
}

function independent(t, bridgeIndex, p, derivative = false) {
  const s = independentState(bridgeIndex, p);
  const first = endpoint(t, s.first, s.length, derivative);
  const second = endpoint(t, s.second, s.length, derivative);
  return first.map((x, j) => (1 - s.a) * x + s.a * second[j]);
}

function chebyshevU(k, c) {
  if (k === 0) return 1;
  let previous = 1, current = 2 * c;
  for (let j = 2; j <= k; j++) [previous, current] = [current, 2 * c * current - previous];
  return current;
}

function independentRadius(s) {
  // Bisect in COSINE using the polynomial recurrence. The browser bisects
  // in orbit angle using shifted sine sums; the exact proof gives uniqueness.
  const polynomial = c => -s.length +
    140 * ((1 - s.blend) * chebyshevU(s.first[0] - 1, c) + s.blend * chebyshevU(s.second[0] - 1, c)) +
    65 * ((1 - s.blend) * chebyshevU(s.first[1] - 1, c) + s.blend * chebyshevU(s.second[1] - 1, c));
  let low = 0, high = 1;
  for (let j = 0; j < 52; j++) {
    const mid = (low + high) / 2;
    if (polynomial(mid) > 0) high = mid;
    else low = mid;
  }
  return Math.acos((low + high) / 2);
}

let largestCrossingResidual = 0;
for (let b = 0; b < 2; b++) {
  for (let j = 0; j <= 3000; j++) {
    const p = j / 1000, s = M.state(b, p);
    const t = M.cycle * ((j * 613 % 3001) / 3001);
    check(distance(M.position(t, s), independent(t, b, p)) < 5e-12, `Position, bridge ${b}, place ${p}`);
    check(distance(M.velocity(t, s), independent(t, b, p, true)) < 5e-11, `Velocity, bridge ${b}, place ${p}`);
    const point = M.position(t, s), reflected = M.position(-t, s);
    check(distance(reflected, [point[0], -point[1]]) < 1e-12, `Reflection ${b}, ${p}`);
    check(distance(point, M.position(t + M.cycle, s)) < 5e-12, `Orbit closure ${b}, ${p}`);
    check(Math.hypot(...point) >= s.length - 205 - 1e-10, `Distance from center ${b}, ${p}`);
    const h = 1e-5;
    const left = M.position(t - h, s), right = M.position(t + h, s);
    check(distance(M.velocity(t, s), right.map((x, k) => (x - left[k]) / (2 * h))) < 3e-6,
      `Independent finite difference ${b}, ${p}`);
    const window = M.centralWindow(s);
    check(window.radius > 0 && window.radius < Math.PI / 2, `Lens quarter ${b}, ${p}`);
    check(Math.abs(window.radius - independentRadius(s)) < 2e-13, `Independent cosine root ${b}, ${p}`);
    const start = M.position(window.start, s), end = M.position(window.end, s);
    const residual = Math.max(Math.abs(start[1]), Math.abs(end[1]), distance(start, end));
    largestCrossingResidual = Math.max(largestCrossingResidual, residual);
    check(residual < 3e-11, `Reflected ends meet on axis ${b}, ${p}`);
    check(M.velocity(window.end, s)[1] < 0, `Downward return to axis ${b}, ${p}`);
    const inside = M.position(Math.PI + window.radius * .99, s)[1];
    const outside = M.position(Math.PI + window.radius * 1.01, s)[1];
    check(inside > 0 && outside < 0, `Lens root brackets the return ${b}, ${p}`);
  }
  for (const join of [1, 2]) {
    for (let j = 0; j <= 100; j++) {
      const t = M.cycle * j / 100;
      for (const fn of [M.position, M.velocity]) {
        const exact = fn(t, M.state(b, join));
        check(distance(exact, fn(t, M.state(b, join - 1e-9))) < 1e-5 &&
          distance(exact, fn(t, M.state(b, join + 1e-9))) < 1e-5,
        `Both sides of join ${b}, ${join}, ${j}`);
      }
    }
  }
}

for (let j = 0; j <= 100; j++) {
  const t = M.cycle * j / 100;
  check(distance(M.position(t, M.state(0, 3)), M.position(t, M.state(1, 0))) < 1e-12,
    'Both detours share the original 4 / 7 drawing');
  check(distance(M.velocity(t, M.state(0, 3)), M.velocity(t, M.state(1, 0))) < 1e-11,
    'Both detours share the original 4 / 7 parametrization');
}

let minimumSpeed = Infinity, minimumMargin = Infinity;
for (let b = 0; b < 2; b++) {
  for (const p of [...Array.from({ length: 101 }, (_, j) => 3 * j / 100), 1, 2]) {
    const s = M.state(b, p), steps = 7200;
    const first = M.velocity(0, s);
    let previous = first, angle = 0, rayCount = 0, clearance = Infinity;
    let centerAngle = 0, previousPosition = M.position(0, s);
    for (let j = 1; j <= steps; j++) {
      const current = j === steps ? first : M.velocity(M.cycle * j / steps, s);
      const determinant = cross(previous, current);
      angle += Math.atan2(determinant, dot(previous, current));
      if (previous[1] <= 0 && current[1] > 0 && determinant > 0) rayCount++;
      if (current[1] <= 0 && previous[1] > 0 && determinant < 0) rayCount--;
      const difference = current.map((x, k) => x - previous[k]);
      const d2 = dot(difference, difference);
      const fraction = d2 ? Math.max(0, Math.min(1, -dot(previous, difference) / d2)) : 0;
      clearance = Math.min(clearance, Math.hypot(...previous.map((x, k) => x + fraction * difference[k])));
      minimumSpeed = Math.min(minimumSpeed, Math.hypot(...current));
      previous = current;
      const point = M.position(M.cycle * j / steps, s);
      centerAngle += Math.atan2(cross(previousPosition, point), dot(previousPosition, point));
      previousPosition = point;
    }
    const jerkBound = s.length + 140 * ((1 - s.blend) * s.first[0] ** 3 + s.blend * s.second[0] ** 3) +
      65 * ((1 - s.blend) * s.first[1] ** 3 + s.blend * s.second[1] ** 3);
    const error = jerkBound * (M.cycle / steps) ** 2 / 8;
    minimumMargin = Math.min(minimumMargin, clearance - error);
    check(clearance > error, `Smooth velocity trace clears zero, bridge ${b}, place ${p}`);
    check(Math.abs(angle / M.cycle) < 1e-10 && rayCount === 0, `Two independent tangent counts ${b}, ${p}`);
    check(Math.abs(centerAngle / M.cycle - 1) < 1e-10, `Center count ${b}, ${p}`);
  }
}

console.log(`${checks.toLocaleString('en-US')} detour geometry checks passed.`);
console.log(`Largest lens-end residual: ${largestCrossingResidual.toPrecision(5)} drawing units.`);
console.log(`Smallest sampled speed: ${minimumSpeed.toPrecision(8)}; velocity polygon margin: ${minimumMargin.toPrecision(8)}.`);
