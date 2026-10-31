"""Rational census of cooriented bitangents for rhythms 11/6 and 11/8.

Run: python3 experiments/normal_front_census.py [--inner 6|8] [--write]
Standard library only. A fresh whole-orbit cover supplies completeness;
numerical Newton hints only refine roots already enclosed by that cover.
See normal_front_census.md. The frozen intersection solver is unchanged.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path
from time import monotonic

from blend_cusps import Interval as I, require
from certify_intersections import IntersectionCertificate
from normal_front import check_evaluation, dot, equations
from phase_unfolding import inverse
from rhythm_tangencies import evaluate


SPEED = 2305
ACCELERATION = 21345
MIN_SPEED = 775
HERE = Path(__file__).resolve().parent


def absolute(x):
    return I(0 if x.low <= 0 <= x.high else min(abs(x.low), abs(x.high)),
             max(abs(x.low), abs(x.high)))


def disjoint(x, y):
    return x.high < y.low or y.high < x.low


class FrontCensus:
    def __init__(self, inner, partition=512, max_depth=30):
        require(type(inner) is int and inner in (6, 8), 'Choose inner rhythm 6 or 8.')
        require(type(partition) is int and partition >= 128,
                'Use at least 128 rational cells per quarter.')
        require(type(max_depth) is int and max_depth >= 0, 'Use nonnegative subdivision depth.')
        self.inner = inner
        self.K = partition
        self.max_depth = max_depth
        self.evaluator = IntersectionCertificate(11, inner, partition)
        self.stats = Counter()
        self.roots = []

    def near(self, difference):
        """Strictly less than one complete normal turn on an intervening arc.

        Each cell has dt <= 2/K. The normal advances at rate at most
        ACCELERATION/MIN_SPEED, while 2pi > 6. The d+1 cells include both
        closed endpoint cells. Positive curvature excludes equal normals
        at distinct visits on such a short arc, including the cyclic seam.
        """
        return 2*ACCELERATION*(difference+1) < 6*MIN_SPEED*self.K

    @lru_cache(maxsize=32768)
    def bounds(self, domain):
        """Exact outer box for an entire arc of the direction-distance front.

        L1 normalization avoids square roots. Equal normalized normals
        and equal scaled distances mean exactly the same cooriented line.
        A chart radius r_s gives a t-radius at most 2r_s = high-low.
        """
        quarter, low, high = domain
        require(0 <= quarter < 4 and 0 <= low <= high <= 1, 'Invalid circle domain.')
        middle, radius_t = (low+high)/2, high-low
        position, _, raw = self.evaluator.evaluate(quarter, middle)
        velocity = (-Q(raw[1], raw[2]), Q(raw[0], raw[2]))
        points = [I(x-SPEED*radius_t, x+SPEED*radius_t) for x in position]
        velocities = [I(x-ACCELERATION*radius_t, x+ACCELERATION*radius_t) for x in velocity]
        norm = absolute(velocities[0])+absolute(velocities[1])
        require(norm.low > 0, 'The L1 velocity bound needs a finer partition.')
        normal = (-velocities[1]/norm, velocities[0]/norm)
        distance = dot(points, normal)
        return (*normal, distance)

    def contract(self, first, second):
        """Exclude F=0, or certify one unique zero, in a chart rectangle."""
        quarters = (first[0], second[0])
        centers = [(d[1]+d[2])/2 for d in (first, second)]
        radii = [(d[2]-d[1])/2 for d in (first, second)]
        F, J0 = equations(quarters, tuple(I.wrap(x) for x in centers), self.inner)
        _, J = equations(quarters, tuple(I(d[1], d[2]) for d in (first, second)), self.inner)
        try:
            R = inverse([[x.low for x in row] for row in J0])
        except ValueError:
            return 'unknown', None
        defect = [[Q(i == j)-sum(R[i][k]*J[k][j] for k in range(2))
                   for j in range(2)] for i in range(2)]
        offsets = [-sum(R[i][k]*F[k] for k in range(2))+
                   sum(defect[i][j]*I(-radii[j], radii[j]) for j in range(2)) for i in range(2)]
        # Every zero is fixed by x -> x-RF(x), even without a contraction.
        if any(offsets[i].low > radii[i] or offsets[i].high < -radii[i] for i in range(2)):
            return 'empty', None
        norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
        if norm < 1 and all(-radii[i] < offsets[i].low <= offsets[i].high < radii[i] for i in range(2)):
            return 'root', norm
        return 'unknown', None

    def isolate(self, first, second, depth=0):
        if any(disjoint(x, y) for x, y in zip(self.bounds(first), self.bounds(second))):
            self.stats['box_exclusion'] += 1
            return
        status, norm = self.contract(first, second)
        self.stats[status] += 1
        if status == 'empty':
            return
        if status == 'root':
            self.roots.append((first, second))
            return
        require(depth < self.max_depth, 'An unresolved product rectangle needs more subdivision.')
        if first[2]-first[1] >= second[2]-second[1]:
            quarter, low, high = first
            middle = (low+high)/2
            self.isolate((quarter, low, middle), second, depth+1)
            self.isolate((quarter, middle, high), second, depth+1)
        else:
            quarter, low, high = second
            middle = (low+high)/2
            self.isolate(first, (quarter, low, middle), depth+1)
            self.isolate(first, (quarter, middle, high), depth+1)

    def candidates(self):
        """Every remaining arc pair, using only rational box comparisons.

        Closed boxes enter every grid bucket they intersect. Equal front
        points therefore share a bucket in all three coordinates. Hashes
        only implement exact integer tuple membership, not proof decisions.
        """
        require(self.near(0), 'A single cell may make a complete normal turn.')
        grid, buckets, pairs = [], defaultdict(list), set()
        total = 4*self.K
        for i in range(total):
            quarter, k = divmod(i, self.K)
            domain = (quarter, Q(k, self.K), Q(k+1, self.K))
            box = self.bounds(domain)
            grid.append(domain)
            ranges = [range((x.low*scale)//1, (x.high*scale)//1+1)
                      for x, scale in zip(box, (4, 4, Q(1, 32)))]
            seen = set()
            for x in ranges[0]:
                for y in ranges[1]:
                    for h in ranges[2]:
                        for j in buckets[x, y, h]:
                            if j in seen:
                                continue
                            seen.add(j)
                            difference = min(i-j, total-(i-j))
                            if self.near(difference):
                                self.stats['near_exclusion'] += 1
                            elif not any(disjoint(a, b) for a, b in zip(box, self.bounds(grid[j]))):
                                pairs.add((j, i))
                        buckets[x, y, h].append(i)
        return grid, sorted(pairs)

    def hint(self, first, second):
        """Uncertified Newton refinement; checked rationally afterward."""
        s, u = [(float(d[1])+float(d[2]))/2 for d in (first, second)]

        def jets(quarter, parameter):
            w = 1j**quarter*complex(1-parameter*parameter, 2*parameter)/(1+parameter*parameter)
            return [sum(radius*(1j*k)**order*(w**k) for radius, k in
                        ((245, 1), (140, 11), (65, -self.inner))) for order in range(3)]

        def cross(p, q):
            return p.real*q.imag-p.imag*q.real

        for _ in range(8):
            p, v, A = jets(first[0], s)
            q, w, B = jets(second[0], u)
            F, G = cross(v, w), cross(p-q, v)
            a, b = 2*cross(A, w)/(1+s*s), 2*cross(v, B)/(1+u*u)
            c, d = 2*cross(p-q, A)/(1+s*s), 2*cross(v, w)/(1+u*u)
            determinant = a*d-b*c
            s -= (d*F-b*G)/determinant
            u -= (-c*F+a*G)/determinant
        return Q(str(s)), Q(str(u))

    def refine(self, first, second):
        center = self.hint(first, second)
        radius = min(Q(1, 10**11), *(min(s-d[1], d[2]-s)/4 for s, d in zip(center, (first, second))))
        require(radius > 0, 'A refined hint left its certified product rectangle.')
        domains = tuple((d[0], s-radius, s+radius) for d, s in zip((first, second), center))
        status, norm = self.contract(*domains)
        require(status == 'root' and norm < Q(1, 10**6), 'The refined box is not a strong root certificate.')
        require(all(d[1] < small[1] < small[2] < d[2] for d, small in zip((first, second), domains)),
                'A refined root box is not strictly inside its unique-root leaf.')
        weight = Q(self.inner-6, 2)
        positions = [evaluate(d[0], I(d[1], d[2]), weight) for d in domains]
        velocities = [evaluate(d[0], I(d[1], d[2]), weight, 1) for d in domains]
        require(dot(*velocities).low > 0, 'A root has not been proved cooriented.')
        delta = [p-q for p, q in zip(*positions)]
        require(any(x.high < 0 or x.low > 0 for x in delta), 'A root may have coincident points.')
        boxes = [self.bounds(d) for d in domains]
        front_box = tuple(I(max(a.low, b.low), min(a.high, b.high)) for a, b in zip(*boxes))
        return {'quarters': [d[0] for d in domains], 'center': list(map(str, center)),
                'radius': str(radius)}, front_box, norm

    def run(self, progress=True):
        start = monotonic()
        try:
            grid, pairs = self.candidates()
            if progress:
                print(f'11 / {self.inner}: {len(grid)} arcs, {len(pairs)} product candidates.', flush=True)
            for index, (j, i) in enumerate(pairs):
                self.isolate(grid[j], grid[i])
                if progress and (index+1) % 2000 == 0:
                    print(f'  {index+1}/{len(pairs)} products covered.', flush=True)
            records, boxes, norms = [], [], []
            for first, second in self.roots:
                record, box, norm = self.refine(first, second)
                records.append(record)
                boxes.append(box)
                norms.append(norm)
            comparisons = 0
            for i, box in enumerate(boxes):
                for other in boxes[:i]:
                    require(any(disjoint(x, y) for x, y in zip(box, other)),
                            'Two bitangents may describe the same front point.')
                    comparisons += 1
            # Root leaves have disjoint interiors, and every root is strictly
            # interior to its leaf. Thus no root has been counted twice.
            result = {'inner': self.inner, 'partition_per_quarter': self.K,
                      'arcs': len(grid), 'candidate_products': len(pairs),
                      'bitangents': len(records), 'separated_front_pairs': comparisons,
                      'statistics': dict(sorted(self.stats.items())), 'roots': records}
            if progress:
                print(f'11 / {self.inner}: exactly {len(records)} distinct cooriented bitangents; '
                      f'{comparisons} front-pair separations; {monotonic()-start:.2f}s.', flush=True)
            return result
        finally:
            self.bounds.cache_clear()
            self.evaluator.evaluate.cache_clear()


def controls():
    require(check_evaluation() == 136, 'The independent evaluator controls changed.')
    require(SPEED == 245+140*11+65*8 and ACCELERATION == 245+140*11**2+65*8**2,
            'The uniform Fourier derivative bounds changed.')
    require(MIN_SPEED == 1540-245-520 and
            1540*16940-1540*4405-765*16940-765*4405 == 2974975 > 0,
            'The positive speed or curvature argument changed.')
    for inner in (6, 8):
        census = FrontCensus(inner)
        try:
            # Certify the known example, then demand that its actual root
            # domain is admitted rather than excluded by the census filters.
            from normal_front import parameters
            quarters, center = parameters(inner)
            domains = tuple((q, s-Q(1, 10**11), s+Q(1, 10**11)) for q, s in zip(quarters, center))
            require(not any(disjoint(a, b) for a, b in zip(*(census.bounds(d) for d in domains))),
                    'The front bounds exclude a known bitangent.')
            require(census.contract(*domains)[0] == 'root', 'The census rejected a known bitangent.')
            _, candidates = census.candidates()
            cells = []
            for q, low, high in domains:
                require((low*census.K)//1 == (high*census.K)//1,
                        'The known bitangent needs a seam-aware control.')
                cells.append(q*census.K+(low*census.K)//1)
            require(tuple(cells) in candidates, 'The bucket cover omitted a known bitangent product.')
            shifted = (domains[0][0], domains[0][1]+Q(1, 100), domains[0][2]+Q(1, 100))
            require(census.contract(shifted, domains[1])[0] == 'empty', 'A shifted bitangent was not excluded.')
            require(census.near(0) and census.near(1) and not census.near(census.K),
                    'The local normal-turn exclusions changed.')
            # Integer bucket coverage includes a point exactly on an edge,
            # and a negative interval uses floor rather than truncation.
            require(list(range(Q(-1, 4)//1, Q(1, 4)//1+1)) == [-1, 0], 'Signed bucket floor failed.')
        finally:
            census.bounds.cache_clear()
            census.evaluator.evaluate.cache_clear()
    print('Evaluator, derivative-bound, known-root, bucket-inclusion, shifted-root, near-arc, and signed-bucket controls passed.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inner', type=int, choices=(6, 8))
    parser.add_argument('--partition', type=int, default=512)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    require(not args.write or args.inner is None, 'Write both complete endpoint censuses together.')
    controls()
    results = [FrontCensus(inner, args.partition).run() for inner in ((args.inner,) if args.inner else (6, 8))]
    require(all(record['bitangents'] == 106 for record in results), 'The advertised 106-bitangent census failed.')
    if args.write:
        record = {'description': 'Fresh whole-orbit rational covers; roots do not guide discovery.',
                  'endpoints': results}
        (HERE/'normal_front_census.json').write_text(json.dumps(record, indent=2)+'\n')
        print('Wrote normal_front_census.json after both complete proofs.', flush=True)


if __name__ == '__main__':
    main()
