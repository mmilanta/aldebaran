'use strict';

(() => {
  const { cycle, bridges, state, position, velocity, centralWindow } = ArmDetourMath;
  const get = id => document.getElementById(id);
  const slider = get('progress');
  const legNames = ['Lengthen arm', 'Change drawing', 'Bring arm home'];
  const number = x => Number(x.toFixed(1)).toLocaleString('en-US');
  const rhythm = pair => pair.join(' / ');

  function samples(fn, start, end, steps) {
    return Array.from({ length: steps + 1 }, (_, j) => fn(start + (end - start) * j / steps));
  }

  function path(points, map) {
    return points.map((p, j) => {
      const [x, y] = map(p);
      return `${j ? 'L' : 'M'}${x.toFixed(4)} ${y.toFixed(4)}`;
    }).join(' ');
  }

  function marker(id, p, map) {
    const [x, y] = map(p);
    get(id).setAttribute('cx', x);
    get(id).setAttribute('cy', y);
  }

  function arrows(s, times, map, length = 16) {
    return times.map(t => {
      const p = position(t, s), v = velocity(t, s);
      const [x, y] = map(p);
      const [ex, ey] = map([p[0] + v[0], p[1] + v[1]]);
      const speed = Math.hypot(ex - x, ey - y);
      const dx = (ex - x) / speed, dy = (ey - y) / speed;
      const tipX = x + length * dx / 2, tipY = y + length * dy / 2;
      const wing = length * .35;
      return `M${x - length * dx / 2} ${y - length * dy / 2}L${tipX} ${tipY}` +
        `M${tipX - wing * dx + wing * .65 * dy} ${tipY - wing * dy - wing * .65 * dx}` +
        `L${tipX} ${tipY}L${tipX - wing * dx - wing * .65 * dy} ${tipY - wing * dy + wing * .65 * dx}`;
    }).join(' ');
  }

  function scaleBar(prefix, scale, x, y, units) {
    if (units === undefined) {
      const target = 70 / scale;
      const magnitude = 10 ** Math.floor(Math.log10(target));
      units = [1, 2, 5].map(n => n * magnitude).filter(n => n <= target).at(-1);
    }
    get(`${prefix}-scale`).setAttribute('d', `M${x} ${y}v-5h${units * scale}v5`);
    get(`${prefix}-scale-label`).textContent = `${number(units)} drawing units`;
    return units;
  }

  function render(s, bridge) {
    const evaluate = t => position(t, s);
    // One fixed scale per detour, including both original drawings. A
    // longer arm really makes the picture grow instead of shrinking to fit.
    const fullScale = 300 / (bridge.length + 205);
    const fullMap = ([x, y]) => [340 + fullScale * x, 340 - fullScale * y];
    const window = centralWindow(s);
    const loop = samples(evaluate, window.start, window.end, 600);
    const context = samples(evaluate, Math.PI - 1.18 * window.radius,
      Math.PI + 1.18 * window.radius, 720);
    get('drawing-outline').setAttribute('d', path(samples(evaluate, 0, cycle, 4800), fullMap));
    get('drawing-loop').setAttribute('d', path(loop, fullMap));
    get('drawing-arrows').setAttribute('d', arrows(s,
      [.08, .24, .39, .61, .76, .92].map(f => f * cycle), fullMap));
    marker('drawing-halfway', evaluate(Math.PI), fullMap);
    scaleBar('drawing', fullScale, 28, 632, bridge.length === 300 ? 100 : 200);

    const xs = context.map(p => p[0]), ys = context.map(p => p[1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const lensScale = Math.min(360 / (maxX - minX), 230 / (maxY - minY));
    const lensMap = ([x, y]) => [210 + lensScale * (x - (minX + maxX) / 2),
      145 - lensScale * (y - (minY + maxY) / 2)];
    get('lens-context').setAttribute('d', path(context, lensMap));
    get('lens-loop').setAttribute('d', path(loop, lensMap));
    get('lens-arrows').setAttribute('d', arrows(s,
      [Math.PI - .48 * window.radius, Math.PI + .48 * window.radius], lensMap, 17));
    marker('lens-halfway', evaluate(Math.PI), lensMap);
    marker('lens-crossing', evaluate(window.start), lensMap);
    const units = scaleBar('lens', lensScale, 24, 286);
    get('lens-description').textContent = `The gold arc, magnified with equal axis scales. It may cross itself. ` +
      `The gold dot is halfway around the orbit; the arc's two ends meet at the hollow circle. ` +
      `White arrows follow travel around the orbit. The scale bar is ${number(units)} drawing units.`;

    const mapX = [32, 151, 269][s.leg] + [119, 118, 119][s.leg] * s.fraction;
    const mapY = 139 - 92 * (s.length - 245) / (bridge.length - 245);
    marker('map-point', [mapX, mapY], p => p);
    get('map-length').textContent = `First arm: ${bridge.length}`;
  }

  function update() {
    // Native form restoration may happen after the initial script ran.
    const bridgeIndex = Number(document.querySelector('[name="bridge"]:checked').value);
    const bridge = bridges[bridgeIndex];
    const s = state(bridgeIndex, Number(slider.value));
    const percent = `${number(100 * s.fraction)}%`;
    const place = `${s.leg + 1} · ${legNames[s.leg]} · ${percent}`;
    const from = rhythm(bridge.first), to = rhythm(bridge.second);
    let phase;
    if (s.progress === 0) phase = `Start at rhythms ${from}, first arm 245.`;
    else if (s.progress === 3) phase = `Home at rhythms ${to}, first arm back to 245.`;
    else if (s.leg === 0) phase = `Keep rhythms ${from}. Lengthen the first arm from 245 to ${bridge.length}; it is now ${number(s.length)}.`;
    else if (s.leg === 1) phase = `Hold the first arm at ${bridge.length}. Blend ${percent} of the way from ${from} to ${to}.`;
    else phase = `Keep rhythms ${to}. Bring the first arm from ${bridge.length} back to 245; it is now ${number(s.length)}.`;
    get('progress-value').value = place;
    get('arm-length').value = number(s.length);
    if (get('phase').textContent !== phase) get('phase').textContent = phase;
    slider.setAttribute('aria-valuetext', `Leg ${s.leg + 1} of 3: ${legNames[s.leg]}, ${percent}. ${phase}`);
    get('drawing-description').textContent = `Detour from rhythms ${from} to ${to}. ${phase} ` +
      `The gold central arc is magnified beside the drawing. ` +
      `The direction makes zero net turns; the whole drawing winds once around the center.`;
    get('map-description').textContent = `First arm: 245 to ${bridge.length}, then held at ${bridge.length} during the blend, then back to 245. ` +
      `The gold dot is on leg ${s.leg + 1} of 3: ${legNames[s.leg]}, ${percent}. Current length ${number(s.length)}.`;
    for (let j = 0; j < 3; j++) {
      if (s.leg === j) get(`leg-${j}`).setAttribute('aria-current', 'step');
      else get(`leg-${j}`).removeAttribute('aria-current');
    }
    for (const button of document.querySelectorAll('[data-stop]')) {
      const stop = Number(button.dataset.stop);
      button.setAttribute('aria-pressed', String(Math.abs(s.progress - stop) < 1e-12));
      if (stop === 0) button.textContent = `Start: ${from}`;
      if (stop === 3) button.textContent = `Home: ${to}`;
    }
    render(s, bridge);
  }

  slider.addEventListener('input', update);
  slider.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const steps = { ArrowRight: .01, ArrowUp: .01, ArrowLeft: -.01,
      ArrowDown: -.01, PageUp: .1, PageDown: -.1 };
    let p;
    if (event.key === 'Home') p = 0;
    else if (event.key === 'End') p = 3;
    else if (Object.hasOwn(steps, event.key)) {
      p = Number(slider.value) + steps[event.key] * (event.shiftKey ? .1 : 1);
    } else return;
    event.preventDefault();
    slider.value = String(Math.max(0, Math.min(3, p)));
    update();
  });
  for (const radio of document.querySelectorAll('[name="bridge"]')) radio.addEventListener('change', update);
  for (const button of document.querySelectorAll('[data-stop]')) {
    button.addEventListener('click', () => {
      slider.value = button.dataset.stop;
      update();
    });
  }
  window.addEventListener('pageshow', () => { setTimeout(update, 0); });
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
