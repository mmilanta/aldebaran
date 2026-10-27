'use strict';

// Independent geometric checks for the browser's three curves. Requires Node
// alone. These use floating-point samples with a generous clearance check;
// the rational smooth proofs and general invariant theorem live elsewhere.
const assert = require('node:assert/strict');
const M = require('./strangeness_math.js');
const data = require('./strangeness_data.js');
const W = require('./winding_math.js');
let checks = 0, largestPositionError = 0, leastClearanceRatio = Infinity;
function check(condition, message) { assert.ok(condition, message); checks++; }

for (const record of data) {
  const { outer: m, inner: n, word, display_times: times } = record;
  const points = W.orbit(m, n, 96000), bound = W.errorBound(m, n, 96000) + 1e-8;
  const inspect = (x, y) => {
    const result = W.inspect(points, x, y);
    leastClearanceRatio = Math.min(leastClearanceRatio, result.distance / bound);
    check(result.distance > 10 * bound, 'A geometric probe is too close to the curve.');
    return result.count;
  };
  const indices = new Map();
  for (let label = 0; label < record.crossings; label++) {
    const visits = word.flatMap(([v], j) => v === label ? [j] : []);
    check(visits.length === 2, 'A crossing needs two visits.');
    const [a, b] = visits, p = M.orbit(times[a], m, n), q = M.orbit(times[b], m, n);
    const error = Math.hypot(p[0] - q[0], p[1] - q[1]);
    largestPositionError = Math.max(largestPositionError, error);
    check(error < 1e-8, 'Rounded times do not meet.');
    const va = M.velocity(times[a], m, n), vb = M.velocity(times[b], m, n);
    const determinant = va[0] * vb[1] - va[1] * vb[0];
    check(word[a][1] === -Math.sign(determinant) && word[b][1] === Math.sign(determinant),
      'The exponent disagrees with the independently evaluated tangents.');
    const angles = [va, vb].flatMap(([x, y]) => {
      const angle = (Math.atan2(y, x) + 2 * Math.PI) % (2 * Math.PI);
      return [angle, (angle + Math.PI) % (2 * Math.PI)];
    }).sort((a, b) => a - b);
    const sectors = angles.map((angle, j) => {
      const next = j === 3 ? angles[0] + 2 * Math.PI : angles[j + 1];
      const middle = (angle + next) / 2;
      return inspect(p[0] + .05 * Math.cos(middle), p[1] + .05 * Math.sin(middle));
    });
    const mean = sectors.reduce((sum, x) => sum + x, 0) / 4;
    assert.deepEqual([...sectors].sort((a, b) => a - b), [mean - 1, mean, mean, mean + 1]); checks++;
    check(Number.isInteger(mean), 'The four-sector mean must be integral.');
    indices.set(label, mean);
  }
  for (let base = 0; base < word.length; base++) {
    const state = M.state(record, base);
    const p = M.orbit(state.time, m, n), v = M.velocity(state.time, m, n);
    const length = Math.hypot(...v), normal = [-v[1] / length, v[0] / length];
    const left = inspect(p[0] + .02 * normal[0], p[1] + .02 * normal[1]);
    const right = inspect(p[0] - .02 * normal[0], p[1] - .02 * normal[1]);
    check(left - right === 1, 'Winding must increase by one across an oriented edge.');
    check(left + right === state.index2, 'The recurrence disagrees with geometric edge winding.');
    const seen = new Set(); let sum = 0;
    for (let k = 0; k < word.length; k++) {
      const j = (base + k) % word.length, [label] = word[j];
      if (seen.has(label)) continue;
      seen.add(label);
      const other = word.findIndex(([v], i) => v === label && i !== j);
      const va = M.velocity(times[j], m, n), vb = M.velocity(times[other], m, n);
      const weight = -Math.sign(va[0] * vb[1] - va[1] * vb[0]);
      const row = state.rows.find(row => row.label === label);
      check(row.weight === weight && row.index === indices.get(label), 'A displayed row disagrees with geometry.');
      sum += weight * indices.get(label);
    }
    check(state.weightedSum === sum && sum + ((left + right) ** 2 - 1) / 4 === record.strangeness,
      'The geometric strangeness calculation differs.');
    check(state.value === record.strangeness, 'Moving the base changed strangeness.');
  }
}

// Round-trip every archived exact word through the JavaScript integer code.
const atlas = require('./strangeness_atlas.json');
for (const record of atlas.verified) {
  const original = M.walk(record.word, record.initial_index2);
  check(original.value === record.strangeness, 'Archived word has a different strangeness.');
  for (let j = 0; j < record.word.length; j++) {
    const rotated = record.word.slice(j).concat(record.word.slice(0, j));
    check(M.walk(rotated, original.edgeIndices2[j]).value === original.value,
      'An archived starting-edge rotation changed the integer.');
  }
  for (const [word, delta2] of [
    [record.word.map(([v, e]) => [v, -e]), -record.initial_index2],
    [[...record.word].reverse(), -record.initial_index2]
  ]) check(M.walk(word, delta2).value === original.value, 'An archived symmetry changed the integer.');
}

for (const fn of [
  () => M.walk([[0, 1]], 1),
  () => M.walk([[0, 1], [0, 1]], 1),
  () => M.walk([[0, 0], [0, 0]], 1),
  () => M.walk([[0, 1], [0, -1]], 0),
  () => M.walk([], 3),
  () => M.walk([[0, 1], [1, 1], [0, -1], [1, -1]], 1),
  () => M.state(data[0], -1), () => M.state(data[0], 2), () => M.state(data[0], .5)
]) { assert.throws(fn, RangeError); checks++; }
console.log(`${checks} checks passed, including geometric sector and edge probes for all 54 displayed base edges.`);
console.log(`Largest rounded crossing discrepancy ${largestPositionError.toExponential(3)} drawing units; least probe clearance / error bound ${leastClearanceRatio.toFixed(1)}.`);
