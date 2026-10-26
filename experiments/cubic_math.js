'use strict';

// The leading model, not the exact orbital drawing. The note cubic_pockets.md
// derives its normalization and the scope of its limiting area laws.
const CubicMath = (() => {
  const tiltScale = 2 / (3 * Math.sqrt(3));
  const limits = Object.freeze({ opening: [-.5, 1.5], tilt: [-1.5, 1.5], height: 1.65 });
  const value = (v, opening, tilt) => v * (v * v - opening) + tiltScale * tilt;

  function bisect(fn, low, high) {
    let left = fn(low);
    if (left === 0) return low;
    if (fn(high) === 0) return high;
    for (let j = 0; j < 64; j++) {
      const mid = (low + high) / 2;
      if (mid === low || mid === high) break;
      const next = fn(mid);
      if (next === 0) return mid;
      if ((left < 0) === (next < 0)) { low = mid; left = next; }
      else high = mid;
    }
    return (low + high) / 2;
  }

  function state(opening, tilt) {
    if (!Number.isFinite(opening) || !Number.isFinite(tilt) ||
        opening < limits.opening[0] || opening > limits.opening[1] ||
        tilt < limits.tilt[0] || tilt > limits.tilt[1]) {
      throw new RangeError('Parameters outside the cubic explorer.');
    }
    const discriminant = opening ** 3 - tilt ** 2;
    // Floating-point boundary recognition, relative to the terms being
    // subtracted. This does not thicken the cusp by a fixed absolute amount.
    const tolerance = 16 * Number.EPSILON * (Math.abs(opening ** 3) + tilt ** 2);
    let kind, all, meetings;
    if (opening === 0 && tilt === 0) {
      kind = 'cubic'; all = [0, 0, 0];
      meetings = [{ v: 0, kind: 'cubic' }];
    } else if (opening > 0 && Math.abs(discriminant) <= tolerance) {
      kind = 'touch';
      const s = Math.sign(tilt) * Math.sqrt(opening / 3);
      all = [-2 * s, s, s].sort((a, b) => a - b);
      meetings = [{ v: -2 * s, kind: 'crossing' }, { v: s, kind: 'touch' }]
        .sort((a, b) => a.v - b.v);
    } else if (discriminant > 0) {
      kind = 'three';
      const s = Math.sqrt(opening / 3), fn = v => value(v, opening, tilt);
      all = [[-2, -s], [-s, s], [s, 2]].map(([low, high]) => bisect(fn, low, high));
      meetings = all.map(v => ({ v, kind: 'crossing' }));
    } else {
      kind = 'one';
      meetings = [{ v: bisect(v => value(v, opening, tilt), -2, 2), kind: 'crossing' }];
    }
    const pockets = all ? [0, 1].map(j => {
      const low = all[j], high = all[j + 1], third = all[j === 0 ? 2 : 0];
      // Integral of |(v-low)(v-high)(v-third)| on [low, high].
      // Factoring the interval width avoids antiderivative cancellation
      // when two roots coalesce.
      const area = Math.abs(third - (low + high) / 2) * (high - low) ** 3 / 6;
      return { low, high, area };
    }) : [];
    return { opening, tilt, discriminant, kind, meetings, pockets };
  }

  function bezier(opening, tilt, low, high) {
    // q(v) is a cubic and v is affine, so these are exact Bezier controls
    // before floating-point rounding. The SVG needs no polygon sampling.
    const a = value(low, opening, tilt), b = value(high, opening, tilt);
    const span = (high - low) / 3;
    return [[a, low], [a + span * (3 * low * low - opening), low + span],
      [b - span * (3 * high * high - opening), high - span], [b, high]];
  }

  return Object.freeze({ tiltScale, limits, value, state, bezier });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = CubicMath;
