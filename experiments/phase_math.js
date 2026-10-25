'use strict';

// Geometry for the first detour's middle leg, with a phase on BOTH backward
// terms. This is floating-point illustration; phase_unfolding.py certifies
// the local coefficients and six independently checked tangency boxes.
const PhaseMath = (() => {
  const critical = .13950512619441832;
  const minimum = critical - .002;
  const maximum = critical + .006;
  const heightLimit = 32;
  const coefficients = Object.freeze({ A: 2.38406898351825,
    C: -1.9328697090152e-5, B: -91.85891010267 });

  function evaluate(u, a, phase, order = 0, weightDerivative = false) {
    // u is orbit time measured from pi. Keeping that shift explicit avoids
    // errors from subtracting two almost equal full-orbit angles.
    const terms = weightDerivative
      ? [[-140, 2, 0], [140, 4, 0], [65, -3, phase], [-65, -7, phase]]
      : [[-300, 1, 0], [140 * (1 - a), 2, 0], [140 * a, 4, 0],
        [-65 * (1 - a), -3, phase], [-65 * a, -7, phase]];
    let x = 0, y = 0;
    for (const [radius, frequency, offset] of terms) {
      const angle = frequency * u + offset + order * Math.PI / 2;
      const scale = radius * frequency ** order;
      x += scale * Math.cos(angle);
      y += scale * Math.sin(angle);
    }
    return [x, y];
  }

  function radius(a) {
    let low = 0, high = Math.PI / 2;
    for (let j = 0; j < 48; j++) {
      const mid = (low + high) / 2;
      if (evaluate(mid, a, 0)[1] > 0) low = mid;
      else high = mid;
    }
    return (low + high) / 2;
  }

  function branch(y, a, phase, sign, r = radius(a)) {
    const center = sign * r;
    let u = center + y / evaluate(center, a, phase, 1)[1];
    for (let j = 0; j < 9; j++) {
      const p = evaluate(u, a, phase), v = evaluate(u, a, phase, 1);
      if (Math.abs(v[1]) < 100) throw new Error('The local branch left its height chart.');
      u -= (p[1] - y) / v[1];
    }
    const p = evaluate(u, a, phase), v = evaluate(u, a, phase, 1);
    const acc = evaluate(u, a, phase, 2);
    if (Math.abs(p[1] - y) > 1e-8 || Math.abs(u - center) > .15 ||
        sign * u < .46 || sign * u > .76) {
      throw new Error('The local height inversion did not converge.');
    }
    const pa = evaluate(u, a, phase, 0, true), va = evaluate(u, a, phase, 1, true);
    const slope = v[0] / v[1];
    const curvature = (acc[0] * v[1] - v[0] * acc[1]) / v[1] ** 3;
    const ua = -pa[1] / v[1];
    const slopeWeight = ((va[0] + acc[0] * ua) * v[1] - v[0] * (va[1] + acc[1] * ua)) / v[1] ** 2;
    return { x: p[0], y: p[1], u, slope, curvature,
      weight: pa[0] - slope * pa[1], slopeWeight };
  }

  function gap(y, a, phase, r = radius(a)) {
    const plus = branch(y, a, phase, 1, r), minus = branch(y, a, phase, -1, r);
    return { value: plus.x - minus.x, slope: plus.slope - minus.slope,
      weight: plus.weight - minus.weight, curvature: plus.curvature - minus.curvature,
      slopeWeight: plus.slopeWeight - minus.slopeWeight };
  }

  function contact(phase) {
    if (phase === 0) return { height: 0, weight: critical, prediction: 0 };
    const { A, B, C } = coefficients;
    let height = Math.cbrt(B * phase / (4 * C));
    const prediction = -3 * C * height ** 2 / A;
    let weight = critical + prediction;
    for (let j = 0; j < 10; j++) {
      const g = gap(height, weight, phase);
      const det = g.slope * g.slopeWeight - g.weight * g.curvature;
      if (Math.abs(det) < 1e-12) throw new Error('The local contact solve is unresolved.');
      height -= (g.value * g.slopeWeight - g.weight * g.slope) / det;
      weight -= (g.slope * g.slope - g.value * g.curvature) / det;
    }
    const g = gap(height, weight, phase);
    if (Math.abs(g.value) > 1e-8 || Math.abs(g.slope) > 1e-8 ||
        Math.abs(height) > 12 || weight < minimum || weight > maximum) {
      throw new Error('The local contact solve left its window.');
    }
    return { height, weight, prediction };
  }

  function bisect(fn, lo, hi) {
    let left = fn(lo);
    for (let j = 0; j < 42; j++) {
      const mid = (lo + hi) / 2, value = fn(mid);
      if (value * left > 0) { lo = mid; left = value; }
      else hi = mid;
    }
    return (lo + hi) / 2;
  }

  function meetings(a, phase, r = radius(a)) {
    // Split at numerical extrema, so a touching zero is retained even
    // when the separation does not change sign. Counts are local to the
    // displayed height window; they are not a whole-orbit census.
    if (phase === 0 && Math.abs(a - critical) < 1e-13) {
      return [{ height: 0, kind: 'cubic' }];
    }
    const fn = y => gap(y, a, phase, r);
    const cuts = [-heightLimit];
    let previous = -heightLimit, slope = fn(previous).slope;
    for (let j = 1; j <= 128; j++) {
      const y = -heightLimit + 2 * heightLimit * j / 128;
      const next = fn(y).slope;
      if (slope * next < 0) cuts.push(bisect(h => fn(h).slope, previous, y));
      previous = y; slope = next;
    }
    cuts.push(heightLimit);
    const result = [];
    for (const y of cuts) {
      if (Math.abs(fn(y).value) < 1e-9) result.push({ height: y, kind: 'touch' });
    }
    for (let j = 0; j < cuts.length - 1; j++) {
      const lo = cuts[j], hi = cuts[j + 1];
      const gl = fn(lo).value, gh = fn(hi).value;
      if (Math.abs(gl) >= 1e-9 && Math.abs(gh) >= 1e-9 && gl * gh < 0) {
        result.push({ height: bisect(y => fn(y).value, lo, hi), kind: 'crossing' });
      }
    }
    return result.sort((a, b) => a.height - b.height);
  }

  return Object.freeze({ critical, minimum, maximum, heightLimit, coefficients,
    evaluate, radius, branch, gap, contact, meetings });
})();

if (typeof module !== 'undefined') module.exports = PhaseMath;
