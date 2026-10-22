'use strict';

// Independent checks of the browser's continuous angle choices, including
// the places where a principal atan2 angle jumps by a whole turn.
const assert = require('node:assert/strict');
const math = require('./two_lobes_math.js');
const winding = require('./winding_math.js');
const { cycle, firstVisit, secondVisit, position, velocity, turns } = math;
const steps = 100000;
const angle = (p, q) => Math.atan2(p[0] * q[1] - p[1] * q[0], p[0] * q[0] + p[1] * q[1]);
const close = (a, b, tolerance = 1e-10) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);
let centerSum = 0;
let tangentSum = 0;
let previousPoint = position(0);
let previousVelocity = velocity(0);
let maximumError = 0;
for (let i = 0; i <= steps; i++) {
  const fraction = i / steps;
  const point = position(cycle * fraction);
  const direction = velocity(cycle * fraction);
  centerSum += angle(previousPoint, point) / cycle;
  tangentSum += angle(previousVelocity, direction) / cycle;
  const result = turns(fraction);
  maximumError = Math.max(maximumError, Math.abs(centerSum - result.center), Math.abs(tangentSum - result.tangent));
  assert.ok(maximumError < 1e-10, `Angle lift failed at ${fraction}`);
  previousPoint = point;
  previousVelocity = direction;
}
close(centerSum, 1);
close(tangentSum, 0);

// Perturb every cut of the velocity's principal argument and the endpoints.
for (const c of [(-28 + Math.sqrt(394)) / 78, (-28 - Math.sqrt(394)) / 78]) {
  for (const fraction of [Math.acos(c) / cycle, 1 - Math.acos(c) / cycle]) {
    const before = turns(fraction - 1e-9).tangent;
    const after = turns(fraction + 1e-9).tangent;
    assert.ok(Math.abs(before - after) < 1e-7);
  }
}
for (const f of [1e-9, 0.5 - 1e-9, 0.5 + 1e-9, 1 - 1e-9]) {
  assert.ok(Math.abs(turns(f).tangent) < 1e-7);
}
const a = position(cycle * firstVisit);
const b = position(cycle * secondVisit);
close(a[0], b[0]);
close(a[1], b[1]);
close(turns(firstVisit).center, 0.5);
close(turns(secondVisit).center, 0.5);
assert.ok(turns(firstVisit).tangent > 0 && turns(firstVisit).tangent < 0.5);
assert.ok(turns(secondVisit).tangent < 0 && turns(secondVisit).tangent > -0.5);
close(turns(firstVisit).tangent, -turns(secondVisit).tangent);

// Region labels use a separate signed-crossing implementation. Clearance
// transfers each sampled-polygon answer to the smooth curve.
const polygon = winding.orbit(2, 3);
for (const [x, y, expected] of [[0, 0, 1], [-150, 0, -1], [-200, 0, 0]]) {
  const result = winding.inspect(polygon, x, y);
  assert.equal(result.count, expected);
  assert.ok(result.distance > winding.errorBound(2, 3));
}

// Check the analytic area primitive by independent midpoint integration.
let integral = 0;
for (let i = 0; i < steps; i++) {
  const t = cycle * (firstVisit + (secondVisit - firstVisit) * (i + 0.5) / steps);
  const [x, y] = position(t);
  const [vx, vy] = velocity(t);
  integral += (x * vy - y * vx) * cycle * (secondVisit - firstVisit) / (2 * steps);
}
close(integral, math.areaPrimitive(cycle * secondVisit) - math.areaPrimitive(cycle * firstVisit), 1e-5);
console.log(`${steps + 1} angle-lift comparisons passed; maximum error ${maximumError.toExponential(3)}.`);
console.log('Crossing visits, branch cuts, smooth region labels, and lobe area checks passed.');
