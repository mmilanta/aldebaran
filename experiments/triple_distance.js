'use strict';

// A lower bound for routes using only ordinary triple passages.
//   node experiments/triple_distance.js
// Add --saved to omit fresh smooth endpoint proofs, or --write to save a
// small summary after both independent searches agree. Standard libraries only.
// The search deliberately admits non-geometric moves. See triple_distance.md.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const encode = word => word.map(([label, exponent]) => 2 * label + (exponent > 0 ? 1 : 0));
const decode = key => Array.from(key, c => c.charCodeAt(0));
const hash = value => crypto.createHash('sha256').update(value).digest('hex');

function validate(word) {
  assert(word.length > 0 && word.length < 32768 && word.length % 2 === 0);
  const labels = new Map();
  for (const code of word) {
    assert(Number.isSafeInteger(code) && code >= 0 && code < 65536);
    const label = Math.floor(code / 2);
    if (!labels.has(label)) labels.set(label, []);
    labels.get(label).push(code % 2);
  }
  for (const visits of labels.values()) assert.deepEqual(visits.sort(), [0, 1]);
}

// First representation: cyclic words, with labels renamed in first-visit order.
function canonical(word) {
  let best = null;
  for (let start = 0; start < word.length; start++) {
    const labels = new Map(), next = [];
    for (let k = 0; k < word.length; k++) {
      const code = word[(start + k) % word.length], old = Math.floor(code / 2);
      if (!labels.has(old)) labels.set(old, labels.size);
      next.push(2 * labels.get(old) + code % 2);
    }
    const key = String.fromCharCode(...next);
    if (best === null || key < best) best = key;
  }
  return best;
}

function neighbors(key) {
  const word = decode(key), N = word.length, edges = new Map(), adjacent = new Map();
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N, a = word[i] >> 1, b = word[j] >> 1;
    if (a === b) continue;
    const pair = Math.min(a, b) + ',' + Math.max(a, b);
    if (!edges.has(pair)) edges.set(pair, []);
    edges.get(pair).push([i, j]);
    if (!adjacent.has(a)) adjacent.set(a, new Set());
    if (!adjacent.has(b)) adjacent.set(b, new Set());
    adjacent.get(a).add(b);
    adjacent.get(b).add(a);
  }
  const result = new Set();
  for (const [a, bs] of adjacent) {
    for (const b of bs) {
      if (b <= a) continue;
      for (const c of bs) {
        if (c <= b || !adjacent.get(b).has(c)) continue;
        for (const ab of edges.get(a + ',' + b)) {
          for (const ac of edges.get(a + ',' + c)) {
            for (const bc of edges.get(b + ',' + c)) {
              if (new Set([...ab, ...ac, ...bc]).size !== 6) continue;
              const moved = [...word];
              for (const [i, j] of [ab, ac, bc]) [moved[i], moved[j]] = [moved[j], moved[i]];
              result.add(canonical(moved));
            }
          }
        }
      }
    }
  }
  return result;
}

// Second representation: the forward distance to each visit's partner, plus
// its sign. No crossing labels or first-appearance renaming enter this search.
function gaps(word) {
  const positions = new Map(), N = word.length;
  word.forEach((code, i) => {
    const label = Math.floor(code / 2);
    if (!positions.has(label)) positions.set(label, []);
    positions.get(label).push(i);
  });
  return word.map((code, i) => {
    const other = positions.get(Math.floor(code / 2)).find(j => j !== i);
    return 2 * ((other - i + N) % N) + code % 2;
  });
}

// Booth's minimum-rotation algorithm, independently checked against all shifts.
function rotateMinimum(values) {
  const N = values.length;
  let i = 0, j = 1, k = 0;
  while (i < N && j < N && k < N) {
    const a = values[(i + k) % N], b = values[(j + k) % N];
    if (a === b) { k++; continue; }
    if (a > b) { i += k + 1; if (i === j) i++; }
    else { j += k + 1; if (i === j) j++; }
    k = 0;
  }
  const start = Math.min(i, j);
  return String.fromCharCode(...values.slice(start), ...values.slice(0, start));
}

