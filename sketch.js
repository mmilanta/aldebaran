'use strict';

const canvas = document.querySelector('#sketch');
const ctx = canvas.getContext('2d');
const arms = document.querySelector('#arms');
const armCtx = arms.getContext('2d');
const showArms = document.querySelector('#show-arms');
const rhythm = document.querySelector('#rhythm');
const echo = document.querySelector('#echo');
const study = document.querySelector('#study');
const pause = document.querySelector('#pause');
const status = document.querySelector('#status');
const shareStatus = document.querySelector('#share-status');
const shareFallback = document.querySelector('#share-fallback');
const drawingLink = document.querySelector('#drawing-link');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const totalSteps = 24000;
const cycle = Math.PI * 2;
let step = 0;
let running = !reducedMotion.matches;
let frame = null;
let lastTime = null;
let shareAttempt = 0;
let linkTimer = null;
let lastLinkWrite = -Infinity;

function rhythmsFromLink(url) {
  const params = new URL(url).searchParams;
  // Treat the pair as a unit: malformed or incomplete links keep the default.
  const values = [params.getAll('outer'), params.getAll('inner')];
  if (values.some(entries => entries.length !== 1 || !/^\d+$/.test(entries[0]))) return null;
  const [outer, inner] = values.map(entries => Number(entries[0]));
  if (outer < Number(rhythm.min) || outer > Number(rhythm.max) ||
      inner < Number(echo.min) || inner > Number(echo.max)) return null;
  return [outer, inner];
}

function readLink() {
  const pair = rhythmsFromLink(window.location.href);
  if (pair === null) return false;
  const [outer, inner] = pair;
  rhythm.value = String(outer);
  echo.value = String(inner);
  return true;
}

function linkToDrawing() {
  const url = new URL(window.location.href);
  url.searchParams.set('outer', rhythm.value);
  url.searchParams.set('inner', echo.value);
  return url.href;
}

function writeLink() {
  linkTimer = null;
  if (drawingLink.value === window.location.href) return;
  lastLinkWrite = performance.now();
  // Replacing this entry keeps slider gestures out of the browser's Back stack.
  try { window.history.replaceState(null, '', drawingLink.value); }
  catch { /* The copyable link still works when history changes are unavailable. */ }
}

function updateLink() {
  shareAttempt++;
  shareStatus.textContent = '';
  shareFallback.hidden = true;
  drawingLink.value = linkToDrawing();
  // WebKit limits history writes. Keep at most one pending update while dragging.
  const delay = Math.max(0, 250 - (performance.now() - lastLinkWrite));
  if (delay === 0) {
    if (linkTimer !== null) clearTimeout(linkTimer);
    writeLink();
  } else if (linkTimer === null) linkTimer = setTimeout(writeLink, delay);
}

function greatestCommonDivisor(a, b) {
  while (b !== 0) [a, b] = [b, a % b];
  return a;
}

function describeSectors(folds) {
  const angle = cycle / folds;
  const x = 44 * Math.sin(angle);
  const y = -44 * Math.cos(angle);
  document.querySelector('#sector-wedge').setAttribute('d', folds === 1
    ? 'M0 -44 A44 44 0 1 1 0 44 A44 44 0 1 1 0 -44 Z'
    : `M0 0 L0 -44 A44 44 0 0 1 ${x} ${y} Z`);
  const spokes = [];
  for (let sector = 0; sector < folds && folds > 1; sector++) {
    const a = sector * angle;
    spokes.push(`M0 0 L${44 * Math.sin(a)} ${-44 * Math.cos(a)}`);
  }
  document.querySelector('#sector-spokes').setAttribute('d', spokes.join(' '));
  document.querySelector('#sector-caption').textContent = folds === 1
    ? 'One sector spans a full turn.'
    : `One highlighted sector is 1/${folds} of a turn.`;
}

function describeRhythms() {
  const outer = Number(rhythm.value);
  const inner = Number(echo.value);
  const folds = greatestCommonDivisor(outer - 1, inner + 1);
  const pair = `${outer},${inner}`;
  study.value = Array.from(study.options).some(option => option.value === pair) ? pair : 'custom';
  const name = study.value === 'custom' ? 'Rhythms' : study.selectedOptions[0].textContent.split(' · ')[0];
  document.querySelector('#drawing-caption').textContent = `Study 001 · ${name} · ${outer} / ${inner}`;
  document.querySelector('#symmetry').textContent = folds === 1
    ? 'One full turn. This pair has no smaller repeating sector.'
    : `${folds}-fold symmetry. The curve repeats ${folds === 2 ? 'twice' : `${folds} times`} around its center.`;
  document.querySelector('#symmetry-reason').textContent =
    `For ${outer} and ${inner}, that gives ${outer - 1} and ${inner + 1}. ` +
    `Their greatest common divisor is ${folds}, so ${folds === 1 ? 'the whole curve is one sector' : `there are ${folds} equal sectors`}.`;
  canvas.setAttribute('aria-label',
    `A golden and blue orbital curve with rhythms ${outer} and ${inner}. ` +
    (folds === 1 ? 'No smaller repeating sector.' : `${folds}-fold rotational symmetry.`) +
    (pair === '8,21' ? ' The point stops and turns at a single cusp on the rightmost tip.' : ''));
  describeSectors(folds);
}

function joints(t, outer = Number(rhythm.value), inner = Number(echo.value)) {
  const points = [[500, 500]];
  for (const [length, angle] of [[245, t], [140, outer * t], [65, -inner * t]]) {
    const [x, y] = points[points.length - 1];
    points.push([x + length * Math.cos(angle), y + length * Math.sin(angle)]);
  }
  return points;
}

