"""Rational crossing charts for the seven- and fourteenfold phase turns.

fold_movie_census.py uses these charts for its complete event census.
No sampled crossing count is a certificate. The companion contact
elimination supplies the exhaustive pair count; strict contractions
account for it throughout closed phase intervals. See fold_movie.md.
"""

from collections import Counter
from contextlib import redirect_stdout
from fractions import Fraction as Q
from functools import lru_cache
from itertools import permutations
from io import StringIO
from math import atan, atan2, cos, lcm, pi, sin, tan
from time import process_time

from blend_cusps import Interval as I, require
from certify_intersections import IntersectionCertificate
from fold_contacts import HINTS as CONTACT_HINTS, circle, round_interval
from phase_unfolding import inverse


class PhaseCurve(IntersectionCertificate):
    """An exact phase on its circle, with an optional rational chart seam."""

    def __init__(self, d, phase_quarter, phase, shift=Q(0), partition=1024):
        require(type(d) is int and d in (7, 14), 'Use seven or fourteen folds.')
        require(type(phase) in (int, Q) and 0 <= phase <= 1,
                'Use an exact phase-chart parameter in [0,1].')
        require(type(phase_quarter) is int and phase_quarter in (0, 1, 2),
                'Use a phase quarter on the closed half-turn.')
        require(phase_quarter < 2 or phase == 0, 'Phase exceeds a half-turn.')
        require(type(shift) is Q and 0 <= shift < 1, 'Use an exact seam shift in [0,1).')
        super().__init__(d+1, d-1, partition)
        self.d, self.phase_quarter, self.phase, self.shift = d, phase_quarter, Q(phase), shift
        u, v = (x.low for x in circle(phase_quarter, Q(phase)))
        self.terms = [(1, Q(245), Q(0)), (d+1, Q(140), Q(0)), (1-d, 65*u, 65*v)]
        self.common = lcm(*(x.denominator for _, a, b in self.terms for x in (a, b)))
        self.integer_terms = [(k, int(a*self.common), int(b*self.common)) for k, a, b in self.terms]
        self.degree = d+1

    @lru_cache(maxsize=16384)
    def evaluate(self, quarter, s):
        require(type(quarter) is int and 0 <= quarter < 4 and type(s) is Q,
                'Use an exact orbit chart.')
        a, b = s.numerator, s.denominator
        x, y, D = b*b-a*a, 2*a*b, b*b+a*a
        for _ in range(quarter):
            x, y = -y, x
        a, b = self.shift.numerator, self.shift.denominator
        x, y, D = x*(b*b-a*a)-y*2*a*b, y*(b*b-a*a)+x*2*a*b, D*(b*b+a*a)
        powers, denominators = [(1, 0)], [1]
        for _ in range(self.degree):
            u, v = powers[-1]
            powers.append((u*x-v*y, u*y+v*x))
            denominators.append(denominators[-1]*D)
        px = py = vx = vy = 0
        for k, real, imag in self.integer_terms:
            u, v = powers[abs(k)]
            if k < 0:
                v = -v
            scale = denominators[self.degree-abs(k)]
            xx, yy = scale*(real*u-imag*v), scale*(real*v+imag*u)
            px, py, vx, vy = px+xx, py+yy, vx+k*xx, vy+k*yy
        den = self.common*denominators[-1]
        factor = 2/(1+s*s)
        return ((Q(px, den), Q(py, den)),
                (-Q(vy, den)*factor, Q(vx, den)*factor), (vx, vy, den))

    def numerical(self, quarter, s):
        shift = float(self.shift)
        w = (1j**quarter)*complex(1-s*s, 2*s)/(1+s*s)
        w *= complex(1-shift*shift, 2*shift)/(1+shift*shift)
        z = sum(complex(float(a), float(b))*w**k for k, a, b in self.terms)
        v = sum(1j*k*complex(float(a), float(b))*w**k for k, a, b in self.terms)*2/(1+s*s)
        return z, v

    @lru_cache(maxsize=16384)
    def phase_motion(self, quarter, s):
        # Isolate the backward term from the full Fourier sum.
        p = self.evaluate(quarter, s)[0]
        a = self.shift
        w = ((1-s*s)/(1+s*s), 2*s/(1+s*s))
        for _ in range(quarter):
            w = -w[1], w[0]
        u, v = (1-a*a)/(1+a*a), 2*a/(1+a*a)
        w = w[0]*u-w[1]*v, w[0]*v+w[1]*u
        power = w
        for _ in range(self.d):
            power = power[0]*w[0]-power[1]*w[1], power[0]*w[1]+power[1]*w[0]
        back = tuple(p[j]-245*w[j]-140*power[j] for j in range(2))
        factor = 2/(1+self.phase*self.phase)
        return -back[1]*factor, back[0]*factor

    def clear(self):
        self.evaluate.cache_clear()
        self.phase_motion.cache_clear()


