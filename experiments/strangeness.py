"""Compute Arnold's strangeness from certified orbital crossing data.

Run: python3 experiments/strangeness.py
     python3 experiments/strangeness.py --all --jobs 2 --write
     python3 experiments/strangeness.py --pair 4 7
     python3 experiments/strangeness.py --saved
Only the standard library is used. The frozen smooth certificate is imported,
never edited. See strangeness.md for conventions, checks, and scope.
"""

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stdout
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import io
import json
from math import atan, pi
from pathlib import Path
from time import monotonic

from certify_intersections import IntersectionCertificate, require
from verify_smooth_atlas import read_atlas


HERE = Path(__file__).resolve().parent


def validate_word(word):
    """Each crossing occurs twice, with opposite unit exponents."""
    visits = defaultdict(list)
    for label, exponent in word:
        require(type(label) is int and label >= 0, 'Use nonnegative integer crossing labels.')
        require(type(exponent) is int and exponent in (-1, 1), 'A crossing exponent must be +1 or -1.')
        visits[label].append(exponent)
    require(all(sorted(values) == [-1, 1] for values in visits.values()),
            'Each crossing must occur twice with opposite exponents.')
    return visits


@dataclass
class WordResult:
    value: int
    indices: dict
    weights: dict
    edge_indices2: list
    correction: int


def from_word(word, initial_index2):
    """Use doubled edge indices so that the entire recurrence uses integers.

    initial_index2 is twice the winding index of the edge BEFORE word[0].
    An exterior edge has index2 = +1 or -1; interior edges need not.
    This function checks local consistency, not planar realizability.
    """
    validate_word(word)
    require(type(initial_index2) is int and initial_index2 % 2 == 1,
            'Twice an edge index must be an odd integer.')
    if not word:
        require(abs(initial_index2) == 1, 'A simple closed curve has edge index +1/2 or -1/2.')
    edge2 = initial_index2
    indices, weights, edge_indices2 = {}, {}, []
    for label, exponent in word:
        edge_indices2.append(edge2)
        vertex = (edge2 + exponent) // 2
        if label in indices:
            require(indices[label] == vertex, 'The two visits give different vertex indices.')
        else:
            indices[label], weights[label] = vertex, exponent
        edge2 += 2 * exponent
    require(edge2 == initial_index2, 'The edge-index walk does not close.')
    correction = (initial_index2**2 - 1) // 4
    value = sum(weights[v] * indices[v] for v in indices) + correction
    return WordResult(value, indices, weights, edge_indices2, correction)


@dataclass
class FaceResult:
    value: int
    indices: dict
    edge_indices2: list
    face_counts: dict
    tangent_index: int


def from_faces(word, exterior_halfedge):
    """Build a planar rotation system and propagate winding from the exterior.

    Edge 2*k leaves visit k along the curve. Edge 2*k+1 follows that same
    arc backwards. The caller must identify a halfedge with exterior on its
    left. The mean of all FOUR sectors is used even if a face repeats.
    This calculation does not use the word's edge-index recurrence.
    """
    visits = validate_word(word)
    E = len(word)
    require(E > 0, 'A crossing-free curve is handled separately.')
    require(type(exterior_halfedge) is int and 0 <= exterior_halfedge < 2*E,
            'The exterior halfedge is out of range.')
    positions = defaultdict(list)
    for k, (label, _) in enumerate(word):
        positions[label].append(k)
    outgoing, following = {}, {}
    for label in visits:
        a, b = positions[label]
        # exponent at the first visit = -sign det(v_first, v_second).
        pa, pb = 2*a, 2*b
        ma, mb = 2*((a-1) % E)+1, 2*((b-1) % E)+1
        rays = [pa, pb, ma, mb] if word[a][1] < 0 else [pa, mb, ma, pb]
        outgoing[label] = rays
        for k, ray in enumerate(rays):
            following[ray ^ 1] = rays[k-1]
    faces, count = {}, 0
    for start in range(2*E):
        if start in faces:
            continue
        ray = start
        while ray not in faces:
            faces[ray] = count
            ray = following[ray]
        require(ray == start, 'A face walk did not close at its start.')
        count += 1
    require(count == len(visits)+2, 'The crossing word does not give a sphere embedding.')
    outside = faces[exterior_halfedge]
    adjacency = defaultdict(list)
    for k in range(E):
        left, right = faces[2*k], faces[2*k+1]
        require(left != right, 'An arc has the same region on both sides.')
        adjacency[right].append((left, 1))
        adjacency[left].append((right, -1))
    labels, pending = {outside: 0}, deque([outside])
    while pending:
        face = pending.popleft()
        for other, change in adjacency[face]:
            if other in labels:
                require(labels[other] == labels[face]+change, 'Inconsistent region winding labels.')
            else:
                labels[other] = labels[face]+change
                pending.append(other)
    require(len(labels) == count, 'The dual graph is disconnected.')
    edge_indices2 = [labels[faces[2*((k-1) % E)]] + labels[faces[2*((k-1) % E)+1]]
                     for k in range(E)]
    indices, weights = {}, {}
    for label, rays in outgoing.items():
        sectors = [labels[faces[ray]] for ray in rays]
        require(sum(sectors) % 4 == 0, 'A vertex winding average is not an integer.')
        index = sum(sectors)//4
        require(sorted(sectors) == [index-1, index, index, index+1], 'Unexpected crossing sectors.')
        indices[label] = index
        weights[label] = word[positions[label][0]][1]
    delta2 = edge_indices2[0]
    value = sum(weights[v]*indices[v] for v in indices) + (delta2**2-1)//4
    bins = Counter(labels[f] for f in labels if f != outside)
    tangent = sum(labels[f] for f in labels if f != outside) - sum(indices.values())
    return FaceResult(value, indices, edge_indices2, dict(sorted(bins.items())), tangent)


