'use strict';

// Numerical drawing geometry. Rational event and coefficient certificates
// live in rhythm_tangencies.py; no floating-point drawing is a proof.
const TouchMath = (() => {
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

  function state(event, progress, reflected = false) {
    if (!Number.isFinite(progress) || progress < -100 || progress > 100) {
      throw new RangeError('The touch position must be between -100 and 100.');
    }
    const sign = reflected ? -1 : 1;
    return { event, progress, reflected: Boolean(reflected),
      weight: event.weight + event.range * progress / 100,
      times: reflected ? event.times.map(t => cycle - t).reverse() : [...event.times],
      center: [event.center[0], sign * event.center[1]],
      tangent: [event.tangent[0], sign * event.tangent[1]] };
  }

  function local(s, p, vector = false) {
    const x = p[0] - (vector ? 0 : s.center[0]), y = p[1] - (vector ? 0 : s.center[1]);
    const [ex, ey] = s.tangent;
    return [ex * x + ey * y, -ey * x + ex * y];
  }

  function branch(s, index, x) {
    const seed = s.times[index];
    let t = seed;
    for (let k = 0; k < 9; k++) {
      const p = local(s, orbit(t, s.weight)), v = local(s, orbit(t, s.weight, 1), true);
      if (Math.abs(v[0]) < 300) throw new RangeError('The selected branch left its graph chart.');
      t -= (p[0] - x) / v[0];
    }
    const point = orbit(t, s.weight), p = local(s, point);
    const v = local(s, orbit(t, s.weight, 1), true);
    const a = local(s, orbit(t, s.weight, 2), true);
    if (Math.abs(p[0] - x) > 1e-8 || Math.abs(t - seed) > .04) {
      throw new RangeError('The branch inversion did not converge inside its local chart.');
    }
    return { t, point, x: p[0], y: p[1], slope: v[1] / v[0],
      curvature: (a[1] * v[0] - a[0] * v[1]) / v[0] ** 3, direction: Math.sign(v[0]) };
  }

  function gap(s, x) {
    const first = branch(s, 0, x), second = branch(s, 1, x);
    return { value: first.y - second.y, slope: first.slope - second.slope,
      curvature: first.curvature - second.curvature };
  }

  function bisect(fn, low, high) {
    let left = fn(low), right = fn(high);
    if (left * right > 0) throw new RangeError('A local root was not bracketed.');
    for (let k = 0; k < 42; k++) {
      const middle = (low + high) / 2, value = fn(middle);
      if (left * value > 0) { low = middle; left = value; }
      else { high = middle; right = value; }
    }
    return (low + high) / 2;
  }

  function meetings(s) {
    if (s.progress === 0) return [0]; // rounded location of the certified exact touch
    const half = s.event.half_size;
    const extremum = bisect(x => gap(s, x).slope, -half, half);
    const cuts = [-half, extremum, half], result = [];
    for (let j = 0; j < 2; j++) {
      if (gap(s, cuts[j]).value * gap(s, cuts[j + 1]).value < 0) {
        result.push(bisect(x => gap(s, x).value, cuts[j], cuts[j + 1]));
      }
    }
    const expected = Math.sign(s.progress) === s.event.pocket_side ? 2 : 0;
    if (result.length !== expected) throw new RangeError('The selected local crossing count is unresolved.');
    return result;
  }

  function area(s, roots, count = 128) {
    if (roots.length !== 2 || s.progress === 0) return 0;
    if (!Number.isInteger(count) || count <= 0 || count % 2) {
      throw new RangeError('Use a positive even number of Simpson intervals.');
    }
    const [low, high] = roots, h = (high - low) / count;
    let sum = 0;
    for (let j = 0; j <= count; j++) {
      sum += (j === 0 || j === count ? 1 : j % 2 ? 4 : 2) * gap(s, low + j * h).value;
    }
    return Math.abs(h * sum / 3);
  }

  function samples(start, end, count, fn) {
    return Array.from({ length: count + 1 }, (_, j) => fn(start + (end - start) * j / count));
  }

  return Object.freeze({ cycle, orbit, state, local, branch, gap, bisect, meetings, area, samples });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = TouchMath;
