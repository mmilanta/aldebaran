'use strict';

// Independent numerical geometry controls. Completeness belongs to the
// rational cover; these checks never accept or reject a proof box.
const assert = require('node:assert/strict');
const Census = require('./offset_leg_census.json'), Radial = require('./radial_word.json');
const rational = s => { const [a, b = '1'] = s.split('/'); return Number(a) / Number(b); };
const middle = b => (rational(b[0]) + rational(b[1])) / 2;
const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
const minus = (a, b) => a.map((x, i) => x - b[i]);
let checks = 0, pointError = 0, signError = 0, reflectionError = 0, areaError = 0;
function check(condition, message) { assert.ok(condition, message); checks++; }

function jet(t, inner, offset = 0) {
  const p = [0, 0], v = [0, 0], a = [0, 0];
  for (const [radius, k] of [[245, 1], [140, 11], [65, -inner]]) {
    const c = Math.cos(k * t), s = Math.sin(k * t);
    p[0] += radius * c; p[1] += radius * s;
    v[0] -= radius * k * s; v[1] += radius * k * c;
    a[0] -= radius * k * k * c; a[1] -= radius * k * k * s;
  }
  const speed = Math.hypot(...v), normal = [-v[1] / speed, v[0] / speed];
  const factor = 1 + offset * cross(v, a) / speed ** 3;
  return { original: p, point: p.map((x, i) => x - offset * normal[i]), normal,
    velocity: v.map(x => factor * x), factor };
}

function crossing(times, inner, offset, first, second) {
  let t = times[first], u = times[second];
  for (let step = 0; step < 8; step++) {
    const a = jet(t, inner, offset), b = jet(u, inner, offset);
    const h = minus(a.point, b.point), delta = cross(a.velocity, b.velocity);
    t -= cross(h, b.velocity) / delta;
    u -= cross(h, a.velocity) / delta;
  }
  const a = jet(t, inner, offset), b = jet(u, inner, offset);
  check(Math.hypot(...minus(a.point, b.point)) < 2e-7, 'A nearby curved crossing did not close.');
  check(Math.max(Math.abs(t - times[first]), Math.abs(u - times[second])) < .002,
    'A nearby curved crossing left its local visits.');
  return a.point;
}

