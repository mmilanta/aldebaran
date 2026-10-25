'use strict';

(() => {
  const M = PhaseMath;
  const get = id => document.getElementById(id);
  const phaseSlider = get('phase'), weightSlider = get('weight');
  const signed = (n, digits) => `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(digits)}`;
  const percent = a => `${(100 * a).toFixed(5)}%`;
  const ns = 'http://www.w3.org/2000/svg';

  function path(points, map) {
    return points.map((p, j) => {
      const [x, y] = map(p);
      return `${j ? 'L' : 'M'}${x.toFixed(4)} ${y.toFixed(4)}`;
    }).join(' ');
  }

  function render(a, phase, meetings) {
    const r = M.radius(a);
    const heights = Array.from({ length: 385 }, (_, j) => -M.heightLimit + 2 * M.heightLimit * j / 384);
    const graphMap = ([gap, y]) => [342 + 130 * gap, 277 - 235 * y / M.heightLimit];
    for (const [id, p] of [['gap-line', phase], ['gap-reference', 0]]) {
      get(id).setAttribute('d', path(heights.map(y => [M.gap(y, a, p, r).value, y]), graphMap));
    }
    get('meetings').replaceChildren(...meetings.map(meeting => {
      const circle = document.createElementNS(ns, 'circle');
      const [x, y] = graphMap([0, meeting.height]);
      circle.setAttribute('cx', x); circle.setAttribute('cy', y);
      circle.setAttribute('r', meeting.kind === 'crossing' ? 4.5 : 6.5);
      circle.setAttribute('class', meeting.kind === 'crossing' ? 'meeting' : 'touch');
      return circle;
    }));
    get('gap-description').textContent = `Horizontal separation between the later gold and earlier blue branch, ` +
      `plotted against height from minus 32 to plus 32 drawing units. ` +
      `The current turn is ${signed(phase * 1000, 2)} milliradians; blend weight ${percent(a)}. ` +
      `The dashed reference restores zero turn at the same weight. ` +
      `Meetings in this window: ${meetings.map(m => `${m.kind} at height ${signed(m.height, 3)}`).join('; ')}. ` +
      `The horizontal and vertical scales are different.`;

    const scale = 170 / 505;
    const fullMap = ([x, y]) => [210 + scale * x, 210 - scale * y];
    get('outline').setAttribute('d', path(Array.from({ length: 2401 }, (_, j) =>
      M.evaluate(-Math.PI + 2 * Math.PI * j / 2400, a, phase)), fullMap));
    for (const [id, sign] of [['branch-plus', 1], ['branch-minus', -1]]) {
      get(id).setAttribute('d', path(heights.map(y => [M.branch(y, a, phase, sign, r).x, y]), fullMap));
    }
    const x0 = (M.branch(0, a, phase, 1, r).x + M.branch(0, a, phase, -1, r).x) / 2;
    const [patchX, patchY] = fullMap([x0, M.heightLimit]);
    get('patch').setAttribute('x', patchX - 12);
    get('patch').setAttribute('y', patchY - 6);
    get('patch').setAttribute('height', 2 * M.heightLimit * scale + 12);
    get('drawing-description').textContent = `The first arm is 300 drawing units long. ` +
      `Blend weight ${percent(a)}, backward-arm turn ${signed(phase * 1000, 2)} milliradians. ` +
      `Gold marks the later visit, blue the earlier visit. A dashed box locates their near overlap to the left of center. ` +
      `The full drawing has equal axis scales and stays at a fixed scale.`;
  }

  function update() {
    const phase = Number(phaseSlider.value) / 1000, a = Number(weightSlider.value);
    const contact = M.contact(phase);
    const meetings = M.meetings(a, phase);
    const turn = `${signed(phase * 1000, 2)} ${Math.abs(phase) === .001 ? 'milliradian' : 'milliradians'}`;
    get('phase-value').value = turn;
    get('weight-value').value = percent(a);
    get('contact-weight').value = percent(contact.weight);
    get('contact-height').value = signed(contact.height, 3);
    phaseSlider.setAttribute('aria-valuetext', `${turn}. ${phase === 0 ? 'Mirror restored.' : `Contact ${phase > 0 ? 'above' : 'below'} the axis.`}`);
    weightSlider.setAttribute('aria-valuetext', `${percent(a)} of the way from rhythms 2 / 3 to 4 / 7.`);
    let status;
    if (meetings.some(m => m.kind === 'cubic')) {
      status = 'One cubic contact on the axis. The mirror makes both slope and curvature agree.';
    } else if (meetings.some(m => m.kind === 'touch')) {
      status = 'Two meetings in the window: one crossing and one touch away from the axis.';
    } else if (meetings.length === 1) {
      status = 'One crossing in the window. The two extra nearby crossings have yet to appear.';
    } else if (meetings.length === 3) {
      status = 'Three crossings in the window. The two extra nearby crossings have appeared.';
    } else status = `${meetings.length} meetings in the displayed window.`;
    if (get('status').textContent !== status) get('status').textContent = status;
    for (const button of document.querySelectorAll('[data-stop]')) {
      button.setAttribute('aria-pressed', String(Math.abs(a - contact.weight - Number(button.dataset.stop)) < 1e-12));
    }
    render(a, phase, meetings);
  }

  for (const slider of [phaseSlider, weightSlider]) slider.addEventListener('input', update);
  weightSlider.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const steps = { ArrowRight: .0001, ArrowUp: .0001, ArrowLeft: -.0001,
      ArrowDown: -.0001, PageUp: .001, PageDown: -.001 };
    let value;
    if (event.key === 'Home') value = M.minimum;
    else if (event.key === 'End') value = M.maximum;
    else if (Object.hasOwn(steps, event.key)) {
      value = Number(weightSlider.value) + steps[event.key] * (event.shiftKey ? .1 : 1);
    } else return;
    event.preventDefault();
    weightSlider.value = String(Math.max(M.minimum, Math.min(M.maximum, value)));
    update();
  });
  for (const button of document.querySelectorAll('[data-stop]')) {
    button.addEventListener('click', () => {
      weightSlider.value = String(M.contact(Number(phaseSlider.value) / 1000).weight + Number(button.dataset.stop));
      update();
    });
  }
  get('mirror').addEventListener('click', () => {
    phaseSlider.value = '0'; weightSlider.value = String(M.critical); update();
  });
  window.addEventListener('pageshow', () => { setTimeout(update, 0); });
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
