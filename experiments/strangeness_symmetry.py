"""Audit rotational quotient words and the strangeness lift formula.

Run: python3 experiments/strangeness_symmetry.py
Standard library only. This audits saved exact words, without repeating
their smooth proofs. See strangeness_symmetry.md for the general argument.
"""

from fractions import Fraction as Q
from math import gcd

from certify_intersections import require
from strangeness import HERE, audit_word, from_faces, from_word, saved_records
from verify_smooth_atlas import read_atlas


def quotient(record):
    d = gcd(record['outer']-1, record['inner']+1)
    word, delta2 = record['word'], record['initial_index2']
    E = len(word)
    if not word:
        require(record['strangeness'] == 0, 'A simple curve has nonzero strangeness.')
        return d, 0, 0
    require(E % (2*d) == 0, 'A sector does not contain complete crossing-orbit visits.')
    L, rotation = E//d, {}
    for k, (label, e) in enumerate(word):
        other, exponent = word[(k+L) % E]
        require(e == exponent, 'Rotating a visit changed its exponent.')
        require(label not in rotation or rotation[label] == other, 'The two visits induce different rotations.')
        rotation[label] = other
    require(len(set(rotation.values())) == len(rotation), 'The crossing rotation is not a permutation.')
    groups, orbit_for = {}, {}
    for label in rotation:
        if label in orbit_for:
            continue
        members, current = [], label
        for _ in range(d):
            require(current not in members, 'A crossing has a shorter rotation orbit.')
            members.append(current)
            orbit_for[current] = label
            current = rotation[current]
        require(current == label, 'A crossing rotation does not close after d steps.')
        groups[label] = members
    sector = [(orbit_for[v], e) for v, e in word[:L]]
    faces = from_faces(sector, 2*(L-1)+(1 if delta2 > 0 else 0))
    small = audit_word(sector, delta2, faces)
    large = from_word(word, delta2)
    voltage = 0
    for group in groups:
        visits = [(v, e) for v, e in word[:L] if orbit_for[v] == group]
        require(len(visits) == 2 and visits[0][1] == -visits[1][1], 'A quotient crossing has invalid visits.')
        (first, e), (second, _) = visits
        current, offset = second, 0
        while current != first:
            current = rotation[current]
            offset += 1
        require(all(large.indices[v] == large.indices[first] for v in groups[group]),
                'A rotation orbit has different winding indices.')
        voltage += e*large.indices[first]*offset
    require(large.value == d*small.value-2*voltage, 'The exact lift formula failed.')
    require(voltage % d == 0 and large.value % d == 0, 'The center-winding-one divisibility failed.')
    return d, small.value, voltage


def ray_checks():
    primitive = lambda k: Q(k**3, 3)-Q(k, 12)
    count = 0
    for k in range(-10, 11):
        for sign in (-1, 1):
            require(primitive(k)-primitive(k-sign) == sign*(Q(k)-Q(sign, 2))**2,
                    'The winding-ray telescoping primitive failed.')
            count += 1
    return count


def main():
    atlas = read_atlas(HERE/'smooth_atlas.json')
    records = saved_records(atlas)
    symmetric, exceptional = 0, []
    for record in records:
        d, small, voltage = quotient(record)
        symmetric += d > 1
        if voltage:
            exceptional.append((record['outer'], record['inner'], d, small, voltage, record['strangeness']))
    require(exceptional == [(15, 6, 7, 2, 14, -14)], 'The archived nonzero sheet correction changed.')
    print(f'{len(records)} sector words and lift identities passed, including {symmetric} curves with d > 1.')
    print(f'{ray_checks()} exact telescoping-primitive checks passed.')
    print('All archived St values are divisible by their fold count.')
    print('15/6 is a useful control: d=7, quotient St=2, sheet sum=14; St=7*2-2*14=-14.')
    print('This audits saved words; rerun strangeness.py --all for their smooth proofs.')


if __name__ == '__main__':
    main()
