"""A rectangle where the two selected branches are the whole drawing.

Run: python3 experiments/pocket_room.py
Standard library only. Rational arc bounds exclude every other orbit time
from a spatial rectangle, uniformly over the phase study's full controls.
The two selected time charts are unique height graphs and stay inside its
x bounds. Any closed pocket between them in the height window is
therefore one face of the full curve. This is not a global crossing census.
See pocket_room.md.
"""

from fractions import Fraction as Q

from blend_cusps import Interval as I, require
from phase_unfolding import certify_charts, certify_tangency, coefficients, evaluate


WEIGHT = I(Q(1375, 10000), Q(1456, 10000))
PHASE = I(Q(-1, 1000), Q(1, 1000))
ROOM = (I(Q(-212), Q(-190)), I(Q(-32), Q(32)))
CHARTS = [(Q(-76, 100), Q(-46, 100)), (Q(46, 100), Q(76, 100))]
OUTSIDE = [(Q(-16, 5), CHARTS[0][0]), (CHARTS[0][1], CHARTS[1][0]),
           (CHARTS[1][1], Q(16, 5))]


def separation(point, room=ROOM):
    """Positive distance in at least one coordinate certifies exclusion."""
    gaps = [max(wall.low-value.high, value.low-wall.high) for value, wall in zip(point, room)]
    return max(gaps)


def cover(low, high, predicate, depth=0):
    point = evaluate(I(low, high), WEIGHT, PHASE)
    margin = predicate(point)
    if margin > 0:
        return [(low, high, margin)]
    require(depth < 16, 'The spatial arc bound did not resolve this interval.')
    middle = (low+high)/2
    return (cover(low, middle, predicate, depth+1)
            + cover(middle, high, predicate, depth+1))


def check_partition(arcs, low, high):
    require(arcs[0][0] == low and arcs[-1][1] == high
            and all(a[1] == b[0] for a, b in zip(arcs, arcs[1:])),
            'The parameter cover has a gap.')
    # Re-evaluate successful leaves independently of the adaptive decisions.
    require(all(a < b for a, b, _ in arcs), 'An arc interval is empty.')


def certify_room():
    # arctan(1) = pi/4. A finite alternating geometric expansion under
    # its defining integral gives this strict rational upper bound.
    pi_upper = 4*sum(Q((-1)**k, 2*k+1) for k in range(21))
    require(pi_upper < Q(16, 5), 'The time cover does not contain a complete orbit.')
    excluded, inside = [], []
    for low, high in OUTSIDE:
        arcs = cover(low, high, separation)
        check_partition(arcs, low, high)
        require(all(separation(evaluate(I(a, b), WEIGHT, PHASE)) > 0 for a, b, _ in arcs),
                'An excluded leaf failed its independent check.')
        excluded.extend(arcs)
    horizontal_margin = lambda p: min(p[0].low-ROOM[0].low, ROOM[0].high-p[0].high)
    for low, high in CHARTS:
        arcs = cover(low, high, horizontal_margin)
        check_partition(arcs, low, high)
        require(all(horizontal_margin(evaluate(I(a, b), WEIGHT, PHASE)) > 0 for a, b, _ in arcs),
                'A chart left the x bounds.')
        inside.extend(arcs)
    return excluded, inside


def check_contacts(data):
    c, a = data['cosine'], data['weight']
    chebyshev = [I.wrap(1), c]
    for _ in range(2, 8):
        chebyshev.append(2*c*chebyshev[-1]-chebyshev[-2])
    x = (-300*c+140*(1-a)*chebyshev[2]+140*a*chebyshev[4]
         -65*(1-a)*chebyshev[3]-65*a*chebyshev[7])
    require(ROOM[0].low < x.low <= x.high < ROOM[0].high,
            'The mirror contact is outside the room.')
    require(WEIGHT.low < a.low <= a.high < WEIGHT.high, 'The mirror weight is outside the controls.')
    for phase in (Q(1, 1000), Q(-1, 1000), Q(1, 10000), Q(-1, 10000),
                  Q(1, 100000), Q(1, 1000000)):
        record = certify_tangency(phase, data)
        u, v, weight = record['box']
        require(CHARTS[1][0] < u.low <= u.high < CHARTS[1][1]
                and CHARTS[0][0] < v.low <= v.high < CHARTS[0][1]
                and WEIGHT.low < weight.low <= weight.high < WEIGHT.high,
                'A finite contact box is outside the selected controls or charts.')
        point = evaluate(u, weight, phase)
        require(all(wall.low < coordinate.low <= coordinate.high < wall.high
                    for coordinate, wall in zip(point, ROOM)),
                'A finite contact is outside the spatial room.')
    print('The mirror contact and all six earlier finite-phase contact boxes lie strictly inside the room.')


def check_controls():
    # The halfway visit is a third branch. The chosen room excludes it;
    # a room enlarged to contain it must fail this predicate.
    halfway = evaluate(I.wrap(0), I.wrap(Q(7, 50)), I.wrap(0))
    require(halfway == (I.wrap(-225), I.wrap(0)), 'The exact halfway control changed.')
    require(separation(halfway) > 0, 'The chosen room includes the halfway visit.')
    enlarged = (I(Q(-230), Q(-190)), ROOM[1])
    require(separation(halfway, enlarged) < 0, 'An included third visit was incorrectly excluded.')
    boundary = (I.wrap(ROOM[0].low), I.wrap(0))
    require(separation(boundary) == 0, 'A boundary point was incorrectly strictly excluded.')
    try:
        cover(Q(-1, 100), Q(1, 100), lambda p: separation(p, enlarged), depth=16)
    except ValueError as error:
        require('did not resolve' in str(error), 'The negative control failed for another reason.')
    else:
        raise ValueError('A room containing another branch was incorrectly certified.')
    print('Exact halfway, enlarged-room rejection, and strict-boundary controls passed.')


def lower_decimal(x):
    scaled = x*1000
    n = scaled.numerator//scaled.denominator
    return f'{n//1000}.{n%1000:03d}'


def main():
    check_controls()
    excluded, inside = certify_room()
    print(f'{len(excluded)} rational arcs exclude every nonselected visit from '
          'x in [-212,-190], y in [-32,32].')
    print(f'Coordinate separation is greater than {lower_decimal(min(m for _, _, m in excluded))} drawing units.')
    print(f'{len(inside)} rational arcs keep both selected charts strictly between x = -212 and x = -190.')
    data = coefficients()
    chart = certify_charts(data)
    print(f'{chart["intervals"]} existing chart intervals certify unique height graphs over the full window.')
    check_contacts(data)
    print('Any closed gap between these graphs with endpoint heights in [-32,32] is a face of the full drawing.')
    print('This is a uniform spatial isolation certificate, not a global event or crossing census.')


if __name__ == '__main__':
    main()