def audit_word(word, initial_index2, faces=None):
    """Compare the formulations at every base edge and under two symmetries."""
    original = from_word(word, initial_index2)
    if faces is not None:
        require(original.value == faces.value and original.indices == faces.indices and
                original.edge_indices2 == faces.edge_indices2, 'Word and face calculations disagree.')
    for j, delta2 in enumerate(original.edge_indices2):
        rotated = word[j:] + word[:j]
        result = from_word(rotated, delta2)
        require(result.value == original.value and result.indices == original.indices,
                'Changing the starting edge changed strangeness or vertex indices.')
    reflected = [(label, -exponent) for label, exponent in word]
    reversed_word = list(reversed(word))
    for transformed in (reflected, reversed_word):
        result = from_word(transformed, -initial_index2)
        require(result.value == original.value, 'Reflection or traversal reversal changed strangeness.')
        require(result.indices == {v: -index for v, index in original.indices.items()},
                'Reflection or reversal did not negate the winding indices.')
    return original


def checks():
    """Standard-curve normalizations and deliberate convention failures."""
    require(from_word([], 1).value == from_word([], -1).value == 0, 'Jordan circle normalization failed.')
    eight = [(0, 1), (0, -1)]
    require(audit_word(eight, -1, from_faces(eight, 1)).value == 0, 'Figure-eight normalization failed.')
    for k in range(1, 9):
        # A circle with k separate small positive curls represents K_(k+1).
        word = [(j, e) for j in range(k) for e in (1, -1)]
        faces = from_faces(word, 4*k-1)
        require(audit_word(word, 1, faces).value == k and faces.tangent_index == k+1,
                'The standard positive-curl normalization failed.')
    for fn in (
        lambda: from_word([(0, 1)], 1),
        lambda: from_word([(0, 1), (0, 1)], 1),
        lambda: from_word([(0, 0), (0, 0)], 1),
        lambda: from_word(eight, 0),
        lambda: from_word([], 3),
        lambda: from_word([(0, 1), (1, 1), (0, -1), (1, -1)], 1),
        lambda: from_faces(eight, 4),
    ):
        try:
            fn()
        except ValueError:
            pass
        else:
            raise ValueError('A malformed-word negative control was accepted.')
    # An interior base edge has a nonzero correction. Omitting it is wrong.
    result = from_word(eight, 1)
    interior = from_word(eight[1:] + eight[:1], result.edge_indices2[1])
    require(interior.correction == 2 and interior.value == 1,
            'The interior-edge correction control failed.')
    print('Standard curves K0 through K9, all their base edges, both symmetries, and negative controls passed.')


