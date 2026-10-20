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
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const totalSteps = 24000;
const cycle = Math.PI * 2;
let step = 0;
let running = !reducedMotion.matches;
let frame = null;
let lastTime = null;

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
  document.querySelector('#symmetry').textContent = folds === 1
    ? 'One full turn. This pair has no smaller repeating sector.'
    : `${folds}-fold symmetry. The curve repeats ${folds === 2 ? 'twice' : `${folds} times`} around its center.`;
  document.querySelector('#symmetry-reason').textContent =
    `For ${outer} and ${inner}, that gives ${outer - 1} and ${inner + 1}. ` +
    `Their greatest common divisor is ${folds}, so ${folds === 1 ? 'the whole curve is one sector' : `there are ${folds} equal sectors`}.`;
  canvas.setAttribute('aria-label',
    `A golden and blue orbital curve with rhythms ${outer} and ${inner}. ` +
    (folds === 1 ? 'No smaller repeating sector.' : `${folds}-fold rotational symmetry.`));
  describeSectors(folds);
}

function joints(t) {
  const points = [[500, 500]];
  for (const [length, angle] of [[245, t], [140, Number(rhythm.value) * t], [65, -Number(echo.value) * t]]) {
    const [x, y] = points[points.length - 1];
    points.push([x + length * Math.cos(angle), y + length * Math.sin(angle)]);
  }
  return points;
}

function point(t) {
  return joints(t)[3];
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
showArms.addEventListener('change', drawArms);
reducedMotion.addEventListener('change', () => {
  if (!reducedMotion.matches) return;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  lastTime = null;
  draw(totalSteps);
});
for (const control of [rhythm, echo]) control.addEventListener('input', restart);
document.querySelector('#save').addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = `aldebaran-orbits-${rhythm.value}-${echo.value}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
});
restart();
