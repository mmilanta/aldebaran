'use strict';

const innerLength = document.querySelector('#length');
const reference = document.querySelector('#reference');
const showReference = document.querySelector('#show-reference');
const span = 0.05;
const zoom = 14;
const samples = 400;

function offset(t, radius) {
  // Measure from the tip; -2 sin²(a/2) avoids subtracting nearly equal cosines.
  const x = -2 * (245 * Math.sin(t / 2) ** 2 +
    140 * Math.sin(4 * t) ** 2 + radius * Math.sin(10.5 * t) ** 2);
  const y = 245 * Math.sin(t) + 140 * Math.sin(8 * t) - radius * Math.sin(21 * t);
  return [800 + zoom * x, 300 + zoom * y];
}

function curve(radius, start, end) {
  const commands = [];
  for (let sample = 0; sample <= samples; sample++) {
    const t = start + (end - start) * sample / samples;
    const [x, y] = offset(t, radius);
    commands.push(`${sample === 0 ? 'M' : 'L'}${x} ${y}`);
  }
  return commands.join(' ');
}

function crossing(radius) {
  // For 65 < radius <= 72 there is exactly one positive crossing in this lens.
  // The companion note proves existence and uniqueness; bisection locates it.
  let low = 0;
  let high = span;
  for (let iteration = 0; iteration < 50; iteration++) {
    const t = (low + high) / 2;
    const y = 245 * Math.sin(t) + 140 * Math.sin(8 * t) - radius * Math.sin(21 * t);
    if (y < 0) low = t;
    else high = t;
  }
  return offset((low + high) / 2, radius)[0];
}

function update() {
  const radius = Number(innerLength.value);
  document.querySelector('#length-value').value = innerLength.value;
  document.querySelector('#arriving').setAttribute('d', curve(radius, -span, 0));
  document.querySelector('#leaving').setAttribute('d', curve(radius, 0, span));
  const marker = document.querySelector('#crossing');
  marker.setAttribute('visibility', radius > 65 ? 'visible' : 'hidden');
  if (radius > 65) {
    marker.setAttribute('cx', crossing(radius));
    marker.setAttribute('cy', 300);
  }
  for (const button of document.querySelectorAll('[data-length]')) {
    button.setAttribute('aria-pressed', String(Number(button.dataset.length) === radius));
  }
  const title = radius < 65 ? 'A rounded turn' : radius > 65 ? 'A little loop' : 'A moment at rest';
  const description = radius < 65
    ? 'The forward motion wins. The point passes through the tip without stopping, making a rounded turn.'
    : radius > 65
      ? 'The backward motion wins at the tip. The curve crosses itself, enclosing a little loop.'
      : 'The motions balance exactly. The point stops at the tip and turns back along a cusp.';
  document.querySelector('#state-title').textContent = `${radius} · ${title}`;
  document.querySelector('#state-description').textContent = description;
  document.querySelector('#lens-title').textContent = `${title}, with inner arm length ${radius}`;
  document.querySelector('#lens-description').textContent =
    `A close-up of Needle’s rightmost tip. ${description} Blue arrives and gold leaves.`;
}

innerLength.addEventListener('input', update);
for (const button of document.querySelectorAll('[data-length]')) {
  button.addEventListener('click', () => {
    innerLength.value = button.dataset.length;
    update();
  });
}
showReference.addEventListener('change', () => {
  reference.setAttribute('visibility', showReference.checked ? 'visible' : 'hidden');
});
reference.setAttribute('d', curve(65, -span, span));
update();