@lru_cache(maxsize=4)
def endpoint_cuts(d, steps):
    """Suggestions separating roots that coalesce at a phase endpoint.

    At phi=pi the residual factors as (Q-P)^2 ((Q+P)^2-49^2),
    and at phi=0 as (Q+P)^2 ((Q-P)^2-49^2). Include zeros of P-Q
    and P+Q so a fixed scan cannot step over a narrow pair of roots.
    These floating-point cuts carry no proof status.
    """
    cuts = [pi/2*j/steps for j in range(1, steps+1)]
    for sign in (-1, 1):
        def f(b):
            return 28*sin((d+1)*b)+sign*13*sin((d-1)*b)

        previous, fp = 1e-12, f(1e-12)
        for b in cuts[:steps]:
            fb = f(b)
            if fp*fb < 0:
                a, z, fa = previous, b, fp
                for _ in range(48):
                    m = (a+z)/2
                    fm = f(m)
                    if fa*fm < 0:
                        z = m
                    else:
                        a, fa = m, fm
                cuts.append((a+z)/2)
            previous, fp = b, fb
    return sorted(cuts+[abs(t-u)/2 for t, u, _ in CONTACT_HINTS[d]])


def pair_hints(d, phase_quarter, phase, shift=Q(0), steps=2048):
    """Numerical suggestions from the complete pair elimination, never proof."""
    phi = phase_quarter*pi/2+2*atan(float(phase))
    c, s = [float(x.low) for x in circle(phase_quarter, Q(phase))]
    # Preserve 1+cos(phi) near pi and 1-cos(phi) near zero, where a
    # subtraction would lose the small residual that splits double roots.
    endpoint_distance = s*s/(1-c if c < 0 else 1+c)
    require(0 < phi < pi, 'Interior hint search only.')

    def triangle(b):
        return 28*sin((d+1)*b)/sin(b), 13*sin((d-1)*b)/sin(b)

    def residual(b):
        P, Qb = triangle(b)
        if c < 0:
            return (Qb-P)**2*((Qb+P)**2-2401)-4802*P*Qb*endpoint_distance
        return (Qb+P)**2*((Qb-P)**2-2401)+4802*P*Qb*endpoint_distance

    cuts = endpoint_cuts(d, steps)
    # The excluded diagonal has a strictly positive analytic speed bound.
    previous, fprevious = 1e-12, residual(1e-12)
    roots = []
    for b in cuts:
        f = residual(b)
        if f*fprevious < 0:
            lo, hi, flo = previous, b, fprevious
            for _ in range(48):
                mid = (lo+hi)/2
                fm = residual(mid)
                if fm*flo < 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            roots.append((lo+hi)/2)
        previous, fprevious = b, f
    hints = []
    seam = 2*atan(float(shift))
    for b in roots:
        P, Qb = triangle(b)
        ca = (Qb*Qb-2401-P*P)/(98*P)
        sa = 49*Qb*s/(Qb*Qb-P*P)
        a = atan2(sa, ca)/d
        for k in range(d):
            times = sorted(((a+2*pi*k/d+offset-seam) % (2*pi) for offset in (-b, b)))
            chart = []
            for t in times:
                q = min(3, int(t/(pi/2)))
                chart.append((q, Q(round(tan((t-q*pi/2)/2)*10**12), 10**12)))
            hints.append(tuple(chart))
    return hints


