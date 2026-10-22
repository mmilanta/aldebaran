'use strict';

(() => {
  const { cycle, firstVisit, secondVisit, position, velocity, turns } = TwoLobesMath;
  const progress = document.querySelector('#progress');
  const stops = { start: 0, first: firstVisit, middle: 0.5, second: secondVisit, home: 1 };
  const mainMap = ([x, y]) => [230 + x, 400 - y];
  const insetMap = ([x, y]) => [130 + 2 * (x + 145), 170 - 2 * y];
  const get = id => document.querySelector(`#${id}`);

  function path(start, end, map) {
    const steps = Math.max(1, Math.ceil((end - start) * 2400));
    const commands = [];
    for (let i = 0; i <= steps; i++) {
      const [x, y] = map(position(cycle * (start + (end - start) * i / steps)));
      commands.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(4)} ${y.toFixed(4)}`);
    }
    return commands.join(' ');
  }

  function trail(id, start, end, fraction, map) {
    get(id).setAttribute('d', fraction > start ? path(start, Math.min(end, fraction), map) : '');
  }

  function tracker(pointId, directionId, fraction, map, length) {
    const t = cycle * fraction;
    const [x, y] = map(position(t));
    const [vx, vy] = velocity(t);
    const speed = Math.hypot(vx, vy);
    const dx = vx / speed;
    const dy = -vy / speed;
    const tipX = x + length * dx;
    const tipY = y + length * dy;
    get(pointId).setAttribute('cx', x);
    get(pointId).setAttribute('cy', y);
    get(directionId).setAttribute('d', `M${x - 12 * dx} ${y - 12 * dy} L${tipX} ${tipY}` +
      ` M${tipX - 9 * dx + 5 * dy} ${tipY - 9 * dy - 5 * dx}` +
      ` L${tipX} ${tipY} L${tipX - 9 * dx - 5 * dy} ${tipY - 9 * dy + 5 * dx}`);
    return [x, y];
  }

  function count(value) {
    // Avoid a distracting minus sign when a tiny negative value rounds to zero.
    if (Math.abs(value) < 0.005) return '0.00';
    return `${value > 0 ? '+' : '−'}${Math.abs(value).toFixed(2)}`;
  }

  function update() {
    const fraction = Number(progress.value);
    const { center, tangent } = turns(fraction);
    const percent = `${(fraction * 100).toFixed(1).replace(/\.0$/, '')}%`;
    get('progress-value').value = percent;
    get('center-turns').value = count(center);
    get('tangent-turns').value = count(tangent);
    get('center-dial').setAttribute('transform', `rotate(${-360 * center} 40 40)`);
    get('tangent-dial').setAttribute('transform', `rotate(${-90 - 360 * tangent} 40 40)`);
    const [x, y] = tracker('point', 'direction', fraction, mainMap, 40);
    get('spoke').setAttribute('x2', x);
    get('spoke').setAttribute('y2', y);
    tracker('inset-point', 'inset-direction', fraction, insetMap, 35);
    // The inset is a window, not another copy of the whole orbit. Keep an
    // offscreen tracker out of its accessibility description and clipped frame.
    const loopVisible = fraction >= firstVisit - 0.02 && fraction <= secondVisit + 0.02;
    get('inset-tracker').setAttribute('visibility', loopVisible ? 'visible' : 'hidden');
    trail('early-trail', 0, firstVisit, fraction, mainMap);
    trail('loop-trail', firstVisit, secondVisit, fraction, mainMap);
    trail('late-trail', secondVisit, 1, fraction, mainMap);
    trail('inset-early', 0, firstVisit, fraction, insetMap);
    trail('inset-trail', firstVisit, secondVisit, fraction, insetMap);
    trail('inset-late', secondVisit, 1, fraction, insetMap);

    let phase = fraction < firstVisit
      ? 'Tracing the large lobe. The point travels towards its first visit to the crossing.'
      : fraction < secondVisit
        ? 'Tracing the little loop. The point goes clockwise around its blue interior.'
        : 'Finishing the large lobe. The point is on its way home.';
    if (fraction === 0) phase = 'Start. Both counters start at zero; the arrow points up.';
    if (Math.abs(fraction - firstVisit) < 1e-12) phase = 'First crossing. The point enters the clockwise loop, heading down and left.';
    if (fraction === 0.5) phase = 'Inside the loop. The arrow points up again. The line from the center has made half a net turn.';
    if (Math.abs(fraction - secondVisit) < 1e-12) phase = 'Second crossing. The point leaves the loop, heading down and right.';
    if (fraction === 1) phase = 'Home. One net turn around the center; zero net turns of the direction of travel.';
    get('phase').textContent = phase;
    progress.setAttribute('aria-valuetext', `${percent} of the orbit. ${phase} Around the center: ${count(center)} net turns. Direction of travel: ${count(tangent)} net turns.`);
    get('orbit-description').textContent = `A large gold lobe has winding count plus one; a small blue loop has count minus one. ${phase} The dotted line has made ${count(center)} net turns; the white arrow has made ${count(tangent)} net turns.`;
    for (const button of document.querySelectorAll('[data-stop]')) {
      button.setAttribute('aria-pressed', String(Math.abs(fraction - stops[button.dataset.stop]) < 1e-12));
    }
  }

  get('large-fill').setAttribute('d', path(secondVisit, 1 + firstVisit, mainMap) + ' Z');
  get('small-fill').setAttribute('d', path(firstVisit, secondVisit, mainMap) + ' Z');
  get('outline').setAttribute('d', path(0, 1, mainMap));
  get('inset-fill').setAttribute('d', path(firstVisit, secondVisit, insetMap) + ' Z');
  get('inset-outline').setAttribute('d', path(0, 1, insetMap));
  get('crossing').setAttribute('cx', mainMap(position(cycle * firstVisit))[0]);
  get('inset-crossing').setAttribute('cx', insetMap(position(cycle * firstVisit))[0]);
  progress.addEventListener('input', update);
  progress.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    // Native keyboard increments for step="any" differ between engines.
    // Keep exact crossing presets and give all browsers the same small steps.
    const increments = { ArrowRight: 0.01, ArrowUp: 0.01, ArrowLeft: -0.01,
      ArrowDown: -0.01, PageUp: 0.1, PageDown: -0.1 };
    let value;
    if (event.key === 'Home') value = 0;
    else if (event.key === 'End') value = 1;
    else if (Object.hasOwn(increments, event.key)) {
      value = Number(progress.value) + increments[event.key] * (event.shiftKey ? 0.1 : 1);
    } else return;
    event.preventDefault();
    progress.value = String(Math.max(0, Math.min(1, value)));
    update();
  });
  for (const button of document.querySelectorAll('[data-stop]')) {
    button.addEventListener('click', () => {
      progress.value = String(stops[button.dataset.stop]);
      update();
    });
  }
  update();
})();
