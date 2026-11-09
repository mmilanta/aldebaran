'use strict';

// Exact quadratic arcs with rounded SVG coordinates. The record is checked
// separately by rational envelope integrals and complete line arrangements.
const fs = require('node:fs'), path = require('node:path');
const record = require('./parabolic_pockets.json');
const tradeoff = require('./parabolic_tradeoff.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
// Quadratic-field values stay exact in the record; only the SVG is rounded.
const value = x => typeof x === 'string' ? rational(x)
  : rational(x.rational) + rational(x.radical) * Math.sqrt(x.radicand);
const n = x => {
  if (!Number.isFinite(x)) throw new Error('A drawing coordinate is not finite.');
  return String(Math.round(x * 1e6) / 1e6);
};
const xy = p => p.map(n).join(',');
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const colors = { white: '#f4f1e8', ink: '#c7c7d4', muted: '#aaaabd', gold: '#e8b66e', blue: '#9fc7eb', green: '#a7d9bb' };
const text = (x, y, s, size = 20, color = colors.ink, extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${esc(s)}</text>`;
const data = row => ({ ...row, p: row.slopes.map(rational), cells: row.cells.map(c =>
  ({ ...c, lo: rational(c.lo), hi: rational(c.hi), area: rational(c.area) })),
  faces: row.faces.map(f => ({ ...f, straight_vertices: f.straight_vertices.map(v => v.map(rational)) })) });
const X = (p, y, straight) => straight ? -p * y + p * p / 2 : (y - p) ** 2 / 2;
function arc(p, lo, hi, map, straight = false, move = true) {
  const a = [X(p, lo, straight), lo], b = [X(p, hi, straight), hi];
  const begin = move ? `M${xy(map(a))}` : '';
  if (straight) return `${begin}L${xy(map(b))}`;
  const control = [a[0] + (lo - p) * (hi - lo) / 2, (lo + hi) / 2];
  return `${begin}Q${xy(map(control))} ${xy(map(b))}`;
}
function envelope(row, which, map, straight, reverse = false) {
  let cells = row.cells.filter(c => c.area > 0);
  if (reverse) cells = cells.slice().reverse();
  return cells.map((c, i) => arc(row.p[c[which]], reverse ? c.hi : c.lo,
    reverse ? c.lo : c.hi, map, straight, i === 0)).join('');
}
function band(row, map, straight = false) {
  return envelope(row, 'inner', map, straight) + envelope(row, 'outer', map, straight, true).replace(/^M/, 'L') + 'Z';
}
const faceColors = [colors.gold, colors.blue, '#d1b6ea'];
function pocket(row, face, map, straight = false) {
  const v = face.straight_vertices;
  return face.branches.map((branch, k) => arc(row.p[branch], v[k][1],
    v[(k + 1) % v.length][1], map, straight, k === 0)).join('') + 'Z';
}
function root(height, title, description) {
  return [`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="${height}" viewBox="0 0 1200 ${height}" role="img" aria-labelledby="title description">`,
    `<title id="title">${esc(title)}</title><desc id="description">${esc(description)}</desc>`,
    `<rect width="1200" height="${height}" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">`];
}
function legend(parts, y) {
  for (const [x, label, color] of [[35, 'Nearer outer curve', colors.gold], [380, 'Nearest of all curves', colors.blue]]) {
    parts.push(`<path d="M${x},${y - 7}h33" stroke="${color}" stroke-width="4"/>`, text(x + 45, y, label, 21));
  }
  parts.push(`<rect x="760" y="${y - 19}" width="30" height="18" fill="${colors.blue}" fill-opacity=".25"/>`,
    text(802, y, 'All bounded pockets', 21));
}
function chart(parts, row, left, top, width, height, scale, straight, id, options = {}) {
  const plot = { x: left + 24, y: top + 78, w: width - 48, h: height - 126 };
  const origin = left + (straight ? width / 2 : width * .255);
  const center = plot.y + plot.h / 2;
  const map = ([x, y]) => [origin + scale * x, center - scale * y];
  parts.push(`<g data-chart="${id}" data-scale="${scale}" data-origin="${n(origin)}" data-center="${n(center)}" data-straight="${straight}" data-slopes="${row.slopes.join(',')}">`,
    `<rect x="${left}" y="${top}" width="${width}" height="${height}" rx="14" fill="#141829" stroke="#383b50"/>`,
    text(left + 22, top + 36, options.title || (straight ? 'Straightened' : 'Curved pockets'), 27, colors.white),
    text(left + 22, top + 64, options.subtitle || (straight ? 'U = X − Y²/2 · same area' : 'Xᵢ = (Y − pᵢ)²/2'), 18),
    `<defs><clipPath id="${id}-clip"><rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}"/></clipPath></defs>`,
    `<rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}" fill="#0b0e1a"/>`);
  for (const y of [-2, -1, 0, 1, 2]) {
    const sy = map([0, y])[1];
    parts.push(`<path d="M${plot.x},${n(sy)}H${plot.x + plot.w}" stroke="#252b42"/>`,
      text(plot.x + 6, sy - 5, y, 14, colors.muted));
  }
  parts.push(`<g clip-path="url(#${id}-clip)">`);
  if (options.faces) {
    const minimum = Math.min(...row.faces.map(f => rational(f.area)));
    row.faces.forEach((face, i) => {
      const color = options.balance ? (rational(face.area) === minimum ? colors.gold : colors.blue) : faceColors[face.last - face.first];
      parts.push(`<path d="${pocket(row, face, map, straight)}" fill="${color}" fill-opacity=".48" data-role="face" data-face="${i}" data-area="${face.area}"/>`);
    });
  } else parts.push(`<path d="${band(row, map, straight)}" fill="${colors.blue}" fill-opacity=".25" data-role="band"/>`);
  for (const p of row.p) parts.push(`<path d="${arc(p, -2.2, 2.2, map, straight)}" fill="none" stroke="#c7c7d4" stroke-opacity=".4" stroke-width="1.5" data-role="branch"/>`);
  for (const [which, color] of options.faces ? [] : [['outer', colors.gold], ['inner', colors.blue]]) {
    parts.push(`<path d="${envelope(row, which, map, straight)}" fill="none" stroke="${color}" stroke-width="3.2" stroke-linejoin="round" data-role="${which}"/>`);
  }
  // One horizontal row makes the shear's unchanged widths visible.
  const y = 0, near = row.p.reduce((a, b) => Math.abs(a - y) <= Math.abs(b - y) ? a : b);
  const far = Math.abs(row.p[0] - y) <= Math.abs(row.p.at(-1) - y) ? row.p[0] : row.p.at(-1);
  const a = map([X(near, y, straight), y]), b = map([X(far, y, straight), y]);
  if (options.slice !== false) parts.push(`<path d="M${xy(a)}L${xy(b)}" stroke="${colors.white}" stroke-width="2" stroke-dasharray="4 4" data-role="slice"/>`,
    ...[a, b].map(p => `<circle cx="${n(p[0])}" cy="${n(p[1])}" r="3" fill="${colors.white}"/>`));
  if (options.vertices) {
    for (let i = 0; i < row.p.length; i++) for (let j = i + 1; j < row.p.length; j++) {
      const y = (row.p[i] + row.p[j]) / 2, p = map([X(row.p[i], y, straight), y]);
      parts.push(`<circle cx="${n(p[0])}" cy="${n(p[1])}" r="2.6" fill="${colors.white}" data-role="crossing"/>`);
    }
  }
  if (options.faces) row.faces.forEach((face, i) => {
    const v = face.straight_vertices;
    const y = v.reduce((s, p) => s + p[1], 0) / v.length;
    // Balance the polygon centroid with its horizontal slice midpoint;
    // a small label then fits even the slanted triangles' narrow ends.
    const u = v.reduce((s, p) => s + p[0], 0) / v.length;
    const centroid = straight ? u : u + y * y / 2;
    const lo = Math.max(...row.p.slice(face.first, face.last + 1).map(p => X(p, y, straight)));
    const hi = Math.min(X(row.p[face.first - 1], y, straight), X(row.p[face.last + 1], y, straight));
    const p = map([(2 * centroid + (lo + hi) / 2) / 3, y]);
    parts.push(text(n(p[0]), n(p[1] + 5.5), options.balance && !options.letters ? face.area : String.fromCharCode(65 + i),
      16, colors.white, 'text-anchor="middle" data-role="face-label"'));
  });
  parts.push('</g>', text(plot.x + plot.w - 6, top + height - 18, straight ? 'U →' : 'X →', 17, colors.muted, 'text-anchor="end"'),
    text(plot.x + plot.w - 6, top + 64, 'Y ↑', 17, colors.muted, 'text-anchor="end"'), '</g>');
  return map;
}
function rail(parts, row, top) {
  const start = 88, width = 1024, p0 = row.p[0], span = row.p.at(-1) - p0;
  const x = p => start + width * (p - p0) / span;
  parts.push(text(35, top - 40, 'Slope positions', 18, colors.muted));
  row.p.forEach((p, i) => parts.push(`<circle cx="${n(x(p))}" cy="${top}" r="4" fill="${colors.white}"/>`,
    text(x(p), top - 13, row.slopes[i], 18, colors.ink, 'text-anchor="middle"')));
  row.gaps.forEach((g, i) => parts.push(`<path d="M${n(x(row.p[i]) + 6)},${top}H${n(x(row.p[i + 1]) - 6)}" stroke="${i % 2 ? colors.blue : colors.gold}" stroke-width="4"/>`,
    text((x(row.p[i]) + x(row.p[i + 1])) / 2, top + 29, `g = ${g}`, 18, colors.muted, 'text-anchor="middle"')));
}
function bandFigure() {
  const parts = root(1590, 'All the pockets, one band',
    'Five limit parabolas with slopes between minus two and plus two. The gold edge is the nearer of the two extreme parabolas; the blue edge is the nearest of all five. Every bounded pocket, and no unbounded face, lies in the shaded band between them. In each row, subtracting Y squared over two straightens the complete arrangement without changing horizontal widths. Both arrangements have six bounded pockets. Equal gaps give total area five halves; gaps one, three halves, five quarters, and one quarter instead give 615 over 256. All four panels use equal and identical unit scales. White horizontal slices at Y=0 have unchanged widths. This is an exact arrangement of limiting parabolas, with no finite-offset or full-orbital-drawing claim.');
  parts.push(text(35, 65, 'All the pockets, one band.', 48, colors.white),
    text(35, 110, 'Follow two envelopes. The shaded space gathers every bounded pocket.', 23));
  legend(parts, 157);
  record.band_examples.forEach((entry, i) => {
    const row = data(entry), top = 225 + 650 * i;
    parts.push(text(35, top - 20, `${entry.name} · ${entry.face_count} pockets · total area ${entry.area}`, 28, colors.white));
    chart(parts, row, 35, top, 540, 440, 72, false, `band-curved-${i}`);
    chart(parts, row, 625, top, 540, 440, 72, true, `band-straight-${i}`);
    rail(parts, row, top + 500);
    parts.push(text(35, top + 570, i === 0 ? '(4³ − 1³ − 1³ − 1³ − 1³) / 24 = 5/2' : '(4³ − 1³ − (3/2)³ − (5/4)³ − (1/4)³) / 24 = 615/256', 24, colors.white));
  });
  parts.push(text(35, 1507, 'Equal gaps give the largest total area at fixed slope count and span.', 24, colors.white),
    text(35, 1545, 'Equal unit scales throughout. These are complete limit arrangements; finite drawings need separate bounds.', 18, colors.muted),
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_envelope.svg'), parts.join('\n') + '\n');
}
function insertionFigure() {
  const parts = root(1040, 'Where should the next parabola go?',
    'Three equal-scale panels show slopes minus two, zero, two; insertion of minus one; and redistribution to four equally spaced slopes minus two, minus two thirds, two thirds, two. Total areas are two, nine quarters, and 64 over 27. Splitting one existing gap at its midpoint adds the most area when the old slopes are held fixed: one quarter here. The green patch marks exactly the newly added area, inside the gold outer envelope. Moving all four slopes to equal spacing gives a larger global area. A best single insertion and a best complete arrangement solve different constrained problems. These are exact limiting parabolas at scaled route parameter zero.');
  parts.push(text(35, 65, 'Where should the next parabola go?', 45, colors.white),
    text(35, 110, 'Split a wide gap at its midpoint. Then compare with spacing every slope again.', 23));
  record.insertion_examples.forEach((entry, i) => {
    const row = data(entry), left = 25 + 395 * i;
    const map = chart(parts, row, left, 205, 360, 400, 56, false, `insert-${i}`,
      { title: ['Keep three slopes', 'Add one slope', 'Move all four'][i], subtitle: `p = (${entry.slopes.join(', ')})`, slice: false });
    // Append only the new band, using its two new nearest-slope pieces.
    // The original blue band is preserved underneath; no signed fills.
    if (i === 1) {
      const lo = -1.5, mid = -1, hi = -.5;
      const d = arc(-1, lo, hi, map) + arc(0, hi, mid, map, false, false)
        + arc(-2, mid, lo, map, false, false) + 'Z';
      parts.push(`<g clip-path="url(#insert-${i}-clip)"><path d="${d}" fill="${colors.green}" fill-opacity=".7" data-role="added-band"/></g>`);
    }
    parts.push(text(left + 20, 660, `Total area = ${entry.area}`, 25, colors.white),
      text(left + 20, 698, ['One pocket', 'Three pockets · gain 1/4', 'Three pockets · largest total'][i], 19),
      text(left + 20, 741, `Gaps: ${entry.gaps.join(', ')}`, 20, colors.muted));
  });
  parts.push(`<rect x="35" y="797" width="1130" height="156" rx="12" fill="#141829" stroke="#383b50"/>`,
    text(58, 837, 'In a fixed gap of length g, insertion splits it into a + b = g.', 23, colors.white),
    text(58, 879, 'Added area = abg/8 = g³/32 − (g/8)(a − g/2)².', 27, colors.green),
    text(58, 924, 'The largest fixed-gap gain is at its midpoint; a larger gap gives a larger gain.', 21),
    text(35, 1000, 'A best single addition keeps the old slopes fixed. The best full arrangement can move them.', 20, colors.muted),
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_insertion.svg'), parts.join('\n') + '\n');
}
function runsFigure() {
  const row = data(record.band_examples[0]);
  const parts = root(1290, 'A pocket chooses a run',
    'Six bounded pockets of the five parabolas with slopes minus two, minus one, zero, one, two. Each pocket is identified by the slopes of the curves lying to its left: a nonempty consecutive run of the three interior slopes. The same letters A through F mark the curved pockets and their straightened images. One-slope runs A, D, F are gold and have area one quarter each; two-slope runs B, E are blue and have area one half each; the three-slope run C is lilac and has area three quarters. The cards list every run and repeat these areas. Both panels use identical unit scales. In a straightened arrangement every one-slope face is a triangle and every longer-run face is a quadrilateral. The classification applies to distinct slopes, including unequal gaps; only these simple area multiples need equal spacing. These are complete exact limit arrangements, not a finite orbital drawing.');
  parts.push(text(35, 65, 'A pocket chooses a run.', 48, colors.white),
    text(35, 110, 'Look left from inside a pocket. Those curves always have consecutive slopes.', 23));
  [['One slope · area 1/4', 35], ['Two slopes · area 1/2', 410], ['Three slopes · area 3/4', 785]].forEach(([label, x], i) =>
    parts.push(`<rect x="${x}" y="143" width="25" height="18" fill="${faceColors[i]}" fill-opacity=".7"/>`, text(x + 37, 160, label, 20)));
  chart(parts, row, 35, 205, 540, 520, 86, false, 'runs-curved', { faces: true, slice: false });
  chart(parts, row, 625, 205, 540, 520, 86, true, 'runs-straight', { faces: true, slice: false });
  parts.push(text(35, 765, 'Every nonempty run of the interior slopes −1, 0, 1 appears exactly once:', 23, colors.white));
  for (let size = 1; size <= 3; size++) {
    const faces = row.faces.map((face, i) => ({ ...face, label: String.fromCharCode(65 + i) })).filter(f => f.last - f.first + 1 === size);
    const width = 340, gap = 35, start = (1200 - faces.length * width - (faces.length - 1) * gap) / 2;
    faces.forEach((face, k) => {
      const left = start + k * (width + gap), top = 790 + 110 * (size - 1), color = faceColors[size - 1];
      parts.push(`<rect x="${left}" y="${top}" width="${width}" height="95" rx="10" fill="#141829" stroke="#383b50"/>`,
        text(left + 20, top + 29, `${face.label} · ${size === 1 ? 'one slope' : `${size} slopes`} · area ${face.area}`, 21, colors.white));
      const bead = i => left + 55 + (i - 1) * 115;
      if (size > 1) parts.push(`<path d="M${bead(face.first)},${top + 55}H${bead(face.last)}" stroke="${color}" stroke-width="3"/>`);
      for (let i = 1; i <= 3; i++) {
        const active = face.first <= i && i <= face.last;
        parts.push(`<circle cx="${bead(i)}" cy="${top + 55}" r="4" fill="${active ? color : '#555b78'}"/>`,
          text(bead(i), top + 82, row.slopes[i], 18, active ? color : colors.muted, 'text-anchor="middle"'));
      }
    });
  }
  parts.push(text(35, 1165, 'Total = 3 × 1/4 + 2 × 1/2 + 1 × 3/4 = 5/2.', 27, colors.white),
    text(35, 1210, 'n distinct slopes give (n − 1)(n − 2)/2 bounded pockets, even when gaps differ.', 23),
    text(35, 1250, 'Equal unit scales in both panels. This classifies exact limit parabolas, with no finite-orbital face claim.', 18, colors.muted),
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_runs.svg'), parts.join('\n') + '\n');
}
function balanceFigure() {
  const parts = root(1720, 'Make the smallest pocket larger',
    'Two four-parabola arrangements with fixed outer slopes minus two and plus two. Equal gaps maximize total area, 64 over 27, with individual pocket areas 16 over 27, 32 over 27, and 16 over 27. Gaps one, two, one instead make all three pocket areas exactly three quarters, with total nine quarters. This second arrangement uniquely maximizes the smallest pocket at this span, despite its smaller total. Gold marks the smallest pockets; blue marks a larger pocket. Exact areas are written inside the pockets. Both drawing panels use identical unit scales. Below, a graph shows all efficient compromises: increasing total area reduces the smallest area. A green point at gaps six fifths, eight fifths, six fifths has total 294 over 125 and smallest area 84 over 125. This graph compares areas with different axis scales. Its curve is an exact cubic Bezier with rounded coordinates. These are complete limit arrangements, not finite orbital drawings.');
  parts.push(text(35, 65, 'Make the smallest pocket larger.', 46, colors.white),
    text(35, 110, 'The most total area and the largest smallest pocket can need different spacing.', 23));
  for (const [x, color, label] of [[35, colors.gold, 'Smallest pockets'], [410, colors.blue, 'A larger pocket']]) parts.push(
    `<rect x="${x}" y="143" width="25" height="18" fill="${color}" fill-opacity=".7"/>`, text(x + 37, 160, label, 21));
  record.balance_examples.forEach((entry, i) => {
    const row = data(entry), left = 35 + 590 * i;
    parts.push(text(left, 210, entry.name, 28, colors.white));
    chart(parts, row, left, 230, 540, 520, 86, false, `balance-${i}`,
      { faces: true, slice: false, balance: true, title: i ? 'Gaps in the ratio 1 : 2 : 1' : 'Equal gaps', subtitle: `p = (${entry.slopes.join(', ')})` });
    const minimum = entry.faces.reduce((a, f) => rational(f.area) < rational(a) ? f.area : a, entry.faces[0].area);
    parts.push(text(left + 22, 804, `Total area = ${entry.area}`, 27, colors.white),
      text(left + 22, 849, `Smallest pocket = ${minimum}`, 27, colors.gold),
      text(left + 22, 894, `Gaps: ${entry.gaps.join(', ')}`, 22, colors.muted));
  });
  parts.push(text(35, 963, 'With span L and four slopes: no smallest pocket can exceed 3L³/256.', 25, colors.white),
    text(35, 1038, 'Between them, a smooth compromise.', 29, colors.white),
    text(35, 1079, 'Along this curve, more total area always costs some of the smallest pocket.', 22));
  const plot = { x: 110, y: 1130, w: 970, h: 370, low: 2.235, high: .77, sx: 970 / .15, sy: 370 / .195 };
  const project = ([total, smallest]) => [plot.x + (total - plot.low) * plot.sx, plot.y + (plot.high - smallest) * plot.sy];
  parts.push(`<g data-area-plot="compromise" data-left="${plot.x}" data-top="${plot.y}" data-low="${plot.low}" data-high="${plot.high}" data-x-scale="${plot.sx}" data-y-scale="${plot.sy}">`,
    `<rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}" fill="#0b0e1a" stroke="#383b50"/>`);
  for (const [value, label] of [[.75, '3/4'], [2 / 3, '2/3'], [16 / 27, '16/27']]) {
    const y = project([plot.low, value])[1];
    parts.push(`<path d="M${plot.x},${n(y)}h${plot.w}" stroke="#252b42"/>`,
      text(plot.x - 14, y + 6, label, 18, colors.muted, 'text-anchor="end"'));
  }
  for (const [value, label] of [[9 / 4, '9/4'], [7 / 3, '7/3'], [64 / 27, '64/27']]) {
    const x = project([value, .77])[0];
    parts.push(`<path d="M${n(x)},${plot.y}v${plot.h}" stroke="#252b42"/>`,
      text(x, plot.y + plot.h + 29, label, 18, colors.muted, 'text-anchor="middle"'));
  }
  const controls = record.compromise.bezier.map(p => project(p.map(rational)));
  parts.push(`<path d="M${xy(controls[0])}C${xy(controls[1])} ${xy(controls[2])} ${xy(controls[3])}" fill="none" stroke="${colors.white}" stroke-width="3" data-role="compromise"/>`);
  const middle = project(record.compromise.middle.areas.map(rational));
  for (const [p, color] of [[controls[0], colors.gold], [middle, colors.green], [controls[3], colors.blue]]) parts.push(
    `<circle cx="${n(p[0])}" cy="${n(p[1])}" r="5" fill="${color}" stroke="#0b0e1a" stroke-width="1.5"/>`);
  parts.push(text(controls[0][0] + 19, controls[0][1] - 14, 'Equal pockets', 19, colors.gold),
    text(middle[0] + 19, middle[1] - 14, 'A compromise', 19, colors.green),
    text(controls[3][0] - 199, controls[3][1] - 14, 'Largest total', 19, colors.blue),
    text(plot.x, plot.y - 15, 'Smallest area ↑', 18),
    text(plot.x + plot.w, plot.y + plot.h + 70, 'Total area →', 18, colors.ink, 'text-anchor="end"'), '</g>',
    text(35, 1570, 'Green: gaps 6/5, 8/5, 6/5 · total 294/125 · smallest 84/125.', 18, colors.green),
    text(35, 1615, 'Odd slope counts favor equal gaps. Larger even counts favor alternating gaps.', 22),
    text(35, 1655, 'Drawing panels have equal unit scales. The area graph uses different scales. These are exact limit models.', 18, colors.muted),
    '<a href="https://mmilanta.github.io/aldebaran/experiments/parabolic_balance.md">', text(35, 1695, 'Follow the sharp bounds, the compromise curve, and the alternating-gap formula ↗', 21, colors.gold), '</a>',
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_balance.svg'), parts.join('\n') + '\n');
}
function tradeoffFigure() {
  const parts = root(1980, 'Ten pockets, one compromise',
    'Two six-parabola arrangements with the same outer slopes minus two and plus two and ten bounded pockets each. Equal gaps four fifths give total 64 over 25 and smallest area 16 over 125. Alternating gaps two thirds, one, two thirds, one, two thirds give total 275 over 108 and smallest area five thirty-sixths. Letters A through J name the same consecutive runs of interior slopes in both drawings; the area lists identify every pocket. Gold marks the four smallest pockets, blue the other six. Both panels use equal and identical coordinate scales. Below, one cubic graph follows every efficient compromise for six slopes: alternating short and long gaps. Its final point uniquely maximizes the smallest area, about 0.140251, with total about 2.529349. The green point is the rational arrangement shown above. It uniquely maximizes total plus five times the smallest area, with score 175 over 54; a dashed green supporting line holds that score constant. The graph uses different scales for the two area measures. Exact rational and quadratic-field controls are rounded only for drawing. These are complete exact limit parabolas at scaled route parameter zero, not finite orbital faces.');
  parts.push(text(35, 65, 'Ten pockets, one compromise.', 47, colors.white),
    text(35, 110, 'Give the smallest pockets more room. Some larger ones must give way.', 23));
  for (const [x, color, label] of [[35, colors.gold, 'Four smallest pockets'], [465, colors.blue, 'Six larger pockets']]) parts.push(
    `<rect x="${x}" y="143" width="25" height="18" fill="${color}" fill-opacity=".7"/>`, text(x + 37, 160, label, 21));
  tradeoff.examples.forEach((entry, i) => {
    const row = data(entry), left = 35 + 590 * i;
    parts.push(text(left, 200, entry.name, 28, colors.white));
    chart(parts, row, left, 220, 540, 600, 112, false, `tradeoff-${i}`,
      { faces: true, slice: false, balance: true, letters: true,
        title: i ? 'Short, long, short, long, short' : 'Equal gaps', subtitle: `p = (${entry.slopes.join(', ')})` });
    parts.push(text(left + 22, 865, `Total area = ${entry.area}`, 27, colors.white),
      text(left + 22, 908, `Smallest pocket = ${entry.smallest}`, 27, colors.gold),
      text(left + 22, 950, `Gaps: ${entry.gaps.join(', ')}`, 20, colors.muted));
    const groups = new Map();
    entry.faces.forEach((face, j) => {
      if (!groups.has(face.area)) groups.set(face.area, []);
      groups.get(face.area).push(String.fromCharCode(65 + j));
    });
    [...groups.entries()].sort((a, b) => rational(a[0]) - rational(b[0])).forEach(([area, letters], j) =>
      parts.push(text(left + 22, 1010 + 32 * j, `${letters.join(', ')}: ${area} each`, 21,
        area === entry.smallest ? colors.gold : colors.ink, 'data-role="area-list"')));
  });
  parts.push(text(35, 1180, 'Every efficient choice lies on this curve.', 30, colors.white),
    text(35, 1221, 'More total area means a smaller minimum. Alternating gaps give the whole boundary.', 22));
  const plot = { x: 110, y: 1270, w: 970, h: 400, low: 2.527, high: .1415, sx: 970 / .035, sy: 400 / .0145 };
  const project = ([total, smallest]) => [plot.x + (total - plot.low) * plot.sx, plot.y + (plot.high - smallest) * plot.sy];
  parts.push(`<g data-area-plot="six-slope" data-left="${plot.x}" data-top="${plot.y}" data-low="${plot.low}" data-high="${plot.high}" data-x-scale="${plot.sx}" data-y-scale="${plot.sy}">`,
    `<rect x="${plot.x}" y="${plot.y}" width="${plot.w}" height="${plot.h}" fill="#0b0e1a" stroke="#383b50"/>`);
  for (const tick of [.128, .135, .14]) {
    const y = project([plot.low, tick])[1];
    parts.push(`<path d="M${plot.x},${n(y)}h${plot.w}" stroke="#252b42"/>`,
      text(plot.x - 14, y + 6, tick.toFixed(3), 18, colors.muted, 'text-anchor="end"'));
  }
  for (const tick of [2.53, 2.54, 2.55, 2.56]) {
    const x = project([tick, plot.high])[0];
    parts.push(`<path d="M${n(x)},${plot.y}v${plot.h}" stroke="#252b42"/>`,
      text(x, plot.y + plot.h + 29, tick.toFixed(2), 18, colors.muted, 'text-anchor="middle"'));
  }
  const controls = tradeoff.bezier.map(p => project(p.map(value)));
  const score = value(tradeoff.weighted_example.score), price = value(tradeoff.weighted_example.price);
  const lineStart = project([score - price * plot.high, plot.high]);
  const lineEnd = project([plot.low + plot.w / plot.sx, (score - plot.low - plot.w / plot.sx) / price]);
  parts.push(`<path d="M${xy(lineStart)}L${xy(lineEnd)}" fill="none" stroke="${colors.green}" stroke-opacity=".75" stroke-width="1.7" stroke-dasharray="7 7" data-role="weighted-support"/>`,
    text(760, 1350, 'Total + 5 × smallest = 175/54', 18, colors.green));
  parts.push(`<path d="M${xy(controls[0])}C${xy(controls[1])} ${xy(controls[2])} ${xy(controls[3])}" fill="none" stroke="${colors.white}" stroke-width="3" data-role="six-slope-compromise"/>`);
  const middle = project([rational(tradeoff.examples[1].area), rational(tradeoff.examples[1].smallest)]);
  for (const [p, color, role] of [[controls[0], colors.blue, 'equal'], [middle, colors.green, 'rational'], [controls[3], colors.gold, 'optimal']]) parts.push(
    `<circle cx="${n(p[0])}" cy="${n(p[1])}" r="5" fill="${color}" stroke="#0b0e1a" stroke-width="1.5" data-point="${role}"/>`);
  parts.push(text(controls[0][0] - 155, controls[0][1] - 15, 'Largest total', 19, colors.blue),
    text(middle[0] + 18, middle[1] - 18, 'The rational example', 19, colors.green),
    text(controls[3][0] + 19, controls[3][1] - 15, 'Largest minimum', 19, colors.gold),
    text(plot.x, plot.y - 15, 'Smallest area ↑', 18),
    text(plot.x + plot.w, plot.y + plot.h + 70, 'Total area →', 18, colors.ink, 'text-anchor="end"'), '</g>',
    text(35, 1795, 'Green: total 275/108 · smallest 5/36 · gaps 2/3, 1, 2/3, 1, 2/3.', 21, colors.green),
    text(35, 1837, 'Gold endpoint: total ≈ 2.529349 · smallest ≈ 0.140251.', 21, colors.gold),
    text(35, 1879, 'Green uniquely maximizes total + 5 × smallest area. The dashed line holds that score constant.', 20),
    text(35, 1918, 'Parabola panels have identical unit scales. The area graph uses separate scales. These are exact limit models.', 17, colors.muted),
    '<a href="https://mmilanta.github.io/aldebaran/experiments/parabolic_tradeoff.md">',
    text(35, 1956, 'Follow the complete bound, the equality case, and the exact cubic coordinates ↗', 21, colors.gold), '</a>',
    '</g></svg>');
  fs.writeFileSync(path.join(__dirname, 'parabolic_tradeoff.svg'), parts.join('\n') + '\n');
}
if (record.shear !== 'U=X-Y^2/2' || record.band_examples.map(e => e.area).join(',') !== '5/2,615/256'
    || record.insertion_examples.map(e => e.area).join(',') !== '2,9/4,64/27') {
  throw new Error('Regenerate the rational envelope record first.');
}
bandFigure();
insertionFigure();
runsFigure();
balanceFigure();
tradeoffFigure();
console.log('Wrote five pocket SVGs from exact face data and quadratic/cubic paths; SVG coordinates are rounded.');
