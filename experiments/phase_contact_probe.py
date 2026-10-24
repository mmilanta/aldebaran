"""Numerical exploration: break reflection at the first central contact.

Run: python3 experiments/phase_contact_probe.py
Standard library only. Multiply BOTH backward-frequency terms by exp(i phi).
This follows one local tangency numerically; it is not a census or an exact
event certificate for the perturbed family. See the 2026-10-24 journal entry.
"""

import cmath
from math import copysign, pi

from arm_detour import BRIDGES
from arm_detour_events import events
from arm_detour_lens import central_radius
from certify_intersections import require


FIRST, SECOND = BRIDGES[0][1:3]


def endpoint(t, order, pair, phase):
    m, n, length = pair
    w = cmath.exp(1j*t)
    return (length*1j**order*w + 140*(1j*m)**order*w**m
            + 65*cmath.exp(1j*phase)*(-1j*n)**order*w**-n)


def orbit(t, order, weight, phase):
    return ((1-weight)*endpoint(t, order, FIRST, phase)
            + weight*endpoint(t, order, SECOND, phase))


def weight_derivative(t, order, phase):
    return endpoint(t, order, SECOND, phase)-endpoint(t, order, FIRST, phase)


def branch(height, weight, phase, time):
    t = time+height/orbit(time, 1, weight, phase).imag
    for _ in range(12):
        t -= (orbit(t, 0, weight, phase).imag-height)/orbit(t, 1, weight, phase).imag
    position, v, acc = [orbit(t, k, weight, phase) for k in (0, 1, 2)]
    require(abs(position.imag-height) < 1e-9 and abs(t-time) < .15,
            'The local height inversion failed or left its neighborhood.')
    pa, va = [weight_derivative(t, k, phase) for k in (0, 1)]
    slope = v.real/v.imag
    curvature = (acc.real*v.imag-v.real*acc.imag)/v.imag**3
    time_derivative = -pa.imag/v.imag
    slope_derivative = (((va.real+acc.real*time_derivative)*v.imag
                         - v.real*(va.imag+acc.imag*time_derivative))/v.imag**2)
    return (position.real, slope, pa.real-slope*pa.imag, curvature, slope_derivative)


def gap(height, weight, phase):
    radius = central_radius(FIRST, SECOND, weight)
    plus = branch(height, weight, phase, pi+radius)
    minus = branch(height, weight, phase, pi-radius)
    # Separation, its y derivative, a derivative, yy derivative, ya derivative.
    return tuple(p-q for p, q in zip(plus, minus))


def main():
    record, = events(FIRST, SECOND, 'tangent')
    critical = float(record['weight'].midpoint())
    radius = central_radius(FIRST, SECOND, critical)
    v, acc, jerk = [orbit(pi+radius, k, critical, 0) for k in (1, 2, 3)]
    cubic = (jerk.real*v.imag-3*acc.real*acc.imag)/(6*v.imag**4)
    a_prime = gap(0, critical, 0)[4]/2
    phase_derivative = (gap(0, critical, 1e-6)[0]-gap(0, critical, -1e-6)[0])/(2e-6)
    require(cubic < 0 < a_prime and phase_derivative != 0, 'The expected local normal form changed.')
    print('Exploratory floating-point solves, not a perturbed-family event certificate.')
    print(f'C ≈ {cubic:.12g}; A′ ≈ {a_prime:.12g}; separation phase derivative ≈ {phase_derivative:.12g}.')
    for phase in (1e-3, -1e-3, 1e-4, -1e-4, 1e-5, 1e-6):
        # Leading separation: 2 A′ (a-a0) y + 2 C y^3 + B phi.
        guess_y = copysign((abs(phase_derivative*phase)/(4*abs(cubic)))**(1/3),
                           -phase_derivative*phase)
        predicted_shift = 3*abs(cubic)*guess_y**2/a_prime
        height, weight = guess_y, critical+predicted_shift
        for _ in range(12):
            g, gy, ga, gyy, gya = gap(height, weight, phase)
            determinant = gy*gya-ga*gyy
            require(abs(determinant) > 1e-12, 'The numerical tangency solve is ill-conditioned.')
            height -= (g*gya-ga*gy)/determinant
            weight -= (gy*gy-g*gyy)/determinant
            require(0 < weight < 1 and abs(height) < 20, 'The solve left the local search window.')
        residual = gap(height, weight, phase)
        require(abs(residual[0]) < 1e-9 and abs(residual[1]) < 1e-9,
                'The numerical tangency residual is unresolved.')
        require(abs(residual[3]) > 1e-5 and abs(residual[2]) > 1e-3,
                'The numerical contact is not an ordinary unfolding.')
        print(f'phi={phase:+.0e}: height ≈ {height:+.9f}, weight ≈ {weight:.12f}, '
              f'shift/predicted shift ≈ {(weight-critical)/predicted_shift:.9f}.')
    print('Found local quadratic tangencies; the predicted weight shift is proportional to |phi|^(2/3).')
    print('No claim about other perturbed crossings or tangencies is made.')


if __name__ == '__main__':
    main()
