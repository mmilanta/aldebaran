"""Certify selected meetings of the central arc along the arm detours.

Run: python3 experiments/arm_detour_events.py
Standard library only. See arm_detour_events.md. These events concern the
axis return selected by the lens and its meeting with t = pi, not the
whole crossing graph.
"""

from fractions import Fraction as Q
from math import pi, sqrt
import argparse
import cmath
from arm_detour import BRIDGES
from arm_detour_lens import central_polynomial, central_radius, certify_lens
from blend_cusps import (Interval, add, bound, derivative, product, remainder,
                        require, scale, sturm_sequence, trim, value, variations)
from certify_intersections import IntersectionCertificate


def quotient(p, q):
    """Polynomial division that requires an exactly zero remainder."""
    p, q = list(trim(p)), trim(q)
    require(q != (0,), 'Polynomial division by zero.')
    result = [Q(0)]*max(1, len(p)-len(q)+1)
    while len(p) >= len(q) and p != [0]:
        factor, shift = p[-1]/q[-1], len(p)-len(q)
        result[shift] = factor
        for j, coefficient in enumerate(q):
            p[j+shift] -= factor*coefficient
        p = list(trim(p))
    require(p == [0], 'An event polynomial division has nonzero remainder.')
    return trim(result)


def squarefree(p):
    require(p != (0,), 'A persistent meeting needs a separate argument.')
    a, b = p, derivative(p)
    while b != (0,):
        a, b = b, remainder(a, b)
    result = quotient(p, a)
    return scale(result, 1/result[-1])


def isolate(p, bits=54):
    """All distinct roots in (0,1), including exact dyadic midpoint roots.

    A midpoint root is divided out and the remaining polynomial is isolated
    again. Nothing is discarded or assigned a floating-point sign.
    """
    if len(p) == 1:
        return []
    require(value(p, 0) != 0 and value(p, 1) != 0, 'Remove boundary roots first.')
    sequence = sturm_sequence(p)

    class MidpointRoot(Exception):
        pass

    def visit(lo, hi, vl, vh):
        count = vl-vh
        require(count >= 0, 'Sturm variations increased.')
        if count == 0:
            return []
        if count == 1 and hi-lo <= Q(1, 2**bits):
            return [Interval(lo, hi)]
        mid = (lo+hi)/2
        if value(p, mid) == 0:
            raise MidpointRoot(mid)
        vm = variations(sequence, mid)
        return visit(lo, mid, vl, vm)+visit(mid, hi, vm, vh)

    count = variations(sequence, Q(0))-variations(sequence, Q(1))
    try:
        roots = visit(Q(0), Q(1), variations(sequence, Q(0)), variations(sequence, Q(1)))
    except MidpointRoot as error:
        c = error.args[0]
        roots = [Interval(c, c)]+isolate(quotient(p, (-c, 1)), bits)
    roots.sort(key=lambda c: c.low)
    require(len(roots) == count, 'The isolated roots do not match the Sturm count.')
    require(all(a.high < b.low for a, b in zip(roots, roots[1:])),
            'Event root boxes overlap; use more precision.')
    return roots


def polynomials(endpoint):
    """G: axis return; H: x'/sin(u); D: [x(pi+u)-x(pi)]/(1-c)."""
    m, n, length = endpoint
    T, U = [(Q(1),), (Q(0), Q(1))], [(Q(1),), (Q(0), Q(2))]
    for family in (T, U):
        for _ in range(2, max(m, n)+1):
            family.append(add(product((0, 2), family[-1]), scale(family[-2], -1)))
    X = add((0, -length), add(scale(T[m], 140), scale(T[n], -65)))
    H = add((length,), add(scale(U[m-1], -140*m), scale(U[n-1], 65*n)))
    D = quotient(add(X, (-value(X, 1),)), (1, -1))
    return central_polynomial(endpoint), H, D


def family_bound(first, second, c, a, order=0):
    for _ in range(order):
        first, second = derivative(first), derivative(second)
    return (1-a)*bound(first, c)+a*bound(second, c)


