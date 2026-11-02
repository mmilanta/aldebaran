'use strict';

(() => {
  if (typeof ParallelOffsetView === 'undefined') return;
  const Model = ParallelOffsetMath, View = ParallelOffsetView;
  const get = id => document.getElementById(id), control = get('passage');
  const format = (x, places) => x.toFixed(places).replace('-', '−');

  function update() {
    try {
      const progress = Number(control.value), state = Model.state(progress), triangle = Model.triangle(state);
      get('lens-picture').innerHTML = View.lens(state);
      // Clip only the geometric paths. The explanatory labels stay outside.
      for (const node of get('lens-picture').children) {
        if (node.tagName.toLowerCase() !== 'text') node.setAttribute('clip-path', 'url(#lens-clip)');
      }
      get('offset-value').textContent = format(state.offset, 5);
      const delta = progress * .0015;
      get('area-ratio').textContent = progress === 0
        ? `${ParallelOffsetData.areaCoefficient.toFixed(8)} (limit)`
        : (triangle.area / (delta * delta)).toFixed(6);
      get('difference-value').textContent = `${delta > 0 ? '+' : ''}${format(delta, 4)}`;
      get('area-value').textContent = progress === 0 ? '0' : format(triangle.area, 6);
      const phrase = progress < 0 ? 'Before the meeting' : progress > 0 ? 'After the meeting' : 'At the selected meeting';
      get('passage-value').textContent = `${phrase} · ${delta > 0 ? '+' : ''}${format(delta, 4)} drawing units beyond its distance`;
      control.setAttribute('aria-valuetext', `${phrase}, outward distance ${state.offset.toFixed(5)} drawing units`);
      get('status').textContent = progress === 0
        ? 'Three visits share one point. Their travel directions remain different. The displayed meeting distance is rounded from its rational enclosure.'
        : `${phrase}: three separate pairwise crossings enclose the shaded triangle. Move ${progress < 0 ? 'forward' : 'back'} toward the center setting to bring its corners together.`;
      get('lens-description').textContent = `Outward distance ${state.offset.toFixed(5)} for rhythms 11 / 6. ${get('status').textContent} The fixed square is two drawing units wide and high.`;
      for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
        get(id).setAttribute('aria-pressed', String(progress === value));
      }
      get('explorer').hidden = false;
      get('fallback').hidden = true;
    } catch (error) {
      get('explorer').hidden = true;
      get('fallback').hidden = false;
      console.error(error);
    }
  }

  try {
    get('circle-picture').innerHTML = View.circle();
    for (const node of get('circle-picture').children) {
      if (node.tagName.toLowerCase() !== 'text') node.setAttribute('clip-path', 'url(#circle-clip)');
    }
  } catch (error) {
    console.error(error);
    return;
  }
  control.addEventListener('input', update);
  for (const [id, value] of [['before', -100], ['meeting', 0], ['after', 100]]) {
    get(id).addEventListener('click', () => { control.value = value; update(); });
  }
  window.addEventListener('pageshow', update);
  update();
})();
