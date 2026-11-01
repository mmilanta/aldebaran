'use strict';

(() => {
  const M = PositiveFrontMath, data = PositiveFrontData;
  const states = M.replay(data);
  const $ = id => document.getElementById(id);
  const moveInput = $('move'), progressInput = $('progress');
  const colors = ['#e8b66e', '#9fc7eb', '#d1b6ea', '#f4f1e8'];
  const names = { commute: 'Independent crossings exchange order', triangle: 'Three strands slide past one another', cycle: 'The cut passes one crossing' };
  const n = value => String(Math.round(value * 1000) / 1000);
  const path = points => points.map(([x, y], i) => `${i ? 'L' : 'M'}${n(x)},${n(y)}`).join('');
  const line = (d, color, width = 2, extra = '') => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" ${extra}/>`;
  const dot = (x, y, color, radius = 5) => `<circle cx="${n(x)}" cy="${n(y)}" r="${radius}" fill="${color}" stroke="#0b0e1a" stroke-width="1.5"/>`;
  let index = data.moves.findIndex(move => move[0] === 'triangle');

  function drawStrip() {
    const word = [...states[index]], [kind, at] = data.moves[index];
    const labels = Array.from({ length: 11 }, (_, i) => i);
    const paths = labels.map((_, i) => `M38,${n(170 - 12 * i)}`);
    const dx = 1044 / word.length, selected = kind === 'cycle' ? [0] :
      Array.from({ length: kind === 'triangle' ? 3 : 2 }, (_, k) => at + k);
    const active = new Set();
    for (let k = 0; k < word.length; k++) {
      const lower = word[k] - 1, x = 38 + dx * k;
      if (selected.includes(k)) { active.add(labels[lower]); active.add(labels[lower + 1]); }
      for (let rank = 0; rank < 11; rank++) {
        const target = rank === lower ? lower + 1 : rank === lower + 1 ? lower : rank;
        paths[labels[rank]] += `L${n(x + dx * .2)},${n(170 - 12 * rank)}` +
          `L${n(x + dx * .8)},${n(170 - 12 * target)}L${n(x + dx)},${n(170 - 12 * target)}`;
      }
      [labels[lower], labels[lower + 1]] = [labels[lower + 1], labels[lower]];
    }
    $('strip-strands').innerHTML = paths.map((d, label) => line(d, active.has(label) ? '#e8b66e' : '#737b99', active.has(label) ? 1.8 : .9)).join('');
    $('strip-highlights').innerHTML = selected.map(k =>
      `<rect x="${n(38 + dx * k)}" y="43" width="${n(dx)}" height="136" fill="#e8b66e" fill-opacity=".12" stroke="#e8b66e" stroke-width=".7"/>`).join('');
    $('strip-description').textContent = `Word before move ${index + 1} of ${data.moves.length}. ${names[kind]}. ${selected.length} active crossing${selected.length > 1 ? 's' : ''} highlighted. Join matching heights across the seam.`;
  }

  function drawLocal() {
    const word = [...states[index]], move = data.moves[index], kind = move[0];
    const u = Number(progressInput.value) / 100;
    const model = M.local(word, move, 0, u), [low, high] = model.range;
    const xMap = x => 55 + 500 * (x + 1) / 2;
    const yMap = h => 390 - 335 * (h - low) / (high - low);
    const color = i => {
      const at = model.labels.indexOf(i);
      return at < 0 ? '#737b99' : colors[at % colors.length];
    };
    const curves = model.heights.map(() => []);
    for (let k = 0; k <= 240; k++) {
      const x = -1 + k / 120, values = M.local(word, move, x, u);
      values.heights.forEach((h, i) => curves[i].push([xMap(x), yMap(h)]));
    }
    $('local-strands').innerHTML = curves.map((points, i) => line(path(points), color(i), model.labels.includes(i) ? 2.7 : 1)).join('');
    // Concentric, unfilled rings remain visible at a triple or shared line.
    $('local-marks').innerHTML = model.labels.map((i, order) => {
      const coincidentBefore = model.labels.slice(0, order).filter(j => Math.abs(model.heights[j] - model.heights[i]) < 1e-10).length;
      return `<circle cx="305" cy="${n(yMap(model.heights[i]))}" r="${5 + 3 * coincidentBefore}" fill="none" stroke="${color(i)}" stroke-width="2"/>`;
    }).reverse().join('');
    $('cut').toggleAttribute('hidden', kind !== 'cycle');
    if (kind === 'cycle') {
      const x = xMap(-.7 + 1.4 * u);
      $('cut').setAttribute('d', `M${n(x)},55V390`);
    }
    const points = M.points(model), active = model.labels;
    // Equal x/y scales; fit every active point and its full tangent marker.
    const extent = Math.max(2.8, ...active.map(i => Math.abs(model.heights[i]) + .5),
      ...active.map(i => Math.abs(model.slopes[i]) + .55));
    const scale = Math.min(75, 155 / extent), centerX = 300, centerY = 220;
    $('point-lines').innerHTML = active.map(i => {
      const x = centerX + scale * (points[i][0] + 25);
      return line(`M${n(x)},65V375`, color(i), 1.3, 'stroke-dasharray="5 6" opacity=".8"');
    }).join('');
    $('point-marks').innerHTML = active.map(i => {
      const x = centerX + scale * (points[i][0] + 25), y = centerY - scale * points[i][1];
      return dot(x, y, color(i), 6) + line(`M${n(x + 13)},${n(y - 12)}v24m-4,-5l4,5l4,-5`, color(i), 1.5);
    }).join('');
    const halfway = Number(progressInput.value) === 50;
    const position = u === 0 ? 'Before' : u === 1 ? 'After' : halfway ? 'Halfway' : 'Between';
    $('progress-value').textContent = `${position} · ${Math.round(100 * u)}%`;
    progressInput.setAttribute('aria-valuetext', `${position}, ${Math.round(100 * u)} percent`);
    $('progress-label').textContent = kind === 'triangle' ? 'Move the three strands' : kind === 'commute' ? 'Exchange the crossing order' : 'Move the cut';
    $('local-description').textContent = kind === 'triangle' ?
      `Three strands in a smooth local model. ${halfway ? 'All three heights agree, with three distinct slopes.' : 'Three crossings form a small triangle.'} Progress ${Math.round(100 * u)} percent.` :
      kind === 'commute' ? 'Two crossings on separate strand pairs exchange order at different heights.' :
        'The same graph stays fixed while the white dashed cut moves past its crossing.';
    $('points-description').textContent = kind === 'triangle' ?
      `At the center normal, the three original points are separate. ${halfway ? 'Their three tangent lines now coincide.' : 'Two share one tangent line; the middle point has a different line.'}` :
      `${active.length} distinct points at the center normal, reconstructed from the local distances and slopes. Arrows show travel direction.`;
    $('points-note').textContent = kind === 'triangle' ? (halfway ? 'One line · three distinct places' : 'Different slopes keep the points apart') :
      kind === 'commute' ? 'Independent contacts · separate height bands' : 'Same points · a different place to start';
    $('local-caption').textContent = kind === 'triangle' ?
      'A smooth model of the selected three-strand move. Its crossings have the same order as the highlighted word. Angle and distance have different units.' :
      kind === 'commute' ? 'Two separate strand pairs exchange crossing order. At halfway, their crossings align horizontally but remain at different heights. Other strands stay in place.' :
        'The white dashed cut passes a crossing. Reading from that cut moves the first crossing to the end. The graph itself stays fixed.';
    $('points-caption').textContent = kind === 'triangle' ?
      'Distance places each tangent line; slope places the point along it. At halfway, all three lie on one line and stay distinct. This local reconstruction uses equal coordinate scales.' :
      'Dots reconstruct the active strands at the center direction. Dashed lines are their tangent lines; arrows point along travel. Both axes use the same scale, fitted to this move.';
  }

  function select(at) {
    index = Math.max(0, Math.min(data.moves.length - 1, at));
    moveInput.value = String(index);
    progressInput.value = '0';
    const [kind, position] = data.moves[index];
    $('move-value').textContent = `Move ${(index + 1).toLocaleString('en-US')} of ${data.moves.length.toLocaleString('en-US')}`;
    moveInput.setAttribute('aria-valuetext', `Move ${index + 1} of ${data.moves.length}: ${names[kind]}`);
    const word = [...states[index]], width = kind === 'triangle' ? 3 : kind === 'commute' ? 2 : 1;
    const before = kind === 'cycle' ? [word[0]] : word.slice(position, position + width);
    const afterWord = [...states[index + 1]], after = kind === 'cycle' ? [afterWord.at(-1)] : afterWord.slice(position, position + width);
    $('status').textContent = `${names[kind]}. ` + (kind === 'cycle' ?
      `Crossing ${before[0]} moves from the beginning to the end of the closed word.` :
      `Crossings ${before.join(' · ')} become ${after.join(' · ')}. Move the lower slider to see how.`);
    $('previous').disabled = index === 0;
    $('next').disabled = index === data.moves.length - 1;
    $('first').disabled = index === 0;
    $('last').disabled = index === data.moves.length - 1;
    for (const kind of ['triangle', 'commute', 'cycle']) $(kind).disabled = M.next(data.moves, index, kind, 1) === index;
    drawStrip(); drawLocal();
  }

  moveInput.max = String(data.moves.length - 1);
  moveInput.addEventListener('input', () => select(Number(moveInput.value)));
  progressInput.addEventListener('input', drawLocal);
  $('previous').addEventListener('click', () => select(index - 1));
  $('next').addEventListener('click', () => select(index + 1));
  $('first').addEventListener('click', () => select(0));
  $('last').addEventListener('click', () => select(data.moves.length - 1));
  for (const kind of ['triangle', 'commute', 'cycle']) $(kind).addEventListener('click', () => select(M.next(data.moves, index, kind, 1)));
  document.querySelectorAll('[data-progress]').forEach(button => button.addEventListener('click', () => {
    progressInput.value = button.dataset.progress;
    drawLocal();
  }));
  select(index);
  $('explorer').hidden = false;
  $('fallback').hidden = true;
})();
