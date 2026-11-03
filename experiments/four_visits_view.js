'use strict';
const FourVisitsView = (() => {
  const M = typeof module !== 'undefined' && module.exports ? require('./four_visits_math.js') : FourVisitsMath;
  const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea', '#a7d9bb'];
  const number = x => {
    if (!Number.isFinite(x)) throw new RangeError('A diagram coordinate must be finite.');
    return String(Math.round(x * 10000) / 10000);
  };
  const text = (x, y, content, size = 19, color = '#c7c7d4', extra = '') =>
    `<text x="${number(x)}" y="${number(y)}" font-size="${size}" fill="${color}" ${extra}>${content}</text>`;
  const project = (point, event) => [300 + 243 * (point[0] - event.center[0]) / event.halfSize,
    300 - 243 * (point[1] - event.center[1]) / event.halfSize];
  function lens(state, clip = 'four-window-clip') {
    const { event, crossings } = state;
    const parts = [`<g clip-path="url(#${clip})">`, '<path d="M57,300H543M300,57V543" stroke="#282d43" stroke-dasharray="3 7"/>'];
    if (state.progress !== 0) parts.push(`<path d="${crossings.map((c, i) => (i ? 'L' : 'M') + project(c.point, event).map(number).join(',')).join('')}Z" fill="#e8b66e" fill-opacity=".22"/>`);
    M.normals.forEach((normal, i) => {
      const tangent = [normal[1], -normal[0]], distance = M.shifts[i] - state.weight - M.dot(normal, event.center);
      const center = event.center.map((x, k) => x + distance * normal[k]);
      const ends = [-3, 3].map(side => project(center.map((x, k) => x + side * event.halfSize * tangent[k]), event));
      const selected = event.indices.includes(i);
      parts.push(`<path d="M${ends[0].map(number).join(',')}L${ends[1].map(number).join(',')}" fill="none" stroke="${colors[i]}" stroke-width="${selected ? 3 : 1.5}" opacity="${selected ? 1 : .25}" ${selected ? '' : 'stroke-dasharray="5 6"'}/>`);
      if (selected) {
        const along = (event.indices.indexOf(i) - 1) * .45 * event.halfSize;
        const tip = project(center.map((x, k) => x + along * tangent[k]), event);
        const tx = tangent[0], ty = -tangent[1];
        parts.push(`<path d="M${number(tip[0] - 10 * tx + 5 * ty)},${number(tip[1] - 10 * ty - 5 * tx)}L${tip.map(number).join(',')}L${number(tip[0] - 10 * tx - 5 * ty)},${number(tip[1] - 10 * ty + 5 * tx)}" fill="none" stroke="${colors[i]}" stroke-width="2.5"/>`);
      }
    });
    for (const point of state.progress === 0 ? [event.center] : crossings.map(c => c.point)) {
      const [x, y] = project(point, event);
      parts.push(`<circle cx="${number(x)}" cy="${number(y)}" r="${state.progress === 0 ? 7 : 4.5}" fill="#0b0e1a" stroke="#f4f1e8" stroke-width="2"/>`);
    }
    parts.push('</g>', text(27, 33, state.progress < 0 ? 'Before this triple' : state.progress > 0 ? 'After this triple' : 'At this triple'),
      text(27, 579, 'First-order lines · equal scales', 18));
    return parts.join('');
  }
  function circle(indices) {
    const parts = ['<circle cx="300" cy="300" r="199" fill="none" stroke="#737b99" stroke-dasharray="5 7"/>',
      text(27, 33, 'Four unit left normals'), text(27, 579, 'Counterclockwise order: 1 → 4 → 3 → 2', 18)];
    M.normals.forEach((n, i) => {
      const [x, y] = [300 + 199 * n[0], 300 - 199 * n[1]], selected = indices.includes(i);
      parts.push(`<path d="M300,300L${number(x)},${number(y)}" stroke="${colors[i]}" opacity="${selected ? 1 : .3}"/>`,
        `<circle cx="${number(x)}" cy="${number(y)}" r="${selected ? 7 : 4}" fill="#0b0e1a" stroke="${colors[i]}" stroke-width="2"/>`,
        text(300 + 226 * n[0], 306 - 226 * n[1], String(i + 1), 23, colors[i], 'text-anchor="middle"'));
    });
    const selected = indices.map(i => M.normals[i]);
    parts.push(`<path d="${selected.map((n, i) => `${i ? 'L' : 'M'}${number(300 + 199 * n[0])},${number(300 - 199 * n[1])}`).join('')}Z" fill="#e8b66e" fill-opacity=".10" stroke="#e8b66e" stroke-width="1"/>`);
    return parts.join('');
  }
  return Object.freeze({ colors, number, text, project, lens, circle });
})();
if (typeof module !== 'undefined' && module.exports) module.exports = FourVisitsView;
