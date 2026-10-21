'use strict';

// Run with `node experiments/winding_check.js`. No packages or browser needed.
const assert = require('node:assert/strict');
const W = require('./winding_math.js');
const cycle = 2 * Math.PI;
let seed = 21;
let comparisons = 0;

function random() {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed / 2 ** 32;
}

function angleSum(points, x, y) {
  // Independent definition: add the signed angle subtended by every edge.
  let angle = 0;
  for (let i = 0; i < points.length; i += 2) {
    const next = (i + 2) % points.length;
    const ax = points[i] - x;
    const ay = points[i + 1] - y;
    const bx = points[next] - x;
    const by = points[next + 1] - y;
    angle += Math.atan2(ax * by - ay * bx, ax * bx + ay * by);
  }
  const turns = angle / cycle;
  assert.ok(Math.abs(turns - Math.round(turns)) < 1e-9);
  return Math.round(turns) || 0; // Normalize JavaScript's signed zero.
}

function checkPoint(points, x, y, expected) {
  const result = W.inspect(points, x, y);
  assert.equal(result.count, expected === undefined ? angleSum(points, x, y) : expected);
  comparisons++;
  return result;
}

function checkField(points, size, extent, allPixels = false) {
  const { counts, levels } = W.field(points, size, extent);
  const indices = new Set();
  if (allPixels) for (let i = 0; i < counts.length; i++) indices.add(i);
  else {
    for (let i = 0; i < 64; i++) indices.add(Math.floor(random() * counts.length));
    // Include even rare colors, rather than relying on random sampling alone.
    for (const level of levels) indices.add(counts.indexOf(level));
  }
  for (const index of indices) {
    const x = -extent + (index % size + 0.5) * 2 * extent / size;
    const y = -extent + (Math.floor(index / size) + 0.5) * 2 * extent / size;
    const result = W.inspect(points, x, y);
    // The count on the actual boundary is undefined, so do not compare it.
    if (result.distance < 1e-9) continue;
    assert.equal(counts[index], angleSum(points, x, y), `field at ${x}, ${y}`);
    assert.equal(result.count, counts[index]);
    comparisons++;
  }
  return levels;
}

function polygonCases() {
  const square = new Float64Array([-1, -1, 1, -1, 1, 1, -1, 1]);
  checkPoint(square, 0, 0, 1);
  checkPoint(square, 2, 0, 0);
  checkPoint(square, -2, 1, 0); // A ray along two vertices and a horizontal edge.
  assert.equal(W.inspect(square, 1, 0).distance, 0);
  assert.equal(W.inspect(square, 0, 0).distance, 1);
  checkField(square, 16, 2, true);
  const reversed = new Float64Array([-1, 1, 1, 1, 1, -1, -1, -1]);
  checkPoint(reversed, 0, 0, -1);
  checkField(reversed, 16, 2, true);
  const twice = new Float64Array([...square, ...square]);
  checkPoint(twice, 0, 0, 2);
  checkField(twice, 16, 2, true);
  // Repeated vertices, a closing duplicate, a self-crossing, half-pixel vertices.
  for (const values of [
    [-1, -1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1],
    [-1.5, -1.5, 1.5, 1.5, -1.5, 1.5, 1.5, -1.5],
    [-1.5, -1.5, 1.5, -1.5, 0, 1.5],
    // A polygon enclosing the entire raster exercises clipped scanline events.
    [-4, -4, 4, -4, 4, 4, -4, 4]
  ]) checkField(new Float64Array(values), 16, 2, true);
}

function orbitalCases() {
  let greatestError = 0;
  for (let outer = 2; outer <= 15; outer++) {
    for (let inner = 3; inner <= 25; inner++) {
      const points = W.orbit(outer, inner);
      checkPoint(points, 0, 0, 1);
      for (let i = 0; i < 8; i++) {
        const a = random() * cycle;
        const r = random() * 39;
        checkPoint(points, r * Math.cos(a), r * Math.sin(a), 1);
      }
      checkField(points, 128, 480);
      const bound = W.errorBound(outer, inner);
      for (let sample = 0; sample < 64; sample++) {
        const index = Math.floor(random() * points.length / 2);
        const fraction = random();
        const t = cycle * (index + fraction) / (points.length / 2);
        const x = 245 * Math.cos(t) + 140 * Math.cos(outer * t) + 65 * Math.cos(inner * t);
        const y = 245 * Math.sin(t) + 140 * Math.sin(outer * t) - 65 * Math.sin(inner * t);
        const next = (2 * index + 2) % points.length;
        const px = points[2 * index] * (1 - fraction) + points[next] * fraction;
        const py = points[2 * index + 1] * (1 - fraction) + points[next + 1] * fraction;
        const error = Math.hypot(x - px, y - py);
        greatestError = Math.max(greatestError, error);
        assert.ok(error <= bound + 1e-10, `${outer}/${inner}: interpolation error`);
      }
    }
  }
  console.log(`All 322 rhythm pairs: center and inner disk count +1; sampled field and angle sums agree.`);
  console.log(`20,608 interpolation samples respect their bounds; largest observed gap ${greatestError.toPrecision(5)}.`);
}

function displayedCases() {
  for (const [outer, inner, examples, levels] of [
    [7, 13, [[0, 460, 460], [1, 0, 0], [2, -5, -264], [3, 149, 0]], [0, 1, 2, 3]],
    [2, 25, [[-7, -154, 0], [-6, -138, 31], [-5, -110, -6], [-4, -192, -6],
      [-3, -77, 7], [-2, -206, 52], [-1, -100, 287], [0, 460, 460], [1, 0, 0]],
    [-7, -6, -5, -4, -3, -2, -1, 0, 1]]
  ]) {
    const points = W.orbit(outer, inner);
    assert.deepEqual(checkField(points, 960, 480), levels);
    for (const [count, x, y] of examples) {
      const result = checkPoint(points, x, y, count);
      assert.equal(angleSum(points, x, y), count);
      assert.ok(result.distance > 1);
      assert.ok(result.distance > W.errorBound(outer, inner));
      // Count does not change after refining the polygon by a factor of two.
      checkPoint(W.orbit(outer, inner, 48000), x, y, count);
    }
  }
  assert.equal(W.areaCoefficient(7, 13), 142300);
  assert.equal(W.areaCoefficient(2, 25), -6400);
}

polygonCases();
orbitalCases();
displayedCases();
console.log(`${comparisons.toLocaleString('en')} winding comparisons passed, including every displayed count button.`);
