'use strict';

// Numerical illustration of one separately certified triple. Not a census.
const ParallelOffsetMath = (() => {
  const Orbit = typeof module !== 'undefined' && module.exports ? require('./weave_math.js') : WeaveMath;
  const Data = typeof module !== 'undefined' && module.exports ? require('./parallel_offset_data.js') : ParallelOffsetData;
  const cycle = 2 * Math.PI;

  function jet(t, offset = 0) {
    if (!Number.isFinite(t) || !Number.isFinite(offset) || offset < 0) {
      throw new RangeError('Use a finite time and a nonnegative outward offset.');
    }
    const original = Orbit.orbit(t, 0), v = Orbit.orbit(t, 0, 1), a = Orbit.orbit(t, 0, 2);
    const speed = Math.hypot(...v), normal = [-v[1] / speed, v[0] / speed];
    const curvature = (v[0] * a[1] - v[1] * a[0]) / speed ** 3;
    return { original, normal, curvature,
      point: original.map((x, i) => x - offset * normal[i]),
      velocity: v.map(x => (1 + offset * curvature) * x) };
  }

  function state(progress) {
    if (!Number.isFinite(progress) || progress < -100 || progress > 100) {
      throw new RangeError('Choose a passage position between -100 and 100.');
    }
    return { progress, offset: Data.offset + .0015 * progress, times: [...Data.times],
      center: [...Data.point], halfSize: 1 };
  }

  function intersection(s, first, second) {
    if (!Number.isInteger(first) || !Number.isInteger(second) || first < 0 || second > 2 || first >= second) {
      throw new RangeError('Choose two different branches in increasing order.');
    }
    let t = s.times[first], u = s.times[second];
    for (let k = 0; k < 10; k++) {
      const a = jet(t, s.offset), b = jet(u, s.offset), [vx, vy] = a.velocity, [wx, wy] = b.velocity;
      const [fx, fy] = a.point.map((x, i) => x - b.point[i]);
      const determinant = vy * wx - vx * wy;
      if (Math.abs(determinant) < 1) throw new RangeError('The crossing is unresolved.');
      t -= (-wy * fx + wx * fy) / determinant;
      u -= (-vy * fx + vx * fy) / determinant;
    }
    const p = jet(t, s.offset).point, q = jet(u, s.offset).point;
    if (Math.hypot(...p.map((x, i) => x - q[i])) > 1e-8 ||
        Math.abs(t - s.times[first]) > .001 || Math.abs(u - s.times[second]) > .001) {
      throw new RangeError('The selected crossing left its local branches.');
    }
    return { times: [t, u], point: p, branches: [first, second] };
  }

  function triangle(s) {
    const ab = intersection(s, 0, 1), bc = intersection(s, 1, 2), ac = intersection(s, 0, 2);
    const edges = [{ start: ab.times[1], end: bc.times[0], branch: 1 },
      { start: bc.times[1], end: ac.times[1], branch: 2 },
      { start: ac.times[0], end: ab.times[0], branch: 0 }];
    const points = edges.flatMap(edge => sample(edge.start, edge.end, 24, s.offset));
    // Integrate relative to the fixed lens center to avoid cancellation.
    let area = 0;
    for (const edge of edges) {
      const count = 32, step = (edge.end - edge.start) / count;
      let integral = 0;
      for (let i = 0; i <= count; i++) {
        const { point, velocity } = jet(edge.start + step * i, s.offset);
        const [x, y] = point.map((v, j) => v - s.center[j]);
        integral += (i === 0 || i === count ? 1 : i % 2 ? 4 : 2) * (x * velocity[1] - y * velocity[0]);
      }
      area += integral * step / 6;
    }
    return { crossings: [ab, bc, ac], edges, points, area: Math.abs(area) };
  }

  function sample(start, end, count, offset) {
    if (!Number.isInteger(count) || count < 1 || count > 24000) throw new RangeError('Use between 1 and 24000 segments.');
    return Array.from({ length: count + 1 }, (_, i) => jet(start + (end - start) * i / count, offset).point);
  }

  function circle(count = 360) {
    if (!Number.isInteger(count) || count < 4 || count > 4096) throw new RangeError('Use between 4 and 4096 circle segments.');
    return Array.from({ length: count + 1 }, (_, i) =>
      Data.point.map((x, j) => x + Data.offset * (j ? Math.sin(cycle * i / count) : Math.cos(cycle * i / count))));
  }

  return Object.freeze({ cycle, jet, state, intersection, triangle, sample, circle });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = ParallelOffsetMath;