function gapNeighbors(key) {
  const codes = decode(key), N = codes.length;
  const partners = codes.map((x, i) => (i + (x >> 1)) % N);
  const result = new Set();
  // Enumerate triples of adjacent edges, without constructing a label graph.
  for (let i = 0; i < N; i++) {
    const ii = (i + 1) % N;
    if (partners[i] === ii) continue;
    for (let j = i + 2; j < N; j++) {
      const jj = (j + 1) % N;
      if (jj === i || partners[j] === jj) continue;
      // Two sides of a triangle must share exactly one paired crossing.
      const links = Number(partners[i] === j || partners[i] === jj) +
        Number(partners[ii] === j || partners[ii] === jj);
      if (links !== 1) continue;
      for (let k = j + 2; k < N; k++) {
        const kk = (k + 1) % N;
        if (kk === i || partners[k] === kk) continue;
        const sites = [i, ii, j, jj, k, kk];
        if (!sites.every(p => sites.includes(partners[p]))) continue;
        const permutation = Array.from({ length: N }, (_, p) => p);
        for (const [a, b] of [[i, ii], [j, jj], [k, kk]]) {
          permutation[a] = b;
          permutation[b] = a;
        }
        const moved = new Array(N);
        for (let p = 0; p < N; p++) {
          const q = permutation[p], r = permutation[partners[p]];
          moved[q] = 2 * ((r - q + N) % N) + codes[p] % 2;
        }
        result.add(rotateMinimum(moved));
      }
    }
  }
  return result;
}

function gapToWord(key) {
  const codes = decode(key), N = codes.length, labels = new Map();
  return codes.map((x, i) => {
    const other = (i + (x >> 1)) % N;
    assert(other !== i && (other + (codes[other] >> 1)) % N === i);
    assert(codes[i] % 2 !== codes[other] % 2);
    if (!labels.has(i)) { const label = labels.size / 2; labels.set(i, label); labels.set(other, label); }
    return 2 * labels.get(i) + x % 2;
  });
}

function ball(start, radius, next, report = true) {
  const seen = new Set([start]), layers = [1];
  let frontier = [start];
  for (let depth = 1; depth <= radius; depth++) {
    const added = [];
    for (const old of frontier) {
      for (const key of next(old)) {
        if (!seen.has(key)) { seen.add(key); added.push(key); }
      }
    }
    layers.push(added.length);
    frontier = added;
    if (report) console.log(`  depth ${depth}: ${added.length} new states; ${seen.size} total`);
  }
  return { seen, layers };
}

function checks() {
  // A three-crossing word with a triangle, including one edge across the seam.
  const triangle = [0, 2, 1, 4, 3, 5];
  validate(triangle);
  assert(neighbors(canonical(triangle)).size > 0);
  assert(gapNeighbors(rotateMinimum(gaps(triangle))).size > 0);
  // Unequal extra curls break rotational symmetry. The specified move needs
  // the last/first edge, so a missing cyclic edge cannot hide behind a rotation.
  const seam = [0, 6, 7, 2, 1, 8, 9, 4, 3, 5], seamMoved = [...seam];
  validate(seam);
  for (const [a, b] of [[3, 4], [7, 8], [9, 0]]) [seamMoved[a], seamMoved[b]] = [seamMoved[b], seamMoved[a]];
  assert(neighbors(String.fromCharCode(...seam)).has(canonical(seamMoved)));
  assert(gapNeighbors(String.fromCharCode(...gaps(seam))).has(rotateMinimum(gaps(seamMoved))));
  const fixtures = [triangle, [0, 1, 2, 3, 4, 5], [0, 2, 4, 1, 3, 5]];
  for (const word of fixtures) {
    validate(word);
    const original = canonical(word), expected = neighbors(original);
    const independent = new Set([...gapNeighbors(rotateMinimum(gaps(word)))].map(k => canonical(gapToWord(k))));
    assert.deepEqual(independent, expected);
    for (const moved of expected) assert(neighbors(moved).has(original), 'A move must be reversible.');
    for (let i = 0; i < word.length; i++) {
      const shifted = word.slice(i).concat(word.slice(0, i));
      assert.equal(canonical(shifted), original);
      const renamed = shifted.map(x => 2 * (100 - (x >> 1)) + x % 2);
      assert.equal(canonical(renamed), original);
      assert.equal(rotateMinimum(gaps(shifted)), rotateMinimum(gaps(word)));
    }
  }
  assert.equal(neighbors(canonical([0, 1, 2, 3])).size, 0, 'Two labels cannot make a three-crossing move.');
  assert.equal(neighbors(canonical(fixtures[1])).size, 1,
    'The relaxed graph must admit the outer triangle of three separate curls.');
  // An exhaustive small alphabet catches periodic and repeated minima.
  for (let n = 1; n <= 8; n++) {
    for (let bits = 0; bits < 2 ** n; bits++) {
      const values = Array.from({ length: n }, (_, i) => (bits >> i) & 1);
      const all = values.map((_, i) => String.fromCharCode(...values.slice(i), ...values.slice(0, i)));
      assert.equal(rotateMinimum(values), all.sort()[0]);
    }
  }
  for (const bad of [[0], [0, 0], [0, 1, 2, 2], [0, NaN]]) assert.throws(() => validate(bad));
  console.log('Cyclic seams, relabeling, inverse moves, minimum rotations, and invalid-word controls passed.');
}

