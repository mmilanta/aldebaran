'use strict';

// Illustration from the separately rerunnable rational complete census.
const fs = require('node:fs'), path = require('node:path');
const census = require('./offset_leg_census.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = bounds => (rational(bounds[0]) + rational(bounds[1])) / 2;
const colors = { ink: '#f4f1e8', soft: '#c7c7d4', muted: '#9999ae', grid: '#383b50',
  positive: '#e8b66e', negative: '#9fc7eb', mixed: '#d1b6ea' };
const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const ledger = ['drawing,event_order,offset_lower,offset_upper,offset_approx,event,positive_after_resolution,negative_after_resolution,strangeness_before,strangeness_after'];
const text = (x, y, value, size = 20, color = colors.soft, extra = '') =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${escape(value)}</text>`;
const parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1140" viewBox="0 0 1200 1140" role="img" aria-labelledby="title description">',
  '<title id="title">Every meeting on the way out</title>',
  '<desc id="description">Two complete outward offset legs. Rhythms 11 / 6 have 94 ordinary off-axis triples and eleven mirror-axis fourfolds; 11 / 8 have 96 triples and nine fourfolds. Resolving the fourfolds gives 138 and 132 ordinary triples. Each plotted position is one ordered event weight, not an equal increment of offset distance. Gold segments increase strangeness, blue segments decrease it, and lilac diamonds mark cancelling fourfolds. The step counts end at minus 87 and minus 101. Hover an event for its distance and signs. The rational proof covers every nonnegative offset, including the infinite tail.</desc>',
  '<rect width="1200" height="1140" fill="#101323"/><g font-family="ui-sans-serif,system-ui,sans-serif">',
  text(40, 68, 'Every meeting on the way out.', 43, colors.ink),
  text(40, 108, 'A complete circle census accounts for both outward legs, at every distance M ≥ 0.', 22),
  '<path d="M40 147h27" stroke="#e8b66e" stroke-width="4"/>', text(78, 154, 'positive passage', 19),
  '<path d="M302 147h27" stroke="#9fc7eb" stroke-width="4"/>', text(340, 154, 'negative passage', 19),
  '<path d="M583 140l7 7-7 7-7-7Z" fill="#d1b6ea"/>', text(604, 154, 'fourfold: four triple subsets', 19)];

census.endpoints.forEach((endpoint, row) => {
  const top = 198 + row * 440, left = 100, right = 1128, plotTop = top + 86, height = 217;
  const start = endpoint.inner === 6 ? 15 : 11, finish = endpoint.inner === 6 ? -87 : -101;
  const events = endpoint.events;
  if (!events?.length) throw new Error('A complete ordered event record is required.');
  const X = rank => left + (right - left) * rank / (events.length + 1);
  const Y = value => plotTop + height * (20 - value) / 130;
  parts.push(text(40, top + 14, `11 / ${endpoint.inner}    ${endpoint.off_axis_triples} ordinary triples + ${endpoint.axis_fourfolds} fourfolds`, 27, colors.ink),
    text(40, top + 49, `After local resolution: ${endpoint.positive_triples} positive + ${endpoint.negative_triples} negative = ${endpoint.positive_triples + endpoint.negative_triples} triples`, 20));
  for (const value of [0, -50, -100]) {
    const y = Y(value);
    parts.push(`<path d="M${left} ${y}H${right}" stroke="${colors.grid}" stroke-dasharray="4 5"/>`,
      text(left - 16, y + 6, value === 0 ? '0' : `−${-value}`, 17, colors.muted, 'text-anchor="end"'));
  }
  parts.push(text(left, plotTop - 14, 'Strangeness', 17, colors.muted));
  let value = start, previous = 0;
  events.forEach((event, index) => {
    const x = X(index + 1), before = value;
    const jump = event.positive_triples - event.negative_triples;
    value += jump;
    ledger.push([`11/${endpoint.inner}`, index + 1, ...event.offset, middle(event.offset).toFixed(8),
      event.kind === 'axis_fourfold' ? 'axis fourfold' : 'reflected triples',
      event.positive_triples, event.negative_triples, before, value].join(','));
    const color = jump > 0 ? colors.positive : jump < 0 ? colors.negative : colors.mixed;
    parts.push(`<path d="M${X(previous)} ${Y(before)}H${x}" fill="none" stroke="${colors.soft}" stroke-width="2"/>`);
    const label = `Event ${index + 1}; M ≈ ${middle(event.offset).toFixed(8)}; ${event.kind === 'axis_fourfold' ? 'one axis fourfold' : 'two reflected ordinary triples'}; ${event.positive_triples} positive, ${event.negative_triples} negative; strangeness ${before} to ${value}.`;
    parts.push(`<g><title>${escape(label)}</title>`,
      `<path d="M${x} ${Y(before)}V${Y(value)}" stroke="${color}" stroke-width="3"/>`);
    if (event.kind === 'axis_fourfold') {
      const y = Y(value);
      parts.push(`<path d="M${x} ${y - 4}l4 4-4 4-4-4Z" fill="${color}"/>`);
    } else {
      parts.push(`<circle cx="${x}" cy="${Y(value)}" r="2.5" fill="${color}"/>`);
    }
    parts.push('</g>');
    previous = index + 1;
  });
  if (value !== finish || events.reduce((n, e) => n + e.roots.length, 0) !== endpoint.roots.length) {
    throw new Error('The diagram does not reproduce the complete signed count.');
  }
  parts.push(`<path d="M${X(previous)} ${Y(value)}H${right}" stroke="${colors.soft}" stroke-width="2"/>`,
    text(left - 14, Y(start) - 2, `+${start}`, 18, colors.ink, 'text-anchor="end"'),
    text(right + 14, Y(finish) + 6, `−${-finish}`, 18, colors.ink));
  const axisY = plotTop + height + 24;
  parts.push(`<path d="M${left} ${axisY}H${right}" stroke="${colors.grid}"/>`);
  for (let rank = 10; rank <= events.length; rank += 10) {
    parts.push(`<path d="M${X(rank)} ${axisY}v6" stroke="${colors.muted}"/>`,
      text(X(rank), axisY + 27, rank, 16, colors.muted, 'text-anchor="middle"'));
  }
  parts.push(text(left, axisY + 59, `${events.length} ordered event weights · horizontal spacing is event order, not offset distance`, 18),
    text(left, axisY + 89, `First: M ≈ ${middle(events[0].offset).toFixed(5)}`, 18),
    text(right, axisY + 89, `Last: M ≈ ${middle(events.at(-1).offset).toFixed(5)}`, 18, colors.soft, 'text-anchor="end"'));
});
parts.push(text(40, 1103, 'The sufficiently distant full construction has 138 + 722 + 132 = 992 triples, after local generic resolution.', 20, colors.ink),
  '</g></svg>');
fs.writeFileSync(path.join(__dirname, 'offset_leg_census.svg'), parts.join('\n') + '\n');
fs.writeFileSync(path.join(__dirname, 'offset_leg_census.csv'), ledger.join('\n') + '\n');
console.log('Wrote offset_leg_census.svg and the CSV event ledger from the complete rational record.');
