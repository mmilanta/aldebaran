'use strict';

(() => {
  const { cycle, events, position, velocity, acceleration, tangentIndex,
    lensPoint, lensVector, cuspTolerance, regularPosition, regularVelocity,
    regularAcceleration } = BlendMath;
  const get = id => document.getElementById(id);
  const slider = get('blend');
  const stops = { start: 0, first: events[0].blend, between: 1 / 3,
    second: events[1].blend, finish: 1 };
  const drawingMap = ([x, y]) => [400 + x, 400 - y];
  const windowRadius = 0.24;
  let selectedEvent = 0;
  let regular = false;

  function points(fn, start, end, steps) {
    return Array.from({ length: steps + 1 }, (_, i) => fn(start + (end - start) * i / steps));
  }

  function path(samples, map) {
    return samples.map((p, i) => {
      const [x, y] = map(p);
      return `${i ? 'L' : 'M'}${x.toFixed(4)} ${y.toFixed(4)}`;
    }).join(' ');
  }

  function marker(id, point, map) {
    const [x, y] = map(point);
    get(id).setAttribute('cx', x);
    get(id).setAttribute('cy', y);
  }

  function arrows(fn, derivative, times, map, length) {
    return times.map(t => {
      const p = fn(t);
      const v = derivative(t);
      const [x, y] = map(p);
      const [ex, ey] = map([p[0] + v[0], p[1] + v[1]]);
      const speed = Math.hypot(ex - x, ey - y);
      if (speed < 1e-8) return '';
      const dx = (ex - x) / speed;
      const dy = (ey - y) / speed;
      const tipX = x + length / 2 * dx;
      const tipY = y + length / 2 * dy;
      const wing = length * 0.35;
      return `M${x - length / 2 * dx} ${y - length / 2 * dy} L${tipX} ${tipY}` +
        ` M${tipX - wing * dx + wing * 0.65 * dy} ${tipY - wing * dy - wing * 0.65 * dx}` +
        ` L${tipX} ${tipY} L${tipX - wing * dx - wing * 0.65 * dy} ${tipY - wing * dy + wing * 0.65 * dx}`;
    }).join(' ');
  }

  function renderDiagram(prefix, fn, derivative, a, map) {
    const evaluate = t => fn(t, a);
    const time = events[selectedEvent].time;
    const full = points(evaluate, 0, cycle, 3600);
    if (prefix === 'velocity') {
      const maxX = Math.max(...full.map(p => Math.abs(p[0])));
      const maxY = Math.max(...full.map(p => Math.abs(p[1])));
      const scale = Math.min(184 / maxX, 144 / maxY);
      map = ([x, y]) => [210 + scale * x, 170 - scale * y];
    }
    get(`${prefix}-outline`).setAttribute('d', path(full, map));
    get(`${prefix}-gold`).setAttribute('d', path(points(evaluate,
      time - windowRadius, time + windowRadius, 480), map));
    get(`${prefix}-blue`).setAttribute('d', path(points(evaluate,
      cycle - time - windowRadius, cycle - time + windowRadius, 480), map));
    marker(`${prefix}-mark-gold`, fn(time, a), map);
    marker(`${prefix}-mark-blue`, fn(cycle - time, a), map);
    get(`${prefix}-arrows`).setAttribute('d', arrows(evaluate, t => derivative(t, a),
      [0.06, 0.17, 0.35, 0.47, 0.53, 0.65, 0.83, 0.94].map(t => t * cycle), map, 15));
  }

  function renderLens(a) {
    const event = events[selectedEvent];
    const evaluate = t => lensPoint(t, a, selectedEvent, regular ? regularPosition : position);
    const samples = points(evaluate, event.time - windowRadius, event.time + windowRadius, 720);
    const xs = samples.map(p => p[0]);
    const ys = samples.map(p => p[1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const width = maxX - minX, height = maxY - minY;
    const scale = Math.min(364 / width, 192 / height);
    const map = ([x, y]) => [28 + (364 - scale * width) / 2 + scale * (x - minX),
      24 + (192 - scale * height) / 2 + scale * (maxY - y)];
    get('lens-path').setAttribute('d', path(samples, map));
    marker('lens-mark', [0, 0], map);
    get('lens-arrows').setAttribute('d', arrows(evaluate,
      t => lensVector((regular ? regularVelocity : velocity)(t, a), selectedEvent),
      [event.time - 0.17, event.time + 0.17], map, 15));
    const targetLength = 70 / scale;
    const magnitude = 10 ** Math.floor(Math.log10(targetLength));
    const units = [1, 2, 5].map(x => x * magnitude).filter(x => x <= targetLength).at(-1);
    const length = units * scale;
    get('lens-scale').setAttribute('d', `M24 241v-5h${length}v5`);
    get('lens-scale-label').textContent = `${Number(units.toPrecision(2))} drawing units`;
    const name = selectedEvent === 0 ? 'first' : 'second';
    get('lens-title').textContent = `Close-up of the ${name} straight-route cusp neighborhood`;
    get('lens-description').textContent = `The gold parameter window near the ${name} upper cusp of the straight route, now on the ${regular ? 'route that keeps moving' : 'straight route'}. It is rotated and magnified with equal scales on both axes. The white arrows follow the curve. The scale bar is ${units} drawing units.`;
    get('lens-caption').textContent = `The ${name} event’s gold segment, rotated and fitted to the window. Both axes have the same scale. The blue segment is its reflection.`;
    for (const button of document.querySelectorAll('[data-lens]')) {
      button.setAttribute('aria-pressed', String(Number(button.dataset.lens) === selectedEvent));
    }
  }

  function update() {
    const a = Number(slider.value);
    const index = regular ? 0 : tangentIndex(a);
    const percent = `${(100 * a).toFixed(2)}%`;
    const cusp = regular ? -1 : events.findIndex(event => Math.abs(a - event.blend) <= cuspTolerance);
    let phase;
    if (cusp !== -1) {
      phase = `${cusp === 0 ? 'First' : 'Second'} cusp pair (rounded blend). The tracing point stops at two reflected places. Its direction’s turn count is undefined here.`;
    } else if (regular) {
      phase = 'This route keeps the point moving. The direction’s left and right turns cancel at every blend.';
    } else if (index === -2) {
      phase = 'Between the two cusp events. Two clockwise loops give the direction two extra clockwise turns.';
    } else if (a < events[0].blend) {
      phase = 'Before the first cusp pair. The direction’s left and right turns cancel over the whole orbit.';
    } else {
      phase = 'After the second cusp pair. The direction’s left and right turns cancel again.';
    }
    if (a === 0) phase = 'Rhythms 2 / 3. One large lobe and one little clockwise loop; zero net turns of the direction.';
    if (a === 1) phase = 'Rhythms 4 / 7. A different drawing, with zero net turns of the direction again.';
    get('blend-value').value = percent;
    get('route-description').textContent = regular
      ? 'Combine the points’ angles and distances around the center. Each point follows a curved route, and its orbit velocity never reaches zero.'
      : 'Match the two drawings’ points at the same moment. Each point moves along a straight line as you change the blend.';
    get('intervals').classList.toggle('regular', regular);
    get('tangent-count').value = index === null ? 'Cusp' : index === -2 ? '−2' : '0';
    get('phase').textContent = phase;
    slider.setAttribute('aria-valuetext', `${percent}. ${phase} The whole drawing winds once around its center.`);
    get('drawing-description').textContent = `${percent} of the ${regular ? 'angle-and-distance route' : 'straight blend'} from rhythms 2 / 3 to 4 / 7. ${phase} Gold marks the selected parameter neighborhood; blue marks its reflection. The whole drawing winds once around its center.`;
    get('velocity-description').textContent = index === null
      ? 'The velocity trace reaches the zero-velocity dot at two parameter times. The tangent’s turn count is undefined at this cusp pair.'
      : `Place every velocity arrow’s tail at the white dot. Their tips trace this curve. It makes ${index === -2 ? 'two net clockwise turns' : 'zero net turns'} around the dot.`;
    renderDiagram('drawing', regular ? regularPosition : position,
      regular ? regularVelocity : velocity, a, drawingMap);
    renderDiagram('velocity', regular ? regularVelocity : velocity,
      regular ? regularAcceleration : acceleration, a);
    renderLens(a);
    for (const button of document.querySelectorAll('[data-stop]')) {
      button.setAttribute('aria-pressed', String(Math.abs(a - stops[button.dataset.stop]) < 1e-14));
      if (button.dataset.stop === 'first') button.textContent = regular ? '22.63%' : 'First cusps';
      if (button.dataset.stop === 'second') button.textContent = regular ? '50.89%' : 'Second cusps';
    }
  }

  slider.addEventListener('input', update);
  for (const radio of document.querySelectorAll('[name="route"]')) {
    radio.addEventListener('change', () => {
      regular = radio.value === 'regular';
      update();
    });
  }
  slider.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const increments = { ArrowRight: 0.01, ArrowUp: 0.01, ArrowLeft: -0.01,
      ArrowDown: -0.01, PageUp: 0.1, PageDown: -0.1 };
    let a;
    if (event.key === 'Home') a = 0;
    else if (event.key === 'End') a = 1;
    else if (Object.hasOwn(increments, event.key)) {
      a = Number(slider.value) + increments[event.key] * (event.shiftKey ? 0.1 : 1);
    } else return;
    event.preventDefault();
    slider.value = String(Math.max(0, Math.min(1, a)));
    update();
  });
  for (const button of document.querySelectorAll('[data-stop]')) {
    button.addEventListener('click', () => {
      slider.value = String(stops[button.dataset.stop]);
      if (button.dataset.stop === 'first') selectedEvent = 0;
      if (button.dataset.stop === 'second') selectedEvent = 1;
      update();
    });
  }
  for (const button of document.querySelectorAll('[data-lens]')) {
    button.addEventListener('click', () => {
      selectedEvent = Number(button.dataset.lens);
      update();
    });
  }
  update();
})();
