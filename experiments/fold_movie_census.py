"""Certify every meeting on the seven- and fourteenfold phase half-turns.

Run: python3 experiments/fold_movie_census.py --jobs 2
     python3 experiments/fold_movie_census.py --write --jobs 2
Standard library only. The default repeats rational proofs on the saved
partition, all eight event windows, and four endpoint crossing words.
--write discovers a new partition, checkpointing after each accepted slab,
and saves the complete record only after every proof passes.
--write --resume PATH reuses a partial partition as proposals, freshly
verifies every slab, and checkpoints discovery after each accepted slab.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stdout
from fractions import Fraction as Q
from io import StringIO
import json
from math import pi
from pathlib import Path
from time import monotonic

from blend_cusps import Interval as I, require
from fold_contacts import (HERE, HINTS as CONTACTS, census, circle, contract,
                           dot, evaluate, hint_chart, round_interval, serialize)
from fold_movie import PhaseCurve, PhaseSlab, contains, overlap, pair_hints
from fold_triples import HINTS as TRIPLES, chart
from strangeness import audit_word, certified_word, from_faces
from triple_area import linear_data

ARCHIVE = HERE/'fold_movie.json'
WINDOW_RADIUS = Q(1, 10**7)
# Exact domain choices, initially suggested numerically. Their root
# inclusions are proved again; libm never defines the archived partition.
PHASE_CENTERS = (
    (7, 'contact', 0, 0, '2973895611532551/5000000000000000'),
    (7, 'contact', 1, 1, '4291306983184449/5000000000000000'),
    (7, 'triple', 0, 1, '8865182266797993/10000000000000000'),
    (14, 'contact', 0, 1, '7614293217553983/10000000000000000'),
    (14, 'triple', 1, 1, '3934712716523933/5000000000000000'),
    (14, 'contact', 1, 1, '4448907995016907/5000000000000000'),
    (14, 'triple', 2, 1, '9196211179234637/10000000000000000'),
    (14, 'triple', 3, 1, '4656717213923641/5000000000000000'),
)


def event_windows(d):
    require(type(d) is int and d in (7, 14), 'Use a supported phase family.')
    result = [{'folds': d, 'quarter': q, 'low': str(Q(c)-WINDOW_RADIUS),
               'high': str(Q(c)+WINDOW_RADIUS), 'kind': kind, 'index': index}
              for dd, kind, index, q, c in PHASE_CENTERS if dd == d]
    return sorted(result, key=lambda row: (row['quarter'], Q(row['low'])))


def expected_count(proof, quarter, low, high):
    # Cosine decreases throughout this closed half-turn. Point evaluation
    # gives exact extreme cosines, avoiding interval dependency inflation.
    c_low, c_high = circle(quarter, high)[0].low, circle(quarter, low)[0].high
    passed = 0
    for critical in proof['critical']:
        c = critical['cos_phase']
        if c.low > c_high:
            passed += 1
        elif c.high < c_low:
            pass
        else:
            raise ValueError('A contact phase lies in a proposed regular slab.')
    return proof['crossing_pairs'][passed]


def audit_partition(rows, folds=(7, 14)):
    require(bool(rows), 'The regular partition is empty.')
    allowed = {'folds', 'quarter', 'low', 'high', 'shift', 'crossings', 'stats'}
    require(all(set(row) == allowed for row in rows), 'Unexpected regular-partition fields.')
    for row in rows:
        require(type(row['folds']) is int and row['folds'] in folds
                and type(row['quarter']) is int and row['quarter'] in (0, 1), 'Unsupported partition family or quarter.')
        require(all(type(row[k]) is str for k in ('low', 'high', 'shift')), 'Partition bounds must be rational strings.')
        require(Q(row['shift']) in (Q(0), Q(1, 3)), 'Unknown orbit seam.')
        require(0 <= Q(row['low']) < Q(row['high']) <= 1, 'A regular slab leaves its phase quarter.')
    for d in folds:
        for quarter in (0, 1):
            pieces = [(Q(row['low']), Q(row['high'])) for row in rows+event_windows(d)
                      if row['folds'] == d and row['quarter'] == quarter]
            pieces.sort()
            require(pieces and pieces[0][0] == 0 and pieces[-1][1] == 1,
                    'A phase quarter has an uncovered endpoint.')
            require(all(a[1] == b[0] for a, b in zip(pieces, pieces[1:])),
                    'A phase partition has a gap or an interior overlap.')


def verify_regular(row, proof):
    low, high, shift = (Q(row[k]) for k in ('low', 'high', 'shift'))
    count = expected_count(proof, row['quarter'], low, high)
    require(row['crossings'] == count, 'An archived count differs from the fresh elimination.')
    slab = PhaseSlab(row['folds'], row['quarter'], low, high, shift)
    try:
        slab.charts(count)
        slab.no_triples()
        return dict(slab.stats)
    finally:
        slab.clear()


def discover_leaf(d, quarter, low, high, proof):
    count = expected_count(proof, quarter, low, high)
    errors = []
    for shift in (Q(0), Q(1, 3)):
        slab = PhaseSlab(d, quarter, low, high, shift, budget=2)
        try:
            slab.charts(count)
            slab.no_triples()
            return {'folds': d, 'quarter': quarter, 'low': str(low), 'high': str(high),
                    'shift': str(shift), 'crossings': count, 'stats': dict(slab.stats)}
        except (ValueError, ZeroDivisionError, OverflowError) as error:
            errors.append(str(error))
        finally:
            slab.clear()
    raise ValueError(' | '.join(errors))


def gaps(proofs):
    for d, proof in proofs.items():
        for quarter in (0, 1):
            previous = Q(0)
            for event in event_windows(d):
                if event['quarter'] == quarter:
                    yield d, quarter, previous, Q(event['low']), proof
                    previous = Q(event['high'])
            yield d, quarter, previous, Q(1), proof


def atomic_json(path, record):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(serialize(record), indent=2)+'\n')
    temporary.replace(path)


def compare_archive(archive, record):
    """Check saved answers only after rebuilding them from fresh proofs."""
    canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(',', ':'))
    require(canonical(archive) == canonical(serialize(record)),
            'The saved proof results differ from the fresh census.')


def audit_proposal(rows, pending):
    """A checkpoint is a tiling proposal, never a proof certificate."""
    placeholders = []
    for gap in pending:
        require(set(gap) == {'folds', 'quarter', 'low', 'high', 'depth'},
                'Unexpected pending-gap fields.')
        require(type(gap['depth']) is int and 0 <= gap['depth'] <= 28,
                'A pending gap has an invalid discovery depth.')
        placeholders.append({k: gap[k] for k in ('folds', 'quarter', 'low', 'high')}
                            | {'shift': '0', 'crossings': None, 'stats': {}})
    audit_partition(rows+placeholders)


def read_proposal(path, windows):
    record = json.loads(path.read_text())
    require(record.get('event_windows') == windows, 'The proposal has different event windows.')
    schema = record.get('schema')
    if schema == 'aldebaran-fold-movie-partial-v1':
        pending = [record['pending_regular_gap'] | {'depth': 0}]
    elif schema == 'aldebaran-fold-movie-proposal-v1':
        pending = record['pending_regular_gaps']
    elif schema == 'aldebaran-fold-movie-v1':
        pending = []
    else:
        raise ValueError('Unknown discovery proposal schema.')
    rows = record['regular_windows']
    audit_proposal(rows, pending)
    return rows, pending


def discover_checkpointed(rows, pending, proofs, windows, path):
    """Depth-first search with atomic, exact-tiling progress snapshots.

    A resumed slab remains only a proposal until the main verifier reruns
    its proof. A stopped run cannot overwrite the complete proof archive.
    """
    rows, pending = list(rows), list(pending)
    started = monotonic()

    def save():
        atomic_json(path, {'schema': 'aldebaran-fold-movie-proposal-v1',
                          'status': 'Unverified proposals; never accept as a complete certificate.',
                          'event_windows': windows, 'regular_windows': rows,
                          'pending_regular_gaps': pending})

    audit_proposal(rows, pending)
    save()
    accepted = 0
    while pending:
        gap = pending[0]
        d, quarter, low, high, depth = (gap[k] for k in ('folds', 'quarter', 'low', 'high', 'depth'))
        low, high = Q(low), Q(high)
        try:
            row = discover_leaf(d, quarter, low, high, proofs[d])
        except ValueError as error:
            require(depth < 28, f'Unresolved phase slab: {d}, {quarter}, {low}, {high}: {error}')
            middle = (low+high)/2
            pending[:1] = [gap | {'low': str(a), 'high': str(b), 'depth': depth+1}
                           for a, b in ((low, middle), (middle, high))]
        else:
            rows.append(row)
            pending.pop(0)
            accepted += 1
            if accepted % 25 == 0:
                print(f'Checkpoint: {accepted} new slabs; {d} folds, quarter {quarter}, '
                      f'endpoint {float(high):.10f}; {len(pending)} gaps; '
                      f'{monotonic()-started:.1f}s.', flush=True)
        save()
    audit_partition(rows)
    return rows


def contact_window(row, proof):
    d, index, qp = row['folds'], row['index'], row['quarter']
    low, high = Q(row['low']), Q(row['high'])
    critical = proof['critical'][index]['cos_phase']
    require(circle(qp, low)[0].low > critical.high
            and circle(qp, high)[0].high < critical.low, 'The contact root leaves its phase window.')
    before = proof['crossing_pairs'][index]
    slab = PhaseSlab(d, qp, low, high)
    try:
        hints = pair_hints(d, qp, low)
        require(len(hints) == before, 'The persistent-contact suggestions need refinement.')
        slab.charts(before, hints)
        slab.no_triples()
        t, u, phase = CONTACTS[d][index]
        patches = []
        boundary_leaves = disk_arcs = 0
        for k in range(d):
            times = sorted((tt+2*pi*k/d) % (2*pi) for tt in (t, u))
            qs, cs = hint_chart((*times, phase))
            root = contract(d, qs, cs)
            image = root['root_image']
            require(low < image[2].low <= image[2].high < high, 'A rotated contact leaves its phase window.')
            w, v = [circle(q, s) for q, s in zip(qs[:2], image[:2])]
            y = (1+dot(w, v))/2
            critical_y = proof['critical'][index]['y']
            require(max(y.low, critical_y.low) <= min(y.high, critical_y.high),
                    'A rotated contact is not identified with the global critical root.')
            r = Q(1, 10000)
            patch = [(q, s-r, s+r) for q, s in zip(qs[:2], cs[:2])]
            require(all(0 < A[1] < A[2] < 1 for A in patch) and patch[0] < patch[1]
                    and not overlap(*patch), 'A contact patch leaves a quarter or meets the diagonal.')
            require(all(contains(A, (q, x.low, x.high)) for A, q, x in zip(patch, qs, image)),
                    'The contact root leaves its product patch.')
            require(all(not (overlap(A, patch[0]) and overlap(B, patch[1]))
                        for A, B in slab.root_charts+patches), 'Contact product patches are not disjoint.')
            boundary_leaves += slab.boundary_empty(*patch)
            disk_arcs += slab.two_branch_disk(list(zip(qs[:2], cs[:2])), patch)
            patches.append(tuple(patch))
        return {'kind': 'contact', 'folds': d, 'index': index, 'ordinary_touches': d,
                'persistent_pairs': before, 'boundary_exclusions': boundary_leaves,
                'disk_excluded_arcs': disk_arcs, 'regular_stats': dict(slab.stats)}
    finally:
        slab.clear()


def triple_window(row, proof):
    index, d, qp = row['index'], row['folds'], row['quarter']
    low, high = Q(row['low']), Q(row['high'])
    dd, times, phase, expected_sign = TRIPLES[index]
    require(dd == d, 'The triple window has the wrong family.')
    count = expected_count(proof, qp, low, high)
    slab = PhaseSlab(d, qp, low, high)
    try:
        roots = []
        positions = []
        worst_norm = Q(0)
        for k in range(d):
            rotated = sorted((t+2*pi*k/d) % (2*pi) for t in times)
            qs, cs = chart(rotated, phase)
            r = Q(1, 100000)
            slots = [(q, s-min(r, s/2, (1-s)/2), s+min(r, s/2, (1-s)/2))
                     for q, s in zip(qs[:3], cs[:3])]
            require(all(0 < A[1] < A[2] < 1 for A in slots)
                    and all(A < B and not overlap(A, B) for A, B in zip(slots, slots[1:])),
                    'A large triple cube meets its diagonal or a quarter seam.')
            phase_box = I(cs[3]-r, cs[3]+r)
            status, _, norm = slab.triple_image(slots, phase_box)
            require(status == 'root', 'A large triple cube is not a unique-root contraction.')
            worst_norm = max(worst_norm, norm)
            tiny = Q(1, 10**10)
            small = [(q, s-tiny, s+tiny) for q, s in zip(qs[:3], cs[:3])]
            small_phase = I(cs[3]-tiny, cs[3]+tiny)
            require(all(contains(A, B) for A, B in zip(slots, small))
                    and phase_box.low < small_phase.low < small_phase.high < phase_box.high,
                    'The small root cube leaves its unique-root cube.')
            status, image, _ = slab.triple_image(small, small_phase)
            require(status == 'root' and low < image[3].low <= image[3].high < high,
                    'A selected triple is not inside the complete event window.')
            velocities, motions = [[evaluate(d, q, s, qp, image[3], order, motion)
                                    for q, s in zip(qs[:3], image[:3])]
                                   for order, motion in ((1, False), (0, True))]
            determinants, H = linear_data(velocities, motions)
            require(all(x.sign() in (-1, 1) for x in determinants)
                    and H.sign() == expected_sign, 'A triple is nonordinary or has a different sign.')
            positions.append(evaluate(d, qs[0], image[0], qp, image[3]))
            roots.append((slots, phase_box))
        require(all(any(A[j].high < B[j].low or B[j].high < A[j].low for j in range(2))
                    for k, A in enumerate(positions) for B in positions[:k]),
                'Two rotational triple roots may share an image.')
        slab.charts(count)
        labels, candidates = set(), 0
        for slots in slab.triple_candidates():
            candidates += 1
            matches = [k for k, (known, p) in enumerate(roots)
                       if all(contains(B, A) for A, B in zip(slots, known))
                       and p.low <= low < high <= p.high]
            if matches:
                require(len(matches) == 1, 'A triple candidate has ambiguous unique-root cubes.')
                labels.update(matches)
            else:
                slab.triple_empty(slots, I(low, high))
        require(labels == set(range(d)), 'The pair charts did not identify every selected triple.')
        return {'kind': 'triple', 'folds': d, 'index': index, 'ordinary_triples': d,
                'passage_sign': expected_sign, 'crossing_pairs': count,
                'candidate_products': candidates, 'worst_contraction_norm': round_interval(worst_norm).high,
                'regular_stats': dict(slab.stats)}
    finally:
        slab.clear()


def endpoint(d, half_turn):
    curve = PhaseCurve(d, 2 if half_turn else 0, Q(0), Q(1, 3))
    try:
        with redirect_stdout(StringIO()):
            curve.run()
            curve.refine()
        word, _, _ = certified_word(curve)
        # The ellipse proves tangent index d+1 independently of the graph.
        # Normalizing a face of true winding n to zero shifts this index by
        # -2n, since F-V=2. Hence this condition fixes the winding gauge.
        for edge in range(2*len(word)):
            faces = from_faces(word, edge)
            if faces.tangent_index == d+1:
                value = audit_word(word, faces.edge_indices2[0], faces)
                return {'folds': d, 'phase': 'pi' if half_turn else '0',
                        'crossing_pairs': len(word)//2, 'strangeness': value.value,
                        'tangent_index': faces.tangent_index, 'winding_regions': faces.face_counts,
                        'initial_index2': faces.edge_indices2[0], 'word': word}
        raise ValueError('No face normalization matches the independent tangent index.')
    finally:
        curve.clear()


def verify_event(row, proof):
    result = contact_window(row, proof) if row['kind'] == 'contact' else triple_window(row, proof)
    print(f'{row["folds"]} folds: complete {row["kind"]} window {row["index"]} passed.', flush=True)
    return result


def controls(rows):
    for bad in ([], rows[:-1], rows+[rows[0]]):
        try:
            audit_partition(bad)
        except ValueError:
            pass
        else:
            raise ValueError('An empty, incomplete, or overlapping partition was accepted.')
    d, times, phase, _ = TRIPLES[0]
    qs, cs = chart(times, phase)
    slab = PhaseSlab(d, qs[3], cs[3]-WINDOW_RADIUS, cs[3]+WINDOW_RADIUS)
    try:
        r = Q(1, 10**10)
        slots = [(q, s-r, s+r) for q, s in zip(qs[:3], cs[:3])]
        phase_box = I(cs[3]-r, cs[3]+r)
        require(slab.triple_image(slots, phase_box)[0] == 'root',
                'The known triple failed the exclusion control.')
        displaced = phase_box+Q(1, 100000)
        require(slab.triple_image(slots, displaced)[0] == 'empty',
                'A displaced triple cube was not excluded.')
    finally:
        slab.clear()
    for bad in ((True, 0, Q(0)), (7, 2, Q(1, 10)), (7, 0, .5)):
        try:
            PhaseCurve(*bad)
        except ValueError:
            pass
        else:
            raise ValueError('An invalid phase family was accepted.')
    return 8


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Rediscover and atomically replace the proof record.')
    parser.add_argument('--jobs', type=int, default=2, help='Independent proof processes.')
    parser.add_argument('--resume', type=Path, help='Reuse a partial record or checkpoint as proposals; requires --write.')
    parser.add_argument('--checkpoint', type=Path,
                        help='Discovery snapshot (default: experiments/fold_movie_checkpoint.json); requires --write.')
    args = parser.parse_args()
    require(args.jobs > 0, 'Use a positive number of proof processes.')
    require(args.write or not (args.resume or args.checkpoint), '--resume and --checkpoint require --write.')
    require(args.checkpoint is None or args.checkpoint.resolve() != ARCHIVE.resolve(),
            'A discovery checkpoint cannot replace the complete proof archive.')
    started = monotonic()
    proofs = {d: census(d) for d in (7, 14)}
    windows = [row for d in (7, 14) for row in event_windows(d)]
    if args.write:
        if args.resume:
            rows, pending = read_proposal(args.resume, windows)
        else:
            rows = []
            pending = [{'folds': d, 'quarter': q, 'low': str(a), 'high': str(b), 'depth': 0}
                       for d, q, a, b, _ in gaps(proofs)]
        checkpoint = args.checkpoint or HERE/'fold_movie_checkpoint.json'
        rows = discover_checkpointed(rows, pending, proofs, windows, checkpoint)
        rows.sort(key=lambda row: (row['folds'], row['quarter'], Q(row['low'])))
    else:
        archive = json.loads(ARCHIVE.read_text())
        require(archive['schema'] == 'aldebaran-fold-movie-v1' and archive['event_windows'] == windows,
                'The proof record has an unknown schema or different event windows.')
        rows = archive['regular_windows']
    audit_partition(rows)
    require(controls(rows) == 8, 'A failure control was skipped.')
    totals = Counter()
    events = []
    fresh_rows = []
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        tasks = {pool.submit(verify_regular, row, proofs[row['folds']]): row for row in rows}
        tasks.update({pool.submit(verify_event, row, proofs[row['folds']]): None for row in windows})
        for n, task in enumerate(as_completed(tasks), 1):
            result = task.result()
            if tasks[task] is None:
                events.append(result)
            else:
                totals.update(result)
                fresh_rows.append(tasks[task] | {'stats': result})
            if n % 100 == 0 or n == len(tasks):
                print(f'Fresh proof tasks {n}/{len(tasks)}; {monotonic()-started:.1f}s elapsed.', flush=True)
    ends = [endpoint(d, turn) for d in (7, 14) for turn in (False, True)]
    for d in (7, 14):
        a, b = [row for row in ends if row['folds'] == d]
        net = sum(row['ordinary_triples']*row['passage_sign'] for row in events
                  if row['folds'] == d and row['kind'] == 'triple')
        require(a['strangeness'] == d and b['strangeness'] == 2*d,
                'The certified endpoint strangeness values changed.')
        require(b['strangeness']-a['strangeness'] == net, 'The endpoint words disagree with the complete signed event count.')
        require([a['crossing_pairs'], b['crossing_pairs']] == proofs[d]['endpoint_pairs'],
                'The endpoint crossing words disagree with the exhaustive elimination.')
    events.sort(key=lambda row: (row['folds'], row['kind'], row['index']))
    fresh_rows.sort(key=lambda row: (row['folds'], row['quarter'], Q(row['low'])))
    record = {'schema': 'aldebaran-fold-movie-v1',
              'scope': 'Every two-visit tangency and triple passage for d=7,14 on 0<=phase<=pi; no other multiple meeting.',
              'event_windows': windows, 'regular_windows': fresh_rows, 'event_proofs': events,
              'endpoints': ends, 'invalid_controls': 8, 'regular_totals': dict(totals)}
    if args.write:
        atomic_json(ARCHIVE, record)
    else:
        compare_archive(archive, record)
    print(f'{len(rows)} regular slabs and eight complete event windows cover both half-turns.')
    print('Exactly 7 positive triples for seven folds; 28 positive and 14 negative for fourteen.')
    print('Endpoint strangeness: 7 -> 14 and 14 -> 28; independent exact crossing words agree.')
    print(f'Complete rational census passed in {monotonic()-started:.2f}s.')


if __name__ == '__main__':
    main()
