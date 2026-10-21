'use strict';

const shapes = {
  garden: {
    name: 'Garden', outer: 7, inner: 13,
    examples: [[0, 0, 61], [1, 0, 0], [2, -5, -264], [3, 149, 0]]
  },
  backwards: {
    name: 'A negative total', outer: 2, inner: 25,
    examples: [[-7, -154, 0], [-6, -138, 31], [-5, -110, -6], [-4, -192, -6],
      [-3, -77, 7], [-2, -206, 52], [-1, -100, 287], [0, -130, 168], [1, 0, 0]]
  }
};
const map = document.querySelector('#map');
const ctx = map.getContext('2d');
const probe = document.querySelector('#probe');
const probeCtx = probe.getContext('2d');
const pointX = document.querySelector('#point-x');
const pointY = document.querySelector('#point-y');
const showColors = document.querySelector('#show-colors');
const extent = 480;
const size = map.width;
const colorMap = document.createElement('canvas');
colorMap.width = colorMap.height = size;
let currentShape = shapes.garden;
let points;
let curve;

function signed(count) {
  return count > 0 ? `+${count}` : String(count).replace('-', '−');
}

function color(count) {
  if (count === 0) return [11, 14, 26];
  const dark = count > 0 ? [104, 80, 54] : [40, 78, 115];
  const light = count > 0 ? [255, 224, 177] : [188, 223, 250];
  const mix = 1 - Math.exp(-(Math.abs(count) - 1) / 2.5);
  return dark.map((channel, i) => Math.round(channel + (light[i] - channel) * mix));
}

function drawMap() {
  if (showColors.checked) ctx.drawImage(colorMap, 0, 0);
  else {
    ctx.fillStyle = '#0b0e1a';
    ctx.fillRect(0, 0, size, size);
  }
  ctx.strokeStyle = 'rgba(244, 241, 232, .75)';
  ctx.lineWidth = 1;
  ctx.stroke(curve);
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, 40, 0, 2 * Math.PI);
  ctx.setLineDash([3, 5]);
  ctx.strokeStyle = '#f4f1e8';
  ctx.stroke();
  ctx.setLineDash([]);
  // The small fixed cross distinguishes the center from the movable white ring.
  ctx.beginPath();
  ctx.moveTo(size / 2 - 4, size / 2);
  ctx.lineTo(size / 2 + 4, size / 2);
  ctx.moveTo(size / 2, size / 2 - 4);
  ctx.lineTo(size / 2, size / 2 + 4);
  ctx.stroke();
}

function updatePoint() {
  const x = Number(pointX.value);
  const y = Number(pointY.value);
  document.querySelector('#x-value').value = pointX.value;
  document.querySelector('#y-value').value = pointY.value;
  const { count, distance } = WindingMath.inspect(points, x, y);
  // A one-unit visual margin also strictly exceeds the interpolation error.
  const near = distance <= Math.max(1, WindingMath.errorBound(currentShape.outer, currentShape.inner));
  const description = near ? 'Near the curve. Move the point a little farther from the line to count its turns.'
    : count === 0 ? 'No net turns. Clockwise and counterclockwise turns balance here.'
      : `${Math.abs(count) === 1 ? 'One' : Math.abs(count)} net ` +
        `${count > 0 ? 'counterclockwise' : 'clockwise'} ${Math.abs(count) === 1 ? 'turn' : 'turns'}.`;
  document.querySelector('#count').value = near ? 'Near curve' : signed(count);
  document.querySelector('#count-description').textContent = description;
  map.setAttribute('aria-label', `${currentShape.name}, rhythms ${currentShape.outer} and ${currentShape.inner}. ` +
    `Point at ${x}, ${y}. ${description}`);
  for (const button of document.querySelectorAll('[data-count]')) {
    button.setAttribute('aria-pressed', String(!near && Number(button.dataset.count) === count));
  }
  probeCtx.clearRect(0, 0, size, size);
  probeCtx.beginPath();
  probeCtx.arc(extent + x, extent - y, 8, 0, 2 * Math.PI);
  probeCtx.strokeStyle = '#0b0e1a';
  probeCtx.lineWidth = 6;
  probeCtx.stroke();
  probeCtx.strokeStyle = '#f4f1e8';
  probeCtx.lineWidth = 2;
  probeCtx.setLineDash(near ? [3, 3] : []);
  probeCtx.stroke();
  probeCtx.setLineDash([]);
}

