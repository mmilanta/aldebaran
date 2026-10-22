"""Recompute the exact proofs recorded in smooth_atlas.json.

Run: python3 experiments/verify_smooth_atlas.py --pair 4 7
     python3 experiments/verify_smooth_atlas.py --jobs 2
The full atlas takes several minutes. Standard library only. Stored counts
are assertions to check, not inputs to the intersection search.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from time import monotonic

from certify_intersections import IntersectionCertificate, require
from region_census import census
from tangent_turning import certify_turning


def read_atlas(path):
    atlas = json.loads(path.read_text())
    require(atlas['version'] == 1, 'Unsupported atlas format.')
    require(atlas['lengths'] == [245, 140, 65], 'Unexpected arm lengths.')
    require(atlas['outer_range'] == [2, 15] and atlas['inner_range'] == [3, 25],
            'Unexpected rhythm ranges.')
    require(atlas['singular'] == [[8, 21]], 'The known cusp must remain separate.')
    regular = {(m, n) for m in range(2, 16) for n in range(3, 26) if (m, n) != (8, 21)}
    verified = [(case['outer'], case['inner']) for case in atlas['verified']]
    unresolved = [tuple(pair) for pair in atlas['unresolved']]
    require(len(verified) == len(set(verified)), 'Duplicate verified pair.')
    require(len(unresolved) == len(set(unresolved)), 'Duplicate unresolved pair.')
    require(not set(verified) & set(unresolved), 'A pair has two statuses.')
    require(set(verified) | set(unresolved) == regular, 'The statuses do not cover exactly the regular rhythms.')
    return atlas


def verify_case(case):
    m, n, partition = case['outer'], case['inner'], case['partition']
    solver = IntersectionCertificate(m, n, partition)
    start = monotonic()
    try:
        # Keep the constructor's detailed progress out of the atlas summary.
        with redirect_stdout(io.StringIO()):
            solver.run()
            solver.refine()
        result = solver.graph()
        expected = {'crossings': case['crossings'], 'bounded_faces': case['bounded_regions'],
                    'face_counts': {int(k): v for k, v in case['winding_regions'].items()}}
        require(result == expected, f'{m}/{n}: smooth census differs from archive.')
        # Independent checks: the sampled planar graph and the exact velocity
        # polygon. Neither supplies roots or decisions to the smooth search.
        sampled = census(m, n)
        require(all(sampled[key] == result[key] for key in result), f'{m}/{n}: sampled census differs.')
        tangent = certify_turning(m, n).turns
        require(tangent == case['tangent_index'] == sampled['graph_index'],
                f'{m}/{n}: tangent indices differ.')
        return m, n, result['crossings'], monotonic()-start
    finally:
        solver.evaluate.cache_clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair', nargs=2, type=int, metavar=('OUTER', 'INNER'))
    parser.add_argument('--jobs', type=int, default=1, help='Number of independent proof processes (default: 1).')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive.')
    atlas = read_atlas(Path(__file__).with_name('smooth_atlas.json'))
    cases = atlas['verified']
    if args.pair:
        cases = [case for case in cases if [case['outer'], case['inner']] == args.pair]
        if not cases:
            parser.error('That pair has no completed smooth proof in this atlas.')
    start = monotonic()
    if args.jobs == 1:
        results = map(verify_case, cases)
        for i, (m, n, crossings, seconds) in enumerate(results, 1):
            if args.pair or i % 20 == 0 or i == len(cases):
                print(f'{i}/{len(cases)} verified; last {m}/{n}: {crossings} crossings ({seconds:.2f}s).', flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for i, (m, n, crossings, seconds) in enumerate(pool.map(verify_case, cases), 1):
                if args.pair or i % 20 == 0 or i == len(cases):
                    print(f'{i}/{len(cases)} verified; last {m}/{n}: {crossings} crossings ({seconds:.2f}s).', flush=True)
    print(f'{len(cases)} smooth censuses reverified in {monotonic()-start:.2f}s. '
          f'The atlas leaves {len(atlas["unresolved"])} regular pairs unresolved.', flush=True)


if __name__ == '__main__':
    main()
