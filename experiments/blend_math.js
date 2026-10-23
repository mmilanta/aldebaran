'use strict';

// Positive y is up. No browser dependencies. Algebraic event locations are
// rounded here; blend_cusps.py certifies their isolation and completeness.
const BlendMath = (() => {
  const cycle = 2 * Math.PI;
  const events = Object.freeze([
    Object.freeze({ blend: 0.22629590822544784, time: 1.5042508087214244 }),
    Object.freeze({ blend: 0.5089319824608064, time: 1.6370701415951053 })
  ]);
  const cuspTolerance = 5e-13;

  function position(t, a) {
    return [245 * Math.cos(t) + 140 * ((1 - a) * Math.cos(2 * t) + a * Math.cos(4 * t)) +
      65 * ((1 - a) * Math.cos(3 * t) + a * Math.cos(7 * t)),
    245 * Math.sin(t) + 140 * ((1 - a) * Math.sin(2 * t) + a * Math.sin(4 * t)) -
      65 * ((1 - a) * Math.sin(3 * t) + a * Math.sin(7 * t))];
  }

  function velocity(t, a) {
    return [-245 * Math.sin(t) - 140 * (2 * (1 - a) * Math.sin(2 * t) + 4 * a * Math.sin(4 * t)) -
      65 * (3 * (1 - a) * Math.sin(3 * t) + 7 * a * Math.sin(7 * t)),
    245 * Math.cos(t) + 140 * (2 * (1 - a) * Math.cos(2 * t) + 4 * a * Math.cos(4 * t)) -
      65 * (3 * (1 - a) * Math.cos(3 * t) + 7 * a * Math.cos(7 * t))];
  }

  function acceleration(t, a) {
    return [-245 * Math.cos(t) - 140 * (4 * (1 - a) * Math.cos(2 * t) + 16 * a * Math.cos(4 * t)) -
      65 * (9 * (1 - a) * Math.cos(3 * t) + 49 * a * Math.cos(7 * t)),
    -245 * Math.sin(t) - 140 * (4 * (1 - a) * Math.sin(2 * t) + 16 * a * Math.sin(4 * t)) +
      65 * (9 * (1 - a) * Math.sin(3 * t) + 49 * a * Math.sin(7 * t))];
  }

  function tangentIndex(a) {
    if (events.some(event => Math.abs(a - event.blend) <= cuspTolerance)) return null;
    return a > events[0].blend && a < events[1].blend ? -2 : 0;
  }

  const complexProduct = ([x, y], [u, v]) => [x * u - y * v, x * v + y * u];
  function complexQuotient([x, y], [u, v]) {
    const norm2 = u * u + v * v;
    return [(x * u + y * v) / norm2, (y * u - x * v) / norm2];
  }

  // z_safe = exp(it) exp((1-a) Log f_A + a Log f_B). Both f's have
  // positive real part, so their principal logarithms are continuous and
  // periodic. regular_blend.py proves the velocity never vanishes for ANY a.
  function regularState(t, a, order) {
    const fA = [245 + 140 * Math.cos(t) + 65 * Math.cos(4 * t),
      140 * Math.sin(t) - 65 * Math.sin(4 * t)];
    const fB = [245 + 140 * Math.cos(3 * t) + 65 * Math.cos(8 * t),
      140 * Math.sin(3 * t) - 65 * Math.sin(8 * t)];
    const radius = Math.exp((1 - a) * Math.log(Math.hypot(...fA)) + a * Math.log(Math.hypot(...fB)));
    const angle = t + (1 - a) * Math.atan2(fA[1], fA[0]) + a * Math.atan2(fB[1], fB[0]);
    const p = [radius * Math.cos(angle), radius * Math.sin(angle)];
    if (order === 0) return p;
    const pA = position(t, 0), pB = position(t, 1);
    const qA = complexQuotient(velocity(t, 0), pA);
    const qB = complexQuotient(velocity(t, 1), pB);
    const q = qA.map((x, i) => (1 - a) * x + a * qB[i]);
    if (order === 1) return complexProduct(p, q);
    const rA = complexQuotient(acceleration(t, 0), pA);
    const rB = complexQuotient(acceleration(t, 1), pB);
    const qA2 = complexProduct(qA, qA), qB2 = complexProduct(qB, qB);
    const qPrime = rA.map((x, i) => (1 - a) * (x - qA2[i]) + a * (rB[i] - qB2[i]));
    const q2 = complexProduct(q, q);
    return complexProduct(p, q2.map((x, i) => x + qPrime[i]));
  }

  const regularPosition = (t, a) => a === 0 || a === 1 ? position(t, a) : regularState(t, a, 0);
  const regularVelocity = (t, a) => a === 0 || a === 1 ? velocity(t, a) : regularState(t, a, 1);
  const regularAcceleration = (t, a) => a === 0 || a === 1 ? acceleration(t, a) : regularState(t, a, 2);

  // This orientation is fixed at the selected event. The drawing is translated
  // to its marked parameter point, without changing the scale of either axis.
  function lensVector([dx, dy], eventIndex) {
    const event = events[eventIndex];
    const direction = acceleration(event.time, event.blend);
    const length = Math.hypot(...direction);
    const ux = direction[0] / length;
    const uy = direction[1] / length;
    return [-dx * ux - dy * uy, dx * uy - dy * ux];
  }

  function lensPoint(t, a, eventIndex, evaluate = position) {
    const origin = evaluate(events[eventIndex].time, a);
    const p = evaluate(t, a);
    return lensVector([p[0] - origin[0], p[1] - origin[1]], eventIndex);
  }

  return Object.freeze({ cycle, events, cuspTolerance, position, velocity,
    acceleration, tangentIndex, lensPoint, lensVector,
    regularPosition, regularVelocity, regularAcceleration });
})();

if (typeof module !== 'undefined') module.exports = BlendMath;