for (const [endpointIndex, endpoint] of Census.endpoints.entries()) {
  const { inner, roots } = endpoint, axis = new Map();
  check(roots.length === (inner === 6 ? 138 : 132), 'The complete root count changed.');
  check(endpoint.off_axis_triples === (inner === 6 ? 94 : 96), 'The off-axis count changed.');
  check(endpoint.axis_fourfolds === (inner === 6 ? 11 : 9), 'The fourfold count changed.');
  let positive = 0, negative = 0;
  for (const [index, root] of roots.entries()) {
    const times = root.root_box.map((b, i) => root.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(b)));
    const offset = middle(root.offset), center = root.point.map(middle);
    check(times.every((t, i) => t > 0 && t < 2 * Math.PI && (i === 0 || times[i - 1] < t)), 'Visits are not in orbit order.');
    check(Number.isFinite(offset) && offset > 0, 'A circle has no positive finite radius.');
    const samples = times.map(t => jet(t, inner, offset)), normals = samples.map(s => s.normal);
    for (const s of samples) {
      const error = Math.hypot(...minus(s.point, center));
      pointError = Math.max(pointError, error);
      check(error < 2e-7, 'An independently reconstructed visit missed the circle center.');
      check(Math.abs(Math.hypot(...minus(s.original, center)) - offset) < 2e-7, 'A visit has the wrong circle radius.');
      check(s.factor > 1, 'Positive curvature failed on an outward branch.');
    }
    const determinants = [[0, 1], [1, 2], [2, 0]].map(([i, j]) => cross(normals[i], normals[j]));
    check(determinants.every(d => Math.abs(d) > 1e-7), 'A tangent pair may be parallel.');
    const H = -determinants.reduce((a, b) => a + b, 0);
    signError = Math.max(signError, Math.abs(H - middle(root.normalized_unfolding)));
    check(Math.sign(H) === root.strangeness_jump, 'An independent triple sign disagrees.');
    check(Math.abs(H - middle(root.normalized_unfolding)) < 1e-12, 'The normalized unfolding disagrees.');
    if (H > 0) positive++; else negative++;
    if (root.axis_event !== undefined) {
      if (!axis.has(root.axis_event)) axis.set(root.axis_event, []);
      axis.get(root.axis_event).push(root);
      check(Math.abs(center[1]) < 2e-7, 'An axis event has nonzero height.');
    } else {
      const partner = roots[root.reflection];
      check(partner.reflection === index && partner.strangeness_jump === root.strangeness_jump, 'Reflection pairing failed.');
      const partnerTimes = partner.root_box.map((b, i) => partner.quarters[i] * Math.PI / 2 + 2 * Math.atan(middle(b)));
      const error = Math.max(...times.map((t, i) => Math.abs(2 * Math.PI - t - partnerTimes[2 - i])));
      reflectionError = Math.max(reflectionError, error);
      check(error < 2e-13, 'Reflected orbital visits disagree.');
      check(Math.hypot(center[0] - middle(partner.point[0]), center[1] + middle(partner.point[1])) < 2e-7,
        'Reflected centers disagree.');
    }
    // Follow actual curved crossings on both sides. Three vertex areas
    // share the leading normal-only coefficient of the curved pocket.
    const K = H * H / (2 * Math.abs(determinants.reduce((a, b) => a * b, 1)));
    // Near opposing tangent directions the local validity scale shrinks
    // quadratically with their angle. Scale the control displacement too.
    const delta = .00001 * (1 + offset) * Math.min(...determinants.map(Math.abs)) ** 2;
    for (const side of [-1, 1]) {
      const vertices = [[0, 1], [1, 2], [0, 2]].map(([i, j]) =>
        crossing(times, inner, offset + side * delta, i, j));
      const area = Math.abs(cross(minus(vertices[1], vertices[0]), minus(vertices[2], vertices[0]))) / 2;
      const error = Math.abs(area / (delta * delta * K) - 1);
      areaError = Math.max(areaError, error);
      check(Number.isFinite(error) && error < .02,
        `A nearby curved triangle missed its first-order area prediction: inner=${inner}, root=${index}, M=${offset}, H=${H}, K=${K}, delta=${delta}, area=${area}, error=${error}.`);
    }
  }
  check(positive === endpoint.positive_triples && negative === endpoint.negative_triples, 'Signed totals disagree.');
  check(axis.size === endpoint.axis_fourfolds && [...axis.values()].every(rs => rs.length === 4), 'Fourfold grouping failed.');
  const radial = Radial.endpoints[endpointIndex];
  check(radial.original_strangeness + positive - negative === radial.strangeness, 'The independent radial signed balance failed.');
  if (endpoint.events) {
    const covered = endpoint.events.flatMap(e => e.roots);
    check(covered.length === roots.length && new Set(covered).size === roots.length, 'Ordered events lost or duplicated a root.');
    for (const event of endpoint.events) {
      const rs = event.roots.map(i => roots[i]);
      check(rs.filter(r => r.strangeness_jump > 0).length === event.positive_triples, 'An event positive count disagrees.');
      check(rs.filter(r => r.strangeness_jump < 0).length === event.negative_triples, 'An event negative count disagrees.');
      check(middle(event.offset) < Number(endpoint.no_higher_meeting_from), 'A circle exceeds the stated global higher-meeting tail.');
    }
  }
}
check(Census.endpoints[0].positive_triples + Radial.movie.positive_triples + Census.endpoints[1].negative_triples === 494,
  'The full-route positive count failed.');
check(Census.endpoints[0].negative_triples + Radial.movie.negative_triples + Census.endpoints[1].positive_triples === 498,
  'The full-route negative count failed.');
console.log(`${checks} independent full-circle, transverse-pair, sign, reflection, curved-crossing, area-law, and signed-balance controls passed.`);
console.log(JSON.stringify({ pointError, signError, reflectionError, areaError }));
