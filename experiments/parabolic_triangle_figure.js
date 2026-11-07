'use strict';

// Exact quadratic paths, with rounded drawing coordinates. The rational
// vertices and areas are regenerated separately by parabolic_triangle.py.
const fs = require('node:fs'), path = require('node:path');
const record = require('./parabolic_triangle.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea'];
const white = '#f4f1e8', ink = '#c7c7d4', muted = '#9999ae';
const number = x => {
  if (!Number.isFinite(x)) throw new Error('A drawing coordinate is not finite.');
  return String(Math.round(x * 1e5) / 1e5);
};
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const text = (x, y, s, size = 20, color = ink, extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${esc(s)}</text>`;
const xy = p => p.map(number).join(',');
const rowData = row => ({ p: row.slopes.map(rational), b: row.rates.map(rational),
  mu: rational(row.mu), vertices: row.vertices.map(v => v.map(rational)),
  straight: row.straight_vertices.map(v => v.map(rational)) });
const equation = (row, i, y, straight) => {
  const { p, b, mu } = row;
  return (straight ? -p[i] * y + p[i] ** 2 / 2 : (y - p[i]) ** 2 / 2) + b[i] * mu;
};
function arc(row, i, start, end, map, straight = false, move = true) {
  const a = [equation(row, i, start, straight), start];
  const b = [equation(row, i, end, straight), end];
  const begin = move ? `M${xy(map(a))}` : '';
  if (straight) return `${begin}L${xy(map(b))}`;
  const control = [a[0] + (start - row.p[i]) * (end - start) / 2, (start + end) / 2];
  return `${begin}Q${xy(map(control))} ${xy(map(b))}`;
}
function pocket(row, map, straight = false) {
  return [1, 2, 0].map((branch, k) =>
    arc(row, branch, row.vertices[k][1], row.vertices[(k + 1) % 3][1], map, straight, k === 0)).join('') + 'Z';
}
function root(height, title, description) {
  return [`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="${height}" viewBox="0 0 1200 ${height}" role="img" aria-labelledby="title description">`,
    `<title id="title">${esc(title)}</title><desc id="description">${esc(description)}</desc>`,
    `<rect width="1200" height="${height}" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">`];
}
function chart(parts, row, left, top, width, height, scale, origin, straight, id, yHalf = 2.2) {
  const plot = { x: left + 30, y: top + 78, w: width - 60, h: height - 125 };
  const map = ([x, y]) => [left + origin + scale * x, plot.y + plot.h / 2 - scale * y];
  parts.push(`<defs><clipPath id="${id}"><rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}"/></clipPath></defs>`,
    `<g data-chart="${id}" data-scale="${scale}" data-straight="${straight}">`,
    `<rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}" fill="#0b0e1a"/>`);
  const zero = map([0, 0]);
  for (const y of [-2, -1, 0, 1, 2].filter(y => Math.abs(y) < yHalf)) {
    const sy = map([0, y])[1];
    parts.push(`<path d="M${plot.x},${number(sy)}H${plot.x + plot.w}" stroke="#252b42" stroke-width="1"/>`);
    if (y !== 2) parts.push(text(plot.x + 8, sy - 6, y, 14, muted));
  }
  parts.push(`<g clip-path="url(#${id})">`,
    `<path d="M${number(zero[0])},${plot.y}V${plot.y + plot.h}" stroke="#555b78" stroke-width="1" stroke-dasharray="4 6"/>`,
    `<path d="${pocket(row, map, straight)}" fill="${white}" fill-opacity=".16" data-role="pocket"/>`);
  for (let i = 0; i < 3; i++) parts.push(`<path d="${arc(row, i, -yHalf, yHalf, map, straight)}" fill="none" stroke="${colors[i]}" stroke-width="2.6" data-branch="${i}"/>`);
  const vertices = straight ? row.straight : row.vertices;
  // A triple has one visible mark, rather than three superposed rings.
  const marks = vertices.filter((v, i) => !vertices.slice(0, i).some(w => v[0] === w[0] && v[1] === w[1]));
  for (const v of marks) {
    const p = map(v);
    parts.push(`<circle cx="${number(p[0])}" cy="${number(p[1])}" r="4" fill="${white}" stroke="#0b0e1a" stroke-width="1.4" data-role="crossing"/>`);
  }
  parts.push('</g>',
    text(plot.x + plot.w - 10, top + height - 18, straight ? 'U →' : 'X →', 17, ink, 'text-anchor="end"'),
    text(plot.x + 8, plot.y + 22, 'Y ↑', 17), '</g>');
}

