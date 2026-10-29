"""Complete continuous windows around the four selected reflected touches.

Run: python3 experiments/rhythm_touch_windows.py
Standard library only. Every orbit time and every weight in each stated
window is covered. This does not classify the full route. See
rhythm_tangencies.md for the distinction from the smaller event boxes.
"""

import argparse
from contextlib import redirect_stdout
from fractions import Fraction as Q
import io
from time import monotonic

from blend_cusps import Interval as I, require
from rhythm_passages import Family, RhythmBlend, contains, overlap, snapshot
from rhythm_tangencies import HINTS, certify_event, evaluate


def hull(intervals):
    return I(min(x.low for x in intervals), max(x.high for x in intervals))


class ContactWindow(Family):
    def __init__(self, index):
        self.index = index
        center = Q(str(HINTS[index][2]))
        super().__init__(center-Q(1, 100000), center+Q(1, 100000))
        self.proofs = [certify_event(index, reflected) for reflected in (False, True)]
        self.contacts = [tuple((q, s-Q(1, 1000), s+Q(1, 1000))
                               for q, s in zip(p['quarters'], p['center'][:2])) for p in self.proofs]

    def graph(self, proof, slots):
        """Exactly one tangent meeting in the complete contact product chart.

        Both branches are graphs of the same physical coordinate X. On the
        entire product chart, g_XX and g_a have fixed, nonzero signs. A common
        X interval brackets a unique critical point at every weight. Its
        critical value is strictly monotone in weight, so it can vanish once.
        The earlier small contraction box proves that it does vanish here.
        """
        axis, other = proof['axis'], 1-proof['axis']
        weight = I(self.low, self.high)
        data = []
        for q, low, high in slots:
            velocities, curvatures, motions = [], [], []
            for k in range(16):
                s = I(low+(high-low)*Q(k, 16), low+(high-low)*Q(k+1, 16))
                v = evaluate(q, s, weight, 1)
                A = evaluate(q, s, weight, 2)
                W = evaluate(q, s, weight, 0, True)
                v[axis].sign()
                slope = v[other]/v[axis]
                velocities.append(v[axis])
                curvatures.append((A[other]*v[axis]-A[axis]*v[other])/(v[axis]*v[axis]*v[axis]))
                motions.append(W[other]-slope*W[axis])
            velocity = hull(velocities)
            velocity.sign()
            data.append({'speed': min(abs(velocity.low), abs(velocity.high)),
                         'curvature': hull(curvatures), 'motion': hull(motions)})
        beta = data[0]['curvature']-data[1]['curvature']
        alpha = data[0]['motion']-data[1]['motion']
        beta_sign, alpha_sign = beta.sign(), alpha.sign()
        require(-beta_sign*alpha_sign == proof['pocket_side'], 'The uniform lens side changed.')

        center = proof['center']
        X0 = evaluate(slots[0][0], center[0], center[2])[axis].midpoint()
        half = Q(1) if self.index == 0 else Q(1, 2)
        center_slopes = []
        for slot, s0, branch in zip(slots, center[:2], data):
            q, low, high = slot
            endpoint_values = [evaluate(q, s, weight)[axis] for s in (low, high)]
            if endpoint_values[0].midpoint() > endpoint_values[1].midpoint():
                endpoint_values.reverse()
            require(endpoint_values[0].high < X0-half < X0+half < endpoint_values[1].low,
                    'The common graph interval is not bracketed for every weight.')
            origin_error = evaluate(q, s0, center[2])[axis]-X0
            # X_s = X_t * 2/(1+s^2), with the factor >= 1 on [0,1].
            # The mean value theorem therefore encloses the graph visit
            # with X=X0 for every weight in this window.
            error = (max(abs(origin_error.low), abs(origin_error.high))+130*self.radius)/branch['speed']
            require(low < s0-error < s0+error < high, 'The central graph inverse left its slot.')
            v = evaluate(q, I(s0-error, s0+error), weight, 1)
            center_slopes.append(v[other]/v[axis])
        slope = center_slopes[0]-center_slopes[1]
        curvature_floor = min(abs(beta.low), abs(beta.high))
        require(max(abs(slope.low), abs(slope.high)) < curvature_floor*half,
                'The common interval does not bracket the unique critical point.')
        require(self.low < proof['box'][2].low < proof['box'][2].high < self.high,
                'The event box is not inside the continuous weight window.')
        require(all(contains(slot, (q, x.low, x.high))
                    for slot, q, x in zip(slots, proof['quarters'], proof['box'][:2])),
                'The event box left its contact chart.')
        print('  Uniform graph curvature and separation speed have fixed signs; '
              'the unique critical value crosses zero exactly once.')
        return {'alpha': alpha, 'beta': beta, 'central_slope': slope, 'half': half}

    def charts(self):
        """Regular charts for all crossings outside the two contact charts."""
        solver = RhythmBlend(self.low)
        try:
            with redirect_stdout(io.StringIO()):
                solver.run()
                solver.refine()
            hints = []
            skipped = 0
            for A, B, _ in solver.refined:
                if any(contains(C, A) and contains(D, B) for C, D in self.contacts):
                    skipped += 1
                    continue
                x, y = [float((D[1]+D[2])/2) for D in (A, B)]
                for _ in range(12):
                    p, v = self.curve.numerical(A[0], x)
                    q, w = self.curve.numerical(B[0], y)
                    f = p-q
                    a, b, c, d = v.real, -w.real, v.imag, -w.imag
                    det = a*d-b*c
                    x -= (d*f.real-b*f.imag)/det
                    y -= (-c*f.real+a*f.imag)/det
                hints.append(((A[0], Q(round(x*10**12), 10**12)),
                              (B[0], Q(round(y*10**12), 10**12))))
        finally:
            solver.evaluate.cache_clear()
        require(skipped == (4 if self.proofs[0]['pocket_side'] < 0 else 0),
                'The low endpoint has unexpected contact-chart crossings.')
        regular = []
        for (qa, x), (qb, y) in hints:
            for denominator in (100000, 50000, 20000, 10000, 5000, 2000, 1000):
                r = Q(1, denominator)
                A, B = (qa, x-r, x+r), (qb, y-r, y+r)
                if min(A[1], B[1]) > 0 and max(A[2], B[2]) < 1 and self.contract(A, B) == 'root':
                    regular.append((A, B))
                    break
            else:
                raise ValueError('A regular crossing has no uniform root chart.')
        require(len(regular) == 36, 'Expected 36 persistent regular crossings.')
        # All individual visit slots are disjoint, including the contacts.
        # Thus no third visit can join any crossing anywhere in the window.
        slots = [D for pair in regular+self.contacts for D in pair]
        require(all(not overlap(A, B) for j, A in enumerate(slots) for B in slots[:j]),
                'A possible triple requires further analysis.')
        self.regular_charts = regular
        self.root_charts = regular+self.contacts
        return self.root_charts


