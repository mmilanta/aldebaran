'use strict';

(() => {
  if (typeof TouchMath === 'undefined' || typeof TouchData === 'undefined') return;
  const M = TouchMath, D = TouchData, ns = 'http://www.w3.org/2000/svg';
  const get = id => document.getElementById(id);
  const eventControl = get('event'), progressControl = get('progress'), reflection = get('reflected');
  const colors = ['#9fc7eb', '#e8b66e'];
  const wholePoint = ([x, y]) => [300 + .59 * x, 300 - .59 * y];

  function element(name, attributes) {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  }

  function path(points, project, close = false) {
    return 'M' + points.map(p => project(p).map(v => v.toFixed(5)).join(',')).join(' L') + (close ? ' Z' : '');
  }

  function render() {
    const index = Math.max(0, Math.min(D.events.length - 1, Number(eventControl.value)));
    const progress = Math.max(-100, Math.min(100, Number(progressControl.value)));
    const s = M.state(D.events[index], progress, reflection.checked), e = s.event;
    const roots = M.meetings(s), area = M.area(s, roots);
    const half = e.half_size, scale = 270 / half;
    const lensPoint = ([x, y]) => [300 + scale * x, 300 - scale * y];
    const graphPoint = ([x, gap]) => [300 + 245 * x / half, 160 - 105 * gap / e.gap_limit];
    const phase = progress < 0 ? 'Before' : progress > 0 ? 'After' : 'Touch (approx.)';
    const weight = (100 * s.weight).toFixed(4) + '%';
    const directions = e.direct ? 'the same direction' : 'opposite directions';
    get('progress-value').textContent = `${phase} · ${weight} of the blend`;
    progressControl.setAttribute('aria-valuetext', `${phase}, ${weight} of the blend`);
    get('status').textContent = progress === 0
      ? `Near the exact touch. The two regular branches share a tangent and travel in ${directions}.`
      : `${phase} the touch. ${roots.length === 2 ? 'Two crossings enclose a small lens.' : 'The selected branches have separated.'} They travel in ${directions}.`;
    get('area').textContent = roots.length === 2 ? area.toFixed(5) : progress === 0 ? '0 (limit)' : 'No lens';
    const delta = e.range * progress / 100;
    get('ratio').textContent = roots.length === 2 ? (area / Math.abs(delta) ** 1.5).toFixed(2) : '—';
    get('limit').textContent = e.coefficient.toFixed(2);
    for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
      get(id).setAttribute('aria-pressed', String(progress === value));
    }

    get('outline').setAttribute('d', path(M.samples(0, M.cycle, 12000, t => M.orbit(t, s.weight)), wholePoint));
    const [cx, cy] = wholePoint(s.center);
    get('room').setAttribute('cx', cx); get('room').setAttribute('cy', cy);
    get('room').setAttribute('r', Math.max(9, .59 * half));
    const branches = [], highlights = [], arrows = [], markers = [], graphMarkers = [];
    for (let j = 0; j < 2; j++) {
      const points = M.samples(-half, half, 360, x => M.branch(s, j, x));
      branches.push(element('path', { d: path(points.map(p => [p.x, p.y]), lensPoint),
        fill: 'none', stroke: colors[j], 'stroke-width': 2.6 }));
      highlights.push(element('path', { d: path(points.map(p => p.point), wholePoint),
        fill: 'none', stroke: colors[j], 'stroke-width': 3 }));
      const b = M.branch(s, j, (j ? .86 : -.86) * half);
      const point = lensPoint([b.x, b.y]), norm = Math.hypot(1, b.slope);
      const ux = b.direction / norm, uy = -b.direction * b.slope / norm;
      arrows.push(element('path', { d: `M${point[0] - 6 * ux + 5 * uy},${point[1] - 6 * uy - 5 * ux} L${point[0] + 7 * ux},${point[1] + 7 * uy} L${point[0] - 6 * ux - 5 * uy},${point[1] - 6 * uy + 5 * ux}`,
        fill: 'none', stroke: colors[j], 'stroke-width': 2.6 }));
    }
    for (const x of roots) {
      const b = M.branch(s, 0, x), [px, py] = lensPoint([b.x, b.y]);
      markers.push(element('circle', { cx: px, cy: py, r: progress === 0 ? 5 : 3.8, class: 'meeting' }));
      const [gx, gy] = graphPoint([x, 0]);
      graphMarkers.push(element('circle', { cx: gx, cy: gy, r: 4.5, class: 'meeting' }));
    }
    const boundary = roots.length === 2 ? [
      ...M.samples(roots[0], roots[1], 100, x => { const p = M.branch(s, 0, x); return [p.x, p.y]; }),
      ...M.samples(roots[1], roots[0], 100, x => { const p = M.branch(s, 1, x); return [p.x, p.y]; })
    ] : [];
    get('pocket').setAttribute('d', boundary.length ? path(boundary, lensPoint, true) : '');
    const gapPoints = M.samples(-half, half, 280, x => [x, M.gap(s, x).value]);
    get('gap-line').setAttribute('d', path(gapPoints, graphPoint));
    get('gap-fill').setAttribute('d', roots.length === 2
      ? path(M.samples(roots[0], roots[1], 100, x => [x, M.gap(s, x).value]), graphPoint, true) : '');
    const reference = M.state(e, 0, reflection.checked);
    get('gap-reference').setAttribute('d', path(M.samples(-half, half, 280, x => [x, M.gap(reference, x).value]), graphPoint));
    get('highlights').replaceChildren(...highlights);
    get('branches').replaceChildren(...branches);
    get('arrows').replaceChildren(...arrows);
    get('markers').replaceChildren(...markers);
    get('gap-markers').replaceChildren(...graphMarkers);
    get('x-low').textContent = `−${half}`; get('x-high').textContent = String(half);
    get('y-low').textContent = `−${e.gap_limit}`; get('y-high').textContent = String(e.gap_limit);
    get('lens-caption').textContent = `Equal scales, rotated to put the common tangent horizontally. The view spans ${(600 / scale).toFixed(1)} drawing units each way. Arrows follow travel.`;
    get('whole-description').textContent = `The full drawing at ${weight} of the blend. A ring locates touch ${index + 1} ${reflection.checked ? 'below' : 'above'} the axis.`;
    get('lens-description').textContent = `Earlier blue and later gold branches travel in ${directions}. ${progress === 0 ? 'A white ring approximates their certified tangent meeting.' : roots.length === 2 ? 'Two white dots mark crossings bounding a pale lens.' : 'There are no crossings between these branches in the displayed neighborhood.'}`;
    get('gap-description').textContent = `Earlier branch minus later branch, measured normal to the common tangent. Horizontal range minus ${half} to plus ${half}; vertical range minus ${e.gap_limit} to plus ${e.gap_limit}. Scales differ. ${roots.length} ${progress === 0 ? 'touch' : 'crossing'} markers. The dashed curve is their separation at the touch weight.`;
  }

  function update() {
    try { render(); }
    catch (error) {
      get('explorer').hidden = true; get('fallback').hidden = false;
      console.error(error);
    }
  }

  render();
  eventControl.addEventListener('change', update);
  reflection.addEventListener('change', update);
  progressControl.addEventListener('input', update);
  for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
    get(id).addEventListener('click', () => { progressControl.value = value; update(); });
  }
  window.addEventListener('pageshow', update);
  get('explorer').hidden = false; get('fallback').hidden = true;
})();
