'use strict';

const assert = require('node:assert/strict');
const M = require('./positive_front_math.js');
const data = require('./positive_front_data.js');
const record = require('./positive_front.json');
const source = require('./normal_front_braid.json');
assert.deepEqual(data, record);
assert.deepEqual(data.start, source.endpoints[0].word);
assert.deepEqual(data.finish, source.endpoints[1].word);
const states = M.replay(data), counts = {}, cycled = [];
let checks = 4;
for (const [at, move] of data.moves.entries()) {
  counts[move[0]] = (counts[move[0]] || 0) + 1;
  assert.equal(states[at].length, 106);
  assert.deepEqual(M.apply([...states[at]], move), [...states[at + 1]]);
  if (move[0] === 'cycle') cycled.push(states[at][0]);
  checks += 2;
}
assert.deepEqual(counts, data.counts);
assert.deepEqual(cycled, source.conjugator);
assert.equal(states.length, 6368);
checks += 3;

const cases = [];
for (let i = 1; i <= 9; i++) {
  cases.push([[i, i + 1, i], ['triangle', 0]], [[i + 1, i, i + 1], ['triangle', 0]]);
}
for (let i = 1; i <= 10; i++) {
  cases.push([[i], ['cycle', 1]]);
  for (let j = 1; j <= 10; j++) {
    if (Math.abs(i - j) > 1) cases.push([[i, j], ['commute', 0]]);
  }
}
let worstFirst = 0, worstSecond = 0, largestCoefficient = -Infinity;
const h = 1e-5;
for (const [word, move] of cases) {
  for (const progress of [0, .13, .49, .5, .51, .87, 1]) {
    for (let k = 0; k <= 100; k++) {
      const x = -1 + k / 50;
      const model = M.local(word, move, x, progress);
      const points = M.points(model, x);
      const n = [Math.cos(x), Math.sin(x)], np = [-n[1], n[0]];
      for (let i = 0; i < model.heights.length; i++) {
        const projection = points[i][0] * n[0] + points[i][1] * n[1];
        const slope = points[i][0] * np[0] + points[i][1] * np[1];
        assert.ok(Math.abs(projection - model.heights[i] + 25) < 2e-14);
        assert.ok(Math.abs(slope - model.slopes[i]) < 1.1e-14);
        const coefficient = model.heights[i] + model.seconds[i];
        largestCoefficient = Math.max(largestCoefficient, coefficient);
        assert.ok(coefficient < 25);
        checks += 3;
      }
      if (k === 0 || k === 100) {
        assert.ok(model.slopes.every(v => Math.abs(v) < 1e-13));
        assert.ok(model.seconds.every(v => Math.abs(v) < 1e-13));
        checks += 2;
      } else {
        const left = M.local(word, move, x - h, progress), right = M.local(word, move, x + h, progress);
        for (let i = 0; i < model.heights.length; i++) {
          const first = Math.abs((right.heights[i] - left.heights[i]) / (2 * h) - model.slopes[i]);
          const second = Math.abs((right.slopes[i] - left.slopes[i]) / (2 * h) - model.seconds[i]);
          worstFirst = Math.max(worstFirst, first); worstSecond = Math.max(worstSecond, second);
          // At a quintic's C² join, a centered difference straddles a
          // jump in the third derivative. Its error is O(h), not O(h²).
          // |S'''| <= 60 gives 15 h / w³ there (w >= .56).
          assert.ok(first < 1e-8); assert.ok(second < 15 * h / .56 ** 3 + 2e-7);
          checks += 2;
        }
      }
    }
    if (move[0] === 'cycle') {
      assert.deepEqual(M.local(word, move, .37, progress), M.local(word, move, .37, 0));
      checks++;
    }
  }
}

// Independently find and read the three transverse pairwise crossings.
function crossing(word, progress, a, b) {
  let low = -1, high = 1;
  const gap = x => {
    const model = M.local(word, ['triangle', 0], x, progress);
    return model.heights[a] - model.heights[b];
  };
  const sign = Math.sign(gap(low));
  for (let i = 0; i < 50; i++) {
    const middle = (low + high) / 2;
    if (Math.sign(gap(middle)) === sign) low = middle;
    else high = middle;
  }
  const x = (low + high) / 2, model = M.local(word, ['triangle', 0], x, progress);
  assert.ok(Math.abs(gap(x)) < 1e-13);
  assert.ok(Math.abs(model.slopes[a] - model.slopes[b]) > 1);
  checks += 2;
  return { x, a, b };
}
for (const word of [[1, 2, 1], [2, 1, 2]]) {
  for (const progress of [0, .1, .49, .5, .51, .9, 1]) {
    const meetings = [[0, 1], [0, 2], [1, 2]].map(([a, b]) => crossing(word, progress, a, b));
    if (progress === .5) {
      assert.ok(meetings.every(meeting => Math.abs(meeting.x) < 1e-14));
    } else {
      meetings.sort((a, b) => a.x - b.x);
      const order = [0, 1, 2], result = [];
      for (const { a, b } of meetings) {
        const i = order.indexOf(a), j = order.indexOf(b);
        assert.equal(Math.abs(i - j), 1);
        result.push(Math.min(i, j) + 1);
        [order[i], order[j]] = [order[j], order[i]];
        checks++;
      }
      assert.deepEqual(result, progress < .5 ? word : M.apply(word, ['triangle', 0]));
    }
    checks++;
  }
}

for (const bad of [
  () => M.apply([1, 2], ['commute', 0]), () => M.apply([1, 3, 1], ['triangle', 0]),
  () => M.apply([1], ['cycle', 0]), () => M.apply([], ['cycle', 1]),
  () => M.apply([1, 3], ['commute', -1]), () => M.apply([1, 3], ['commute', 0, 1]),
  () => M.apply([1, 11], ['commute', 0]), () => M.apply([1, -3], ['commute', 0]),
  () => M.apply([1, 3], ['commute', true]), () => M.apply([1, 3], ['erase', 0]),
  () => M.local([1], ['cycle', 1], NaN, 0), () => M.local([1], ['cycle', 1], 0, 1.1),
  () => M.local([1], ['cycle', 1], -1.1, 0), () => M.points({ heights: [], slopes: [] }, Infinity),
  () => M.next(data.moves, -1, 'triangle', 1), () => M.next(data.moves, 0, 'erase', 1),
  () => M.next(data.moves, 0, 'triangle', 0),
]) { assert.throws(bad, RangeError); checks++; }
assert.equal(M.next(data.moves, 0, 'triangle', 1), 39);
assert.equal(M.next(data.moves, 39, 'triangle', -1), 39);
assert.equal(M.next(data.moves, data.moves.length - 1, 'cycle', 1), data.moves.length - 1);
checks += 3;
console.log(`${checks.toLocaleString('en-US')} checks: full movie replay, all local rule patterns, derivatives, reconstruction, slope separation, and invalid controls.`);
console.log(`Largest finite-difference errors: first ${worstFirst}, second ${worstSecond}; largest sampled h+h'' ${largestCoefficient} < 25.`);
console.log('Numerical geometry checks accompany the analytic local-model and offset arguments.');
