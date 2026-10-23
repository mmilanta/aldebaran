'use strict';

// Independent numerical checks of the browser formulas. The exact existence,
// completeness, and index certificates live in blend_cusps.py.
const assert = require('node:assert/strict');
const B = require('./blend_math.js');
const { cycle, events, position, velocity, acceleration, tangentIndex,
  lensPoint, lensVector, regularPosition, regularVelocity, regularAcceleration } = B;
let checks = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };
const distance = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1]);
const cross = (p, q) => p[0] * q[1] - p[1] * q[0];
const dot = (p, q) => p[0] * q[0] + p[1] * q[1];

// A separately evaluated complex Fourier sum, including its first two
// derivatives. Terms have signed frequencies; no hand-expanded formulas.
function fourier(t, a, derivative) {
  const terms = [[245, 1], [140 * (1 - a), 2], [140 * a, 4],
    [65 * (1 - a), -3], [65 * a, -7]];
  return terms.reduce((sum, [length, frequency]) => {
    const angle = frequency * t + derivative * Math.PI / 2;
    const coefficient = length * frequency ** derivative;
    return [sum[0] + coefficient * Math.cos(angle), sum[1] + coefficient * Math.sin(angle)];
  }, [0, 0]);
}

for (let j = 0; j <= 1000; j++) {
  const a = j / 1000;
  const t = cycle * ((j * 613 % 1001) / 1001);
  for (const [fn, order] of [[position, 0], [velocity, 1], [acceleration, 2]]) {
    check(distance(fn(t, a), fourier(t, a, order)) < 2e-11,
      `Fourier derivative ${order}, blend ${a}`);
  }
  const start = position(t, 0), finish = position(t, 1);
  check(distance(position(t, a), start.map((x, i) => (1 - a) * x + a * finish[i])) < 1e-12,
    `Linear position interpolation ${a}`);
  check(distance(position(-t, a), [position(t, a)[0], -position(t, a)[1]]) < 1e-12,
    `Position reflection ${a}`);
  const h = 1e-5;
  const left = position(t - h, a), right = position(t + h, a);
  check(distance(velocity(t, a), right.map((x, i) => (x - left[i]) / (2 * h))) < 1e-6,
    `Independent position difference ${a}`);
  for (let event = 0; event < 2; event++) {
    const p = position(t, a), origin = position(events[event].time, a);
    check(Math.abs(Math.hypot(...lensPoint(t, a, event)) - distance(p, origin)) < 1e-12,
      `Lens preserves distance ${event}, ${a}`);
    const v = velocity(t, a), acc = acceleration(t, a);
    const lv = lensVector(v, event), la = lensVector(acc, event);
    check(Math.abs(cross(lv, la) - cross(v, acc)) < 1e-8,
      `Lens preserves orientation ${event}, ${a}`);
  }
}

for (const event of events) {
  check(tangentIndex(event.blend) === null, 'Withhold the index at a rounded cusp');
  check(Math.hypot(...velocity(event.time, event.blend)) < 2e-10, 'Cusp velocity residual');
  check(Math.hypot(...velocity(cycle - event.time, event.blend)) < 2e-10,
    'Reflected cusp velocity residual');
  check(tangentIndex(event.blend - 1e-10) !== null &&
    tangentIndex(event.blend + 1e-10) !== null, 'Restore counts outside the warning band');
}

