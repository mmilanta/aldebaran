'use strict';
(() => {
  const M = FourVisitsMath, V = FourVisitsView, get = id => document.getElementById(id);
  const passage = get('passage');
  let selected = 0;
  const signed = n => (n < 0 ? '−' : '+') + Math.abs(n).toFixed(5);
  function update() {
    const state = M.state(selected, Number(passage.value)), names = state.event.indices.map(i => i + 1).join(', ');
    const where = state.progress < 0 ? 'Before' : state.progress > 0 ? 'After' : 'At';
    get('weight').value = 'd = ' + signed(state.weight);
    get('area').value = state.area === 0 ? '0' : state.area.toFixed(6);
    passage.setAttribute('aria-valuetext', `${where} visits ${names} meet; model weight ${signed(state.weight)}`);
    get('model-drawing').innerHTML = V.lens(state);
    get('directions-drawing').innerHTML = V.circle(state.event.indices);
    get('model-description').textContent = `${where} the triple of visits ${names} in the first-order local lines. ` +
      `Weight d is ${signed(state.weight)}. Triangle area ${state.area.toFixed(6)} model square units. ` +
      'Both axes have the same scale. The selected passage has positive sign. The faint fourth line stays away from the triangle.';
    const status = state.progress === 0 ? `Visits ${names} meet. The triangle has zero area; the fourth line stays away. Passage sign +1.` :
      `${where} visits ${names} meet. ${state.progress < 0 ? 'The thin triangle closes as the slider approaches zero.' : 'The triangle has reopened on the other side. Passage sign +1.'}`;
    if (get('status').textContent !== status) get('status').textContent = status;
    for (const button of document.querySelectorAll('[data-meeting]')) button.setAttribute('aria-pressed', String(Number(button.dataset.meeting) === selected));
    for (const button of document.querySelectorAll('[data-progress]')) button.setAttribute('aria-pressed', String(Number(button.dataset.progress) === state.progress));
  }
  passage.addEventListener('input', update);
  for (const button of document.querySelectorAll('[data-meeting]')) button.addEventListener('click', () => { selected = Number(button.dataset.meeting); update(); });
  for (const button of document.querySelectorAll('[data-progress]')) button.addEventListener('click', () => { passage.value = button.dataset.progress; update(); });
  window.addEventListener('pageshow', () => { setTimeout(update, 0); });
  update();
  get('explorer').hidden = false;
  get('fallback').hidden = true;
})();
