'use strict';

// Shumakovitch's Gauss-word convention. Edge indices are stored doubled;
// all crossing arithmetic below is integer arithmetic. See strangeness.md.
const StrangenessMath = (() => {
  function walk(word, initialIndex2) {
    if (!Number.isSafeInteger(initialIndex2) || initialIndex2 % 2 === 0) {
      throw new RangeError('Twice an edge index must be an odd integer.');
    }
    const vertices = new Map(), edgeIndices2 = [];
    let edge2 = initialIndex2;
    for (const [label, exponent] of word) {
      if (!Number.isSafeInteger(label) || label < 0 || ![1, -1].includes(exponent)) {
        throw new RangeError('Invalid signed crossing.');
      }
      edgeIndices2.push(edge2);
      const index = (edge2 + exponent) / 2;
      if (vertices.has(label)) {
        const previous = vertices.get(label);
        if (previous.visits !== 1 || previous.weight === exponent || previous.index !== index) {
          throw new RangeError('Inconsistent crossing visits.');
        }
        previous.visits++;
      } else vertices.set(label, { label, weight: exponent, index, visits: 1 });
      edge2 += 2 * exponent;
    }
    if (edge2 !== initialIndex2 || [...vertices.values()].some(v => v.visits !== 2) ||
        word.length === 0 && Math.abs(initialIndex2) !== 1) {
      throw new RangeError('The crossing word does not close.');
    }
    const rows = [...vertices.values()].sort((a, b) => a.label - b.label)
      .map(v => ({ ...v, contribution: v.weight * v.index }));
    const weightedSum = rows.reduce((sum, v) => sum + v.contribution, 0);
    const correction = (initialIndex2 ** 2 - 1) / 4;
    return { rows, edgeIndices2, weightedSum, correction, value: weightedSum + correction };
  }

  function state(record, base) {
    const E = record.word.length;
    if (!Number.isInteger(base) || base < 0 || base >= E) throw new RangeError('Starting edge out of range.');
    const original = walk(record.word, record.initial_index2);
    const sequence = record.word.slice(base).concat(record.word.slice(0, base));
    const index2 = original.edgeIndices2[base];
    const result = walk(sequence, index2);
    const end = record.display_times[base];
    const start = base === 0 ? record.display_times[E - 1] - 2 * Math.PI : record.display_times[base - 1];
    // Halfway in parameter on the starting arc, except at the exterior reset
    // where t=0 is the exact, uniquely rightmost point of every original curve.
    const time = base === 0 ? 0 : (start + end) / 2;
    return { ...result, sequence, index2, time, base };
  }

  function orbit(t, outer, inner) {
    return [245 * Math.cos(t) + 140 * Math.cos(outer * t) + 65 * Math.cos(inner * t),
      245 * Math.sin(t) + 140 * Math.sin(outer * t) - 65 * Math.sin(inner * t)];
  }

  function velocity(t, outer, inner) {
    return [-245 * Math.sin(t) - 140 * outer * Math.sin(outer * t) - 65 * inner * Math.sin(inner * t),
      245 * Math.cos(t) + 140 * outer * Math.cos(outer * t) - 65 * inner * Math.cos(inner * t)];
  }

  return Object.freeze({ walk, state, orbit, velocity });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = StrangenessMath;
