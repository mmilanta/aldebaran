"""Two reflected pairs of triple passages in the 11/6 -> 11/8 blend.

Run: python3 experiments/rhythm_passages.py
Only the standard library is used. Exact rational covers prove complete
event counts on two short weight windows, not on the whole route.
See rhythm_passages.md. The original intersection solver is unchanged.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from fractions import Fraction as Q
from functools import lru_cache
import io
from math import cos, inf, lcm, nextafter, pi, sin, tan
from time import monotonic

from blend_cusps import Interval as I, require
from certify_intersections import IntersectionCertificate
from phase_unfolding import inverse
from strangeness import HERE, audit_word, certified_word, from_faces
from triple_passage import DetourCurve


WINDOWS = ((Q(471, 10000), Q(472, 10000)),
           (Q(755, 10000), Q(756, 10000)))
# Numerical hints only. Contraction tests, not these digits, decide acceptance.
HINTS = ((.80257128573195, 1.29085195523226, 1.73080732399980, .04712004456938),
         (.14158372717885, .55725741465979, 1.09228544426946, .07551167638036))
POSITION_CHANGE = 130
VELOCITY_CHANGE = 910


class RhythmBlend(IntersectionCertificate):
    """Reuse rational Fourier evaluation and the frozen crossing solver."""

    evaluate = DetourCurve.evaluate
    numerical = DetourCurve.numerical

    def __init__(self, weight, partition=1024):
        require(type(weight) in (int, Q) and 0 <= weight <= 1,
                'Use an exact weight in [0,1].')
        super().__init__(11, 6, partition)
        self.weight = Q(weight)
        a = self.weight
        self.terms = [(k, Q(r)) for k, r in
                      ((1, 245), (11, 140), (-6, 65*(1-a)), (-8, 65*a)) if r]
        self.M = sum(abs(r)*k*k for k, r in self.terms)
        self.V = sum(abs(r*k) for k, r in self.terms)
        self.L2 = 4*self.M+2*self.V
        self.degree = 11
        self.common = lcm(*(r.denominator for k, r in self.terms))
        self.integer_terms = [(k, int(r*self.common)) for k, r in self.terms]


def orbit(t, weight, order=0):
    """Floating-point geometry for figures and Newton hints only."""
    return sum(r*(1j*k)**order*complex(cos(k*t), sin(k*t)) for k, r in
               ((1, 245), (11, 140), (-6, 65*(1-weight)), (-8, 65*weight)))


def snapshot(weight, partition=1024, charts=None):
    """Fresh smooth census, exact word, two invariant formulations."""
    solver = RhythmBlend(weight, partition)
    try:
        with redirect_stdout(io.StringIO()):
            solver.run()
            solver.refine()
        word, times, points = certified_word(solver)
        faces = from_faces(word, 2*(len(word)-1)+1)
        result = audit_word(word, 1, faces)
        require(faces.tangent_index == 11, 'The regular blend changed tangent index.')
        record = {'weight': str(weight), 'crossings': len(word)//2,
                  'strangeness': result.value, 'winding_regions': faces.face_counts,
                  'tangent_index': faces.tangent_index, 'initial_index2': 1,
                  'word': word, 'display_times': times, 'display_points': points}
        if charts is not None:
            occurrences = sorted((D, old) for old, (A, B, _) in enumerate(solver.refined) for D in (A, B))
            names = {}
            for _, old in occurrences:
                names.setdefault(old, len(names))
            contributions = []
            for C, D in charts:
                matches = [names[old] for old, (A, B, _) in enumerate(solver.refined)
                           if contains(C, A) and contains(D, B)]
                require(len(matches) == 1, 'A fresh endpoint crossing left its uniform chart.')
                label, = matches
                contributions.append(result.weights[label]*result.indices[label])
            record['chart_contributions'] = contributions
        return record
    finally:
        solver.evaluate.cache_clear()


def check_evaluation():
    ends = [RhythmBlend(a) for a in (0, 1)]
    originals = [IntersectionCertificate(11, n, 1) for n in (6, 8)]
    comparisons = 0
    for quarter in range(4):
        for s in (Q(0), Q(1, 7), Q(2, 3), Q(1)):
            for end, original in zip(ends, originals):
                require(end.evaluate(quarter, s) == original.evaluate(quarter, s),
                        'An endpoint differs from the frozen rational evaluator.')
                comparisons += 7
            for a in (Q(1, 3), Q(1, 2), *[v for w in WINDOWS for v in w]):
                blend = RhythmBlend(a)
                p, v, raw = blend.evaluate(quarter, s)
                A, B = [end.evaluate(quarter, s) for end in ends]
                for row, actual in ((0, p), (1, v)):
                    require(actual == tuple((1-a)*x+a*y for x, y in zip(A[row], B[row])),
                            'An affine evaluator comparison failed.')
                require(tuple(Q(x, raw[2]) for x in raw[:2]) ==
                        tuple((1-a)*Q(x, A[2][2])+a*Q(y, B[2][2])
                              for x, y in zip(A[2][:2], B[2][:2])),
                        'An affine raw-velocity comparison failed.')
                comparisons += 6
    # The frequency-11 term dominates every other term throughout the route.
    require(140*11-245-65*8 == 775, 'The global speed bound changed.')
    RhythmBlend.evaluate.cache_clear()
    IntersectionCertificate.evaluate.cache_clear()
    print(f'{comparisons} exact evaluator component comparisons; speed >= 775 everywhere.')


class Family:
    """Rational uniform crossing charts for one complete weight interval."""

    def __init__(self, low, high, partition=1024):
        require(type(low) in (int, Q) and type(high) in (int, Q) and 0 <= low < high <= 1,
                'Use exact increasing window endpoints in [0,1].')
        self.low, self.high = low, high
        self.middle, self.radius = (low+high)/2, (high-low)/2
        self.curve = RhythmBlend(self.middle, partition)
        self.ends = [RhythmBlend(a, partition) for a in (0, 1)]
        self.M = 245+140*121+65*(1-low)*36+65*high*64
        self.V = 245+140*11+65*(1-low)*6+65*high*8
        self.L2 = 4*self.M+2*self.V
        self.stats = Counter()

    @lru_cache(maxsize=16384)
    def weight_derivative(self, quarter, s):
        first, last = [end.evaluate(quarter, s) for end in self.ends]
        return tuple(y-x for x, y in zip(first[0], last[0]))

    def contract(self, A, B):
        """Parametric contraction / exclusion on a closed pair of time arcs.

        The preconditioner is fixed at their midpoints and the middle weight.
        Affinity gives the EXACT weight derivative of F there. All s-derivative
        changes have bound L2*r_s + 2*910*r_a, since dt/ds <= 2.
        """
        mids = [(D[1]+D[2])/2 for D in (A, B)]
        radii = [(D[2]-D[1])/2 for D in (A, B)]
        p, va, _ = self.curve.evaluate(A[0], mids[0])
        q, vb, _ = self.curve.evaluate(B[0], mids[1])
        det = va[1]*vb[0]-va[0]*vb[1]
        if not det:
            return 'unknown'
        C = ((-vb[1]/det, vb[0]/det), (-va[1]/det, va[0]/det))
        f = [x-y for x, y in zip(p, q)]
        da, db = [self.weight_derivative(D[0], m) for D, m in zip((A, B), mids)]
        fa = [x-y for x, y in zip(da, db)]
        column_errors = [self.L2*r+2*VELOCITY_CHANGE*self.radius for r in radii]
        centers, errors, norms = [], [], []
        for row in C:
            size = sum(abs(x) for x in row)
            centers.append(-sum(x*y for x, y in zip(row, f)))
            errors.append(abs(sum(x*y for x, y in zip(row, fa)))*self.radius
                          + size*sum(e*r for e, r in zip(column_errors, radii)))
            norms.append(size*sum(column_errors))
        if any(abs(c) > r+e for c, r, e in zip(centers, radii, errors)):
            return 'empty'
        if all(abs(c)+e < r and n < 1 for c, e, r, n in zip(centers, errors, radii, norms)):
            return 'root'
        return 'unknown'

    def charts(self):
        # A nearby generic weight avoids using rounded event geometry as data.
        solver = RhythmBlend(self.low)
        try:
            with redirect_stdout(io.StringIO()):
                solver.run()
                solver.refine()
            hints = []
            for A, B, _ in solver.refined:
                x, y = [float((D[1]+D[2])/2) for D in (A, B)]
                for _ in range(12):
                    p, v = self.curve.numerical(A[0], x)
                    q, w = self.curve.numerical(B[0], y)
                    f = p-q
                    a, b, c, d = v.real, -w.real, v.imag, -w.imag
                    determinant = a*d-b*c
                    x -= (d*f.real-b*f.imag)/determinant
                    y -= (-c*f.real+a*f.imag)/determinant
                hints.append(((A[0], Q(round(x*10**12), 10**12)),
                              (B[0], Q(round(y*10**12), 10**12))))
        finally:
            solver.evaluate.cache_clear()
        charts = []
        for (qa, x), (qb, y) in hints:
            for denominator in (100000, 50000, 20000, 10000, 5000, 2000, 1000):
                radius = Q(1, denominator)
                A, B = (qa, x-radius, x+radius), (qb, y-radius, y+radius)
                if min(A[1], B[1]) > 0 and max(A[2], B[2]) < 1 and self.contract(A, B) == 'root':
                    charts.append((A, B))
                    break
            else:
                raise ValueError('A crossing failed its uniform root-chart test.')
        require(all(not (overlap(A, C) and overlap(B, D))
                    for j, (A, B) in enumerate(charts) for C, D in charts[:j]),
                'Uniform crossing charts overlap in the product domain.')
        require(all(A < B and not overlap(A, B) for A, B in charts),
                'A crossing chart meets the parameter diagonal or reverses its visits.')
        self.root_charts = charts
        return charts

    def bounds(self, D):
        box = self.curve.bounds(D)
        error = POSITION_CHANGE*self.radius
        return box[0]-error, box[1]+error, box[2]-error, box[3]+error

    def exclude(self, A, B, depth=0):
        if any(contains(C, A) and contains(D, B) for C, D in self.root_charts):
            self.stats['inside_root_chart'] += 1
            return
        a, b = self.bounds(A), self.bounds(B)
        if a[1] < b[0] or b[1] < a[0] or a[3] < b[2] or b[3] < a[2]:
            self.stats['spatial_exclusion'] += 1
            return
        if self.contract(A, B) == 'empty':
            self.stats['contraction_exclusion'] += 1
            return
        require(depth < 24, 'A uniform crossing exclusion needs more refinement.')
        if A[2]-A[1] < B[2]-B[1]:
            A, B = B, A
        q, low, high = A
        mid = (low+high)/2
        # Keep parameter order, including after choosing the longer side.
        for half in ((q, low, mid), (q, mid, high)):
            first, second = sorted((half, B))
            self.exclude(first, second, depth+1)

    def cover(self):
        """Every crossing at EVERY weight lies in a unique regular chart."""
        K, grid, buckets = self.curve.K, [], defaultdict(list)
        N = 4*K
        for i in range(N):
            quarter, k = divmod(i, K)
            D = quarter, Q(k, K), Q(k+1, K)
            vx, vy, denominator = self.curve.evaluate(quarter, D[1])[2]
            single_error = 2*self.M/K+VELOCITY_CHANGE*self.radius
            require(Q(vx*vx+vy*vy, denominator*denominator) > single_error*single_error,
                    'A single arc lacks uniform injectivity.')
            raw = self.bounds(D)
            box = tuple(nextafter(float(v), -inf if j % 2 == 0 else inf) for j, v in enumerate(raw))
            require(all(Q(v) <= r if j % 2 == 0 else Q(v) >= r for j, (v, r) in enumerate(zip(box, raw))),
                    'An outward binary filter failed its rational enclosure check.')
            grid.append((D, box))
            visited = set()
            for x in range(raw[0]//8, raw[1]//8+1):
                for y in range(raw[2]//8, raw[3]//8+1):
                    for j in buckets[x, y]:
                        if j in visited:
                            continue
                        visited.add(j)
                        other = grid[j][1]
                        if box[1] < other[0] or other[1] < box[0] or box[3] < other[2] or other[3] < box[2]:
                            continue
                        difference = min(i-j, N-(i-j))
                        first = j if i-j <= N//2 else i
                        q, s, _ = grid[first][0]
                        vx, vy, denominator = self.curve.evaluate(q, s)[2]
                        error = 2*self.M*(difference+1)/K+VELOCITY_CHANGE*self.radius
                        if Q(vx*vx+vy*vy, denominator*denominator) > error*error:
                            self.stats['monotone_exclusion'] += 1
                            continue
                        require(difference > 1, 'Adjacent arcs lack uniform injectivity.')
                        self.exclude(grid[j][0], D)
                    buckets[x, y].append(i)
        print(f'  {N} arcs cover the complete orbit: {dict(self.stats)}')

    def triple(self, hint, reflected=False):
        """A four-dimensional rational contraction for three equal positions."""
        *times, weight = hint
        if reflected:
            times = [2*pi-t for t in reversed(times)]
        parameters = []
        for t in times:
            quarter = int(t/(pi/2))
            parameters.append((quarter, Q(str(tan((t-quarter*pi/2)/2)))))
        center = [s for q, s in parameters]+[Q(str(weight))]
        # The larger box contains all possible coincident root visits in
        # this window. A second small box gives the printed event enclosure.
        proofs = []
        for time_radius, weight_radius in ((Q(1, 5000), Q(1, 5000)),
                                           (Q(1, 10**9), Q(1, 10**9))):
            radii = [time_radius]*3+[weight_radius]
            proof = self.triple_box(parameters, center, radii)
            proofs.append(proof)
        return {'parameters': parameters, 'center': center, 'large': proofs[0],
                'small': proofs[1], 'reflected': reflected}

    def triple_box(self, parameters, center, radii):
        curve = RhythmBlend(center[3])
        require(0 < center[3]-radii[3] < center[3]+radii[3] < 1,
                'The triple weight box leaves the blend interval.')
        global_L2 = 4*(245+140*121+65*64)+2*(245+140*11+65*8)
        points, velocities, derivatives = [], [], []
        for (quarter, s), radius in zip(parameters, radii):
            p, v, _ = curve.evaluate(quarter, s)
            require(0 < s-radius < s+radius < 1, 'A triple slot leaves its circle quarter.')
            error = global_L2*radius+2*VELOCITY_CHANGE*radii[3]
            velocities.append([I(x-error, x+error) for x in v])
            derivatives.append([I(x-2*VELOCITY_CHANGE*radius, x+2*VELOCITY_CHANGE*radius)
                                for x in self.weight_derivative(quarter, s)])
            points.append(p)
        F = [points[0][axis]-points[j][axis] for j in (1, 2) for axis in (0, 1)]
        J = []
        for j in (1, 2):
            for axis in (0, 1):
                row = [I.wrap(0) for _ in range(4)]
                row[0], row[j] = velocities[0][axis], -velocities[j][axis]
                row[3] = derivatives[0][axis]-derivatives[j][axis]
                J.append(row)
        R = inverse([[x.midpoint() for x in row] for row in J])
        defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
        # Scale by the box radii, so the norm is in a unit cube.
        norm = max(sum(max(abs(x.low), abs(x.high))*radii[j]/radii[i]
                       for j, x in enumerate(row)) for i, row in enumerate(defect))
        require(norm < 1, f'The triple box is not a contraction: {float(norm):.6g}.')
        offsets = [-sum(R[i][k]*F[k] for k in range(4))+
                   sum(defect[i][j]*I(-radii[j], radii[j]) for j in range(4)) for i in range(4)]
        require(all(-r < x.low <= x.high < r for x, r in zip(offsets, radii)),
                'The triple box does not map into its interior.')
        signs = []
        for i, j in ((0, 1), (0, 2), (1, 2)):
            determinant = velocities[i][0]*velocities[j][1]-velocities[i][1]*velocities[j][0]
            signs.append(determinant.sign())
        return {'box': [I(x-r, x+r) for x, r in zip(center, radii)],
                'norm': norm, 'determinant_signs': signs}

    def possible_triples(self, proofs):
        """Only the two selected triple groups have overlapping visit slots."""
        visits = [(D, crossing) for crossing, pair in enumerate(self.root_charts) for D in pair]
        overlaps = defaultdict(set)
        for j, (A, crossing) in enumerate(visits):
            for B, other in visits[:j]:
                if overlap(A, B):
                    require(crossing != other, 'A crossing chart meets the parameter diagonal.')
                    overlaps[crossing].add(other)
                    overlaps[other].add(crossing)
        groups, seen = [], set()
        for first in overlaps:
            if first in seen:
                continue
            group, pending = set(), [first]
            while pending:
                c = pending.pop()
                if c not in group:
                    group.add(c)
                    pending.extend(overlaps[c]-group)
            seen.update(group)
            require(len(group) == 3 and all(len(overlaps[c]) == 2 for c in group),
                    'An extra potential multiple-visit group needs analysis.')
            groups.append(group)
        require(len(groups) == 2, 'Expected exactly two reflected potential triple groups.')
        for proof in proofs:
            box = proof['large']['box']
            slots = [(q, X.low, X.high) for (q, _), X in zip(proof['parameters'], box[:3])]
            matching = []
            for group in groups:
                pairs = []
                for c in group:
                    pair = []
                    for D in self.root_charts[c]:
                        indices = [i for i, S in enumerate(slots) if contains(S, D)]
                        require(len(indices) <= 1, 'Triple time slots overlap.')
                        if indices:
                            pair.append(indices[0])
                    pairs.append(tuple(pair))
                if sorted(pairs) == [(0, 1), (0, 2), (1, 2)]:
                    matching.append(group)
            require(len(matching) == 1, 'A proposed triple does not cover exactly one potential group.')
            require(box[3].low < self.low < self.high < box[3].high,
                    'The unique-triple box does not contain the full weight window.')
            small = proof['small']['box'][3]
            require(self.low < small.low < small.high < self.high,
                    'The triple event is not strictly inside the window.')
            proof['crossing_group'] = matching[0]
        require(proofs[0]['crossing_group'].isdisjoint(proofs[1]['crossing_group']),
                'The reflected triple groups are not disjoint.')
        print('  Only two groups can have three visits; each contains exactly one ordinary triple event.')

    def clear(self):
        self.curve.evaluate.cache_clear()
        self.weight_derivative.cache_clear()


def overlap(A, B):
    return A[0] == B[0] and max(A[1], B[1]) <= min(A[2], B[2])


def contains(A, B):
    return A[0] == B[0] and A[1] < B[1] <= B[2] < A[2]


def certify_window(index):
    low, high = WINDOWS[index]
    family = Family(low, high)
    try:
        print(f'Window [{low}, {high}]:')
        family.charts()
        family.cover()
        proofs = [family.triple(HINTS[index], reflected) for reflected in (False, True)]
        family.possible_triples(proofs)
        ends = [snapshot(a, charts=family.root_charts) for a in (low, high)]
        expected = (15, 13) if index == 0 else (13, 11)
        require(tuple(r['strangeness'] for r in ends) == expected and
                all(r['crossings'] == 40 for r in ends), 'The endpoint invariant audit changed.')
        require(len(family.root_charts) == 40, 'The family does not retain exactly 40 pairwise crossings.')
        changes = [b-a for a, b in zip(ends[0]['chart_contributions'], ends[1]['chart_contributions'])]
        for proof in proofs:
            require(sum(changes[c] for c in proof['crossing_group']) == -1,
                    'A selected triple group does not contribute jump -1.')
        selected = proofs[0]['crossing_group'] | proofs[1]['crossing_group']
        require(all(change == 0 for c, change in enumerate(changes) if c not in selected),
                'An unselected crossing contribution changed.')
        print(f'  Fresh endpoint smooth proofs: St {expected[0]} -> {expected[1]}, 40 crossings at both.')
        print('  The three crossings in each group contribute jump -1; all other contributions stay fixed.')
        return proofs, ends
    finally:
        family.clear()


def check_controls():
    """Invalid weights, a diagonal chart, and false event boxes must fail."""
    for call in (lambda: RhythmBlend(Q(-1, 100)), lambda: RhythmBlend(.5),
                 lambda: RhythmBlend(2), lambda: Family(Q(1, 2), Q(1, 3)),
                 lambda: Family(Q(-1, 10), Q(1, 10))):
        try:
            call()
        except ValueError:
            pass
        else:
            raise ValueError('An invalid-input negative control was accepted.')
    family = Family(*WINDOWS[0])
    try:
        D = 0, Q(1, 4), Q(1, 3)
        require(family.contract(D, D) == 'unknown', 'The parameter diagonal received a root chart.')
        proof = family.triple(HINTS[0])
        center = list(proof['center'])
        center[3] += Q(1, 10**6)
        for parameters, candidate in ((proof['parameters'], center),
                                      ([proof['parameters'][0]]*3, proof['center'])):
            try:
                family.triple_box(parameters, candidate, [Q(1, 10**9)]*4)
            except ValueError:
                pass
            else:
                raise ValueError('A false-event negative control was accepted.')
    finally:
        family.clear()
    print('Invalid inputs, a diagonal chart, a shifted event, and coincident visits were rejected.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--window', type=int, choices=(1, 2), help='Certify just one of the two windows.')
    args = parser.parse_args()
    start = monotonic()
    check_evaluation()
    check_controls()
    for index in ([args.window-1] if args.window else range(2)):
        certify_window(index)
    print(f'Complete continuous-window certificates passed in {monotonic()-start:.2f}s.')
    print('No full-route event census is claimed.')


if __name__ == '__main__':
    main()
