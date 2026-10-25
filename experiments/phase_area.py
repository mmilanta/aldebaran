"""Area between the two selected height graphs near their contact.

Run: python3 experiments/phase_area.py
Standard library only. The limiting laws follow from Taylor expansions in
phase_unfolding.md; the six nonzero-phase coefficients are rationally
enclosed by phase_unfolding.py. Root searches and quadrature here are
numerical cross-checks, not certified integration or a full region census.
"""

from fractions import Fraction as Q
from math import fsum, pi, sin, sqrt

from blend_cusps import require
from phase_contact_probe import gap, orbit
from phase_unfolding import candidate, certify_tangency, coefficients


def bisect(fn, low, high):
    gl, gh = fn(low), fn(high)
    require(gl*gh < 0, 'A pocket endpoint was not bracketed.')
    for _ in range(42):
        mid = (low+high)/2
        if fn(mid)*gl > 0:
            low = mid
        else:
            high = mid
    return (low+high)/2


def integral(fn, low, high, steps=128):
    """Composite Simpson quadrature; illustration only, not an enclosure."""
    h = (high-low)/steps
    return h/3*fsum((1 if j in (0, steps) else 2 if j % 2 == 0 else 4)*fn(low+j*h)
                    for j in range(steps+1))


def check_fold(phase, data):
    record = certify_tangency(phase, data)
    center = candidate(float(phase), data)
    a0 = float(center[2])
    y0 = orbit(pi+float(center[0]), 0, a0, float(phase)).imag
    coefficient = float(record['pocket_coefficient'].midpoint())
    curvature, weight = [float(record[k].midpoint()) for k in ('curvature', 'weight_gap')]
    previous = float('inf')
    for delta in (1e-4, 1e-5, 1e-6, 1e-7):
        a = a0+delta
        width = sqrt(-2*weight*delta/curvature)
        fn = lambda y: gap(y, a, float(phase))[0]
        low = bisect(fn, y0-2*width, y0)
        high = bisect(fn, y0, y0+2*width)
        area = abs(integral(fn, low, high))
        refined = abs(integral(fn, low, high, 256))
        require(abs(refined-area) < 1e-8*area+1e-12, 'Pocket quadrature did not stabilize.')
        ratio = refined/(coefficient*delta**1.5)
        require(abs(ratio-1) < previous and abs(ratio-1) < .006,
                'The fold pocket does not approach its three-halves law.')
        previous = abs(ratio-1)
        print(f'phase {float(phase):+.0e}, delta={delta:.0e}: '
              f'area ≈ {refined:.10g}; area/(K delta^1.5) ≈ {ratio:.9f}.')
    return record


def check_mirror(data):
    a0 = float(data['weight'].midpoint())
    A, C = [float(data[k].midpoint()) for k in ('A_prime', 'C')]
    coefficient = -A*A/(2*C)
    prior = float('inf')
    for delta in (1e-3, 1e-4, 1e-5, 1e-6):
        a = a0+delta
        predicted = sqrt(-A*delta/C)
        fn = lambda y: gap(y, a, 0)[0]
        root = bisect(fn, predicted*.5, predicted*1.5)
        area = integral(fn, 0, root, 256)
        coarse = integral(fn, 0, root)
        require(abs(area-coarse) < 1e-8*area+1e-12, 'Mirror quadrature did not stabilize.')
        reflected = integral(fn, -root, 0, 256)
        require(abs(area+reflected) < 1e-11, 'The mirror pockets do not have opposite graph integrals.')
        ratio = area/(coefficient*delta*delta)
        require(abs(ratio-1) < prior and abs(ratio-1) < .02,
                'The mirror pocket does not approach its quadratic law.')
        prior = abs(ratio-1)
        print(f'mirror, delta={delta:.0e}: each pocket area ≈ {area:.10g}; '
              f'area/(K0 delta^2) ≈ {ratio:.9f}.')


def check_total_area():
    """Uniform polygon areas have an independent discrete Fourier identity."""
    steps, maximum = 4096, 0
    for a in (0, .13950512619441832, .142248319367, .5, 1):
        amplitudes = [(300, 1), (140*(1-a), 2), (140*a, 4),
                      (65*(1-a), -3), (65*a, -7)]
        expected = steps/2*fsum(r*r*sin(2*pi*k/steps) for r, k in amplitudes)
        for phase in (-.001, 0, .001):
            points = [orbit(2*pi*j/steps, 0, a, phase) for j in range(steps)]
            measured = .5*fsum((p.conjugate()*q).imag
                               for p, q in zip(points, points[1:]+points[:1]))
            error = abs(measured-expected)
            require(error < 1e-7, 'The polygon area disagrees with its phase-independent Fourier identity.')
            maximum = max(maximum, error)
        smooth = pi*fsum(r*r*k for r, k in amplitudes)
        require(abs(smooth/pi-(90000+26525*(1-a)**2+48825*a*a)) < 1e-9,
                'The smooth signed-area formula changed.')
    print(f'15 polygon areas agree with the phase-independent Fourier identity; max error {maximum:.2e}.')


def main():
    data = coefficients()
    print('Numerical roots and quadrature; exact coefficient bounds come from the separate tangency boxes.')
    check_mirror(data)
    for phase in (Q(1, 1000), Q(-1, 1000)):
        record = check_fold(phase, data)
        x = record['pocket_coefficient']
        print(f'Certified fold coefficient K in ({float(x.low):.7f}, {float(x.high):.7f}); printed bounds rounded.')
    check_total_area()


if __name__ == '__main__':
    main()
