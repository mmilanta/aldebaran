'use strict';

// Mathematical coordinates, with positive y up. No browser dependencies.
const TwoLobesMath = (() => {
  const cycle = 2 * Math.PI;
  const crossingTime = Math.acos((14 - Math.sqrt(1002)) / 26);
  const firstVisit = crossingTime / cycle;
  const secondVisit = 1 - firstVisit;

  function position(t) {
    return [245 * Math.cos(t) + 140 * Math.cos(2 * t) + 65 * Math.cos(3 * t),
      245 * Math.sin(t) + 140 * Math.sin(2 * t) - 65 * Math.sin(3 * t)];
  }

  function velocity(t) {
    return [-245 * Math.sin(t) - 280 * Math.sin(2 * t) - 195 * Math.sin(3 * t),
      245 * Math.cos(t) + 280 * Math.cos(2 * t) - 195 * Math.cos(3 * t)];
  }

  function turns(fraction) {
    if (fraction === 0 || fraction === 1) return { center: fraction, tangent: 0 };
    if (fraction === 0.5) return { center: 0.5, tangent: 0 };
    const t = cycle * fraction;
    // z(t) = exp(it) [245 + 140 exp(it) + 65 exp(-4it)].
    // The bracket's real part is >= 40, so this argument is continuous.
    const center = (t + Math.atan2(140 * Math.sin(t) - 65 * Math.sin(4 * t),
      245 + 140 * Math.cos(t) + 65 * Math.cos(4 * t))) / cycle;
    const [vx, vy] = velocity(t);
    let tangent = Math.atan2(-vx, vy) / cycle;
    // The upward velocity ray is met only at t = 0 and pi. The angle
    // relative to that ray stays positive in (0,pi), negative in (pi,2pi).
    // See two_lobes.md for the exact polynomial sign argument.
    if (fraction < 0.5 && tangent < 0) tangent += 1;
    if (fraction > 0.5 && tangent > 0) tangent -= 1;
    return { center, tangent };
  }

  function areaPrimitive(t) {
    return 43275 * t + 51450 * Math.sin(t) -
      3981.25 * Math.sin(4 * t) - 910 * Math.sin(5 * t);
  }

  return Object.freeze({ cycle, crossingTime, firstVisit, secondVisit,
    position, velocity, turns, areaPrimitive });
})();

if (typeof module !== 'undefined') module.exports = TwoLobesMath;
