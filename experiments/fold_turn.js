'use strict';

(() => {
  const math = FoldTurnMath;
  const get = id => document.getElementById(id);
  const phase = get('phase'), folds = get('folds'), trace = get('trace');
  const initial = math.parse(window.location.search);
  folds.value = String(initial.folds);
  phase.value = String(initial.phase);
  trace.value = String(initial.trace);
  let lastShape = '';
  let downloadURL;
  let downloadTimer;
  const state = () => ({ folds: Number(folds.value), phase: Number(phase.value), trace: Number(trace.value) });
  const point = (id, p) => {
    get(id).setAttribute('cx', p[0]);
    get(id).setAttribute('cy', -p[1]);
  };
  const lineEnd = (id, p, end = 2) => {
    get(id).setAttribute(`x${end}`, p[0]);
    get(id).setAttribute(`y${end}`, -p[1]);
  };

  function update() {
    const s = state();
    const angle = s.phase * Math.PI / 180;
    const t = math.cycle * s.trace / (1000 * s.folds);
    const shape = `${s.folds}/${s.phase}`;
    if (shape !== lastShape) {
      get('orbit-path').setAttribute('d', math.orbitPath(s.folds, angle));
      get('repeat-path').setAttribute('d', math.orbitPath(s.folds, angle, true));
      get('ellipse-path').setAttribute('d', math.path(u => math.ellipse(u, angle), 0, math.cycle, 1024));
      const range = math.radialRange(angle);
      get('range-value').value = `${range[0].toFixed(2)}–${range[1].toFixed(2)} units`;
      lastShape = shape;
    }
    const { fixed, turning } = math.joints(t, s.folds, angle);
    const radius = Math.hypot(...fixed[3]);
    const percent = `${(s.trace / 10).toFixed(1).replace(/\.0$/, '')}%`;
    const armTurn = (360 * s.trace / (1000 * s.folds)).toFixed(2);
    get('phase-value').value = `${s.phase}°`;
    get('trace-value').value = percent;
    get('radius-value').value = `${radius.toFixed(2)} units`;
    get('turn-value').value = `${armTurn}°`;
    phase.setAttribute('aria-valuetext', `${s.phase} degrees starting angle`);
    trace.setAttribute('aria-valuetext', `${percent} of one repeat; first arm has turned ${armTurn} degrees; distance ${radius.toFixed(2)} units`);
    point('orbit-point', turning[3]);
    point('ellipse-point', fixed[3]);
    point('ellipse-joint', fixed[2]);
    lineEnd('orbit-radius', turning[3]);
    get('ellipse-radius').setAttribute('r', radius);
    lineEnd('ellipse-outer', fixed[2]);
    lineEnd('ellipse-inner', fixed[2], 1);
    lineEnd('ellipse-inner', fixed[3]);
    for (const button of document.querySelectorAll('[data-phase]')) {
      button.setAttribute('aria-pressed', String(Number(button.dataset.phase) === s.phase));
    }
    get('orbit-title').textContent = `An orbital drawing in ${s.folds} repeats`;
    get('orbit-desc').textContent = `${s.folds} rotational folds, with a backward-arm starting angle of ${s.phase} degrees. One repeat is gold. The white point is ${percent} through it, ${radius.toFixed(2)} units from the center. The first arm has turned ${armTurn} degrees.`;
    get('ellipse-desc').textContent = `The first arm stays horizontal in this moving frame. The ellipse has radii 205 and 75 and is tilted ${s.phase / 2} degrees about the first arm's endpoint. The white point is ${percent} through one circuit, ${radius.toFixed(2)} units from the origin. A dotted arc marks that radius.`;
    get('view-link').href = `fold_turn.html?${math.query(s)}`;
  }

  function releaseDownload() {
    if (downloadURL) URL.revokeObjectURL(downloadURL);
    downloadURL = undefined;
    window.clearTimeout(downloadTimer);
  }

  for (const control of [folds, phase, trace]) control.addEventListener('input', update);
  for (const button of document.querySelectorAll('[data-phase]')) {
    button.addEventListener('click', () => { phase.value = button.dataset.phase; update(); });
  }
  get('save').addEventListener('click', () => {
    const s = state();
    try {
      releaseDownload();
      const svg = math.drawing(s.folds, s.phase);
      downloadURL = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }));
      const anchor = document.createElement('a');
      anchor.href = downloadURL;
      anchor.download = `aldebaran-${s.folds}-folds-${s.phase}-degrees.svg`;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      // Leave the URL alive long enough for engines to start the download.
      downloadTimer = window.setTimeout(releaseDownload, 60000);
      get('download-status').textContent = `Saved ${s.folds} folds at ${s.phase}°. The SVG contains the complete drawing, without the point or guides.`;
    } catch (_) {
      get('download-status').textContent = 'The drawing could not be saved here. Try opening this page in a browser with downloads enabled, or save the six still drawings.';
    }
  });
  window.addEventListener('pagehide', releaseDownload);
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