def certified_word(solver):
    """Sort disjoint exact time boxes; retain signs from rational refinement."""
    occurrences = []
    for label, (A, B, sign) in enumerate(solver.refined):
        occurrences.extend([(A, label, -sign), (B, label, sign)])
    occurrences.sort(key=lambda event: event[0])
    for (A, _, _), (B, _, _) in zip(occurrences, occurrences[1:]):
        require(A[0] != B[0] or A[2] < B[1], 'Certified parameter boxes overlap.')
    # Relabel in first-visit order so the archive is independent of root-search order.
    names, word, times, points = {}, [], [], []
    for (quarter, low, high), old, exponent in occurrences:
        label = names.setdefault(old, len(names))
        word.append((label, exponent))
        s = (low+high)/2
        # Times and positions are only display approximations. Neither enters
        # the proof or the integer postprocessor.
        times.append(quarter*pi/2 + 2*atan(float(s)))
        points.append([float(x) for x in solver.evaluate(quarter, s)[0]])
    return word, times, points


def compute_case(case):
    m, n = case['outer'], case['inner']
    solver = IntersectionCertificate(m, n, case['partition'])
    start = monotonic()
    try:
        with redirect_stdout(io.StringIO()):
            solver.run()
            solver.refine()
        expected = {'crossings': case['crossings'], 'bounded_faces': case['bounded_regions'],
                    'face_counts': {int(k): v for k, v in case['winding_regions'].items()}}
        require(solver.graph() == expected, 'The fresh smooth graph differs from the atlas.')
        word, times, points = certified_word(solver)
        speed0 = 245+140*m-65*n
        require(speed0 != 0, 'A stationary point is outside this calculation.')
        initial_index2 = 1 if speed0 > 0 else -1
        if word:
            E = len(word)
            # t=0 is on the wrap edge and is uniquely rightmost. Its east side
            # is exterior: right for upward velocity, left for downward.
            exterior = 2*(E-1) + (1 if speed0 > 0 else 0)
            faces = from_faces(word, exterior)
            require(faces.face_counts == expected['face_counts'], 'The new face walk differs from the smooth atlas.')
            require(faces.tangent_index == case['tangent_index'], 'The graph tangent index differs from the atlas.')
            reflected = from_faces([(label, -e) for label, e in word], exterior ^ 1)
            reverse_exterior = 2*((E-2-exterior//2) % E) + (1-exterior % 2)
            reversed_faces = from_faces(list(reversed(word)), reverse_exterior)
            for transformed in (reflected, reversed_faces):
                require(transformed.value == faces.value and
                        transformed.indices == {v: -index for v, index in faces.indices.items()} and
                        transformed.face_counts == dict(sorted((-k, v) for k, v in faces.face_counts.items())) and
                        transformed.tangent_index == -faces.tangent_index,
                        'A reflected or reversed planar graph has inconsistent invariants.')
        else:
            faces = None
        result = audit_word(word, initial_index2, faces)
        record = {'outer': m, 'inner': n, 'partition': case['partition'],
                  'crossings': case['crossings'], 'tangent_index': case['tangent_index'],
                  'strangeness': result.value, 'initial_index2': initial_index2,
                  'word': [list(visit) for visit in word]}
        # Keep the full atlas compact. The live study needs geometry only for
        # these three curves; the proof uses none of these rounded coordinates.
        if (m, n) in ((2, 3), (4, 7), (6, 11)):
            record['display_times'] = times
            record['display_points'] = points
        return record, monotonic()-start
    finally:
        solver.evaluate.cache_clear()


def saved_records(atlas):
    """Audit archived integers and topology, without rerunning smooth proofs."""
    saved = json.loads((HERE/'strangeness_atlas.json').read_text())
    require(saved['version'] == 1 and saved['singular'] == [[8, 21]], 'Unsupported strangeness archive.')
    require(saved['certificate_code_sha256'] == atlas['certificate_code_sha256'], 'Certificate provenance differs.')
    records = saved['verified']
    cases = {(c['outer'], c['inner']): c for c in atlas['verified']}
    pairs = [(r['outer'], r['inner']) for r in records]
    require(len(pairs) == len(set(pairs)) and set(pairs) == set(cases),
            'The strangeness archive must cover each regular pair exactly once.')
    for record in records:
        require(type(record['strangeness']) is int, 'Saved strangeness must be an integer.')
        case = cases[record['outer'], record['inner']]
        for key in ('partition', 'crossings', 'tangent_index'):
            require(record[key] == case[key], 'A saved case differs from the smooth atlas.')
        require(len(record['word']) == 2*record['crossings'], 'A saved word has the wrong length.')
        require({v for v, _ in record['word']} == set(range(record['crossings'])), 'Unexpected crossing labels.')
        speed0 = 245+140*record['outer']-65*record['inner']
        require(record['initial_index2'] == (1 if speed0 > 0 else -1), 'Unexpected exterior edge index.')
        if record['word']:
            E = len(record['word'])
            exterior = 2*(E-1)+(1 if speed0 > 0 else 0)
            faces = from_faces(record['word'], exterior)
            require(faces.face_counts == {int(k): v for k, v in case['winding_regions'].items()} and
                    faces.tangent_index == case['tangent_index'], 'A saved word has different planar counts.')
        else:
            faces = None
        result = audit_word(record['word'], record['initial_index2'], faces)
        require(result.value == record['strangeness'], 'A saved strangeness differs from its word.')
    return records


def archive_text(output):
    """One record per line keeps exact crossing words compact and diffable."""
    head = {k: v for k, v in output.items() if k != 'verified'}
    return (json.dumps(head, indent=2)[:-2] + ',\n  "verified": [\n' +
            ',\n'.join('    '+json.dumps(record) for record in output['verified']) + '\n  ]\n}\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Reprove and audit all 321 regular pairs.')
    parser.add_argument('--pair', nargs=2, type=int, metavar=('OUTER', 'INNER'))
    parser.add_argument('--jobs', type=int, default=1, help='Independent proof worker processes.')
    parser.add_argument('--write', action='store_true', help='Save a new atlas; requires --all.')
    parser.add_argument('--saved', action='store_true', help='Audit saved words only; does not rerun smooth proofs.')
    args = parser.parse_args()
    if (args.jobs < 1 or args.write and not args.all or args.all and args.pair or
            args.saved and (args.all or args.pair or args.write)):
        parser.error('Use positive jobs, --write only with --all, and choose --all, --pair, or --saved.')
    checks()
    atlas = read_atlas(HERE/'smooth_atlas.json')
    source_hash = hashlib.sha256((HERE/'certify_intersections.py').read_bytes()).hexdigest()
    require(source_hash == atlas['certificate_code_sha256'], 'The frozen certificate source has changed.')
    if args.saved:
        records = saved_records(atlas)
        print(f'{len(records)} saved words agree with both integer formulations and all base edges. '
              'This audit does not rerun the smooth proofs.')
        return
    expected = None
    if not args.write and (HERE/'strangeness_atlas.json').exists():
        expected = {(r['outer'], r['inner']): r for r in saved_records(atlas)}
    cases = atlas['verified']
    if not args.all:
        chosen = [tuple(args.pair)] if args.pair else [(2, 3), (4, 7), (6, 11)]
        cases = [case for case in cases if (case['outer'], case['inner']) in chosen]
        if len(cases) != len(chosen):
            parser.error('That pair is outside the regular smooth atlas.')
    start, records = monotonic(), []
    if args.jobs == 1:
        results = map(compute_case, cases)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.jobs)
        results = pool.map(compute_case, cases)
    try:
        for i, (record, seconds) in enumerate(results, 1):
            if expected is not None:
                proof = {k: v for k, v in record.items() if not k.startswith('display_')}
                saved = {k: v for k, v in expected[record['outer'], record['inner']].items() if not k.startswith('display_')}
                require(proof == saved, 'The fresh proof differs from the saved record.')
            records.append(record)
            if not args.all or i % 20 == 0 or i == len(cases):
                print(f'{i}/{len(cases)}: {record["outer"]}/{record["inner"]}, '
                      f'St={record["strangeness"]}, {record["crossings"]} crossings '
                      f'({seconds:.2f}s).', flush=True)
    finally:
        if pool is not None:
            pool.shutdown()
    print(f'{len(records)} smooth curves audited in {monotonic()-start:.2f}s; '
          f'{sum(2*r["crossings"] for r in records)} base edges checked.')
    if args.write:
        output = {'version': 1, 'date': '2026-10-27',
                  'certificate_code_sha256': source_hash,
                  'method': 'Fresh smooth certificates; integer Gauss recurrence and independent face winding averages.',
                  'singular': [[8, 21]], 'verified': records}
        target = HERE/'strangeness_atlas.json'
        target.write_text(archive_text(output))
        print('Wrote', target.name)


if __name__ == '__main__':
    main()
