"""Certify the first mirror contact's phase unfolding.

Run: python3 experiments/phase_unfolding.py
Standard library only. Exact coefficient bounds prove the local two-thirds
law. Rational contraction boxes also certify one quadratic tangency at each
of six specified nonzero phases; they do not classify the whole family.
Numerical candidates are suggestions only. See phase_unfolding.md.
"""

from fractions import Fraction as Q
from math import copysign, factorial, isqrt, pi

from arm_detour import BRIDGES, certify_leg
from arm_detour_events import events, family_bound, polynomials
from arm_detour_lens import central_radius, certify_lens
from blend_cusps import Interval, add, bound, product, require, scale, value
from phase_contact_probe import gap, orbit


FIRST, SECOND = BRIDGES[0][1:3]


def sqrt_interval(x, bits=80):
    """Outward dyadic square-root bounds, using integer arithmetic only."""
    x = Interval.wrap(x)
    require(x.low >= 0, 'A square-root interval includes negative numbers.')
    denominator = 2**bits
    low = Q(isqrt((x.low.numerator << (2*bits))//x.low.denominator), denominator)
    high = Q(isqrt((x.high.numerator << (2*bits))//x.high.denominator)+1, denominator)
    require(low*low <= x.low and high*high >= x.high, 'Square-root enclosure failed.')
    return Interval(low, high)


def power(x, n):
    result = Interval.wrap(1)
    for _ in range(n):
        result *= x
    return result


def backward_polynomial(n):
    """U_(n-1), so sin(nu) = sin(u) U_(n-1)(cos u)."""
    family = [(Q(1),), (Q(0), Q(2))]
    for _ in range(2, n):
        family.append(add(product((0, 2), family[-1]), scale(family[-2], -1)))
    return family[n-1]


def coefficients():
    """Enclose a0, A', C and B at the unique first-leg cubic contact."""
    certify_lens(FIRST, SECOND)
    record, = events(FIRST, SECOND, 'tangent')
    c, a = record['cosine'], record['weight']
    s = sqrt_interval(1-c*c)
    G0, H0, _ = polynomials(FIRST)
    G1, H1, _ = polynomials(SECOND)
    Gc = family_bound(G0, G1, c, a, 1)
    Hc = family_bound(H0, H1, c, a, 1)
    Gcc = family_bound(G0, G1, c, a, 2)
    Hcc = family_bound(H0, H1, c, a, 2)
    J = Gc*bound(add(H1, scale(H0, -1)), c)-Hc*bound(add(G1, scale(G0, -1)), c)
    K = -6*c*Hc*Gc+(1-c*c)*(3*Hc*Gcc-Hcc*Gc)
    slope_weight = -J/(s*Gc*Gc)
    cubic = K/(6*power(s, 5)*power(Gc, 4))
    V0, V1 = [backward_polynomial(pair[1]) for pair in (FIRST, SECOND)]
    phase = -130*s*family_bound(V0, V1, c, a)
    require(slope_weight.low > 0 and cubic.high < 0 and phase.high < 0,
            'The local unfolding coefficients have unresolved signs.')
    # Convenient human-readable rational enclosures, not decimal rounding.
    for name, x, low, high in [
            ('A prime', slope_weight, Q(2384, 1000), Q(2385, 1000)),
            ('C', cubic, Q(-1933, 10**8), Q(-1932, 10**8)),
            ('B', phase, Q(-91860, 1000), Q(-91858, 1000))]:
        require(low < x.low <= x.high < high, f'The advertised {name} bounds failed.')
    return {'weight': a, 'cosine': c, 'sine': s, 'A_prime': slope_weight,
            'C': cubic, 'B': phase}


def sincos(x):
    """Rational sine/cosine enclosures on a short real interval.

    Taylor polynomials through degree 61 at its rational midpoint have
    Lagrange remainder <= |midpoint|^62/62!. Sine and cosine are both
    1-Lipschitz on the real line. No floating-point proof decisions.
    """
    x = Interval.wrap(x)
    mid = x.midpoint()
    error = abs(mid)**62/Q(factorial(62))+(x.high-x.low)/2
    ss = sum((-1)**k*mid**(2*k+1)/Q(factorial(2*k+1)) for k in range(31))
    cc = sum((-1)**k*mid**(2*k)/Q(factorial(2*k)) for k in range(31))
    return Interval(ss-error, ss+error), Interval(cc-error, cc+error)


def evaluate(u, a, phase, order=0, weight_derivative=False):
    """Enclose z^(order)(pi+u,a,phase), including its weight derivative."""
    # Both forward rhythms are even and both backward rhythms are odd.
    terms = ([(-140, 2, 0), (140, 4, 0), (65, -3, phase), (-65, -7, phase)]
             if weight_derivative else
             [(-300, 1, 0), (140*(1-a), 2, 0), (140*a, 4, 0),
              (-65*(1-a), -3, phase), (-65*a, -7, phase)])
    x, y = Interval.wrap(0), Interval.wrap(0)
    for radius, frequency, offset in terms:
        ss, cc = sincos(frequency*u+offset)
        dx, dy = [(cc, ss), (-ss, cc), (-cc, -ss), (ss, -cc)][order % 4]
        x += radius*frequency**order*dx
        y += radius*frequency**order*dy
    return (x, y)


def cross(p, q):
    return p[0]*q[1]-p[1]*q[0]


def equations(box, phase):
    """Equal position and parallel velocity, with their interval Jacobian."""
    u, v, a = box
    p, q = [evaluate(t, a, phase) for t in (u, v)]
    vp, vq = [evaluate(t, a, phase, 1) for t in (u, v)]
    ap, aq = [evaluate(t, a, phase, 2) for t in (u, v)]
    pa, qa = [evaluate(t, a, phase, 0, True) for t in (u, v)]
    va, wa = [evaluate(t, a, phase, 1, True) for t in (u, v)]
    f = [p[0]-q[0], p[1]-q[1], cross(vp, vq)]
    jac = [[vp[0], -vq[0], pa[0]-qa[0]],
           [vp[1], -vq[1], pa[1]-qa[1]],
           [cross(ap, vq), cross(vp, aq), cross(va, vq)+cross(vp, wa)]]
    return f, jac


def inverse(matrix):
    """Exact rational Gauss-Jordan inverse; a singular candidate is rejected."""
    n = len(matrix)
    rows = [list(row)+[Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j] != 0), None)
        require(pivot is not None, 'The proposed tangency Jacobian is singular.')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        d = rows[j][j]
        rows[j] = [x/d for x in rows[j]]
        for k in range(n):
            if k != j:
                d = rows[k][j]
                rows[k] = [x-d*y for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def candidate(phase, data):
    """Floating-point suggestion, independent of acceptance by contraction."""
    critical = float(data['weight'].midpoint())
    A, C, B = [float(data[key].midpoint()) for key in ('A_prime', 'C', 'B')]
    height = copysign((abs(B*phase)/(4*abs(C)))**(1/3), phase)
    weight = critical-3*C*height*height/A
    for _ in range(12):
        g, gy, ga, gyy, gya = gap(height, weight, phase)
        d = gy*gya-ga*gyy
        require(abs(d) > 1e-12, 'The candidate tangency solve failed.')
        height -= (g*gya-ga*gy)/d
        weight -= (gy*gy-g*gyy)/d
    radius = central_radius(FIRST, SECOND, weight)
    times = []
    for t0 in (pi+radius, pi-radius):
        t = t0+height/orbit(t0, 1, weight, phase).imag
        for _ in range(12):
            t -= (orbit(t, 0, weight, phase).imag-height)/orbit(t, 1, weight, phase).imag
        times.append(t-pi)
    return [Q(str(t)) for t in times]+[Q(str(weight))]


def certify_box(center, phase, radius=Q(1, 10**10)):
    """One unique quadratic tangency in a small rational 3D box.

    T(X)=X-R F(X); ||I-R DF||_infinity < 1 and T(box) lies strictly
    inside box prove existence and uniqueness by the contraction theorem.
    The parameter is a specified exact rational phase, not an interval.
    """
    require(phase != 0 and abs(phase) <= Q(1, 1000), 'Use a nonzero phase with |phase| <= .001.')
    require(radius > 0, 'A tangency box needs positive radius.')
    box = [Interval(x-radius, x+radius) for x in center]
    f, _ = equations([Interval.wrap(x) for x in center], phase)
    _, jac = equations(box, phase)
    R = inverse([[x.midpoint() for x in row] for row in jac])
    defect = [[Q(i == j)-sum(R[i][k]*jac[k][j] for k in range(3))
               for j in range(3)] for i in range(3)]
    norm = max(sum(max(abs(x.low), abs(x.high)) for x in row) for row in defect)
    require(norm < Q(1, 10), 'The proposed box is not a strong contraction.')
    offsets = [-sum(R[i][k]*f[k] for k in range(3))
               + sum(defect[i][j]*Interval(-radius, radius) for j in range(3))
               for i in range(3)]
    require(all(-radius < x.low <= x.high < radius for x in offsets),
            'The tangency contraction does not map the box into itself.')
    u, v, a = box
    require(v.high < 0 < u.low and 0 < a.low <= a.high < 1,
            'The tangency visits or weight are outside the selected neighborhoods.')
    vp, vq = [evaluate(t, a, phase, 1) for t in (u, v)]
    ap, aq = [evaluate(t, a, phase, 2) for t in (u, v)]
    # At equal slope, different height curvatures give a quadratic tangency.
    require(vp[1].high < 0 and vq[1].high < 0, 'Both branches must be regular height graphs.')
    curvature = (cross(ap, vp)/power(vp[1], 3)
                 - cross(aq, vq)/power(vq[1], 3))
    curvature.sign()
    pa, qa = [evaluate(t, a, phase, 0, True) for t in (u, v)]
    weight_gap = pa[0]-vp[0]/vp[1]*pa[1]-(qa[0]-vq[0]/vq[1]*qa[1])
    weight_gap.sign()
    require((weight_gap*curvature).high < 0,
            'The tangency does not create a crossing pair as weight increases.')
    p = evaluate(u, a, phase)
    return {'phase': phase, 'box': box, 'height': p[1], 'contraction': norm,
            'curvature': curvature, 'weight_gap': weight_gap}


def certify_tangency(phase, data):
    return certify_box(candidate(float(phase), data), phase)


def certify_charts(data):
    """Both height graphs exist throughout the entire displayed rectangle.

    On each selected orbit-time chart, y' < -100 and the endpoint
    heights bracket [-32,32], for every displayed weight and phase.
    This certifies the charts, not the number of their intersections.
    """
    a = Interval(Q(1375, 10000), Q(1456, 10000))
    phase = Interval(Q(-1, 1000), Q(1, 1000))
    require(a.low < data['weight'].low-Q(2, 1000)
            and data['weight'].high+Q(6, 1000) < a.high,
            'The height-chart cover does not contain the displayed weight range.')
    count, upper = 0, Q(-10**9)
    for low, high in [(Q(46, 100), Q(76, 100)), (Q(-76, 100), Q(-46, 100))]:
        require(evaluate(Interval.wrap(low), a, phase)[1].low > 32
                and evaluate(Interval.wrap(high), a, phase)[1].high < -32,
                'A local height chart does not bracket the displayed heights.')
        for j in range(16):
            u = Interval(low+(high-low)*Q(j, 16), low+(high-low)*Q(j+1, 16))
            vy = evaluate(u, a, phase, 1)[1]
            require(vy.high < -100, 'A local height chart is not uniformly monotone.')
            upper = max(upper, vy.high)
            count += 1
    return {'intervals': count, 'vertical_velocity_upper': upper}


def check_rejections(data):
    """A nearby nonroot box and invalid phase inputs must not be certified."""
    center = candidate(.001, data)
    center[2] += Q(1, 10000)
    for proposed, phase, expected in [
            (center, Q(1, 1000), 'map the box into itself'),
            (center, Q(0), 'nonzero phase'),
            (center, Q(1, 100), 'nonzero phase')]:
        try:
            certify_box(proposed, phase)
        except ValueError as error:
            require(expected in str(error), 'An unexpected negative-control failure occurred.')
        else:
            raise ValueError('A nonroot box or out-of-scope phase was incorrectly certified.')
    print('A nearby nonroot box, zero phase, and an out-of-range phase were rejected.')


def check_algebra():
    """Independent rational complex powers check the phase coefficient."""
    checked = 0
    for n in (3, 7):
        V = backward_polynomial(n)
        for j in range(1, 33):
            r = Q(j, 32)
            c, s = (1-r*r)/(1+r*r), 2*r/(1+r*r)
            # Repeated exact multiplication of (c+i s), without trig.
            x, y = Q(1), Q(0)
            for _ in range(n):
                x, y = x*c-y*s, x*s+y*c
            require(y == s*value(V, c), 'The phase coefficient polynomial is wrong.')
            checked += 1
    for x in (Q(0), Q(1, 3), Q(1), Q(2), Q(7, 3)):
        r = sqrt_interval(x)
        require(r.low*r.low <= x <= r.high*r.high, 'A square-root control failed.')
    sine, cosine = sincos(Interval.wrap(0))
    require(sine.low == sine.high == 0 and cosine.low == cosine.high == 1,
            'The zero-angle enclosure failed.')
    for q in (Q(-5), Q(-1), Q(-1, 7), Q(1, 7), Q(1), Q(5)):
        ss, cc = sincos(q)
        norm = ss*ss+cc*cc
        require(norm.low <= 1 <= norm.high, 'A Taylor enclosure violates the unit-circle identity.')
        sn, cn = sincos(-q)
        require(sn == -ss and cn == cc, 'The Taylor enclosures violate reflection.')
    matrix = [[Q(1), Q(2), Q(3)], [Q(0), Q(1), Q(4)], [Q(5), Q(6), Q(0)]]
    inv = inverse(matrix)
    require(all(sum(matrix[i][k]*inv[k][j] for k in range(3)) == Q(i == j)
                for i in range(3) for j in range(3)), 'The exact matrix inverse failed.')
    try:
        inverse([[Q(1), Q(2)], [Q(2), Q(4)]])
    except ValueError as error:
        require('singular' in str(error), 'Unexpected matrix-control failure.')
    else:
        raise ValueError('A singular matrix was inverted.')
    a = Q(1, 7)
    for order, expected in [(0, (Q(-225), Q(0))), (1, (Q(0), 175+540*a)),
                            (2, (325+920*a, Q(0)))]:
        result = evaluate(Interval.wrap(0), a, 0, order)
        require(all(x.low == x.high == y for x, y in zip(result, expected)),
                'An exact halfway derivative control failed.')
    print(f'{checked} exact phase-polynomial identities and square-root, trig, matrix, derivative controls passed.')


def main():
    check_algebra()
    data = coefficients()
    check_rejections(data)
    charts = certify_charts(data)
    print(f'Both height graphs exist over the entire control rectangle: '
          f'{charts["intervals"]} rational time intervals; vertical velocity < -100.')
    for key in ('A_prime', 'C', 'B'):
        x = data[key]
        print(f'{key}: [{float(x.low):.14g}, {float(x.high):.14g}] (printed endpoints rounded).')
    print('Nonzero A prime, C and B prove the local |phase|^(2/3) tangency-weight law.')
    for phase in (Q(1, 1000), Q(-1, 1000), Q(1, 10000), Q(-1, 10000),
                  Q(1, 100000), Q(1, 1000000)):
        record = certify_tangency(phase, data)
        print(f'phase={float(phase):+.0e}: unique quadratic tangency in a box of radius 1e-10; '
              f'weight ≈ {float(record["box"][2].midpoint()):.12f}; '
              f'height ≈ {float(record["height"].midpoint()):+.9f}; '
              f'contraction < {float(record["contraction"]):.2e}.')
    # Reuse the complete time/weight covers, then the phase perturbation bound.
    for bridge in BRIDGES:
        for first, second in zip(bridge, bridge[1:]):
            certify_leg(first, second)
    require(1-Q(65*11, 1000) == Q(57, 200), 'The advertised phase speed margin changed.')
    print('All six detour legs retain speed > .285 for every |phase| <= .001.')
    print('Six local boxes certified; no global perturbed-event census is claimed.')


if __name__ == '__main__':
    main()