function main() {
  const args = process.argv.slice(2);
  assert(args.every(x => ['--saved', '--write'].includes(x)), 'Use --saved and/or --write.');
  const started = performance.now(), radius = 5;
  checks();
  const atlas = JSON.parse(fs.readFileSync(path.join(__dirname, 'strangeness_atlas.json'), 'utf8'));
  const source = fs.readFileSync(path.join(__dirname, 'certify_intersections.py'));
  assert.equal(hash(source), atlas.certificate_code_sha256, 'The frozen certificate source changed.');
  const ends = [6, 8].map(n => atlas.verified.find(row => row.outer === 11 && row.inner === n));
  assert(ends.every(e => e && e.crossings === 40 && e.tangent_index === 11));
  assert.deepEqual(ends.map(e => e.strangeness), [15, 11]);
  const control = JSON.parse(fs.readFileSync(path.join(__dirname, 'triple_distance_control.json'), 'utf8'));
  assert.equal(control.certificate_code_sha256, atlas.certificate_code_sha256);
  assert.equal(control.weight, '9/100');
  assert.equal(control.crossings, 40);
  assert.equal(control.strangeness, 11);
  if (!args.includes('--saved')) {
    const fresh = JSON.parse(execFileSync('python3', [path.join(__dirname, 'triple_distance_endpoints.py')], { encoding: 'utf8' }));
    assert.deepEqual(fresh.endpoints, ends);
    assert.deepEqual(fresh.control, control);
    console.log('Three fresh smooth proofs match the endpoint words and the four-triple control.');
  } else console.log('Using archived endpoint words; no fresh smooth endpoint proofs.');
  const words = ends.map(e => encode(e.word));
  words.forEach(validate);
  const controlWord = encode(control.word);
  validate(controlWord);
  const knownStart = ball(canonical(words[0]), 2, neighbors, false);
  const knownEnd = ball(canonical(controlWord), 2, neighbors, false);
  assert([...knownStart.seen].some(k => knownEnd.seen.has(k)), 'The known four-triple route was not found.');
  const gapStart = ball(rotateMinimum(gaps(words[0])), 2, gapNeighbors, false);
  const gapEnd = ball(rotateMinimum(gaps(controlWord)), 2, gapNeighbors, false);
  assert([...gapStart.seen].some(k => gapEnd.seen.has(k)), 'The independent search missed the known route.');
  console.log('Both searches find the known four-triple segment from weight 0 to 9/100.');
  const primary = [], independent = [];
  for (let i = 0; i < 2; i++) {
    console.log(`First-visit word search from 11/${[6, 8][i]}:`);
    primary.push(ball(canonical(words[i]), radius, neighbors));
    console.log(`Partner-distance search from 11/${[6, 8][i]}:`);
    independent.push(ball(rotateMinimum(gaps(words[i])), radius, gapNeighbors));
    assert.deepEqual(independent[i].layers, primary[i].layers);
    const translated = new Set([...independent[i].seen].map(k => canonical(gapToWord(k))));
    assert.deepEqual(translated, primary[i].seen, 'The independent search reached different words.');
  }
  const common = [...primary[0].seen].filter(k => primary[1].seen.has(k));
  assert.equal(common.length, 0, 'The claimed distance lower bound failed.');
  assert.deepEqual(primary.map(b => b.layers), [[1, 16, 121, 615, 2419, 7809], [1, 11, 72, 352, 1374, 4524]]);
  const record = { schema: 'aldebaran-triple-distance-v1',
    method: 'Two independent exact searches in a graph admitting every three-pair triangle swap, including non-geometric ones.',
    radius, endpoints: ends.map((e, i) => ({ outer: 11, inner: e.inner,
      canonical_word_sha256: hash(canonical(words[i])), layers: primary[i].layers, ball_size: primary[i].seen.size })),
    intersection_size: 0, excluded_triple_only_moves: 2 * radius,
    triple_only_lower_bound_with_strangeness_parity: 12,
    certificate_code_sha256: atlas.certificate_code_sha256 };
  if (args.includes('--write')) fs.writeFileSync(path.join(__dirname, 'triple_distance.json'), JSON.stringify(record, null, 2) + '\n');
  console.log('Both exact searches agree on every reached word. The radius-five balls are disjoint.');
  console.log('No triple-only route with ten or fewer passages; strangeness parity raises the lower bound to twelve.');
  console.log(`Completed in ${((performance.now() - started) / 1000).toFixed(2)}s.`);
}

if (require.main === module) main();
module.exports = { canonical, neighbors, gaps, rotateMinimum, gapNeighbors, gapToWord, ball, encode, decode, validate, checks };