function gapsFigure() {
  const parts = root(1640, 'A curved triangle, read with a straight ruler',
    'Three rows compare a pocket bounded by parabolas with the straight triangle obtained by U=X minus Y squared over two. This horizontal shear preserves every horizontal width and therefore area. All plots have the same scale on both axes. The outer slopes stay at minus two and plus two. The middle slopes are zero, one, and seven quarters; the exact areas in each pair are two, three halves, and fifteen thirty-seconds. Bringing two slopes close shrinks the area. These are limiting curves of three selected arcs, not finite-distance enclosures or a face census for a whole drawing.');
  parts.push(text(35, 60, 'A curved triangle,', 45, white),
    text(35, 120, 'read with a straight ruler.', 45, white),
    text(35, 164, 'Subtract the same parabola from every branch. The area stays the same.', 23),
    text(35, 198, 'Gold: first slope · blue: middle · lilac: last. Equal unit scales throughout.', 19, muted));
  const titles = ['Equal gaps · 2 and 2', 'Unequal gaps · 3 and 1', 'Close slopes · 15/4 and 1/4'];
  record.gap_examples.forEach((entry, i) => {
    const row = rowData(entry), top = 215 + i * 420;
    for (const [left, straight, origin] of [[35, false, 78], [625, true, 244]]) {
      parts.push(`<rect x="${left}" y="${top}" width="540" height="400" rx="14" fill="#141829" stroke="#383b50"/>`,
        text(left + 25, top + 36, straight ? `Same area = ${entry.area}` : titles[i], 27, white),
        text(left + 25, top + 64, straight ? 'U = X − Y²/2' : `Xᵢ = (Y − pᵢ)²/2 · p = (${entry.slopes.join(', ')})`, 18));
      chart(parts, row, left, top, 540, 400, 60, origin, straight, `gap-${i}-${straight}`, 2.2);
      parts.push(text(left + 25, top + 382, straight ? 'Straight edges · unchanged horizontal widths' : 'Three parabolas · one bounded pocket', 17, muted));
    }
  });
  parts.push(text(35, 1520, 'Area = (left gap × right gap × total gap) / 8.', 25, white),
    text(35, 1556, 'Fix the outer slopes: equal gaps give the largest pocket.', 22),
    text(35, 1594, 'Limit curves only. Their area is the leading coefficient of physical area × offset.', 18, muted),
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_triangle.svg'), parts.join('\n') + '\n');
}

function clockFigure() {
  const parts = root(1040, 'One clock, through a curved ruler',
    'Before, at, and after the limiting plane triple for slopes minus two, one, and two and route rates zero, one, and zero. The scaled route parameters are zero, three halves, and three. Above, the straightened triangles shrink to a point and grow on the other side by a homothety centered at U=2,Y=0. Below, restoring Y squared over two bends their edges back into parabolas. Before and after both have exact area three halves, although the curved shapes look different. Every panel has equal unit scales, and the same scale is used in all six panels. The plane triple clock is a local limiting statement; these panels do not give a finite-offset threshold or a full-drawing face census.');
  parts.push(text(35, 61, 'One clock, through a curved ruler.', 44, white),
    text(35, 105, 'Lift only the middle branch: X₁ = (Y − 1)²/2 + μ. Slopes stay at −2, 1, 2.', 22),
    text(35, 143, 'The limiting meeting is at μ = 3/2. Both sides have area (3/2)(1 − 2μ/3)².', 22));
  const phases = ['Before · μ = 0', 'Meeting · μ = 3/2', 'After · μ = 3'];
  record.clock_examples.forEach((entry, i) => {
    const row = rowData(entry), left = 25 + 395 * i;
    parts.push(text(left + 17, 194, phases[i], 25, white),
      `<rect x="${left}" y="213" width="360" height="698" rx="14" fill="#141829" stroke="#383b50"/>`,
      text(left + 20, 248, 'Straight ruler', 23, white));
    chart(parts, row, left, 185, 360, 360, 42, 92, true, `clock-straight-${i}`, 2.2);
    parts.push(text(left + 20, 573, 'Curved ruler', 23, white));
    chart(parts, row, left, 510, 360, 360, 42, 36, false, `clock-curved-${i}`, 2.2);
    parts.push(text(left + 20, 884, `Exact limit area = ${entry.area}`, 21, white));
  });
  parts.push(text(35, 954, 'Straight triangles scale about their meeting. The common shear preserves the quadratic area law.', 21),
    text(35, 991, 'Equal unit scales in every panel. These are limit curves of three arcs, with no full-drawing face claim.', 18, muted),
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_clock.svg'), parts.join('\n') + '\n');
}

if (record.shear !== 'U=X-Y^2/2' || record.gap_examples.map(r => r.area).join(',') !== '2,3/2,15/32'
    || record.clock_examples.map(r => r.area).join(',') !== '3/2,0,3/2') {
  throw new Error('Regenerate the rational parabolic triangle record first.');
}
gapsFigure();
clockFigure();
console.log('Wrote parabolic_triangle.svg and parabolic_clock.svg from exact vertices and quadratic Bézier arcs.');
