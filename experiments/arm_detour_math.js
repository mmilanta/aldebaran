'use strict';

// Positive y is up. The full-family speed certificates are in arm_detour.py;
// floating-point geometry here is only for the still drawings and their lens.
const ArmDetourMath = (() => {
  const cycle = 2 * Math.PI;
  const bridges = Object.freeze([
    Object.freeze({ first: Object.freeze([2, 3]), second: Object.freeze([4, 7]), length: 300 }),
    Object.freeze({ first: Object.freeze([4, 7]), second: Object.freeze([6, 11]), length: 700 })
  ]);

  function state(bridgeIndex, progress) {
    const bridge = bridges[bridgeIndex];
    const p = Math.max(0, Math.min(3, progress));
    const leg = Math.min(2, Math.floor(p));
    const fraction = p - leg;
    const length = leg === 0 ? 245 + (bridge.length - 245) * fraction
      : leg === 1 ? bridge.length : bridge.length + (245 - bridge.length) * fraction;
    return { first: bridge.first, second: bridge.second,
      length, blend: leg === 0 ? 0 : leg === 1 ? fraction : 1,
      leg, fraction, progress: p };
  }

  function evaluate(t, s, derivative) {
    const { first: [m, n], second: [p, q], length, blend: a } = s;
    // Explicit signed-frequency derivatives avoid accumulating finite
    // differences in either the tangent arrows or the numerical lens.
    const terms = [[length, 1], [140 * (1 - a), m], [140 * a, p],
      [65 * (1 - a), -n], [65 * a, -q]];
    let x = 0, y = 0;
    for (const [radius, frequency] of terms) {
      const angle = frequency * t;
      if (derivative === 0) {
        x += radius * Math.cos(angle);
        y += radius * Math.sin(angle);
      } else {
        x -= radius * frequency * Math.sin(angle);
        y += radius * frequency * Math.cos(angle);
      }
    }
    return [x, y];
  }

  const position = (t, s) => evaluate(t, s, 0);
  const velocity = (t, s) => evaluate(t, s, 1);

  function centralWindow(s) {
    // arm_detour_lens.py proves a unique noncentral axis crossing in this
    // quarter orbit, continuously along both detours. Reflection makes
    // the arc's ends meet. The arc may also intersect itself in between.
    // The shifted sine sum avoids loss of precision near pi.
    const height = u => -s.length * Math.sin(u) +
      140 * ((1 - s.blend) * Math.sin(s.first[0] * u) + s.blend * Math.sin(s.second[0] * u)) +
      65 * ((1 - s.blend) * Math.sin(s.first[1] * u) + s.blend * Math.sin(s.second[1] * u));
    let low = 0, high = Math.PI / 2;
    for (let j = 0; j < 52; j++) {
      const mid = (low + high) / 2;
      if (height(mid) > 0) low = mid;
      else high = mid;
    }
    const radius = (low + high) / 2;
    return { start: Math.PI - radius, end: Math.PI + radius, radius };
  }

  return Object.freeze({ cycle, bridges, state, position, velocity, centralWindow });
})();

if (typeof module !== 'undefined') module.exports = ArmDetourMath;
