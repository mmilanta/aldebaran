'use strict';

// Algebraic and independent quadrature checks of the model. These do not
// certify the higher-order terms of the actual orbital family.
const assert = require('node:assert/strict');
const M = require('./cubic_math.js');
let checks = 0, maximumResidual = 0;
function check(condition, message) { checks++; assert.ok(condition, message); }
function close(a, b, tolerance, message) {
  check(Math.abs(a - b) <= tolerance, `${message}: ${a} vs ${b}`);
}

// All 60,501 combinations of the two native sliders. Integer arithmetic
// classifies the discriminant independently of the floating-point solver.
for (let i = -50; i <= 150; i++) {
  for (let j = -150; j <= 150; j++) {
    const mu = i / 100, tau = j / 100, data = M.state(mu, tau);
    const sign = i ** 3 - 100 * j ** 2;
    const expected = i === 0 && j === 0 ? 'cubic' : sign === 0 ? 'touch' : sign > 0 ? 'three' : 'one';
    check(data.kind === expected, 'The integer discriminant disagrees.');
    check(data.meetings.length === ({ cubic: 1, touch: 2, three: 3, one: 1 })[expected], 'Wrong distinct root count.');
    for (const meeting of data.meetings) {
      const v = meeting.v;
      // Evaluate in a different order from the solver.
      const residual = Math.abs(v ** 3 - mu * v + 2 * tau / Math.sqrt(27));
      maximumResidual = Math.max(maximumResidual, residual);
      check(residual < 3e-15, 'A meeting is not a root.');
      check(Math.abs(v) < M.limits.height, 'A meeting left the view.');
    }
    const reflection = M.state(mu, -tau);
    close(reflection.meetings.length, data.meetings.length, 0, 'Reflection root count');
    data.meetings.forEach((meeting, k) => {
      close(meeting.v, -reflection.meetings.at(-1 - k).v, 2e-15, 'Reflection height');
    });
    if (data.pockets.length) {
      const [a, b] = data.pockets;
      const roots = [a.low, a.high, b.high];
      close(roots.reduce((x, y) => x + y), 0, 2e-15, 'Vieta sum');
      close(roots[0] * roots[1] + roots[1] * roots[2] + roots[2] * roots[0], -mu, 3e-15, 'Vieta pairs');
      close(roots.reduce((x, y) => x * y, 1), -M.tiltScale * tau, 3e-15, 'Vieta product');
      data.pockets.forEach((pocket, k) => {
        const { low, high, area } = pocket;
        check(high >= low && area >= 0, 'Pocket order or area is negative.');
        // Simpson integrates a cubic exactly. This evaluates the original
        // polynomial, rather than the factored area formula under test.
        const f = v => v ** 3 - mu * v + 2 * tau / Math.sqrt(27);
        const integral = Math.abs((high - low) / 6 * (f(low) + 4 * f((low + high) / 2) + f(high)));
        close(area, integral, 2e-15, 'Independent polynomial integral');
        close(area, reflection.pockets[1 - k].area, 2e-15, 'Reflection pocket area');
      });
      if (tau === 0) {
        close(a.area, mu ** 2 / 4, 2e-15, 'Mirror area');
        close(b.area, mu ** 2 / 4, 2e-15, 'Other mirror area');
      }
    }
  }
}

// The exact Bezier must match the cubic between its controls, including
// short intervals where a pocket is almost closed.
for (const mu of [-.5, 0, .25, 1, 1.5]) {
  for (const tau of [-1.5, -1, 0, .9, 1, 1.5]) {
    for (const [low, high] of [[-1.65, 1.65], [-.1, .2], [.577, .578]]) {
      const p = M.bezier(mu, tau, low, high);
      for (let j = 0; j <= 32; j++) {
        const t = j / 32, u = 1 - t, v = low + t * (high - low);
        const weights = [u ** 3, 3 * u * u * t, 3 * u * t * t, t ** 3];
        close(p.reduce((sum, q, k) => sum + weights[k] * q[0], 0),
          v ** 3 - mu * v + M.tiltScale * tau, 5e-15, 'Bezier separation');
        close(p.reduce((sum, q, k) => sum + weights[k] * q[1], 0), v, 1e-15, 'Bezier height');
      }
    }
  }
}

// A relative boundary tolerance must still distinguish the three cases
// arbitrarily close to the cusp, across many scales.
for (const mu of [1, .01, 1e-6, 1e-12, 1e-20]) {
  const boundary = mu ** 1.5;
  for (const sign of [-1, 1]) {
    check(M.state(mu, sign * boundary).kind === 'touch', 'Missed scaled boundary.');
    check(M.state(mu, sign * boundary * (1 - 1e-8)).kind === 'three', 'Interior rounded to boundary.');
    check(M.state(mu, sign * boundary * (1 + 1e-8)).kind === 'one', 'Exterior rounded to boundary.');
  }
}

let previous = Infinity;
for (const epsilon of [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]) {
  const area = M.state(1 + epsilon, 1).pockets[1].area;
  const ratio = area / (4 / 9 * epsilon ** 1.5);
  check(Math.abs(ratio - 1) < .004 && Math.abs(ratio - 1) < previous,
    'The tilted area is not converging to its three-halves law.');
  previous = Math.abs(ratio - 1);
}
close(M.state(1, 1).pockets[0].area, .75, 1e-15, 'Surviving pocket at touch');
close(M.state(1, 1).pockets[1].area, 0, 0, 'Closed pocket at touch');
// This is far below the precision at which subtracting two large
// antiderivative values would give a reliable pocket area.
const tiny = M.state(1 + 1e-10, 1).pockets[1].area;
check(tiny > 0 && Math.abs(tiny / (4 / 9 * 1e-15) - 1) < 1e-5, 'Lost a tiny pocket area.');
for (const values of [[NaN, 0], [0, Infinity], [-.51, 0], [1.51, 0], [0, 1.51], [0, -1.51], ['1', 0]]) {
  checks++; assert.throws(() => M.state(...values), RangeError);
}
console.log(`${checks.toLocaleString('en-US')} cubic checks passed; largest root residual ${maximumResidual.toExponential(3)}.`);