def events(first, second, kind):
    """Isolate every selected event on one complete leg, with exact signs."""
    require(kind in ('tangent', 'three visits'), 'Unknown central-arc event.')
    G0, H0, D0 = polynomials(first)
    G1, H1, D1 = polynomials(second)
    F0, F1 = (H0, H1) if kind == 'tangent' else (D0, D1)
    gd, fd = add(G1, scale(G0, -1)), add(F1, scale(F0, -1))
    # G = G0+a gd, F = F0+a fd. Eliminate a by one determinant.
    determinant = squarefree(add(product(G0, fd), scale(product(F0, gd), -1)))
    for c in (Q(0), Q(1)):
        while value(determinant, c) == 0:
            determinant = quotient(determinant, (-c, 1))
    roots = isolate(determinant)
    result = []
    for c in roots:
        denominator = bound(gd, c)
        require(denominator.low > 0 or denominator.high < 0,
                'An event needs a different elimination denominator.')
        a = -bound(G0, c)/denominator
        if a.high < 0 or a.low > 1:
            continue
        require(0 < a.low <= a.high < 1, 'An event weight needs finer isolation or endpoint handling.')
        Gc = family_bound(G0, G1, c, a, 1)
        Fc = family_bound(F0, F1, c, a, 1)
        require(Gc.low > 0, 'The event does not lie on the lens’s simple axis return.')
        jacobian = Gc*bound(fd, c)-Fc*bound(gd, c)
        jacobian_sign = jacobian.sign()
        record = {'cosine': c, 'weight': a, 'jacobian_sign': jacobian_sign,
                  'candidates': len(roots)}
        if kind == 'tangent':
            Gcc = family_bound(G0, G1, c, a, 2)
            Hcc = family_bound(H0, H1, c, a, 2)
            cubic = -6*c*Fc*Gc+(1-c*c)*(3*Fc*Gcc-Hcc*Gc)
            record['cubic_sign'] = cubic.sign()
            record['pair_side'] = 'after' if jacobian_sign*cubic.sign() > 0 else 'before'
        else:
            # The halfway velocity is vertical and upward. H != 0 makes
            # both other velocities transverse to it and to one another.
            family_bound(H0, H1, c, a).sign()
        result.append(record)
    return result


def check_algebra():
    require(quotient((2, -3, 1), (-1, 1)) == (-2, 1), 'Polynomial division failed.')
    require(squarefree(product((Q(-1, 2), 1), (Q(-1, 2), 1))) == (Q(-1, 2), 1),
            'Square-free reduction failed.')
    sample_roots = isolate(product(product((Q(-1, 2), 1), (Q(-1, 3), 1)), (-2, 0, 4)))
    require(len(sample_roots) == 3, 'The mixed rational/irrational root check failed.')
    require(any(c.low == c.high == Q(1, 2) for c in sample_roots),
            'An exact midpoint root was not preserved.')
    checked = 0
    for endpoint in {e for bridge in BRIDGES for e in bridge}:
        m, n, length = endpoint
        G, H, D = polynomials(endpoint)
        curve = IntersectionCertificate(m, n, 1)
        try:
            for j in range(1, 17):
                s = Q(j, 16)
                c, sine = (1-s*s)/(1+s*s), 2*s/(1+s*s)
                p, _, (vx, vy, den) = curve.evaluate(2, s)
                x = p[0]-(length-245)*c
                y = p[1]-(length-245)*sine
                horizontal_velocity = -Q(vy, den)+(length-245)*sine
                require(y == sine*value(G, c), 'The event axis polynomial is wrong.')
                require(horizontal_velocity == sine*value(H, c), 'The event velocity polynomial is wrong.')
                require(x-(-length+75) == (1-c)*value(D, c), 'The three-visit polynomial is wrong.')
                checked += 3
        finally:
            curve.evaluate.cache_clear()
    print(f'{checked} exact event-polynomial comparisons passed; root-isolator controls passed.')


