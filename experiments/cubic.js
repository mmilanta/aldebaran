'use strict';

(() => {
  const M = CubicMath, get = id => document.getElementById(id);
  const opening = get('opening'), tilt = get('tilt');
  const ns = 'http://www.w3.org/2000/svg';
  const signed = n => `${n < 0 ? '−' : n > 0 ? '+' : ''}${Math.abs(n).toFixed(2)}`;
  const areaText = n => n === 0 ? '0' : n < .00001 ? n.toExponential(3) : n.toFixed(5);
  const graphMap = ([q, v]) => [330 + 160 * q, 280 - 140 * v];
  const planeMap = ([mu, tau]) => [65 + 165 * (mu + .5), 210 - 76 * tau];
  const pair = p => p.map(n => n.toFixed(5)).join(' ');

  function curve(mu, tau, low, high) {
    const p = M.bezier(mu, tau, low, high).map(graphMap);
    return `M${pair(p[0])} C${pair(p[1])} ${pair(p[2])} ${pair(p[3])}`;
  }

  function update() {
    const mu = Number(opening.value), tau = Number(tilt.value);
    const data = M.state(mu, tau);
    get('opening-value').value = signed(mu);
    get('tilt-value').value = signed(tau);
    opening.setAttribute('aria-valuetext', `${signed(mu)} opening`);
    tilt.setAttribute('aria-valuetext', `${signed(tau)} tilt${tau === 0 ? ', mirror intact' : ''}`);
    get('model-line').setAttribute('d', curve(mu, tau, -M.limits.height, M.limits.height));
    for (let j = 0; j < 2; j++) {
      const pocket = data.pockets[j];
      const area = pocket?.area || 0;
      let d = '';
      if (area > 0) {
        d = curve(mu, tau, pocket.low, pocket.high) +
          ` L${pair(graphMap([0, pocket.high]))} L${pair(graphMap([0, pocket.low]))} Z`;
      }
      get(`pocket-${j}`).setAttribute('d', d);
      get(`area-${j}`).value = areaText(area);
    }
    get('roots').replaceChildren(...data.meetings.map(meeting => {
      const circle = document.createElementNS(ns, 'circle');
      const [x, y] = graphMap([0, meeting.v]);
      circle.setAttribute('cx', x); circle.setAttribute('cy', y);
      circle.setAttribute('r', meeting.kind === 'crossing' ? 4.5 : 7);
      circle.setAttribute('class', meeting.kind === 'crossing' ? 'crossing' : 'touch');
      return circle;
    }));
    const [x, y] = planeMap([mu, tau]);
    get('parameter-point').setAttribute('cx', x);
    get('parameter-point').setAttribute('cy', y);
    const descriptions = {
      one: 'One crossing. No bounded pocket between these two model branches.',
      three: tau === 0 ? 'Three crossings. Two equal pockets, with the mirror intact.' :
        'Three crossings. Two pockets of different areas.',
      touch: `One crossing and one quadratic touch. The ${tau > 0 ? 'upper' : 'lower'} pocket has zero area at the touch.`,
      cubic: 'One cubic contact. Both pockets have zero area at the same meeting.'
    };
    const status = descriptions[data.kind];
    if (get('status').textContent !== status) get('status').textContent = status;
    get('model-description').textContent = `Leading cubic model at opening ${signed(mu)}, tilt ${signed(tau)}. ` +
      status + ` Lower pocket area ${areaText(data.pockets[0]?.area || 0)}; ` +
      `upper pocket area ${areaText(data.pockets[1]?.area || 0)} normalized square units. ` +
      `Meetings at heights ${data.meetings.map(m => `${m.v.toFixed(4)} (${m.kind})`).join(', ')}. ` +
      'The horizontal axis measures separation and has a different scale from height.';
    get('plane-description').textContent = `A map of opening against tilt. ` +
      'The two curved boundaries meet at zero opening and zero tilt. Inside are three crossings and two pockets; outside is one crossing. ' +
      `The current point is opening ${signed(mu)}, tilt ${signed(tau)}. ${status}`;
    for (const button of document.querySelectorAll('[data-opening]')) {
      button.setAttribute('aria-pressed', String(mu === Number(button.dataset.opening) && tau === Number(button.dataset.tilt)));
    }
  }

  for (const slider of [opening, tilt]) slider.addEventListener('input', update);
  for (const button of document.querySelectorAll('[data-opening]')) {
    button.addEventListener('click', () => {
      opening.value = button.dataset.opening;
      tilt.value = button.dataset.tilt;
      update();
    });
  }
  // (mu, tau) = (s², s³) is itself a cubic Bezier curve.
  const r = Math.sqrt(1.5), t = r ** 3;
  const cusp = [[1.5, -t], [-.5, t], [-.5, -t], [1.5, t]].map(planeMap);
  const cuspPath = `M${pair(cusp[0])} C${pair(cusp[1])} ${pair(cusp[2])} ${pair(cusp[3])}`;
  get('cusp-boundary').setAttribute('d', cuspPath);
  get('cusp-fill').setAttribute('d', cuspPath + ' Z');
  // Browsers can restore range values after script initialization on Back.
  window.addEventListener('pageshow', () => { setTimeout(update, 0); });
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