function placePoint(x, y) {
  pointX.value = String(Math.round(Math.min(470, Math.max(-470, x))));
  pointY.value = String(Math.round(Math.min(470, Math.max(-470, y))));
  updatePoint();
}

function selectShape(key) {
  currentShape = shapes[key];
  points = WindingMath.orbit(currentShape.outer, currentShape.inner);
  curve = new Path2D();
  for (let i = 0; i < points.length; i += 2) {
    const x = extent + points[i];
    const y = extent - points[i + 1];
    if (i === 0) curve.moveTo(x, y);
    else curve.lineTo(x, y);
  }
  curve.closePath();
  const { counts } = WindingMath.field(points, size, extent);
  const colorCtx = colorMap.getContext('2d');
  const image = colorCtx.createImageData(size, size);
  const palette = new Map();
  for (let i = 0; i < counts.length; i++) {
    if (!palette.has(counts[i])) palette.set(counts[i], color(counts[i]));
    // The field starts at the bottom; canvas pixels start at the top.
    const pixel = 4 * ((size - 1 - Math.floor(i / size)) * size + i % size);
    const rgb = palette.get(counts[i]);
    image.data.set([...rgb, 255], pixel);
  }
  colorCtx.putImageData(image, 0, 0);
  const legend = document.querySelector('#legend');
  legend.replaceChildren();
  for (const [count, x, y] of currentShape.examples) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.count = String(count);
    button.setAttribute('aria-label', `Visit a region with count ${signed(count)}`);
    const swatch = document.createElement('span');
    swatch.className = 'swatch';
    swatch.style.backgroundColor = `rgb(${color(count).join(',')})`;
    swatch.setAttribute('aria-hidden', 'true');
    button.append(swatch, document.createTextNode(signed(count)));
    button.addEventListener('click', () => placePoint(x, y));
    legend.append(button);
  }
  for (const button of document.querySelectorAll('[data-shape]')) {
    button.setAttribute('aria-pressed', String(button.dataset.shape === key));
  }
  const coefficient = WindingMath.areaCoefficient(currentShape.outer, currentShape.inner);
  document.querySelector('#area').value = `${coefficient < 0 ? '−' : ''}${Math.abs(coefficient).toLocaleString('en')}π`;
  document.querySelector('#area-description').textContent = coefficient < 0
    ? 'The blue regions subtract more than the gold regions add. The center still counts as +1.'
    : 'The gold regions add up, with overlaps counted more than once. The center counts as +1.';
  document.querySelector('#draw-link').href = `../index.html?outer=${currentShape.outer}&inner=${currentShape.inner}`;
  drawMap();
  updatePoint();
}

for (const control of [pointX, pointY]) control.addEventListener('input', updatePoint);
for (const button of document.querySelectorAll('[data-shape]')) {
  button.addEventListener('click', () => selectShape(button.dataset.shape));
}
document.querySelector('#center').addEventListener('click', () => placePoint(0, 0));
showColors.addEventListener('change', drawMap);
map.addEventListener('click', event => {
  const rect = map.getBoundingClientRect();
  placePoint((event.clientX - rect.left) / rect.width * 2 * extent - extent,
    extent - (event.clientY - rect.top) / rect.height * 2 * extent);
});
map.addEventListener('keydown', event => {
  const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] };
  if (!directions[event.key] || event.altKey || event.ctrlKey || event.metaKey) return;
  event.preventDefault();
  const [dx, dy] = directions[event.key];
  const step = event.shiftKey ? 1 : 10;
  placePoint(Number(pointX.value) + step * dx, Number(pointY.value) + step * dy);
});
selectShape('garden');