def orbit_derivative(t, order, first, second, weight):
    """Independent complex derivatives, only for numerical cross-checks."""
    w = cmath.exp(1j*t)
    def endpoint(pair):
        m, n, length = pair
        return sum(radius*(1j*frequency)**order*w**frequency
                   for radius, frequency in [(length, 1), (140, m), (65, -n)])
    return (1-weight)*endpoint(first)+weight*endpoint(second)


def branch_x(height, first, second, weight, time):
    """Invert height near one selected end visit, by floating-point Newton."""
    t = time+height/orbit_derivative(time, 1, first, second, weight).imag
    for _ in range(12):
        t -= ((orbit_derivative(t, 0, first, second, weight).imag-height)
              / orbit_derivative(t, 1, first, second, weight).imag)
    require(abs(orbit_derivative(t, 0, first, second, weight).imag-height) < 1e-9,
            'The numerical branch inversion did not converge.')
    require(abs(t-time) < .15, 'The numerical branch inversion left its local neighborhood.')
    return orbit_derivative(t, 0, first, second, weight).real


def branch_gap(height, first, second, weight):
    radius = central_radius(first, second, weight)
    return (branch_x(height, first, second, weight, pi+radius)
            - branch_x(height, first, second, weight, pi-radius))


def check_contacts():
    """Cross-check the Taylor coefficient and local off-axis intersections.

    These floating-point checks do not decide any proof predicate above.
    """
    checked = 0
    for bridge in BRIDGES:
        for first, second in zip(bridge, bridge[1:]):
            for record in events(first, second, 'tangent'):
                a = float(record['weight'].midpoint())
                radius = central_radius(first, second, a)
                v, acc, jerk = [orbit_derivative(pi+radius, k, first, second, a) for k in (1, 2, 3)]
                C = (jerk.real*v.imag-3*acc.real*acc.imag)/(6*v.imag**4)
                require(C < 0 and abs(branch_gap(1, first, second, a)/2/C-1) < .01,
                        'The independent branch gap disagrees with its cubic coefficient.')
                direction = 1 if record['pair_side'] == 'after' else -1
                for delta in (1e-4, 1e-5, 1e-6):
                    weight = a+direction*delta
                    radius = central_radius(first, second, weight)
                    v = orbit_derivative(pi+radius, 1, first, second, weight)
                    prediction = sqrt(-v.real/v.imag/C)
                    low, high = prediction*.4, prediction*1.6
                    gl, gh = [branch_gap(y, first, second, weight) for y in (low, high)]
                    require(gl*gh < 0, 'The predicted extra crossing was not bracketed.')
                    for _ in range(40):
                        mid = (low+high)/2
                        if branch_gap(mid, first, second, weight)*gl > 0:
                            low = mid
                        else:
                            high = mid
                    observed = (low+high)/2
                    require(abs(observed/prediction-1) < .03,
                            'The off-axis crossing disagrees with the square-root law.')
                    checked += 1
    print(f'{checked} independent off-axis intersection checks passed, approaching all three cubic contacts.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numeric', action='store_true', help='Also cross-check the local branches numerically.')
    args = parser.parse_args()
    check_algebra()
    totals = {'tangent': 0, 'three visits': 0}
    for bridge_index, bridge in enumerate(BRIDGES):
        for leg, (first, second) in enumerate(zip(bridge, bridge[1:])):
            certify_lens(first, second)
            for kind in totals:
                for record in events(first, second, kind):
                    totals[kind] += 1
                    a = record['weight']
                    extra = (f'; cubic sign {record["cubic_sign"]:+d}; '
                             f'extra crossing pair {record["pair_side"]}') if kind == 'tangent' else ''
                    print(f'Detour {bridge_index+1}, leg {leg+1}: {kind}, '
                          f'weight ≈ {float(a.midpoint()):.12f}; '
                          f'width < {float(a.high-a.low):.2e}{extra}.')
    require(totals == {'tangent': 3, 'three visits': 3}, 'Unexpected central-event counts.')
    print('Exactly three cubic axis contacts and three coincidences with the halfway visit.')
    print('This is a census of these selected meetings, not of every crossing-graph change.')
    if args.numeric:
        check_contacts()


if __name__ == '__main__':
    main()
