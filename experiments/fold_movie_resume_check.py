"""Audit interrupted discovery, rejected checkpoints, and endpoint seeds.

Run: python3 experiments/fold_movie_resume_check.py
Standard library only. Real rational slabs check the numerical suggestions;
the complete census is still proved separately by fold_movie_census.py.
"""

from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from blend_cusps import require
from fold_contacts import HERE, census
import fold_movie_census as movie
from fold_movie import PhaseSlab, pair_hints


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('A malformed discovery proposal was accepted.')


def run():
    windows = [row for d in (7, 14) for row in movie.event_windows(d)]
    rows, pending = movie.read_proposal(HERE/'fold_movie_partial.json', windows)
    row = rows[0]
    rows = rows[1:]
    pending.insert(0, {k: row[k] for k in ('folds', 'quarter', 'low', 'high')} | {'depth': 0})
    movie.audit_proposal(rows, pending)
    proofs = {d: census(d) for d in (7, 14)}
    leaf = movie.discover_leaf
    calls = 0

    def interrupt_after_one(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        return leaf(*args)

    with TemporaryDirectory() as directory:
        checkpoint = Path(directory)/'checkpoint.json'
        with patch.object(movie, 'discover_leaf', interrupt_after_one):
            try:
                movie.discover_checkpointed(rows, pending, proofs, windows, checkpoint)
            except KeyboardInterrupt:
                pass
            else:
                raise ValueError('The interruption control did not run.')
        resumed, remaining = movie.read_proposal(checkpoint, windows)
        require(len(resumed) == len(rows)+1 and remaining == pending[1:],
                'An interruption lost an accepted slab or a pending gap.')
        require(resumed[-1]['low'] == row['low'] and resumed[-1]['high'] == row['high'],
                'The checkpoint changed the proved slab endpoints.')
        proposal = json.loads(checkpoint.read_text())
        for change in ('schema', 'events', 'missing', 'duplicate', 'gap', 'depth'):
            bad = deepcopy(proposal)
            if change == 'schema':
                bad['schema'] = 'unknown'
            elif change == 'events':
                bad['event_windows'].pop()
            elif change == 'missing':
                bad['regular_windows'].pop()
            elif change == 'duplicate':
                bad['regular_windows'].append(bad['regular_windows'][0])
            elif change == 'gap':
                bad['pending_regular_gaps'][0]['high'] = '999/1000'
            else:
                bad['pending_regular_gaps'][0]['depth'] = True
            movie.atomic_json(checkpoint, bad)
            rejected(lambda: movie.read_proposal(checkpoint, windows))
        movie.atomic_json(checkpoint, proposal)
        # A proposal with all pending work removed must still fail the full
        # partition audit; the incomplete schema cannot certify a movie.
        rejected(lambda: movie.audit_partition(resumed))
    print('Interrupted discovery retains its exact tiling; seven malformed/incomplete proposals are rejected.')

    reference = json.loads(movie.ARCHIVE.read_text())
    movie.compare_archive(reference, reference)
    for change in ('event', 'endpoint', 'word', 'stats', 'totals', 'fields', 'type'):
        bad = deepcopy(reference)
        if change == 'event':
            bad['event_proofs'][0]['ordinary_touches'] += 1
        elif change == 'endpoint':
            bad['endpoints'][0]['strangeness'] += 1
        elif change == 'word':
            bad['endpoints'][0]['word'][0][1] *= -1
        elif change == 'stats':
            bad['regular_windows'][0]['stats']['invented'] = 1
        elif change == 'totals':
            bad['regular_totals']['invented'] = 1
        elif change == 'fields':
            bad['unproved'] = True
        else:
            bad['endpoints'][0]['tangent_index'] = str(bad['endpoints'][0]['tangent_index'])
        rejected(lambda: movie.compare_archive(bad, reference))
    print('Seven altered event, endpoint, word, statistics, field, and type records are rejected.')

    total = 0
    for d, count in ((7, 35), (14, 126)):
        for p in (Q(99, 100), Q(9999, 10000), 1-Q(1, 10**9)):
            for shift in (Q(0), Q(1, 3)):
                require(len(pair_hints(d, 1, p, shift)) == count,
                        'The endpoint seed scan missed a coalescing pair.')
                radius = Q(1, 10**12)
                slab = PhaseSlab(d, 1, p-radius, p+radius, shift)
                try:
                    slab.charts(count)
                    slab.no_triples()
                    total += count
                finally:
                    slab.clear()
    print(f'{total} disjoint rational crossing charts and all their triple exclusions pass near pi, with both seams.')


if __name__ == '__main__':
    run()
