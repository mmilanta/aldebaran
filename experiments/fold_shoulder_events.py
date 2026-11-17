"""Selected finite triple passages near the radial shoulder.

Run: python3 experiments/fold_shoulder_events.py [--write]
Standard library only. Rational contractions prove selected events, and
the radial quartic supplies the sole possible fourth ellipse preimage.
These are local certificates, not event censuses or a large-fold cutoff.
"""

import argparse
from fractions import Fraction as Q
from itertools import combinations
import json
from time import monotonic

from blend_cusps import Interval as I, require
from fold_contacts import HERE, circle, dot, multiply, round_interval, serialize
from fold_triples import chart, contract

# Numerical leads only. Nothing is accepted without the rational proof.
HINTS = (
    (30, (.19596373405892198, .39428625588586996, .5900468374494885), 2.8744237375298956),
    (60, (.09438622948835818, .1961297289506172, .29752026039586976), 2.8282141714122617),
    (120, (.046342334044894073, .0979280058002221, .14946743496972204), 2.81583281766485),
)


def power(z, n):
    """Binary interval powers; every outward rounding is exact rational."""
    require(type(n) is int and n >= 0, 'Use a nonnegative integer power.')
    result = (I.wrap(1), I.wrap(0))
    while n:
        if n & 1:
            result = tuple(round_interval(x, 45) for x in multiply(result, z))
        n //= 2
        if n:
            z = tuple(round_interval(x, 45) for x in multiply(z, z))
    return result


def evaluate(d, quarter, s, phase_quarter, phase, order=0, motion=False):
    """The same Fourier jets as fold_contacts, using binary powers."""
    require(type(d) is int and d >= 2 and type(order) is int and 0 <= order <= 2,
            'Use at least two folds and jet order zero, one, or two.')
    w, p = circle(quarter, s), circle(phase_quarter, phase)
    back = power(w, d-1)
    terms = [(65, 1-d, multiply((back[0], -back[1]), p))]
    if not motion:
        terms += [(245, 1, w), (140, d+1, power(w, d+1))]
    result = [I.wrap(0), I.wrap(0)]
    for length, frequency, z in terms:
        for _ in range(order):
            z = (-frequency*z[1], frequency*z[0])
        if motion:
            z = (-z[1], z[0])
        for j in range(2):
            result[j] += length*z[j]
    return tuple(result)


def radial_quartic(c, s, radius2):
    """Ascending coefficients in v=tan(dt/2), after clearing (1+v²)²."""
    return (152450+50050*c-radius2,
            136500*s,
            167700-109200*c-2*radius2,
            -9100*s,
            15250-13650*c-radius2)


def fourth_visit(event):
    """Exclude the only remaining ellipse preimage at the exact root.

    The quartic has three distinct known finite real roots. Its nonzero
    leading coefficient excludes the missing chart point. Vieta gives
    the fourth root. At a spatial visit its direction w=z/B would have
    to satisfy w**d=exp(iu), where u=dt. A nonzero residual forbids it.
    """
    d, qs, root = event['folds'], event['quarters'], event['root_image']
    phase = circle(qs[3], root[3])
    z = event['position']
    radius2 = dot(z, z)
    require(radius2.low > 1600, 'The common point must be nonzero.')
    p = radial_quartic(*phase, radius2)
    p[4].sign()
    parameters = []
    for q, r in zip(qs[:3], root[:3]):
        u = power(circle(q, r), d)
        parameters.append(round_interval(u[1]/(1+u[0]), 35))
    require(all(a.high < b.low or b.high < a.low
                for a, b in combinations(parameters, 2)),
            'Known ellipse parameters must be distinct.')
    fourth = round_interval(-p[3]/p[4]-sum(parameters), 35)
    require(all(fourth.high < a.low or a.high < fourth.low for a in parameters),
            'The remaining ellipse preimage is not separated from the three visits.')
    den = 1+fourth*fourth
    cu, su = (1-fourth*fourth)/den, 2*fourth/den
    c, s = phase
    B = (245+(140+65*c)*cu+65*s*su, (140-65*c)*su+65*s*cu)
    B2 = dot(B, B)
    w = ((z[0]*B[0]+z[1]*B[1])/B2,
         (z[1]*B[0]-z[0]*B[1])/B2)
    residual = [round_interval(a-b, 22) for a, b in zip(power(w, d), (cu, su))]
    axis = max(range(2), key=lambda j: min(abs(residual[j].low), abs(residual[j].high)))
    residual[axis].sign()
    return {'radius_squared': round_interval(radius2),
            'quartic_leading': round_interval(p[4]),
            'known_half_angle_parameters': parameters,
            'fourth_half_angle_parameter': fourth,
            'direction_residual': residual, 'excluded_component': axis}


def certify(d, times, phase):
    qs, cs = chart(times, phase)
    event = contract(d, qs, cs, radius=Q(1, 10**12), evaluator=evaluate)
    require(event['passage_sign'] == -1, 'The selected passage is not negative.')
    event['fourth_visit'] = fourth_visit(event)
    return event


def run():
    events = []
    for d, times, phase in HINTS:
        event = certify(d, times, phase)
        events.append(event)
        residual = event['fourth_visit']['direction_residual']
        axis = event['fourth_visit']['excluded_component']
        print(f'{d} folds: phase/pi ~ {float(event["phase_over_pi"].midpoint()):.13f}; '
              f'negative ordinary triple, no fourth visit; '
              f'direction residual[{axis}] ~ {float(residual[axis].midpoint()):.6f}.', flush=True)
    require(all(a['phase_over_pi'].low > b['phase_over_pi'].high
                for a, b in zip(events, events[1:])), 'Selected phases do not decrease.')
    return {'schema': 'aldebaran-fold-shoulder-events-v1',
            'scope': 'One selected rotational batch of negative ordinary triple passages at each of d=30,60,120; no other-event exclusion or quantitative large-fold theorem.',
            'events': events}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Save freshly proved events.')
    args = parser.parse_args()
    start = monotonic()
    record = run()
    if args.write:
        target = HERE/'fold_shoulder_events.json'
        temporary = target.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(serialize(record), indent=2)+'\n')
        temporary.replace(target)
    print(f'All three selected batches passed in {monotonic()-start:.2f}s. This is not a census.')


if __name__ == '__main__':
    main()