def certify(index):
    family = ContactWindow(index)
    try:
        print(f'Complete contact window {index+1}: [{family.low}, {family.high}]')
        for proof, slots in zip(family.proofs, family.contacts):
            family.graph(proof, slots)
        family.charts()
        family.cover()
        ends = [snapshot(a) for a in (family.low, family.high)]
        expected = (40, 36) if family.proofs[0]['pocket_side'] < 0 else (36, 40)
        require(tuple(r['crossings'] for r in ends) == expected and
                all(r['strangeness'] == 11 for r in ends), 'A fresh window-end census changed.')
        print(f'  Exactly two reflected ordinary tangencies, no other event. '
              f'Crossings {expected[0]} -> {expected[1]}; St = 11 at both ends.')
        return {'low': family.low, 'high': family.high, 'ends': ends,
                'regular_crossings': len(family.regular_charts), 'stats': dict(family.stats)}
    finally:
        family.clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--window', type=int, choices=(1, 2, 3, 4))
    parser.add_argument('--controls', action='store_true', help='Also reject two false contact charts.')
    args = parser.parse_args()
    start = monotonic()
    if args.controls:
        family = ContactWindow(0)
        try:
            proof, slots = family.proofs[0], family.contacts[0]
            q, low, high = slots[0]
            for bad in ((slots[0], slots[0]), ((q, high, high+(high-low)), slots[1])):
                try:
                    family.graph(proof, bad)
                except ValueError:
                    pass
                else:
                    raise ValueError('A repeated branch or displaced contact chart was accepted.')
            print('Repeated-branch and displaced-contact-chart controls were rejected.')
        finally:
            family.clear()
    for index in ([args.window-1] if args.window else range(4)):
        certify(index)
    print(f'Complete continuous contact-window certificates passed in {monotonic()-start:.2f}s.')
    print('No complete full-route census is claimed by this program.')


if __name__ == '__main__':
    main()
