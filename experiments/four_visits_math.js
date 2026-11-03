'use strict';

// First-order local lines of one certified orbital fourfold. These lines
// illustrate its unfolding; they are not finite-offset orbital branches.
const FourVisitsMath = (() => {
  const Data = typeof module !== 'undefined' && module.exports ? require('./four_visits_data.js') : FourVisitsData;
  const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const normals = Data.normals, shifts = Data.shifts;
  function intersection(i, j, weight) {
    const a = shifts[i] - weight, b = shifts[j] - weight, d = cross(normals[i], normals[j]);
    return [(a * normals[j][1] - b * normals[i][1]) / d,
      (normals[i][0] * b - normals[j][0] * a) / d];
  }
  const events = Data.triples.map(indices => {
    const [i, j, k] = indices;
    const p = intersection(i, j, 0), q = intersection(i, j, 1);
    const weight = (shifts[k] - dot(normals[k], p)) / (1 + dot(normals[k], q.map((x, a) => x - p[a])));
    const center = intersection(i, j, weight);
    const D = [cross(normals[i], normals[j]), cross(normals[j], normals[k]), cross(normals[k], normals[i])];
    const H = -D.reduce((a, b) => a + b, 0);
    if (!(H > 0)) throw new Error('The first-order triple must have positive sign.');
    return { indices, weight, center, coefficient: H * H / (2 * Math.abs(D.reduce((a, b) => a * b, 1))) };
  }).sort((a, b) => a.weight - b.weight);
  for (const event of events) {
    event.halfSpan = Math.min(...events.filter(other => other !== event).map(other => Math.abs(other.weight - event.weight))) / 4;
    const distances = [-1, 1].flatMap(side => [[0, 1], [1, 2], [2, 0]].map(([a, b]) => {
      const p = intersection(event.indices[a], event.indices[b], event.weight + side * event.halfSpan);
      return Math.hypot(...p.map((x, i) => x - event.center[i]));
    }));
    event.halfSize = 1.25 * Math.max(...distances);
    Object.freeze(event);
  }
  function state(index, progress) {
    if (!Number.isInteger(index) || index < 0 || index >= events.length || !Number.isInteger(progress) || progress < -100 || progress > 100) {
      throw new RangeError('Choose one of four meetings and an integer position from −100 to 100.');
    }
    const event = events[index], delta = event.halfSpan * progress / 100, weight = event.weight + delta;
    const crossings = [[0, 1], [1, 2], [2, 0]].map(([a, b]) => ({
      visits: [event.indices[a], event.indices[b]],
      point: progress === 0 ? event.center.slice() : intersection(event.indices[a], event.indices[b], weight)
    }));
    const area = event.coefficient * delta * delta;
    return { index, progress, event, delta, weight, crossings, area };
  }
  return Object.freeze({ normals, shifts, events: Object.freeze(events), intersection, state, cross, dot });
})();
if (typeof module !== 'undefined' && module.exports) module.exports = FourVisitsMath;
