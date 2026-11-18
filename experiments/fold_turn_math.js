'use strict';

// One moving ellipse, viewed in a frame turning through t. Coordinates have y up.
const FoldTurnMath = (() => {
  const cycle = 2 * Math.PI;
  const folds = Object.freeze([7, 14, 30, 60]);
  const defaults = Object.freeze({ folds: 14, phase: 90, trace: 250 });
  const rotate = ([x, y], angle) => [x * Math.cos(angle) - y * Math.sin(angle),
    x * Math.sin(angle) + y * Math.cos(angle)];

  function ellipse(u, phase) {
    return [245 + 140 * Math.cos(u) + 65 * Math.cos(phase - u),
      140 * Math.sin(u) + 65 * Math.sin(phase - u)];
  }

  function position(t, d, phase) {
    return rotate(ellipse(d * t, phase), t);
  }

  function radialRange(phase) {
    // Distances from q to an axis-aligned ellipse. The unique positive
    // minimum multiplier and the maximum multiplier > A² solve decreasing
    // scalar equations. The half-turn maximum is the separate symmetric case.
    // See fold_annulus.md for global extremality and monotonicity proofs.
    if (phase === 0) return [40, 450];
    if (phase === Math.PI) return [170, Math.sqrt(23155775 / 208)];
    const axes = [205, 75];
    const q = [245 * Math.cos(phase / 2), 245 * Math.sin(phase / 2)];
    const solve = maximum => {
      let low = maximum ? 205 ** 2 : 0;
      let high = maximum ? 205 ** 2 + 205 * 245 + 1 : 205 * 245;
      for (let i = 0; i < 70; i++) {
        const mid = (low + high) / 2;
        const sum = axes.reduce((total, a, j) => total +
          (a * q[j] / (maximum ? mid - a * a : mid + a * a)) ** 2, 0);
        if (sum > 1) low = mid;
        else high = mid;
      }
      const multiplier = (low + high) / 2;
      return Math.hypot(...axes.map((a, j) => multiplier * q[j] /
        (maximum ? multiplier - a * a : multiplier + a * a)));
    };
    return [solve(false), solve(true)];
  }

  function joints(t, d, phase) {
    const fixed = [[0, 0], [245, 0],
      [245 + 140 * Math.cos(d * t), 140 * Math.sin(d * t)], ellipse(d * t, phase)];
    return { fixed, turning: fixed.map(p => rotate(p, t)) };
  }

  function segmentCount(d) {
    // |z''| <= M. Chord error <= M(dt)^2/8, here < .02 drawing units.
    // This illustrates positions; a small chord error does not certify crossings.
    const bound = 245 + 140 * (d + 1) ** 2 + 65 * (d - 1) ** 2;
    return Math.ceil(cycle * Math.sqrt(bound / (8 * .018)));
  }

  function path(fn, start, end, segments) {
    const pieces = [];
    for (let i = 0; i <= segments; i++) {
      const [x, y] = fn(start + (end - start) * i / segments);
      pieces.push(`${i ? 'L' : 'M'}${x.toFixed(4)},${(-y).toFixed(4)}`);
    }
    return pieces.join('');
  }

  function orbitPath(d, phase, repeat = false) {
    const end = repeat ? cycle / d : cycle;
    return path(t => position(t, d, phase), 0, end,
      repeat ? Math.ceil(segmentCount(d) / d) : segmentCount(d));
  }

  function parse(search) {
    const params = new URLSearchParams(search);
    const rules = { folds: n => folds.includes(n),
      phase: n => Number.isInteger(n) && n >= 0 && n <= 180,
      trace: n => Number.isInteger(n) && n >= 0 && n <= 1000 };
    const state = { ...defaults };
    // A partial valid link may specify just a phase or fold count. A malformed
    // recognized value invalidates the whole view; unrelated parameters are fine.
    for (const key of Object.keys(rules)) {
      if (!params.has(key)) continue;
      const values = params.getAll(key);
      if (values.length !== 1 || !/^\d+$/.test(values[0])) return { ...defaults };
      const value = Number(values[0]);
      if (!rules[key](value)) return { ...defaults };
      state[key] = value;
    }
    return state;
  }

  function query(state) {
    return new URLSearchParams({ folds: state.folds, phase: state.phase, trace: state.trace }).toString();
  }

  function drawing(d, degrees) {
    const phase = degrees * Math.PI / 180;
    // Standalone artwork deliberately contains the complete line without guides.
    return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1320" viewBox="-480 -550 960 1056" role="img" aria-labelledby="title description">\n` +
      `<title id="title">One ellipse. ${d} folds.</title>\n` +
      `<desc id="description">An orbital drawing with lengths 245, 140, and 65. The backward arm starts at ${degrees} degrees. Rhythms ${d + 1} and ${d - 1} give ${d} rotational repeats. This sampled illustration does not certify crossings.</desc>\n` +
      '<rect x="-480" y="-550" width="960" height="1056" fill="#0b0e1a"/>\n' +
      `<text x="-438" y="-494" fill="#e8b66e" font-family="ui-sans-serif,system-ui,sans-serif" font-size="19" letter-spacing="2">ALDEBARAN · ${d} FOLDS · ${degrees}°</text>\n` +
      `<path d="${orbitPath(d, phase)}" fill="none" stroke="#9fc7eb" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>\n` +
      `<a href="https://mmilanta.github.io/aldebaran/experiments/fold_turn.html?folds=${d}&amp;phase=${degrees}"><text x="-438" y="482" fill="#c7c7d4" font-family="ui-sans-serif,system-ui,sans-serif" font-size="15">One ellipse. Many folds. ↗</text></a>\n</svg>\n`;
  }

  return Object.freeze({ cycle, folds, defaults, rotate, ellipse, position,
    joints, radialRange, segmentCount, path, orbitPath, parse, query, drawing });
})();

if (typeof module !== 'undefined') module.exports = FoldTurnMath;