function point(t) {
  return joints(t)[3];
}

function drawCusp() {
  // A fixed view of Needle, independent of the current drawing's rhythms.
  for (const [id, start, end] of [['cusp-arriving', -0.04, 0], ['cusp-leaving', 0, 0.04]]) {
    const path = [];
    for (let sample = 0; sample <= 160; sample++) {
      const t = start + (end - start) * sample / 160;
      const [x, y] = joints(t, 8, 21)[3];
      path.push(`${sample === 0 ? 'M' : 'L'}${260 + (x - 950) * 7} ${110 + (y - 500) * 7}`);
    }
    document.querySelector(`#${id}`).setAttribute('d', path.join(' '));
  }
}

function drawArms() {
  armCtx.clearRect(0, 0, arms.width, arms.height);
  if (!showArms.checked) return;
  const points = joints(step / totalSteps * cycle);
  armCtx.lineWidth = 2;
  armCtx.strokeStyle = 'rgba(244, 241, 232, 0.75)';
  armCtx.beginPath();
  armCtx.moveTo(...points[0]);
  for (const p of points.slice(1)) armCtx.lineTo(...p);
  armCtx.stroke();
  for (const [index, p] of points.entries()) {
    armCtx.beginPath();
    armCtx.arc(...p, index === 3 ? 6 : 4, 0, cycle);
    armCtx.fillStyle = index === 3 ? '#e8b66e' : '#f4f1e8';
    armCtx.fill();
  }
}

function draw(count) {
  const end = Math.min(step + count, totalSteps);
  while (step < end) {
    const a = point(step / totalSteps * cycle);
    step++;
    const b = point(step / totalSteps * cycle);
    ctx.strokeStyle = `hsla(${35 + 175 * step / totalSteps}, 72%, 72%, 0.55)`;
    ctx.beginPath();
    ctx.moveTo(...a);
    ctx.lineTo(...b);
    ctx.stroke();
  }
  drawArms();
  if (step === totalSteps) {
    running = false;
    pause.textContent = 'Draw again';
    status.textContent = 'One full cycle. Your drawing is complete.';
  }
}

function tick(time) {
  frame = null;
  if (!running) return;
  // Advance by elapsed time so high-refresh screens draw at the same speed.
  const elapsed = lastTime === null ? 1000 / 60 : Math.min(time - lastTime, 100);
  lastTime = time;
  draw(Math.max(1, Math.round(elapsed * 1.2)));
  if (running) frame = requestAnimationFrame(tick);
}

function schedule() {
  if (running && frame === null) frame = requestAnimationFrame(tick);
}

function restart() {
  // A finished drawing can start afresh; an intentionally paused one stays paused.
  if (step === totalSteps) running = !reducedMotion.matches;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  lastTime = null;
  step = 0;
  ctx.fillStyle = '#0b0e1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.lineWidth = 0.9;
  document.querySelector('#rhythm-value').value = rhythm.value;
  document.querySelector('#echo-value').value = echo.value;
  describeRhythms();
  updateLink();
  status.textContent = running ? 'Tracing a full cycle…' : 'Paused. Press Play to trace the curve.';
  pause.textContent = running ? 'Pause' : 'Play';
  // A static complete drawing respects reduced-motion preferences.
  if (reducedMotion.matches) draw(totalSteps);
  else { draw(1); schedule(); }
}

pause.addEventListener('click', () => {
  if (step === totalSteps) {
    running = true;
    restart();
    return;
  }
  running = !running;
  lastTime = null;
  pause.textContent = running ? 'Pause' : 'Play';
  status.textContent = running ? 'Tracing a full cycle…' : 'Paused.';
  schedule();
});
document.querySelector('#restart').addEventListener('click', restart);
study.addEventListener('change', () => {
  [rhythm.value, echo.value] = study.value.split(',');
  restart();
});
document.querySelector('#try-needle').addEventListener('click', () => {
  rhythm.value = '8';
  echo.value = '21';
  restart();
});
showArms.addEventListener('change', drawArms);
reducedMotion.addEventListener('change', () => {
  if (!reducedMotion.matches) return;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  lastTime = null;
  draw(totalSteps);
});
for (const control of [rhythm, echo]) control.addEventListener('input', restart);
document.querySelector('#share').addEventListener('click', async () => {
  const url = linkToDrawing();
  const attempt = ++shareAttempt;
  shareStatus.textContent = '';
  shareFallback.hidden = true;
  try {
    await navigator.clipboard.writeText(url);
    if (attempt === shareAttempt) shareStatus.textContent = 'Link copied. It remembers these two rhythms.';
  } catch {
    if (attempt !== shareAttempt) return;
    shareStatus.textContent = 'Copy the link below. It remembers these two rhythms.';
    drawingLink.value = url;
    shareFallback.hidden = false;
    drawingLink.focus();
    drawingLink.select();
  }
});
window.addEventListener('popstate', () => {
  if (!readLink()) {
    rhythm.value = rhythm.defaultValue;
    echo.value = echo.defaultValue;
  }
  restart();
});
window.addEventListener('pagehide', () => {
  // Save a final slider change before navigation freezes a cached page's timer.
  if (linkTimer === null) return;
  clearTimeout(linkTimer);
  writeLink();
});
document.querySelector('#save').addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = `aldebaran-orbits-${rhythm.value}-${echo.value}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
});
readLink();
drawCusp();
restart();
