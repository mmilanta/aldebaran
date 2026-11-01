'use strict';

// Local front models and a literal replay, separate from the Python search.
const PositiveFrontMath = (() => {
  const kinds = ['commute', 'triangle', 'cycle'];

  function apply(word, move, strands = 11) {
    if (!Array.isArray(word) || !Number.isInteger(strands) || strands < 2 ||
        !word.every(g => Number.isInteger(g) && g > 0 && g < strands) ||
        !Array.isArray(move) || move.length !== 2 || !Number.isInteger(move[1])) {
      throw new RangeError('Use a positive braid word and an integer move position.');
    }
    const [kind, at] = move, out = [...word];
    if (kind === 'commute' && at >= 0 && at + 1 < word.length && Math.abs(word[at] - word[at + 1]) > 1) {
      [out[at], out[at + 1]] = [out[at + 1], out[at]];
    } else if (kind === 'triangle' && at >= 0 && at + 2 < word.length &&
        word[at] === word[at + 2] && Math.abs(word[at] - word[at + 1]) === 1) {
      out.splice(at, 3, word[at + 1], word[at], word[at + 1]);
    } else if (kind === 'cycle' && at === 1 && word.length) {
      out.push(out.shift());
    } else {
      throw new RangeError('This local move does not apply to the word.');
    }
    return out;
  }

  function replay(data) {
    let word = [...data.start];
    const states = [Uint8Array.from(word)];
    for (const move of data.moves) {
      word = apply(word, move, data.strands);
      states.push(Uint8Array.from(word));
    }
    if (JSON.stringify(word) !== JSON.stringify(data.finish)) throw new Error('The movie misses its target.');
    return states;
  }

  // A quintic step, with two vanishing derivatives at either end.
  function step(t) {
    if (t <= 0) return [0, 0, 0];
    if (t >= 1) return [1, 0, 0];
    return [t ** 3 * (10 + t * (-15 + 6 * t)),
      30 * t ** 2 * (1 - t) ** 2, 60 * t * (1 - t) * (1 - 2 * t)];
  }

  function local(word, move, x, progress) {
    // Validate the rule too: a model never silently invents a move.
    apply(word, move);
    if (!Number.isFinite(x) || x < -1 || x > 1 ||
        !Number.isFinite(progress) || progress < 0 || progress > 1) {
      throw new RangeError('Use a local angle in [-1,1] and progress in [0,1].');
    }
    const [kind, at] = move;
    if (kind === 'triangle') {
      const f = (15 * x - 10 * x ** 3 + 3 * x ** 5) / 8;
      const df = 15 / 8 * (1 - x * x) ** 2;
      const ddf = -7.5 * x * (1 - x * x);
      const g = (1 - x * x) ** 3;
      const dg = -6 * x * (1 - x * x) ** 2;
      const ddg = -6 + 36 * x * x - 30 * x ** 4;
      const delta = Math.sign(word[at] - word[at + 1]) * (1 - 2 * progress) / 4;
      return { heights: [f, delta * g, -f], slopes: [df, delta * dg, -df],
        seconds: [ddf, delta * ddg, -ddf], labels: [0, 1, 2], range: [-1.3, 1.3], delta };
    }
    const generators = kind === 'commute' ? [word[at], word[at + 1]] : [word[0]];
    const low = Math.min(...generators) - 1, high = Math.max(...generators);
    const center = (low + high) / 2, count = high - low + 1;
    const heights = Array.from({ length: count }, (_, i) => low + i - center);
    const slopes = Array(count).fill(0), seconds = Array(count).fill(0);
    const labels = [];
    for (const [i, generator] of generators.entries()) {
      const c = kind === 'cycle' ? 0 : (i ? 1 : -1) * .42 * (1 - 2 * progress);
      const width = kind === 'cycle' ? 1.6 : .56;
      const [value, derivative, second] = step((x - c) / width + .5);
      const rank = generator - 1 - low;
      heights[rank] += value;
      heights[rank + 1] -= value;
      slopes[rank] = derivative / width;
      slopes[rank + 1] = -derivative / width;
      seconds[rank] = second / width ** 2;
      seconds[rank + 1] = -second / width ** 2;
      labels.push(rank, rank + 1);
    }
    return { heights, slopes, seconds, labels, range: [-count / 2 - .4, count / 2 + .4] };
  }

  // h is offset by 25. For these local models h+h'' < 25 everywhere.
  // The angle is x, so the derivatives above are with respect to theta.
  function points(model, angle = 0, offset = 25) {
    if (!Number.isFinite(angle) || !Number.isFinite(offset)) throw new RangeError('Use finite coordinates.');
    const c = Math.cos(angle), s = Math.sin(angle);
    return model.heights.map((h, i) => [(h - offset) * c - model.slopes[i] * s,
      (h - offset) * s + model.slopes[i] * c]);
  }

  function next(moves, current, kind, direction) {
    if (!kinds.includes(kind) || !Number.isInteger(current) || current < 0 || current >= moves.length ||
        (direction !== -1 && direction !== 1)) throw new RangeError('Choose a move kind and search direction.');
    for (let at = current + direction; at >= 0 && at < moves.length; at += direction) {
      if (moves[at][0] === kind) return at;
    }
    return current;
  }

  return Object.freeze({ apply, replay, step, local, points, next });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = PositiveFrontMath;
