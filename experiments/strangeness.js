'use strict';

(() => {
  const M = StrangenessMath, data = StrangenessData;
  const get = id => document.getElementById(id), ns = 'http://www.w3.org/2000/svg';
  const curve = get('curve'), base = get('base');
  const signed = n => `${n < 0 ? '−' : n > 0 ? '+' : ''}${Math.abs(n)}`;
  const number = n => n < 0 ? `−${-n}` : String(n);
  const half = n => `${n < 0 ? '−' : ''}${Math.abs(n) === 1 ? '½' : `${Math.abs(n)}/2`}`;
  const map = ([x, y]) => [320 + .63 * x, 320 - .63 * y];
  const pair = p => p.map(n => n.toFixed(5)).join(' ');
  let selected = 0, lastCurve = -1, state;

  function element(tag, attributes) {
    const node = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  }

  function update() {
    const which = Number(curve.value), record = data[which], E = record.word.length;
    if (which !== lastCurve) {
      base.max = E - 1;
      selected = 0;
      const points = Array.from({ length: 6001 }, (_, j) => map(M.orbit(j * 2 * Math.PI / 6000, record.outer, record.inner)));
      get('curve-line').setAttribute('d', `M${points.map(pair).join(' L')}`);
      get('drawing-label').textContent = `${record.outer} / ${record.inner} · Tangent index 0`;
      get('table-caption').textContent = `Crossing contributions for rhythms ${record.outer} / ${record.inner}`;
      const rows = Array.from({ length: record.crossings }, (_, j) => {
        const row = document.createElement('tr');
        const cell = document.createElement('th'); cell.scope = 'row';
        const button = document.createElement('button'); button.type = 'button';
        button.textContent = j + 1; button.setAttribute('aria-label', `Select crossing ${j + 1}`);
        button.addEventListener('click', () => { selected = j; update(); });
        cell.append(button); row.append(cell);
        for (let k = 0; k < 3; k++) row.append(document.createElement('td'));
        return row;
      });
      get('contributions').replaceChildren(...rows);
      lastCurve = which;
    }
    state = M.state(record, Number(base.value));
    get('base-value').value = `Edge ${state.base + 1} of ${E}`;
    base.setAttribute('aria-valuetext', `Starting edge ${state.base + 1} of ${E}, winding index ${state.index2}/2`);
    get('weighted').value = number(state.weightedSum);
    get('correction').value = state.correction;
    get('invariant').value = number(state.value);
    get('edge-description').textContent = `The starting edge has winding index ${half(state.index2)}. ` +
      `Its correction is (${half(state.index2)})² − ¼ = ${state.correction}.`;
    const status = `Starting on edge ${state.base + 1}. ${number(state.weightedSum)} plus ${state.correction} gives strangeness ${number(state.value)}.`;
    if (get('status').textContent !== status) get('status').textContent = status;
    const [x, y] = map(M.orbit(state.time, record.outer, record.inner));
    get('start-point').setAttribute('cx', x); get('start-point').setAttribute('cy', y);
    const v = M.velocity(state.time, record.outer, record.inner), length = Math.hypot(...v);
    const u = [v[0] / length, -v[1] / length], normal = [-u[1], u[0]];
    const a = [x + 10 * u[0], y + 10 * u[1]], b = [x + 38 * u[0], y + 38 * u[1]];
    const left = b.map((q, j) => q - 8 * u[j] + 5 * normal[j]);
    const right = b.map((q, j) => q - 8 * u[j] - 5 * normal[j]);
    get('start-arrow').setAttribute('d', `M${pair(a)} L${pair(b)} M${pair(left)} L${pair(b)} L${pair(right)}`);
    const markers = state.rows.map(row => {
      const visit = record.word.findIndex(([label]) => label === row.label);
      const [cx, cy] = map(record.display_points[visit]);
      return row.weight > 0 ? element('circle', { cx, cy, r: 5, class: 'positive' }) :
        element('rect', { x: cx - 4.5, y: cy - 4.5, width: 9, height: 9, class: 'negative' });
    });
    get('crossings').replaceChildren(...markers);
    const row = state.rows[selected];
    const visit = record.word.findIndex(([label]) => label === selected);
    const [cx, cy] = map(record.display_points[visit]);
    get('selected-ring').setAttribute('cx', cx); get('selected-ring').setAttribute('cy', cy);
    get('crossing-label').textContent = `White ring: selected crossing ${selected + 1}`;
    get('selection-title').textContent = `Crossing ${selected + 1}`;
    get('selection').textContent = `Weight ${signed(row.weight)} × mean winding count ${signed(row.index)} = ${signed(row.contribution)}. ` +
      `On its first encounter, the other branch points ${row.weight > 0 ? 'left to right' : 'right to left'} across your path.`;
    get('drawing-description').textContent = `Rhythms ${record.outer}/${record.inner}, ${record.crossings} crossings, tangent index zero. ` +
      status + ` White ring selects crossing ${selected + 1}: weight ${signed(row.weight)}, mean winding ${signed(row.index)}. ` +
      'Blue rings have weight plus one; gold squares have weight minus one. The white dot and arrow mark the start and travel direction.';
    for (const [j, tr] of [...get('contributions').children].entries()) {
      const r = state.rows[j];
      tr.querySelector('button').setAttribute('aria-pressed', String(j === selected));
      const cells = tr.querySelectorAll('td');
      [r.weight, r.index, r.contribution].forEach((value, k) => { cells[k].textContent = signed(value); });
    }
    get('word').replaceChildren(...state.sequence.map(([label, e]) => {
      const li = document.createElement('li');
      li.classList.toggle('current', label === selected);
      li.setAttribute('aria-label', `Crossing ${label + 1}, ${e > 0 ? 'plus' : 'minus'} one`);
      li.append(String(label + 1));
      const sup = document.createElement('sup'); sup.textContent = e > 0 ? '+' : '−';
      sup.classList.toggle('minus', e < 0); li.append(sup);
      return li;
    }));
  }

  base.addEventListener('input', update);
  curve.addEventListener('change', () => { base.value = 0; update(); });
  get('outside').addEventListener('click', () => { base.value = 0; update(); });
  get('next').addEventListener('click', () => { base.value = (Number(base.value) + 1) % data[Number(curve.value)].word.length; update(); });
  for (const [id, delta] of [['previous-crossing', -1], ['next-crossing', 1]]) {
    get(id).addEventListener('click', () => {
      const count = data[Number(curve.value)].crossings;
      selected = (selected + delta + count) % count;
      update();
    });
  }
  // A restored range can be clamped to the HTML's default maximum before
  // its restored drawing is applied. Save this page's controls on departure
  // and restore the drawing's maximum before restoring its edge.
  window.addEventListener('pagehide', () => {
    try {
      history.replaceState({ ...history.state, strangeness: {
        curve: Number(curve.value), base: Number(base.value), selected
      } }, '');
    } catch { /* The drawing remains usable if history storage is unavailable. */ }
  });
  window.addEventListener('pageshow', () => {
    setTimeout(() => {
      const saved = history.state?.strangeness;
      if (saved && Number.isInteger(saved.curve) && data[saved.curve] &&
          Number.isInteger(saved.base) && saved.base >= 0 && saved.base < data[saved.curve].word.length) {
        curve.value = saved.curve;
        base.max = data[saved.curve].word.length - 1;
        base.value = saved.base;
        update();
        if (Number.isInteger(saved.selected) && saved.selected >= 0 && saved.selected < data[saved.curve].crossings) {
          selected = saved.selected;
        }
      }
      update();
    }, 0);
  });
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
