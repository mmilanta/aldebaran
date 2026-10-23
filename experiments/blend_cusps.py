"""Certify every cusp of the straight blend from rhythms 2/3 to 4/7.

Run: python3 experiments/blend_cusps.py
Only the standard library is needed. See blend_cusps.md for the argument.
Polynomial coefficients are in ascending order; all proof decisions are exact.
"""

from dataclasses import dataclass
from fractions import Fraction as Q
from math import acos, atan2, cos, fsum, pi, sin
from pathlib import Path
import argparse

from tangent_turning import Certificate, CertificationError, multiply


def require(condition, message):
    if not condition:
        raise ValueError(message)


def trim(p):
    p = list(map(Q, p))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(p, q):
    return trim([(p[i] if i < len(p) else 0) +
                 (q[i] if i < len(q) else 0) for i in range(max(len(p), len(q)))])


def scale(p, k):
    return trim([k * x for x in p])


def product(p, q):
    result = [Q(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            result[i+j] += x*y
    return trim(result)


def derivative(p):
    return trim([i*p[i] for i in range(1, len(p))] or [0])


def value(p, x):
    result = Q(0)
    for coefficient in reversed(p):
        result = result*x + coefficient
    return result


def remainder(p, q):
    p, q = list(trim(p)), trim(q)
    require(q != (0,), 'Polynomial division by zero.')
    while len(p) >= len(q) and p != [0]:
        factor = p[-1] / q[-1]
        shift = len(p) - len(q)
        for i, coefficient in enumerate(q):
            p[i+shift] -= factor*coefficient
        p = list(trim(p))
    return tuple(p)


def sturm_sequence(p):
    sequence = [trim(p), derivative(p)]
    while sequence[-1] != (0,):
        next_p = scale(remainder(sequence[-2], sequence[-1]), -1)
        if next_p == (0,):
            break
        # Positive normalization controls integer sizes without changing signs.
        sequence.append(scale(next_p, 1 / abs(next_p[-1])))
    require(len(sequence[-1]) == 1, 'The polynomial has a repeated root.')
    return sequence


def variations(sequence, x):
    signs = [1 if y > 0 else -1 for p in sequence if (y := value(p, x)) != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def isolate_roots(p, low=Q(-1), high=Q(1), bits=58):
    """Disjoint dyadic intervals containing every simple root in (low, high)."""
    sequence = sturm_sequence(p)
    require(value(p, low) != 0 and value(p, high) != 0, 'A root is on the boundary.')
    roots = []

    def visit(lo, hi, vl, vh):
        count = vl - vh
        require(count >= 0, 'Sturm variations increased.')
        if count == 0:
            return
        if count == 1 and hi-lo <= Q(1, 2**bits):
            roots.append((lo, hi))
            return
        mid = (lo+hi)/2
        require(value(p, mid) != 0, 'A rational root needs a separate exact interval.')
        vm = variations(sequence, mid)
        visit(lo, mid, vl, vm)
        visit(mid, hi, vm, vh)

    visit(low, high, variations(sequence, low), variations(sequence, high))
    return roots


@dataclass(frozen=True)
class Interval:
    low: Q
    high: Q

    def __post_init__(self):
        require(self.low <= self.high, 'An interval is reversed.')

    @staticmethod
    def wrap(x):
        return x if isinstance(x, Interval) else Interval(Q(x), Q(x))

    def __add__(self, other):
        other = self.wrap(other)
        return Interval(self.low+other.low, self.high+other.high)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.high, -self.low)

    def __sub__(self, other):
        return self + -self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other) + -self

    def __mul__(self, other):
        other = self.wrap(other)
        candidates = [x*y for x in (self.low, self.high) for y in (other.low, other.high)]
        return Interval(min(candidates), max(candidates))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.wrap(other)
        require(other.low > 0 or other.high < 0, 'An interval denominator contains zero.')
        return self * Interval(1/other.high, 1/other.low)

    def sign(self):
        require(self.low > 0 or self.high < 0, 'An interval sign was not certified.')
        return 1 if self.low > 0 else -1

    def midpoint(self):
        return (self.low+self.high)/2


def bound(p, x):
    result = Interval.wrap(0)
    for coefficient in reversed(p):
        result = result*x + coefficient
    return result


# x'(t) = -5 sin(t) A(c,a), y'(t) = 5 B(c,a), c = cos(t).
A0 = (10, 112, 156)
A1 = (-52, -560, 2028, 896, -7280, 0, 5824)
B0 = (-56, 166, 112, -156)
B1 = (168, 520, -1008, -4940, 896, 10192, 0, -5824)
H = (22, -23, -5120, 5590, 28080, -15288, -45760, 10192, 23296)


def check_algebra():
    """Derive the velocity polynomials from Chebyshev recurrences exactly."""
    T, U = [(1,), (0, 1)], [(1,), (0, 2)]
    for family in (T, U):
        for _ in range(2, 8):
            family.append(add(product((0, 2), family[-1]), scale(family[-2], -1)))
    require(add(add((49,), scale(U[1], 56)), scale(U[2], 39)) == trim(A0),
            'The unblended horizontal velocity polynomial is wrong.')
    require(add(add(scale(U[1], -56), scale(U[3], 112)),
                add(scale(U[2], -39), scale(U[6], 91))) == trim(A1),
            'The horizontal velocity blend polynomial is wrong.')
    require(add(add((0, 49), scale(T[2], 56)), scale(T[3], -39)) == trim(B0),
            'The unblended vertical velocity polynomial is wrong.')
    require(add(add(scale(T[2], -56), scale(T[4], 112)),
                add(scale(T[3], 39), scale(T[7], -91))) == trim(B1),
            'The vertical velocity blend polynomial is wrong.')
    # Independent small Sturm examples exercise exclusion and separation.
    require(len(isolate_roots((-1, 0, 2), bits=8)) == 2, 'The two-root Sturm check failed.')
    require(isolate_roots((1, 0, 1), bits=8) == [], 'A positive polynomial received a root.')
    try:
        sturm_sequence((1, -2, 1))
    except ValueError:
        pass
    else:
        raise ValueError('A repeated root was not rejected.')


def critical_events():
    """Prove completeness, ordinary cusps, and transverse unfolding in a."""
    require(add(product(A0, B1), scale(product(B0, A1), -1)) == scale(H, -56),
            'The elimination identity failed.')
    # sin(t)=0 gives upward nonzero velocities 330+20a and 230+540a.
    require((5*value(B0, Q(1)), 5*value(B1, Q(1)),
             5*value(B0, Q(-1)), 5*value(B1, Q(-1))) == (330, 20, 230, 540),
            'The axial velocity identities failed.')
    require(min(330, 350, 230, 770) > 0, 'An axial stationary point was not excluded.')
    roots = isolate_roots(H)
    require(len(roots) == 6, 'Unexpected number of candidate cosines in (-1,1).')
    events = []
    for low, high in roots:
        c = Interval(low, high)
        a = -bound(A0, c) / bound(A1, c)
        if a.high < 0 or a.low > 1:
            continue
        require(0 < a.low <= a.high < 1, 'A candidate straddles the blend boundary.')
        # The identity and nonzero A1 turn each root of H into exactly one a.
        Ac = bound(derivative(A0), c) + a*bound(derivative(A1), c)
        Bc = bound(derivative(B0), c) + a*bound(derivative(B1), c)
        Acc = bound(derivative(derivative(A0)), c) + a*bound(derivative(derivative(A1)), c)
        Bcc = bound(derivative(derivative(B0)), c) + a*bound(derivative(derivative(B1)), c)
        sin2 = 1-c*c
        cusp = 25*sin2*(2*c*Ac*Bc + sin2*(Ac*Bcc-Bc*Acc))
        unfolding = 25*sin2*(bound(A1, c)*Bc-bound(B1, c)*Ac)
        cusp.sign()
        unfolding.sign()
        events.append({'cosine': c, 'blend': a, 'cusp_determinant': cusp,
                       'unfolding_determinant': unfolding})
    events.sort(key=lambda event: event['blend'].low)
    require(len(events) == 2 and events[0]['blend'].high < events[1]['blend'].low,
            'The two critical blends were not separated.')
    return events


def certify_blend_turning(blend, max_depth=32):
    """Exact rational velocity disks, independently of the cusp polynomial."""
    a = Q(blend)
    require(0 <= a <= 1, 'The blend must be between zero and one.')
    num, den = a.numerator, a.denominator
    terms = [(1, 49*den), (2, 56*(den-num)), (4, 112*num),
             (-3, -39*(den-num)), (-7, -91*num)]
    L = sum(abs(k*coefficient) for k, coefficient in terms)
    vertices = []
    deepest = 0

    def vertex(quarter, parameter):
        n, d = parameter.numerator, parameter.denominator
        w = (d*d-n*n, 2*n*d)
        for _ in range(quarter):
            w = (-w[1], w[0])
        D = d*d+n*n
        powers, denominators = [(1, 0)], [1]
        for _ in range(7):
            powers.append(multiply(powers[-1], w))
            denominators.append(denominators[-1]*D)
        x = sum(coefficient*powers[abs(k)][0]*denominators[7-abs(k)]
                for k, coefficient in terms)
        y = sum(coefficient*powers[abs(k)][1]*denominators[7-abs(k)]*(1 if k > 0 else -1)
                for k, coefficient in terms)
        return (x, y), denominators[7]

    def visit(quarter, low, high, depth, start):
        nonlocal deepest
        v, D = start
        require(v != (0, 0), 'A zero velocity has no tangent index.')
        width = high-low
        if ((v[0]*v[0]+v[1]*v[1])*width.denominator**2 >
                (2*L*width.numerator*D)**2):
            vertices.append(v)
            deepest = max(deepest, depth)
            return
        if depth >= max_depth:
            raise CertificationError('The blend velocity needs a deeper partition.')
        mid = (low+high)/2
        visit(quarter, low, mid, depth+1, start)
        visit(quarter, mid, high, depth+1, vertex(quarter, mid))

    for quarter in range(4):
        visit(quarter, Q(0), Q(1), 0, vertex(quarter, Q(0)))
    turns = 0
    for p, q in zip(vertices, vertices[1:]+vertices[:1]):
        cross = p[0]*q[1]-p[1]*q[0]
        if p[1] <= 0 < q[1] and cross > 0:
            turns += 1
        elif q[1] <= 0 < p[1] and cross < 0:
            turns -= 1
    return Certificate(turns, len(vertices), deepest)


def position(t, a):
    return complex(245*cos(t)+140*((1-a)*cos(2*t)+a*cos(4*t))+
                   65*((1-a)*cos(3*t)+a*cos(7*t)),
                   245*sin(t)+140*((1-a)*sin(2*t)+a*sin(4*t))-
                   65*((1-a)*sin(3*t)+a*sin(7*t)))


def velocity(t, a):
    return complex(-245*sin(t)-140*(2*(1-a)*sin(2*t)+4*a*sin(4*t))-
                   65*(3*(1-a)*sin(3*t)+7*a*sin(7*t)),
                   245*cos(t)+140*(2*(1-a)*cos(2*t)+4*a*cos(4*t))-
                   65*(3*(1-a)*cos(3*t)+7*a*cos(7*t)))


def sampled_turning(a, steps=32000):
    samples = [velocity(2*pi*j/steps, a) for j in range(steps)]
    return fsum(atan2((q*p.conjugate()).imag, (q*p.conjugate()).real)
                for p, q in zip(samples, samples[1:]+samples[:1])) / (2*pi)


def figure():
    """A standalone, accessible SVG; no optional plotting dependencies."""
    from regular_blend import position as regular_position, velocity as regular_velocity

    gold, blue, white, muted = '#e8b66e', '#9fc7eb', '#f4f1e8', '#9999ae'
    body = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760" role="img" aria-labelledby="title description">',
        '<title id="title">Two routes between two zeros</title>',
        '<desc id="description">The original 2/3 and 4/7 curves have zero tangent turns. Their one-third straight blend has minus two; the one-third angle-and-distance blend has zero. Below each drawing, its velocity trace winds around a white dot with the same count.</desc>',
        '<rect width="1200" height="760" fill="#101323"/>',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#f4f1e8}.muted{fill:#c7c7d4}</style>',
        '<text x="32" y="44" font-size="30">Two routes between two zeros</text>',
        '<text x="32" y="77" font-size="16" class="muted">The straight blend makes cusps near 22.63% and 50.89%. The angle-and-distance route keeps moving.</text>',
    ]
    critical_time = acos(float(critical_events()[0]['cosine'].midpoint()))

    def path(fn, a, map_point, start=0, end=2*pi, steps=2400):
        points = [map_point(fn(start+(end-start)*j/steps, a)) for j in range(steps+1)]
        return ' '.join(f'{"M" if j == 0 else "L"}{x:.4f} {y:.4f}'
                        for j, (x, y) in enumerate(points))

    for column, (a, label, count, pfn, vfn) in enumerate([
            (0, '0% · 2 / 3', '0', position, velocity),
            (1/3, '33⅓% · straight', '−2', position, velocity),
            (1/3, '33⅓% · keep moving', '0', regular_position, regular_velocity),
            (1, '100% · 4 / 7', '0', position, velocity)]):
        left = column*300
        body.append(f'<text x="{left+150}" y="121" text-anchor="middle" font-size="20">{label}</text>')
        drawing_map = lambda z: (left+132+0.32*z.real, 300-0.32*z.imag)
        velocities = [vfn(2*pi*j/3600, a) for j in range(3600)]
        factor = min(124/max(abs(z.real) for z in velocities),
                     86/max(abs(z.imag) for z in velocities))
        velocity_map = lambda z: (left+150+factor*z.real, 579-factor*z.imag)
        for fn, map_point in [(pfn, drawing_map), (vfn, velocity_map)]:
            body.append(f'<path d="{path(fn,a,map_point)}" fill="none" stroke="{muted}" stroke-width="1.1"/>')
            for start, end, color in [(critical_time-.24, critical_time+.24, gold),
                                      (2*pi-critical_time-.24, 2*pi-critical_time+.24, blue)]:
                body.append(f'<path d="{path(fn,a,map_point,start,end,480)}" fill="none" stroke="{color}" stroke-width="2"/>')
        x, y = drawing_map(0j)
        body.append(f'<path d="M{x-4} {y}h8 M{x} {y-4}v8" stroke="{muted}"/>')
        body.append(f'<circle cx="{left+150}" cy="579" r="3" fill="{white}"/>')
        body.append(f'<text x="{left+150}" y="477" text-anchor="middle" font-size="14" class="muted">Velocity trace around zero</text>')
        body.append(f'<text x="{left+150}" y="712" text-anchor="middle" font-size="20">Direction’s net turns: {count}</text>')
    body.extend([
        '<text x="32" y="747" font-size="14" class="muted">Every drawing winds +1 around its center. Equal axis scales within each diagram. Aldebaran · Study 005</text>',
        '</svg>',
    ])
    output = Path(__file__).with_suffix('.svg')
    output.write_text('\n'.join(body)+'\n')
    print('Wrote', output.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', action='store_true', help='Also recreate the standalone SVG.')
    args = parser.parse_args()
    check_algebra()
    events = critical_events()
    for j, event in enumerate(events, 1):
        a = float(event['blend'].midpoint())
        t = acos(float(event['cosine'].midpoint()))
        require(abs(velocity(t, a)) < 1e-8, 'The reported numerical location is inaccurate.')
        print(f'Event {j}: blend {a:.15f}, times ±{t:.15f}, point {position(t,a):.9f}')
        print(f'  Rational blend enclosure width < {float(event["blend"].high-event["blend"].low):.3g}; '
              f'cusp sign {event["cusp_determinant"].sign():+d}; '
              f'unfolding sign {event["unfolding_determinant"].sign():+d}.')
    # One exact witness per regular component suffices, because the complete
    # stationary-point classification excludes zero velocity between witnesses.
    for a, expected in [(Q(0), 0), (Q(1, 3), -2), (Q(1), 0)]:
        certificate = certify_blend_turning(a)
        require(certificate.turns == expected, 'Unexpected certified tangent index.')
        require(abs(sampled_turning(float(a))-expected) < 1e-10,
                'Independent sampled angle sum disagrees.')
        print(f'Blend {a}: certified tangent index {certificate.turns:+d}; '
              f'{certificate.edges} edges, deepest split {certificate.deepest_split}.')
    print('Exactly two critical blends, two ordinary cusps at each. Regular indices: 0, −2, 0.')
    print('The center winds +1 throughout: the factored position has real part at least 40.')
    if args.figure:
        figure()


if __name__ == '__main__':
    main()
