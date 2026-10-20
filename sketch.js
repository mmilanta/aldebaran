'use strict';

const canvas = document.querySelector('#sketch');
const ctx = canvas.getContext('2d');
const arms = document.querySelector('#arms');
const armCtx = arms.getContext('2d');
const showArms = document.querySelector('#show-arms');
const rhythm = document.querySelector('#rhythm');
const echo = document.querySelector('#echo');
const pause = document.querySelector('#pause');
const status = document.querySelector('#status');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const totalSteps = 24000;
const cycle = Math.PI * 2;
let step = 0;
let running = !reducedMotion.matches;
let frame = null;
let lastTime = null;

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
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  lastTime = null;
  step = 0;
  ctx.fillStyle = '#0b0e1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.lineWidth = 0.9;
  document.querySelector('#rhythm-value').value = rhythm.value;
  document.querySelector('#echo-value').value = echo.value;
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
showArms.addEventListener('change', drawArms);
for (const control of [rhythm, echo]) control.addEventListener('input', restart);
document.querySelector('#save').addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = `aldebaran-orbits-${rhythm.value}-${echo.value}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
});
restart();
