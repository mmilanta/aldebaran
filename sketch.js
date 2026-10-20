'use strict';

const canvas = document.querySelector('#sketch');
const ctx = canvas.getContext('2d');
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

function point(t) {
  return [
    500 + 245 * Math.cos(t) + 140 * Math.cos(Number(rhythm.value) * t) + 65 * Math.cos(-Number(echo.value) * t),
    500 + 245 * Math.sin(t) + 140 * Math.sin(Number(rhythm.value) * t) + 65 * Math.sin(-Number(echo.value) * t)
  ];
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
for (const control of [rhythm, echo]) control.addEventListener('input', restart);
document.querySelector('#save').addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = `aldebaran-orbits-${rhythm.value}-${echo.value}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
});
restart();
