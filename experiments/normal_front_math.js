'use strict';

// Numerical drawing geometry, not a crossing census. See normal_front.md.
const NormalFrontMath = (() => {
  const orbitMath = typeof module !== 'undefined' && module.exports
    ? require('./weave_math.js') : WeaveMath;
  const cycle = 2 * Math.PI, turns = 11;

  function rhythm(inner) {
    if (inner !== 6 && inner !== 8) throw new RangeError('Choose inner rhythm 6 or 8.');
  }

  function orbit(t, inner, order = 0) {
    rhythm(inner);
    return orbitMath.orbit(t, (inner - 6) / 2, order);
  }

  // z' = i exp(11it) B, Re B >= 775. Its principal argument has no seam.
  // The left normal's continuous angle is pi + normalTurn(t, inner).
  function normalTurn(t, inner) {
    rhythm(inner);
    const real = 1540 + 245 * Math.cos(10 * t) - 65 * inner * Math.cos((11 + inner) * t);
    const imag = -245 * Math.sin(10 * t) + 65 * inner * Math.sin((11 + inner) * t);
    return 11 * t + Math.atan2(imag, real);
  }

  function timeAt(turn, inner) {
    rhythm(inner);
    if (!Number.isFinite(turn) || turn < 0 || turn > turns * cycle) {
      throw new RangeError('The normal turn must lie in one complete orbit.');
    }
    if (turn === 0) return 0;
    if (turn === turns * cycle) return cycle;
    // |arg B| < pi/2, and the positive-curvature bound proves uniqueness.
    let low = Math.max(0, (turn - Math.PI / 2) / 11);
    let high = Math.min(cycle, (turn + Math.PI / 2) / 11);
    for (let i = 0; i < 46; i++) {
      const middle = (low + high) / 2;
      if (normalTurn(middle, inner) < turn) low = middle;
      else high = middle;
    }
    return (low + high) / 2;
  }

  function visit(beta, branch, inner) {
    if (!Number.isFinite(beta) || beta < 0 || beta > cycle ||
        !Number.isInteger(branch) || branch < 0 || branch >= turns) {
      throw new RangeError('Choose a turn in [0, 2pi] and one of eleven visits.');
    }
    const t = timeAt(beta + branch * cycle, inner);
    const point = orbit(t, inner), theta = Math.PI + beta;
    const normal = [Math.cos(theta), Math.sin(theta)];
    const distance = point[0] * normal[0] + point[1] * normal[1];
    const slope = -point[0] * normal[1] + point[1] * normal[0];
    return { t, point, normal, distance, slope, beta, branch, inner };
  }

  function front(inner, steps = 360) {
    rhythm(inner);
    if (!Number.isInteger(steps) || steps < 4 || steps > 4096) {
      throw new RangeError('Use between 4 and 4096 samples per strand.');
    }
    return Array.from({ length: turns }, (_, branch) =>
      Array.from({ length: steps + 1 }, (_, i) => {
        const beta = cycle * i / steps;
        return [beta, visit(beta, branch, inner).distance];
      }));
  }

  // A sign-changing bracket for one selected pair. This locates an example;
  // it neither counts all bitangents nor certifies their transversality.
  function sharedTangent(inner, first, second, low, high) {
    rhythm(inner);
    if (first === second || !(0 <= low && low < high && high <= cycle)) {
      throw new RangeError('Choose two different visits and a bracket in one turn.');
    }
    const gap = beta => visit(beta, first, inner).distance - visit(beta, second, inner).distance;
    let lowValue = gap(low);
    if (!(lowValue * gap(high) < 0)) throw new RangeError('The shared-tangent bracket has no sign change.');
    for (let i = 0; i < 44; i++) {
      const middle = (low + high) / 2, value = gap(middle);
      if (Math.sign(value) === Math.sign(lowValue)) { low = middle; lowValue = value; }
      else high = middle;
    }
    const beta = (low + high) / 2;
    return { beta, visits: [visit(beta, first, inner), visit(beta, second, inner)] };
  }

  return Object.freeze({ cycle, turns, orbit, normalTurn, timeAt, visit, front, sharedTangent });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = NormalFrontMath;
