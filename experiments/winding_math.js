'use strict';

// Mathematical coordinates: positive y points up. No browser APIs here.
const WindingMath = (() => {
  const cycle = 2 * Math.PI;

  function orbit(outer, inner, steps = 24000) {
    const points = new Float64Array(2 * steps);
    for (let i = 0; i < steps; i++) {
      const t = cycle * i / steps;
      points[2 * i] = 245 * Math.cos(t) + 140 * Math.cos(outer * t) + 65 * Math.cos(inner * t);
      points[2 * i + 1] = 245 * Math.sin(t) + 140 * Math.sin(outer * t) - 65 * Math.sin(inner * t);
    }
    return points;
  }

  function inspect(points, x, y) {
    let count = 0;
    let distanceSquared = Infinity;
    for (let i = 0; i < points.length; i += 2) {
      const next = (i + 2) % points.length;
      const x0 = points[i];
      const y0 = points[i + 1];
      const y1 = points[next + 1];
      const dx = points[next] - x0;
      const dy = y1 - y0;
      const cross = dx * (y - y0) - dy * (x - x0);
      // Half-open intervals count a shared vertex once, including horizontal rays.
      if (y0 <= y && y < y1 && cross > 0) count++;
      else if (y1 <= y && y < y0 && cross < 0) count--;
      const lengthSquared = dx * dx + dy * dy;
      const along = lengthSquared === 0 ? 0 :
        Math.max(0, Math.min(1, ((x - x0) * dx + (y - y0) * dy) / lengthSquared));
      distanceSquared = Math.min(distanceSquared,
        (x - x0 - along * dx) ** 2 + (y - y0 - along * dy) ** 2);
    }
    return { count, distance: Math.sqrt(distanceSquared) };
  }

  function field(points, size, extent) {
    // Bottom row first. Each value belongs to the center of its square pixel.
    const cell = 2 * extent / size;
    const rows = Array.from({ length: size }, () => []);
    for (let i = 0; i < points.length; i += 2) {
      const next = (i + 2) % points.length;
      const x0 = points[i];
      const y0 = points[i + 1];
      const x1 = points[next];
      const y1 = points[next + 1];
      if (y0 === y1) continue;
      const first = Math.max(0, Math.ceil((Math.min(y0, y1) + extent) / cell - 0.5));
      const end = Math.min(size, Math.ceil((Math.max(y0, y1) + extent) / cell - 0.5));
      const sign = y1 > y0 ? 1 : -1;
      for (let row = first; row < end; row++) {
        const y = -extent + (row + 0.5) * cell;
        const x = x0 + (y - y0) * (x1 - x0) / (y1 - y0);
        rows[row].push([x, sign]);
      }
    }
    const counts = new Int16Array(size * size);
    const levels = new Set([0]);
    for (let row = 0; row < size; row++) {
      let count = 0;
      let previous = 0;
      rows[row].sort((a, b) => a[0] - b[0]);
      for (const [x, sign] of rows[row]) {
        const col = Math.min(size, Math.max(0, Math.ceil((x + extent) / cell - 0.5)));
        counts.fill(count, row * size + previous, row * size + col);
        if (col > previous) levels.add(count);
        count -= sign;
        previous = col;
      }
      counts.fill(count, row * size + previous, (row + 1) * size);
      if (previous < size) levels.add(count);
    }
    return { counts, levels: Array.from(levels).sort((a, b) => a - b) };
  }

  function errorBound(outer, inner, steps = 24000) {
    // Linear interpolation is within max|z''| h²/8 of the smooth curve.
    return (245 + 140 * outer ** 2 + 65 * inner ** 2) * (cycle / steps) ** 2 / 8;
  }

  function areaCoefficient(outer, inner) {
    return 245 ** 2 + 140 ** 2 * outer - 65 ** 2 * inner;
  }

  return Object.freeze({ orbit, inspect, field, errorBound, areaCoefficient });
})();

// Also usable by the offline verification script, without a DOM or dependencies.
if (typeof module !== 'undefined') module.exports = WindingMath;
