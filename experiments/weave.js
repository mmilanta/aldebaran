'use strict';

(() => {
  if (typeof WeaveData === 'undefined' || typeof WeaveMath === 'undefined') return;
  const M = WeaveMath, D = WeaveData, ns = 'http://www.w3.org/2000/svg';
  const get = id => document.getElementById(id);
  const eventControl = get('event'), progressControl = get('progress'), reflectedControl = get('reflected');
  const colors = ['#9fc7eb', '#e8b66e', '#d1b6ea'];
  const wholeScale = .59, endpointScale = .51;

  function element(name, attributes) {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  }

  function path(points, project, close = false) {
    return 'M' + points.map(p => project(p).map(v => v.toFixed(5)).join(',')).join(' L') + (close ? ' Z' : '');
  }

  const wholePoint = ([x, y]) => [300 + wholeScale * x, 300 - wholeScale * y];
  const endpointPoint = ([x, y]) => [260 + endpointScale * x, 260 - endpointScale * y];

  function render() {
    const index = Math.max(0, Math.min(D.events.length - 1, Number(eventControl.value)));
    const progress = Math.max(-100, Math.min(100, Number(progressControl.value)));
    const reflected = reflectedControl.checked;
    const s = M.state(D.events[index], progress, reflected), triangle = M.triangle(s);
    const scale = 250 / s.halfSize;
    const lensPoint = ([x, y]) => [300 + scale * (x - s.center[0]), 300 - scale * (y - s.center[1])];
    const phase = progress < 0 ? 'Before' : progress > 0 ? 'After' : 'Meeting (approx.)';
    const ordinal = index === 0 ? 'first' : 'second';
    const side = reflected ? 'below' : 'above';
    const weight = (100 * s.weight).toFixed(4) + '%';
    get('progress-value').textContent = `${phase} · ${weight} of the blend`;
    progressControl.setAttribute('aria-valuetext', `${phase}, ${weight} of the blend`);
    get('status').textContent = progress === 0
      ? `Near the ${ordinal} triple meeting ${side} the axis. Its strangeness jump is −1; its reflected partner meets at the same blend weight.`
      : `${phase} the ${ordinal} passage ${side} the axis. The small triangle ${progress < 0 ? 'closes towards' : 'opens on the other side of'} the meeting.`;
    for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
      get(id).setAttribute('aria-pressed', String(progress === value));
    }
    get('current-curve').setAttribute('d', path(M.points(0, M.cycle, 12000, s.weight), wholePoint));
    const room = wholePoint(s.center), half = (300 / scale) * wholeScale;
    get('room').setAttribute('x', room[0] - half);
    get('room').setAttribute('y', room[1] - half);
    get('room').setAttribute('width', 2 * half);
    get('room').setAttribute('height', 2 * half);
    get('room-ring').setAttribute('cx', room[0]);
    get('room-ring').setAttribute('cy', room[1]);

    const highlights = [], branches = [], arrows = [], crossings = [];
    for (let j = 0; j < 3; j++) {
      const t = s.times[j];
      const points = M.points(t - .014, t + .014, 280, s.weight);
      highlights.push(element('path', { d: path(points, wholePoint), fill: 'none', stroke: colors[j], 'stroke-width': 3 }));
      branches.push(element('path', { d: path(points, lensPoint), class: 'branch', stroke: colors[j] }));
      // Pick a visible location along the branch, away from the meeting.
      let arrowTime = t;
      for (let step = 1; step <= 100; step++) {
        const candidate = t + step * .00002;
        const p = lensPoint(M.orbit(candidate, s.weight));
        const radius = Math.hypot(p[0] - 300, p[1] - 300);
        if (radius > 175 && radius < 235 && p.every(v => v > 30 && v < 570)) {
          arrowTime = candidate;
          break;
        }
      }
      const point = lensPoint(M.orbit(arrowTime, s.weight));
      const v = M.orbit(arrowTime, s.weight, 1), length = Math.hypot(...v);
      const ux = v[0] / length, uy = -v[1] / length;
      const tip = [point[0] + 7 * ux, point[1] + 7 * uy];
      const left = [point[0] - 5 * ux + 5 * uy, point[1] - 5 * uy - 5 * ux];
      const right = [point[0] - 5 * ux - 5 * uy, point[1] - 5 * uy + 5 * ux];
      arrows.push(element('path', { d: `M${left} L${tip} L${right}`, fill: 'none', stroke: colors[j], 'stroke-width': 2.4 }));
    }
    const boundary = triangle.edges.flatMap(e => M.points(e.start, e.end, 80, s.weight));
    get('pocket').setAttribute('d', progress === 0 ? '' : path(boundary, lensPoint, true));
    for (const crossing of (progress === 0 ? [triangle.crossings[0]] : triangle.crossings)) {
      const [x, y] = lensPoint(crossing.point);
      crossings.push(element('circle', { cx: x, cy: y, r: progress === 0 ? 4 : 3, class: 'crossing' }));
    }
    get('highlights').replaceChildren(...highlights);
    get('branches').replaceChildren(...branches);
    get('arrows').replaceChildren(...arrows);
    get('crossings').replaceChildren(...crossings);
    get('whole-description').textContent = `The complete drawing at ${weight} of the blend. A white square marks the ${ordinal} passage ${side} the axis.`;
    get('lens-description').textContent = `${phase} the ${ordinal} passage ${side} the axis. Blue, gold, and lilac follow earlier, middle, and later visits; arrows give travel direction. ${progress === 0 ? 'The three crossings nearly coincide at rounded event coordinates.' : 'Three white dots bound a pale curved triangle.'}`;
    get('lens-caption').textContent = `Equal scales on both axes; the lens spans ${(600 / scale).toFixed(2)} drawing units in each direction. ${progress === 0 ? 'The dot approximates the exact meeting.' : 'White dots mark the three pairwise crossings.'}`;
  }

  function update() {
    try {
      render();
    } catch (error) {
      // Keep the readable still if a restored control or runtime fails.
      get('explorer').hidden = true;
      get('fallback').hidden = false;
      console.error(error);
    }
  }

  for (const [id, weight] of [['first-curve', 0], ['second-curve', 1]]) {
    get(id).setAttribute('d', path(M.points(0, M.cycle, 12000, weight), endpointPoint));
  }
  render();
  eventControl.addEventListener('change', update);
  reflectedControl.addEventListener('change', update);
  progressControl.addEventListener('input', update);
  for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
    get(id).addEventListener('click', () => { progressControl.value = value; update(); });
  }
  // Native form restoration may occur after initial script evaluation.
  window.addEventListener('pageshow', update);
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
