"""Certify intersections and region labels for four smooth orbital curves.

Run: python3 experiments/certify_intersections.py
Standard library only. The companion smooth_census.md explains the rational
arc bounds, exhaustive domain cover, contraction test, and planar graph.
Floating-point Newton steps suggest locations; rational checks certify them.
"""

from fractions import Fraction
from math import nextafter, inf
from collections import defaultdict, Counter, deque
from functools import lru_cache
from time import monotonic


def require(condition, message):
    if not condition:
        raise ValueError(message)


class IntersectionCertificate:
    def __init__(self, m, n, K):
        require(
            2 <= m <= 15 and 3 <= n <= 25 and isinstance(K, int) and K > 0,
            "Use supported integer rhythms and a positive integer partition size.",
        )
        self.m = m
        self.n = n
        self.K = K
        self.M = 245 + 140 * m * m + 65 * n * n
        self.V = 245 + 140 * m + 65 * n
        self.L2 = 4 * self.M + 2 * self.V
        self.stats = Counter()
        self.roots = []

    @lru_cache(maxsize=8192)
    def evaluate(self, q, s):
        """Exact position, derivative with respect to s, and raw z'(t)/i."""
        m, n = self.m, self.n
        a, b = s.numerator, s.denominator
        w = (b * b - a * a, 2 * a * b)
        for _ in range(q):
            w = (-w[1], w[0])
        D = b * b + a * a
        power = [(1, 0)]
        den = [1]
        degree = max(m, n)
        for _ in range(degree):
            x, y = power[-1]
            power.append((x * w[0] - y * w[1], x * w[1] + y * w[0]))
            den.append(den[-1] * D)
        x = (
            245 * w[0] * den[degree - 1]
            + 140 * power[m][0] * den[degree - m]
            + 65 * power[n][0] * den[degree - n]
        )
        y = (
            245 * w[1] * den[degree - 1]
            + 140 * power[m][1] * den[degree - m]
            - 65 * power[n][1] * den[degree - n]
        )
        vx = (
            245 * w[0] * den[degree - 1]
            + 140 * m * power[m][0] * den[degree - m]
            - 65 * n * power[n][0] * den[degree - n]
        )
        vy = (
            245 * w[1] * den[degree - 1]
            + 140 * m * power[m][1] * den[degree - m]
            + 65 * n * power[n][1] * den[degree - n]
        )
        factor = Fraction(2 * b * b, D)
        return (
            (Fraction(x, den[-1]), Fraction(y, den[-1])),
            (-Fraction(vy, den[-1]) * factor, Fraction(vx, den[-1]) * factor),
            (vx, vy, den[-1]),
        )

    def bounds(self, dom):
        """Rational rectangle containing an entire smooth parameter arc."""
        q, a, b = dom
        p = self.evaluate(q, a)[0]
        r = self.evaluate(q, b)[0]
        eps = self.L2 * (b - a) ** 2 / 8
        return (
            min(p[0], r[0]) - eps,
            max(p[0], r[0]) + eps,
            min(p[1], r[1]) - eps,
            max(p[1], r[1]) + eps,
        )

    def contract(self, A, B):
        """Exclude a zero or prove one unique transverse zero of z(s)-z(u).

        The preconditioned fixed-point map is x -> x - inverse(J_mid) F(x).
        Each Jacobian column varies by at most L2 times its parameter radius.
        Row sums bound its contraction norm and its image rectangle exactly.
        """
        qa, la, ha = A
        qb, lb, hb = B
        ma = (la + ha) / 2
        mb = (lb + hb) / 2
        ra = (ha - la) / 2
        rb = (hb - lb) / 2
        p, va, _ = self.evaluate(qa, ma)
        r, vb, _ = self.evaluate(qb, mb)
        F = (p[0] - r[0], p[1] - r[1])
        a, b = va[0], -vb[0]
        c, d = va[1], -vb[1]
        det = a * d - b * c
        if not det:
            return "unknown", None
        C = ((d / det, -b / det), (-c / det, a / det))
        mid = (ma, mb)
        rad = (ra, rb)
        bound = (self.L2 * ra, self.L2 * rb)
        centers = []
        radii = []
        norms = []
        for i in range(2):
            norm = abs(C[i][0]) + abs(C[i][1])
            centers.append(mid[i] - C[i][0] * F[0] - C[i][1] * F[1])
            radii.append(norm * (bound[0] * rad[0] + bound[1] * rad[1]))
            norms.append(norm * sum(bound))
        if any(abs(centers[i] - mid[i]) > rad[i] + radii[i] for i in range(2)):
            return "empty", None
        if all(
            abs(centers[i] - mid[i]) + radii[i] < rad[i] and norms[i] < 1
            for i in range(2)
        ):
            return "root", tuple(centers)
        return "unknown", None

    def isolate(self, A, B, depth=0):
        """Cover a closed parameter rectangle by exclusions and unique-root boxes."""
        ab = self.bounds(A)
        bb = self.bounds(B)
        if ab[1] < bb[0] or bb[1] < ab[0] or ab[3] < bb[2] or bb[3] < ab[2]:
            self.stats["bounds_exclusion"] += 1
            return
        status, center = self.contract(A, B)
        self.stats[status] += 1
        if status == "empty":
            return
        if status == "root":
            self.roots.append((A, B, center))
            return
        if depth >= 24:
            raise ValueError(("depth exceeded", A, B))
        if A[2] - A[1] >= B[2] - B[1]:
            q, a, b = A
            mid = (a + b) / 2
            self.isolate((q, a, mid), B, depth + 1)
            self.isolate((q, mid, b), B, depth + 1)
        else:
            q, a, b = B
            mid = (a + b) / 2
            self.isolate(A, (q, a, mid), depth + 1)
            self.isolate(A, (q, mid, b), depth + 1)

    def run(self):
        start = monotonic()
        K = self.K
        N = 4 * K
        grid = []
        buckets = defaultdict(list)
        candidate = set()
        for i in range(N):
            q, k = divmod(i, K)
            dom = (q, Fraction(k, K), Fraction(k + 1, K))
            vx, vy, denominator = self.evaluate(q, dom[1])[2]
            require(
                (vx * vx + vy * vy) * K * K > (2 * self.M * denominator) ** 2,
                "A single arc needs a finer monotonicity partition.",
            )
            raw = self.bounds(dom)
            box = (
                nextafter(float(raw[0]), -inf),
                nextafter(float(raw[1]), inf),
                nextafter(float(raw[2]), -inf),
                nextafter(float(raw[3]), inf),
            )
            # Fast comparisons use outer binary bounds, whose inclusions are
            # verified rationally. Bucket indices use the rational rectangles.
            require(
                Fraction(box[0]) <= raw[0]
                and Fraction(box[1]) >= raw[1]
                and Fraction(box[2]) <= raw[2]
                and Fraction(box[3]) >= raw[3],
                "A rounded bounding box failed to enclose its rational box.",
            )
            grid.append((dom, box))
            visited = set()
            for x in range(raw[0] // 8, raw[1] // 8 + 1):
                for y in range(raw[2] // 8, raw[3] // 8 + 1):
                    for j in buckets[x, y]:
                        if j in visited:
                            continue
                        visited.add(j)
                        other = grid[j][1]
                        if (
                            box[1] < other[0]
                            or other[1] < box[0]
                            or box[3] < other[2]
                            or other[3] < box[2]
                        ):
                            continue
                        difference = min(i - j, N - (i - j))
                        first = j if i - j <= N // 2 else i
                        q0, s0, _ = grid[first][0]
                        vx, vy, D = self.evaluate(q0, s0)[2]
                        if (vx * vx + vy * vy) * K * K > (
                            2 * self.M * (difference + 1) * D
                        ) ** 2:
                            # The whole intervening velocity stays in the open
                            # half-plane facing the initial velocity. Projection
                            # onto that velocity is strictly monotone.
                            self.stats["monotone"] += 1
                            continue
                        if difference == 1:
                            raise ValueError(("adjacent not certified", i, j))
                        candidate.add((j, i))
                    buckets[x, y].append(i)
        print(
            "grid",
            self.m,
            self.n,
            "K",
            K,
            "candidates",
            len(candidate),
            "seconds",
            monotonic() - start,
            flush=True,
        )
        for j, i in sorted(candidate):
            self.isolate(grid[j][0], grid[i][0])
        print(
            "result",
            self.m,
            self.n,
            "roots",
            len(self.roots),
            "stats",
            self.stats,
            "seconds",
            monotonic() - start,
            flush=True,
        )
        return self.roots

    def numerical(self, q, s):
        """An uncertified Newton hint; every resulting box is checked exactly."""
        w = (1j**q) * complex(1 - s * s, 2 * s) / (1 + s * s)
        z = 245 * w + 140 * w**self.m + 65 * w.conjugate() ** self.n
        v = (
            1j
            * (
                245 * w
                + 140 * self.m * w**self.m
                - 65 * self.n * w.conjugate() ** self.n
            )
            * 2
            / (1 + s * s)
        )
        return z, v

    def refine(self):
        refined = []
        for A, B, center in self.roots:
            q, lo, hi = A
            r, ll, hh = B
            x, y = map(float, center)
            for _ in range(12):
                z, v = self.numerical(q, x)
                w, u = self.numerical(r, y)
                f = z - w
                a, b, c, d = v.real, -u.real, v.imag, -u.imag
                det = a * d - b * c
                x -= (d * f.real - b * f.imag) / det
                y -= (-c * f.real + a * f.imag) / det
            found = False
            for bits in [30, 28, 26, 24]:
                radius = Fraction(1, 2**bits)
                mx = Fraction(round(x * 2**44), 2**44)
                my = Fraction(round(y * 2**44), 2**44)
                AA = (q, mx - radius, mx + radius)
                BB = (r, my - radius, my + radius)
                if not (lo < AA[1] < AA[2] < hi and ll < BB[1] < BB[2] < hh):
                    continue
                status, cc = self.contract(AA, BB)
                if status == "root":
                    _, va, _ = self.evaluate(q, mx)
                    _, vb, _ = self.evaluate(r, my)
                    # The contraction test also makes the Jacobian nonsingular
                    # throughout this box, so its determinant keeps this sign.
                    sign = 1 if va[0] * vb[1] - va[1] * vb[0] > 0 else -1
                    refined.append((AA, BB, sign))
                    found = True
                    break
            if not found:
                raise ValueError(("refinement failed", A, B))
        for i, (A, B, _) in enumerate(refined):
            ab = self.bounds(A)
            for j in range(i):
                cb = self.bounds(refined[j][0])
                require(
                    ab[1] < cb[0] or cb[1] < ab[0] or ab[3] < cb[2] or cb[3] < ab[2],
                    ("intersection image boxes overlap", i, j),
                )
        self.refined = refined
        print("refined", len(refined), "disjoint intersection image boxes", flush=True)

    def graph(self):
        """Recover faces from certified parameter orders and crossing signs."""
        events = []
        for node, (A, B, _) in enumerate(self.refined):
            events.extend([(A[0], A[1], A[2], node, 0), (B[0], B[1], B[2], node, 1)])
        events.sort()
        E = len(events)
        if E == 0:
            # A simple original curve has center winding +1, since 245 > 140+65.
            return {"crossings": 0, "bounded_faces": 1, "face_counts": {1: 1}}
        for a, b in zip(events, events[1:]):
            require(a[0] != b[0] or a[2] < b[1], ("parameter boxes overlap", a, b))
        occur = {}
        for k, e in enumerate(events):
            occur[e[3], e[4]] = k
        outgoing = {}
        following = {}
        for node, (_, _, sign) in enumerate(self.refined):
            a = occur[node, 0]
            b = occur[node, 1]
            pa = 2 * a
            ma = 2 * ((a - 1) % E) + 1
            pb = 2 * b
            mb = 2 * ((b - 1) % E) + 1
            edges = [pa, pb, ma, mb] if sign > 0 else [pa, mb, ma, pb]
            outgoing[node] = edges
            for k, he in enumerate(edges):
                following[he ^ 1] = edges[k - 1]
        face_for = {}
        F = 0
        for first in following:
            if first in face_for:
                continue
            he = first
            while he not in face_for:
                face_for[he] = F
                he = following[he]
            require(he == first, "A face walk failed to close at its start.")
            F += 1
        require(F == len(self.refined) + 2, "Euler face count failed.")
        # The wraparound arc contains t=0, the unique rightmost point x=450.
        # Its east side is outside: right when its tangent points up, left down.
        outside = face_for[
            2 * (E - 1) + (1 if 245 + 140 * self.m - 65 * self.n > 0 else 0)
        ]
        adjacency = defaultdict(list)
        for k in range(E):
            l, r = face_for[2 * k], face_for[2 * k + 1]
            require(l != r, "An oriented arc has the same face on both sides.")
            adjacency[r].append((l, 1))
            adjacency[l].append((r, -1))
        labels = {outside: 0}
        todo = deque([outside])
        while todo:
            i = todo.popleft()
            for j, d in adjacency[i]:
                if j in labels:
                    require(labels[j] == labels[i] + d, "Inconsistent winding labels.")
                else:
                    labels[j] = labels[i] + d
                    todo.append(j)
        require(len(labels) == F, "Not every face received a label.")
        bins = Counter(labels[i] for i in labels if i != outside)
        return {
            "crossings": len(self.refined),
            "bounded_faces": F - 1,
            "face_counts": dict(sorted(bins.items())),
        }


def check_contraction_cases():
    """Analytic linear cases check the root, exclusion, and boundary decisions."""

    class Lines(IntersectionCertificate):
        def __init__(self):
            self.L2 = 0

        def evaluate(self, quarter, s):
            if quarter == 0:
                return (s, Fraction(0)), (Fraction(1), Fraction(0)), None
            return (
                (Fraction(1, 2), s - Fraction(1, 2)),
                (Fraction(0), Fraction(1)),
                None,
            )

    lines = Lines()
    unit = (0, Fraction(0), Fraction(1))
    vertical = (1, Fraction(0), Fraction(1))
    status, center = lines.contract(unit, vertical)
    require(
        status == "root" and center == (Fraction(1, 2), Fraction(1, 2)),
        "The analytic transverse-root check failed.",
    )
    require(
        lines.contract((0, Fraction(0), Fraction(1, 4)), vertical)[0] == "empty",
        "The analytic exclusion check failed.",
    )
    require(
        lines.contract((0, Fraction(0), Fraction(1, 2)), vertical)[0] == "unknown",
        "A boundary root incorrectly received a strict inclusion certificate.",
    )
    require(
        lines.contract(unit, unit)[0] == "unknown",
        "A singular Jacobian incorrectly received a certificate.",
    )


def main():
    from region_census import census

    check_contraction_cases()
    for m, n, K in [(7, 13, 2048), (2, 25, 512), (6, 9, 1024), (9, 23, 32768)]:
        solver = IntersectionCertificate(m, n, K)
        solver.run()
        solver.refine()
        result = solver.graph()
        expected = census(m, n)
        if any(result[key] != expected[key] for key in result):
            raise ValueError("The smooth and sampled graph censuses differ.")
        print("CERTIFIED", m, n, result, flush=True)
        solver.evaluate.cache_clear()
    print(
        "Four smooth-curve censuses certified. Other rhythm pairs remain outside this certificate."
    )


if __name__ == "__main__":
    main()
