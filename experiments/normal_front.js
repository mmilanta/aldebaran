'use strict';

(() => {
  if (typeof NormalFrontMath === 'undefined') return;
  const M = NormalFrontMath, ns = 'http://www.w3.org/2000/svg';
  const get = id => document.getElementById(id);
  const rhythmControl = get('rhythm'), directionControl = get('direction'), visitControl = get('visit');
  const gold = '#e8b66e', lilac = '#d1b6ea', blue = '#9fc7eb';
  const cache = new Map();
  let shared = false, drawnInner;
  const whole = ([x, y]) => [300 + .55 * x, 300 - .55 * y];
  const graph = ([beta, h]) => [65 + 560 * beta / M.cycle, 290 - .5 * h];
  const d = (points, project) => 'M' + points.map(p => project(p).map(x => x.toFixed(4)).join(',')).join('L');
  const degrees = beta => ((180 + beta * 180 / Math.PI) % 360 + 360) % 360;
  const formatted = x => (Math.abs(x) < .005 ? 0 : x).toFixed(2).replace('-', '−');

  function element(name, attributes) {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  }

  function data(inner) {
    if (!cache.has(inner)) {
      const example = M.sharedTangent(inner, 0, 6, (inner === 6 ? 102 : 95) * Math.PI / 180,
        (inner === 6 ? 103 : 96) * Math.PI / 180);
      const curve = Array.from({ length: 6001 }, (_, i) => M.orbit(i * M.cycle / 6000, inner));
      cache.set(inner, { curve, strands: M.front(inner), example });
    }
    return cache.get(inner);
  }

  function mark(visit, color, radius) {
    const [x, y] = whole(visit.point), [gx, gy] = graph([visit.beta, visit.distance]);
    const [nx, ny] = visit.normal;
    const tip = [x + 28 * nx, y - 28 * ny];
    const arrow = `M${x},${y}L${tip}M${tip[0] - 7 * nx + 5 * ny},${tip[1] + 7 * ny + 5 * nx}L${tip}L${tip[0] - 7 * nx - 5 * ny},${tip[1] + 7 * ny - 5 * nx}`;
    return {
      orbit: [element('path', { d: arrow, fill: 'none', stroke: color, 'stroke-width': radius > 4 ? 2.5 : 1.5 }),
        element('circle', { cx: x, cy: y, r: radius, fill: '#0b0e1a', stroke: color, 'stroke-width': radius > 4 ? 2.5 : 1.5 })],
      front: element('circle', { cx: gx, cy: gy, r: radius, fill: radius > 6 ? 'none' : '#0b0e1a', stroke: color, 'stroke-width': 2 })
    };
  }

  function tangent(visit, color) {
    const [nx, ny] = visit.normal, q = visit.point;
    return element('path', { d: d([[q[0] - 1000 * ny, q[1] + 1000 * nx],
      [q[0] + 1000 * ny, q[1] - 1000 * nx]], whole), fill: 'none', stroke: color,
    'stroke-width': 1.5, 'stroke-dasharray': '7 7' });
  }

  function render() {
    const inner = Number(rhythmControl.value), branch = Number(visitControl.value), record = data(inner);
    const beta = shared ? record.example.beta : Number(directionControl.value) * Math.PI / 180;
    if (shared) directionControl.value = beta * 180 / Math.PI;
    const visits = Array.from({ length: 11 }, (_, i) => M.visit(beta, i, inner));
    const selected = shared ? [visits[0], visits[6]] : [visits[branch]];
    if (drawnInner !== inner) {
      get('whole-curve').setAttribute('d', d(record.curve, whole));
      get('front-strands').replaceChildren(...record.strands.map((points, i) =>
        element('path', { d: d(points, graph), fill: 'none', stroke: blue,
          'stroke-width': 1.3, 'data-branch': i })));
      drawnInner = inner;
    }
    for (const path of get('front-strands').children) {
      const i = Number(path.getAttribute('data-branch'));
      const chosen = selected.findIndex(v => v.branch === i);
      path.setAttribute('stroke', chosen === 0 ? gold : chosen === 1 ? lilac : blue);
      path.setAttribute('stroke-width', chosen >= 0 ? 3 : 1.3);
      path.setAttribute('opacity', chosen >= 0 ? 1 : .5);
    }
    const orbitMarks = [], frontMarks = [];
    for (const v of visits.filter(v => !selected.some(s => s.branch === v.branch))) {
      const nodes = mark(v, blue, 3.5);
      orbitMarks.push(...nodes.orbit); frontMarks.push(nodes.front);
    }
    selected.forEach((v, i) => {
      const nodes = mark(v, i ? lilac : gold, i ? 9 : 6);
      orbitMarks.push(...nodes.orbit); frontMarks.push(nodes.front);
    });
    get('orbit-marks').replaceChildren(...orbitMarks);
    get('front-marks').replaceChildren(...frontMarks);
    get('tangents').replaceChildren(tangent(selected[0], gold));
    const v = selected[0], foot = v.normal.map(n => n * v.distance);
    get('distance-lines').replaceChildren(element('path', {
      d: d([[0, 0], foot], whole), fill: 'none', stroke: gold, 'stroke-width': 3, opacity: .65
    }), element('circle', { cx: whole(foot)[0], cy: whole(foot)[1], r: 3, fill: gold }));
    const [cursorX] = graph([beta, 0]);
    get('cursor').setAttribute('d', `M${cursorX},65V515`);
    const angle = formatted(degrees(beta));
    get('direction-value').textContent = `${angle}° · from the positive horizontal axis`;
    directionControl.setAttribute('aria-valuetext', `Normal direction ${angle} degrees`);
    get('selected-value').textContent = shared ? '1 and 7 of 11' : `${branch + 1} of 11`;
    get('distance-value').textContent = formatted(v.distance);
    get('slope-value').textContent = selected.map(v => formatted(v.slope)).join(' / ');
    get('status').textContent = shared
      ? `Visits 1 and 7 share one tangent line. Their points are ${formatted(Math.hypot(...v.point.map((x, i) => x - selected[1].point[i])))} units apart; their graph dots meet with different slopes. Move the direction or choose a visit to continue.`
      : `Visit ${branch + 1} is gold. All eleven arrows point in the same normal direction; the heavy segment from the origin measures its signed distance to the dashed tangent line.`;
    get('whole-description').textContent = `Rhythms 11 / ${inner}. Eleven places have left normal ${angle} degrees. ${shared ? 'Gold visit 1 and lilac visit 7 share a dashed tangent line, while remaining far apart.' : `Visit ${branch + 1} has signed tangent-line distance ${formatted(v.distance)} drawing units.`}`;
    get('front-description').textContent = `Eleven strands of the conormal front for rhythms 11 / ${inner}. At normal ${angle} degrees, ${shared ? 'visits 1 and 7 meet at one height with different slopes.' : `visit ${branch + 1} is highlighted at signed distance ${formatted(v.distance)}.`} The right edge of each strand joins the next strand on the left.`;
  }

  function update() {
    try {
      render();
      get('explorer').hidden = false;
      get('fallback').hidden = true;
    } catch (error) {
      get('explorer').hidden = true;
      get('fallback').hidden = false;
      console.error(error);
    }
  }

  directionControl.addEventListener('input', () => { shared = false; update(); });
  visitControl.addEventListener('change', () => { shared = false; update(); });
  rhythmControl.addEventListener('change', update);
  get('shared').addEventListener('click', () => { shared = true; visitControl.value = '0'; update(); });
  window.addEventListener('pageshow', update);
  update();
})();