class PhaseSlab:
    """Account for every pair on one phase slab by strict contractions."""

    def __init__(self, d, phase_quarter, low, high, shift=Q(0), budget=None):
        require(type(low) is Q and type(high) is Q and 0 <= low < high <= 1,
                'Use a nonempty exact phase slab in one quarter.')
        require(phase_quarter in (0, 1), 'Use a half-turn phase quarter.')
        self.d, self.phase_quarter, self.low, self.high, self.shift = d, phase_quarter, low, high, shift
        self.middle, self.radius = (low+high)/2, (high-low)/2
        self.curve = PhaseCurve(d, phase_quarter, self.middle, shift)
        self.L2 = self.curve.L2
        self.mixed = 260*(d-1)
        self.stats = Counter()
        self.started, self.budget = process_time(), budget

    def check_work(self):
        require(self.budget is None or process_time()-self.started < self.budget,
                'The proposed slab exceeded its discovery work limit.')

    def contract(self, A, B):
        mids = [(D[1]+D[2])/2 for D in (A, B)]
        radii = [(D[2]-D[1])/2 for D in (A, B)]
        p, va, _ = self.curve.evaluate(A[0], mids[0])
        q, vb, _ = self.curve.evaluate(B[0], mids[1])
        det = va[1]*vb[0]-va[0]*vb[1]
        if not det:
            return 'unknown'
        R = ((-vb[1]/det, vb[0]/det), (-va[1]/det, va[0]/det))
        F = [x-y for x, y in zip(p, q)]
        da, db = [self.curve.phase_motion(D[0], m) for D, m in zip((A, B), mids)]
        Fp = [x-y for x, y in zip(da, db)]
        column_errors = [self.L2*r+self.mixed*self.radius for r in radii]
        centers, errors, norms = [], [], []
        for row in R:
            size = sum(abs(x) for x in row)
            centers.append(-sum(x*y for x, y in zip(row, F)))
            # |z_pp| <= 390; the difference's Taylor remainder is <= 390 rp^2.
            errors.append(abs(sum(x*y for x, y in zip(row, Fp)))*self.radius
                          + size*(sum(e*r for e, r in zip(column_errors, radii))
                                  + 390*self.radius*self.radius))
            norms.append(size*sum(column_errors))
        if any(abs(c) > r+e for c, r, e in zip(centers, radii, errors)):
            return 'empty'
        if all(abs(c)+e < r and n < 1 for c, e, r, n in zip(centers, errors, radii, norms)):
            return 'root'
        return 'unknown'

    def charts(self, expected, hints=None):
        charts = []
        hints = pair_hints(self.d, self.phase_quarter, self.middle, self.shift) if hints is None else hints
        if len(hints) != expected:
            # Close to an endpoint, two elimination roots can share a scan
            # interval even though their actual pair charts stay regular.
            # The frozen solver supplies suggestions by a different route.
            solver = PhaseCurve(self.d, self.phase_quarter, self.middle, self.shift)
            try:
                with redirect_stdout(StringIO()):
                    solver.run()
                    solver.refine()
                hints = [((A[0], (A[1]+A[2])/2), (B[0], (B[1]+B[2])/2))
                         for A, B, _ in solver.refined]
            finally:
                solver.clear()
        for (qa, x), (qb, y) in hints:
            self.check_work()
            # Newton digits and chosen radii only suggest boxes. The strict
            # rational contraction decides every accepted product chart.
            u, v = float(x), float(y)
            for _ in range(5):
                p, a = self.curve.numerical(qa, u)
                q, b = self.curve.numerical(qb, v)
                f = p-q
                aa, bb, cc, dd = a.real, -b.real, a.imag, -b.imag
                det = aa*dd-bb*cc
                u -= (dd*f.real-bb*f.imag)/det
                v -= (-cc*f.real+aa*f.imag)/det
            x, y = (Q(round(t*10**12), 10**12) for t in (u, v))
            for denominator in (10**8, 5*10**7, 2*10**7, 10**7, 5*10**6, 2*10**6,
                                10**6, 5*10**5, 2*10**5, 10**5, 5*10**4, 2*10**4,
                                10**4, 5000, 2000, 1000, 500, 200, 100):
                r = Q(1, denominator)
                A, B = (qa, x-r, x+r), (qb, y-r, y+r)
                if min(A[1], B[1]) > 0 and max(A[2], B[2]) < 1 and self.contract(A, B) == 'root':
                    charts.append((A, B))
                    break
            else:
                raise ValueError('No uniform crossing chart.')
        require(len(charts) == expected, 'Charts do not account for the exhaustive algebraic pair count.')
        require(all(A < B and not overlap(A, B) for A, B in charts), 'A crossing chart meets its diagonal.')
        require(all(not (overlap(A, C) and overlap(B, D))
                    for j, (A, B) in enumerate(charts) for C, D in charts[:j]), 'Pair product charts overlap.')
        self.root_charts = charts
        return charts

    def clear(self):
        self.curve.clear()

    def triple_image(self, slots, phase):
        """Mean-value Newton enclosure for three visits and nonlinear phase.

        All entries are rational. Each point derivative is widened using
        global analytic second-derivative bounds on the whole input box.
        """
        require(len(slots) == 3 and 0 <= phase.low < phase.high <= 1
                and all(0 <= D[1] <= D[2] <= 1 for D in slots),
                'A triple candidate leaves its time or phase quarters.')
        mids = [(D[1]+D[2])/2 for D in slots]+[phase.midpoint()]
        radii = [(D[2]-D[1])/2 for D in slots]+[(phase.high-phase.low)/2]
        curve = PhaseCurve(self.d, self.phase_quarter, mids[3], self.shift)
        try:
            points, velocities, motions = [], [], []
            for D, m, r in zip(slots, mids, radii):
                p, v, _ = curve.evaluate(D[0], m)
                error = self.L2*r+self.mixed*radii[3]
                velocities.append([I(x-error, x+error) for x in v])
                error = self.mixed*r+390*radii[3]
                motions.append([I(x-error, x+error) for x in curve.phase_motion(D[0], m)])
                points.append(p)
            F = [points[0][axis]-points[j][axis] for j in (1, 2) for axis in (0, 1)]
            J = []
            for j in (1, 2):
                for axis in (0, 1):
                    row = [I.wrap(0)]*4
                    row[0] = velocities[0][axis]
                    row[j] = -velocities[j][axis]
                    row[3] = motions[0][axis]-motions[j][axis]
                    J.append(row)
            R = inverse([[x.midpoint() for x in row] for row in J])
            defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(4))
                       for j in range(4)] for i in range(4)]
            offsets = [-sum(R[i][k]*F[k] for k in range(4))
                       + sum(defect[i][j]*I(-radii[j], radii[j]) for j in range(4)) for i in range(4)]
            empty = any(x.low > r or x.high < -r for x, r in zip(offsets, radii))
            norm = max(sum(max(abs(x.low), abs(x.high))*radii[j] for j, x in enumerate(row))/radii[i]
                       for i, row in enumerate(defect)) if all(radii) else None
            root = norm is not None and norm < 1 and all(-r < x.low <= x.high < r for x, r in zip(offsets, radii))
            image = [round_interval(I(m+x.low, m+x.high), 30) for m, x in zip(mids, offsets)]
            if root:
                require(all(m-r < x.low <= x.high < m+r for m, r, x in zip(mids, radii, image)),
                        'Outward rounding left a strict triple-root cube.')
            return 'empty' if empty else 'root' if root else 'unknown', image, norm
        finally:
            curve.clear()

    def triple_empty(self, slots, phase, depth=0):
        self.check_work()
        status, image, _ = self.triple_image(slots, phase)
        if status == 'empty':
            self.stats['triple_exclusion'] += 1
            return
        require(depth < 12, 'An unresolved triple candidate remains.')
        radii = [(D[2]-D[1])/2 for D in slots]+[(phase.high-phase.low)/2]
        k = max(range(4), key=lambda j: radii[j])
        if k == 3:
            m = phase.midpoint()
            for half in (I(phase.low, m), I(m, phase.high)):
                self.triple_empty(slots, half, depth+1)
        else:
            q, low, high = slots[k]
            m = (low+high)/2
            for half in ((q, low, m), (q, m, high)):
                new = list(slots)
                new[k] = half
                self.triple_empty(new, phase, depth+1)

    def triple_candidates(self):
        """Every triple uses three distinct pair charts with shared slots."""
        charts = self.root_charts
        adj = {j: set() for j in range(len(charts))}
        for j, pair in enumerate(charts):
            for k, other in enumerate(charts[:j]):
                if any(overlap(A, B) for A in pair for B in other):
                    adj[j].add(k)
                    adj[k].add(j)
        seen = set()
        for j in adj:
            if j in seen:
                continue
            group, pending = set(), [j]
            while pending:
                k = pending.pop()
                if k not in group:
                    group.add(k)
                    pending.extend(adj[k]-group)
            seen.update(group)
            if len(group) < 3:
                continue
            require(len(group) == 3, 'A large possible triple group needs a smaller phase slab.')
            for c, d, e in permutations(group):
                slots = []
                for A, B in ((charts[c][0], charts[d][0]), (charts[c][1], charts[e][0]),
                             (charts[d][1], charts[e][1])):
                    if not overlap(A, B):
                        break
                    slots.append((A[0], max(A[1], B[1]), min(A[2], B[2])))
                if len(slots) == 3:
                    yield slots

    def no_triples(self):
        for slots in self.triple_candidates():
            self.triple_empty(slots, I(self.low, self.high))

    def bounds(self, D):
        box = self.curve.bounds(D)
        motion = 130*self.radius
        return box[0]-motion, box[1]+motion, box[2]-motion, box[3]+motion

    def boundary_empty(self, A, B):
        """No pair root can enter or leave a closed contact product patch."""
        count = 0

        def exclude(X, Y, depth=0):
            nonlocal count
            x, y = self.bounds(X), self.bounds(Y)
            if x[1] < y[0] or y[1] < x[0] or x[3] < y[2] or y[3] < x[2] or self.contract(X, Y) == 'empty':
                count += 1
                return
            require(depth < 22, 'A contact-patch boundary may contain a crossing.')
            if X[2]-X[1] > Y[2]-Y[1]:
                q, a, b = X
                m = (a+b)/2
                for C in ((q, a, m), (q, m, b)):
                    exclude(C, Y, depth+1)
            else:
                q, a, b = Y
                m = (a+b)/2
                for C in ((q, a, m), (q, m, b)):
                    exclude(X, C, depth+1)

        for a in A[1:]:
            exclude((A[0], a, a), B)
        for b in B[1:]:
            exclude(A, (B[0], b, b))
        return count

    def two_branch_disk(self, parameters, patches):
        """A whole-orbit cover admits only two monotone branches to a disk.

        Each complete contact product patch maps inside that disk. Hence
        none of its pair roots can ever participate in a triple.
        """
        require(len(parameters) == len(patches) == 2, 'A contact disk needs two branches.')
        origin = self.curve.evaluate(*parameters[0])[0]
        slots = []
        for q, c in parameters:
            r = min(Q(1, 200), c/2, (1-c)/2)
            require(r > 0, 'A contact branch meets the chart seam.')
            slots.append((q, c-r, c+r))
        require(not overlap(*slots), 'The contact disk slots overlap.')
        for patch, slot in zip(patches, slots):
            require(contains(slot, patch), 'The contact product patch leaves its admitted branch.')
            b = self.bounds(patch)
            require(sum(max(abs(b[2*j]-origin[j]), abs(b[2*j+1]-origin[j]))**2 for j in range(2)) < 1,
                    'A contact product patch leaves its isolation disk.')
        for q, low, high in slots:
            v = self.curve.evaluate(q, (low+high)/2)[1]
            axis = max(range(2), key=lambda j: abs(v[j]))
            signs = []
            for k in range(64):
                a, b = low+(high-low)*Q(k, 64), low+(high-low)*Q(k+1, 64)
                value = self.curve.evaluate(q, (a+b)/2)[1][axis]
                error = self.L2*(b-a)/2+self.mixed*self.radius
                signs.append(I(value-error, value+error).sign())
            require(len(set(signs)) == 1, 'An admitted contact branch is not monotone.')
        count = 0

        def exclude(q, a, b, depth=0):
            nonlocal count
            box = self.bounds((q, a, b))
            distance2 = sum(max(box[2*j]-origin[j], origin[j]-box[2*j+1], 0)**2 for j in range(2))
            if distance2 > 1:
                count += 1
                return
            require(depth < 16, 'A third branch may enter a contact disk.')
            mid = (a+b)/2
            exclude(q, a, mid, depth+1)
            exclude(q, mid, b, depth+1)

        for q in range(4):
            cuts = sorted({Q(k, 256) for k in range(257)}
                          | {x for quarter, lo, hi in slots if quarter == q for x in (lo, hi)})
            for a, b in zip(cuts, cuts[1:]):
                if any(quarter == q and lo <= a < b <= hi for quarter, lo, hi in slots):
                    continue
                exclude(q, a, b)
        return count


def overlap(A, B):
    return A[0] == B[0] and max(A[1], B[1]) <= min(A[2], B[2])


def contains(A, B):
    return A[0] == B[0] and A[1] <= B[1] <= B[2] <= A[2]