for (let j = 0; j <= 1000; j++) {
  const a = j / 1000;
  const t = cycle * ((j * 457 % 1001) / 1001);
  const pA = position(t, 0), pB = position(t, 1);
  const radius = Math.hypot(...pA) ** (1 - a) * Math.hypot(...pB) ** a;
  const angleDifference = Math.atan2(cross(pA, pB), dot(pA, pB));
  const angle = Math.atan2(pA[1], pA[0]) + a * angleDifference;
  const expected = [radius * Math.cos(angle), radius * Math.sin(angle)];
  check(distance(regularPosition(t, a), expected) < 3e-12,
    `Independent polar interpolation ${a}`);
  const h = 1e-5;
  for (const [fn, derivative, tolerance] of [[regularPosition, regularVelocity, 2e-6],
    [regularVelocity, regularAcceleration, 3e-5]]) {
    const left = fn(t - h, a), right = fn(t + h, a);
    check(distance(derivative(t, a), right.map((x, i) => (x - left[i]) / (2 * h))) < tolerance,
      `Regular route derivative ${a}`);
  }
  check(distance(regularPosition(-t, a), [regularPosition(t, a)[0], -regularPosition(t, a)[1]]) < 2e-12,
    `Regular route reflection ${a}`);
  check(distance(regularPosition(t + cycle, a), regularPosition(t, a)) < 5e-12,
    `Regular route closes smoothly ${a}`);
  check(Math.hypot(...regularVelocity(t, a)) > 4, `Certified family speed bound ${a}`);
  for (const end of [0, 1]) {
    check(distance(regularPosition(t, end), position(t, end)) === 0 &&
      distance(regularVelocity(t, end), velocity(t, end)) === 0 &&
      distance(regularAcceleration(t, end), acceleration(t, end)) === 0, `Matching endpoint ${end}`);
  }
}

let observedRegularMinimum = Infinity;
for (let j = 0; j <= 100; j++) {
  const a = j / 100;
  const first = regularVelocity(0, a);
  let previous = first, angle = 0;
  for (let k = 1; k <= 7200; k++) {
    const current = k === 7200 ? first : regularVelocity(cycle * k / 7200, a);
    observedRegularMinimum = Math.min(observedRegularMinimum, Math.hypot(...current));
    angle += Math.atan2(cross(previous, current), dot(previous, current));
    previous = current;
  }
  check(Math.abs(angle / cycle) < 1e-10, `Regular family numerical tangent index ${a}`);
}

let smallestMargin = Infinity;
for (let j = 0; j <= 1000; j++) {
  const a = j / 1000;
  const steps = 9600;
  const first = velocity(0, a);
  let previous = first, angle = 0, rayCount = 0, clearance = Infinity;
  for (let k = 1; k <= steps; k++) {
    const current = k === steps ? first : velocity(cycle * k / steps, a);
    const determinant = cross(previous, current);
    angle += Math.atan2(determinant, dot(previous, current));
    if (previous[1] <= 0 && current[1] > 0 && determinant > 0) rayCount++;
    if (current[1] <= 0 && previous[1] > 0 && determinant < 0) rayCount--;
    const difference = current.map((x, i) => x - previous[i]);
    const d2 = dot(difference, difference);
    const fraction = d2 ? Math.max(0, Math.min(1, -dot(previous, difference) / d2)) : 0;
    clearance = Math.min(clearance, Math.hypot(...previous.map((x, i) => x + fraction * difference[i])));
    previous = current;
  }
  // A separate interpolation bound checks that the sampled velocity polygon
  // stays far enough from zero to represent this smooth velocity trace.
  const thirdDerivativeBound = 245 + 140 * (8 * (1 - a) + 64 * a) +
    65 * (27 * (1 - a) + 343 * a);
  const error = thirdDerivativeBound * (cycle / steps) ** 2 / 8;
  check(clearance > error + 1e-8, `Velocity polygon clearance at blend ${a}`);
  smallestMargin = Math.min(smallestMargin, clearance - error);
  check(Math.abs(angle / cycle - tangentIndex(a)) < 1e-10, `Angle-sum index at blend ${a}`);
  check(rayCount === tangentIndex(a), `Independent polygon ray count at blend ${a}`);
}
console.log(`${checks.toLocaleString('en-US')} browser-math checks passed across both routes.`);
console.log(`Smallest velocity polygon clearance beyond its interpolation bound: ${smallestMargin.toPrecision(5)}.`);
console.log(`Smallest sampled speed on the regular route: ${observedRegularMinimum.toPrecision(8)} (proof gives > 4).`);
