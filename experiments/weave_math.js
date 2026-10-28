'use strict';

// Floating-point drawing geometry. Integer endpoint data and the rational
// continuous-window proofs are generated separately; see rhythm_passages.md.
const WeaveMath = (() => {
  const cycle = 2 * Math.PI;

  function orbit(t, a, order = 0) {
    let x = 0, y = 0;
    for (const [r, k] of [[245, 1], [140, 11], [65 * (1 - a), -6], [65 * a, -8]]) {
      const angle = k * t + order * Math.PI / 2;
      x += r * k ** order * Math.cos(angle);
      y += r * k ** order * Math.sin(angle);
    }
    return [x, y];
  }

  function state(event, progress, reflected) {
    if (!Number.isFinite(progress) || progress < -100 || progress > 100) {
      throw new RangeError('The passage position must be between -100 and 100.');
    }
    const times = reflected ? event.times.map(t => cycle - t).reverse() : [...event.times];
    return { times, weight: event.weight + .003 * progress / 100,
      center: [event.center[0], event.center[1] * (reflected ? -1 : 1)],
      halfSize: event.half_size, progress, reflected: Boolean(reflected) };
  }

  function intersection(s, first, second) {
    let t = s.times[first], u = s.times[second];
    for (let k = 0; k < 12; k++) {
      const p = orbit(t, s.weight), q = orbit(u, s.weight);
      const v = orbit(t, s.weight, 1), w = orbit(u, s.weight, 1);
      const fx = p[0] - q[0], fy = p[1] - q[1];
      const determinant = v[1] * w[0] - v[0] * w[1];
      if (Math.abs(determinant) < 1) throw new RangeError('The selected crossing is unresolved.');
      t -= (-w[1] * fx + w[0] * fy) / determinant;
      u -= (-v[1] * fx + v[0] * fy) / determinant;
    }
    const p = orbit(t, s.weight), q = orbit(u, s.weight);
    if (Math.hypot(p[0] - q[0], p[1] - q[1]) > 1e-7 ||
        Math.abs(t - s.times[first]) > .02 || Math.abs(u - s.times[second]) > .02) {
      throw new RangeError('The selected crossing left its local branches.');
    }
    return { times: [t, u], point: p };
  }

  function triangle(s) {
    const ab = intersection(s, 0, 1), bc = intersection(s, 1, 2), ac = intersection(s, 0, 2);
    return { crossings: [ab, bc, ac], edges: [
      { start: ab.times[1], end: bc.times[0], branch: 1 },
      { start: bc.times[1], end: ac.times[1], branch: 2 },
      { start: ac.times[0], end: ab.times[0], branch: 0 }
    ] };
  }

  function points(start, end, count, weight) {
    return Array.from({ length: count + 1 }, (_, j) => orbit(start + (end - start) * j / count, weight));
  }

  return Object.freeze({ cycle, orbit, state, intersection, triangle, points });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = WeaveMath;
