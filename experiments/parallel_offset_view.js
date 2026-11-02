'use strict';

// Shared SVG illustration for the browser and downloadable still.
const ParallelOffsetView = (() => {
  const MathModel = typeof module !== 'undefined' && module.exports ? require('./parallel_offset_math.js') : ParallelOffsetMath;
  const Data = typeof module !== 'undefined' && module.exports ? require('./parallel_offset_data.js') : ParallelOffsetData;
  const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
  const number = x => {
    if (!Number.isFinite(x)) throw new RangeError('An illustration coordinate is not finite.');
    return String(Math.round(x * 10000) / 10000);
  };
  const project = (point, center, halfSize) => point.map((v, i) => 300 + (i ? -1 : 1) * 254 * (v - center[i]) / halfSize);
  const path = (points, center, halfSize) => points.map((p, i) => `${i ? 'L' : 'M'}${project(p, center, halfSize).map(number).join(',')}`).join('');
  const line = (points, center, halfSize, color, width = 2, extra = '') =>
    `<path d="${path(points, center, halfSize)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" ${extra}/>`;
  const dot = (point, center, halfSize, color, radius = 5) => {
    const [x, y] = project(point, center, halfSize);
    return `<circle cx="${number(x)}" cy="${number(y)}" r="${radius}" fill="#0b0e1a" stroke="${color}" stroke-width="2"/>`;
  };
  const text = (x, y, content, color = '#c7c7d4', size = 17, extra = '') =>
    `<text x="${number(x)}" y="${number(y)}" fill="${color}" font-size="${size}" ${extra}>${content}</text>`;
  const grid = '<path d="M46,300H554M300,46V554" fill="none" stroke="#282d43" stroke-dasharray="3 7"/>';

  function circle() {
    const center = Data.point, halfSize = 14;
    const parts = [grid,
      line(MathModel.circle(), center, halfSize, '#737b99', 1.5, 'stroke-dasharray="6 7"')];
    Data.times.forEach((t, i) => {
      const record = MathModel.jet(t);
      parts.push(line(MathModel.sample(t - .0035, t + .0035, 100, 0), center, halfSize, colors[i], 3),
        line([record.original, center], center, halfSize, colors[i], 1.5, 'stroke-dasharray="3 5"'),
        dot(record.original, center, halfSize, colors[i], 6));
      // A travel arrow stays on the original branch, off its contact dot.
      const a = MathModel.jet(t + .0012), b = MathModel.jet(t + .0021);
      const [x, y] = project(b.point, center, halfSize), speed = Math.hypot(...b.velocity);
      const [vx, vy] = b.velocity.map(v => v / speed);
      parts.push(line([a.point, b.point], center, halfSize, colors[i], 2.5),
        `<path d="M${number(x - 9 * vx - 5 * vy)},${number(y + 9 * vy - 5 * vx)}L${number(x)},${number(y)}L${number(x - 9 * vx + 5 * vy)},${number(y + 9 * vy + 5 * vx)}" fill="none" stroke="${colors[i]}" stroke-width="2.5"/>`);
      const label = project(record.original, center, halfSize);
      const offsets = [[21, -7], [18, -9], [-31, 25]][i];
      parts.push(text(label[0] + offsets[0], label[1] + offsets[1], String(i + 1), colors[i], 20));
    });
    parts.push(dot(center, center, halfSize, '#f4f1e8', 4),
      text(320, 296, 'Center', '#f4f1e8'),
      text(27, 33, 'Three visits of the original 11 / 6 curve'),
      text(27, 578, `Circle radius ${Data.offset.toFixed(5)} drawing units`));
    return parts.join('');
  }

  function lens(s) {
    const parts = [grid], triangle = MathModel.triangle(s);
    if (s.progress !== 0) {
      parts.push(`<path d="${path(triangle.points, s.center, s.halfSize)}Z" fill="#e8b66e" fill-opacity=".18"/>`);
    }
    s.times.forEach((t, i) => parts.push(line(MathModel.sample(t - .0015, t + .0015, 100, s.offset),
      s.center, s.halfSize, colors[i], 2.8)));
    if (s.progress === 0) {
      colors.forEach((color, i) => parts.push(dot(s.center, s.center, s.halfSize, color, 5 + 5 * i)));
    } else {
      for (const crossing of triangle.crossings) parts.push(dot(crossing.point, s.center, s.halfSize, '#f4f1e8', 4));
    }
    parts.push(text(27, 33, s.progress < 0 ? 'Before the three visits meet' : s.progress > 0 ? 'After the three visits meet' : 'At the selected triple (rounded)'),
      text(27, 578, 'Same scale on both axes · 2 × 2 drawing units'));
    return parts.join('');
  }

  return Object.freeze({ colors, number, project, path, text, circle, lens });
})();

if (typeof module !== 'undefined' && module.exports) module.exports = ParallelOffsetView;
