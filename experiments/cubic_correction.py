"""Enclose the next term beyond the leading orbital cubic.

Run: python3 experiments/cubic_correction.py
Standard library only. Rational interval jets enclose all five weighted
degree-five coefficients, the next contact terms, and the next mirror-area
term. Four refined contraction boxes bound finite-phase prediction errors.
The final area integrations are numerical checks, not area certificates.
See cubic_correction.md. The frozen intersection certificate is unchanged.
"""

from fractions import Fraction as Q
from math import factorial, sqrt

from blend_cusps import Interval as I, require
from phase_area import bisect, integral
from phase_contact_probe import gap
from phase_unfolding import candidate, certify_box, coefficients, equations, inverse


DENOMINATOR = 2**100
ZERO = (I.wrap(0), I.wrap(0))
ONE = (I.wrap(1), I.wrap(0))


def outward(x):
    """Round rational intervals outward to a fixed dyadic grid."""
    x = I.wrap(x)
    low, high = x.low*DENOMINATOR, x.high*DENOMINATOR
    return I(Q(low.numerator//low.denominator, DENOMINATOR),
             Q(-(-high.numerator//high.denominator), DENOMINATOR))


def complex_add(a, b):
    return tuple(outward(x+y) for x, y in zip(a, b))


def complex_product(a, b):
    x, y = a
    u, v = b
    return outward(x*u-y*v), outward(x*v+y*u)


def complex_scale(a, k):
    return tuple(outward(x*k) for x in a)


def unit_power(z, n):
    """Integer powers of a unit complex number enclosed by z."""
    if n < 0:
        return unit_power((z[0], -z[1]), -n)
    result = ONE
    for _ in range(n):
        result = complex_product(result, z)
    return result


def exp_i_jet(phase, degree):
    """Taylor coefficients of exp(i phase(h)), with phase(0) = 0.

    Differentiate the formal series: n e_n = i sum(k p_k e_(n-k)).
    Truncation loses no coefficient of degree at most `degree`.
    """
    require(I.wrap(phase[0]) == I.wrap(0), 'The exponential jet needs zero constant phase.')
    result = [ONE]
    for n in range(1, degree+1):
        term = ZERO
        for k in range(1, n+1):
            term = complex_add(term, complex_product((I.wrap(0), phase[k]*k), result[n-k]))
        result.append(complex_scale(term, Q(1, n)))
    return result


def terms(a0, mu):
    """(constant amplitude, h² amplitude, frequency) at time pi+u."""
    return [(-300, 0, 1), (140*(1-a0), -140*mu, 2), (140*a0, 140*mu, 4),
            (-65*(1-a0), 65*mu, -3), (-65*a0, -65*mu, -7)]


def position_jet(time, a0, mu, beta, unit, degree):
    """z(pi+u0+time(h), a0+mu h², beta h³), through given degree."""
    result = [ZERO for _ in range(degree+1)]
    for amp0, amp2, frequency in terms(a0, mu):
        phase = [I.wrap(0)]+[frequency*time[k]+(beta if frequency < 0 and k == 3 else 0)
                              for k in range(1, degree+1)]
        exponential = exp_i_jet(phase, degree)
        base = unit_power(unit, frequency)
        for n in range(degree+1):
            term = complex_scale(exponential[n], amp0)
            if n >= 2:
                term = complex_add(term, complex_scale(exponential[n-2], amp2))
            result[n] = complex_add(result[n], complex_product(base, term))
    return result


def branch_jet(height, mu, beta, data, sign, degree=5):
    """Invert the height series, coefficient by coefficient.

    At step n the unknown time coefficient multiplies only the constant
    nonzero vertical velocity. All other contributions are already known.
    """
    a0 = data['weight']
    unit = (data['cosine'], sign*data['sine'])
    speed = ZERO
    for amp0, _, frequency in terms(a0, mu):
        speed = complex_add(speed, complex_product(unit_power(unit, frequency),
                                                  (I.wrap(0), amp0*frequency)))
    vertical = speed[1]
    require(vertical.high < 0, 'The initial vertical velocity must be negative.')
    time = [I.wrap(0)]*(degree+1)
    for n in range(1, degree+1):
        position = position_jet(time, a0, mu, beta, unit, n)
        target = height if n == 1 else 0
        time[n] = outward((target-position[n][1])/vertical)
    result = position_jet(time, a0, mu, beta, unit, degree)
    for n in range(degree+1):
        residual = result[n][1]-(height if n == 1 else 0)
        require(residual.low <= 0 <= residual.high, 'The height jet inversion failed.')
    return result


def gap_jet(height, mu, beta, data):
    plus = branch_jet(height, mu, beta, data, 1)
    minus = branch_jet(height, mu, beta, data, -1)
    result = [outward(p[0]-m[0]) for p, m in zip(plus, minus)]
    # Reflection removes even powers; the defining contact removes h¹.
    for n in (0, 1, 2, 4):
        require(result[n].low <= 0 <= result[n].high, f'Expected zero at jet degree {n}.')
    cubic = 2*data['A_prime']*mu*height+2*data['C']*height**3+data['B']*beta
    residual = result[3]-cubic
    require(residual.low <= 0 <= residual.high, 'The independently known cubic coefficient disagrees.')
    return result


def integer_cuberoot(n):
    require(n >= 0, 'Use a nonnegative cube-root argument.')
    low, high = 0, 1 << ((n.bit_length()+2)//3)
    while high-low > 1:
        mid = (low+high)//2
        if mid**3 <= n:
            low = mid
        else:
            high = mid
    require(low**3 <= n < (low+1)**3, 'The integer cube-root bracket failed.')
    return low


def cuberoot(x):
    x = I.wrap(x)
    require(x.low >= 0, 'Use a nonnegative cube-root interval.')
    denominator = 2**80
    low = integer_cuberoot((x.low.numerator << 240)//x.low.denominator)
    high = integer_cuberoot((x.high.numerator << 240)//x.high.denominator)+1
    result = I(Q(low, denominator), Q(high, denominator))
    require(result.low**3 <= x.low and result.high**3 >= x.high, 'The cube-root enclosure failed.')
    return result


def next_coefficients(data):
    """g₅ = D y⁵ + E delta y³ + F delta² y + G delta phi + J y² phi."""
    D = gap_jet(1, 0, 0, data)[5]
    step = Q(1, 100)
    plus = gap_jet(1, step, 0, data)[5]
    minus = gap_jet(1, -step, 0, data)[5]
    E = (plus-minus)/(2*step)
    F = ((plus+minus)/2-D)/(step*step)
    G = gap_jet(0, 1, 1, data)[5]
    J = gap_jet(1, 0, 1, data)[5]-D
    # Reflection and weighted degree leave exactly these five monomials.
    # Additional substitutions check their reconstruction independently.
    for y, mu, beta in [(2, 3, 4), (Q(-1, 2), Q(1, 3), Q(-2, 7)), (0, -2, 3)]:
        expected = D*y**5+E*mu*y**3+F*mu*mu*y+G*mu*beta+J*y*y*beta
        residual = gap_jet(y, mu, beta, data)[5]-expected
        require(residual.low <= 0 <= residual.high, 'The degree-five reconstruction failed.')
    A, C, B = [data[k] for k in ('A_prime', 'C', 'B')]
    v0 = cuberoot(B/(4*C))
    k0 = -3*C*v0*v0/A
    R = D*v0*v0*v0*v0*v0+E*k0*v0*v0*v0+F*k0*k0*v0+G*k0+J*v0*v0
    Rv = 5*D*v0*v0*v0*v0+3*E*k0*v0*v0+F*k0*k0+2*J*v0
    k2 = -R/(2*A*v0)
    v2 = -(2*A*k2+Rv)/(12*C*v0)
    length2 = -A/C
    mirror_area = D*length2*length2*length2/6+E*length2*length2/4+F*length2/2
    result = dict(zip(('D', 'E', 'F', 'G', 'J'), (D, E, F, G, J)))
    result.update(v0=v0, k0=k0, v2=v2, k2=k2, mirror_area=mirror_area)
    advertised = [
        ('D', Q('-0.000000003686902453'), Q('-0.000000003686902452')),
        ('E', Q('-0.0000433462083'), Q('-0.0000433462082')),
        ('F', Q('-6.275628730'), Q('-6.275628728')),
        ('G', Q('78.737300156'), Q('78.737300157')),
        ('J', Q('0.00149416340585'), Q('0.00149416340586')),
        ('k2', Q(14737606110, 10**11), Q(14737606113, 10**11)),
        ('v2', Q(-8815903154, 10**8), Q(-8815903152, 10**8)),
        ('mirror_area', Q('-1704971.255'), Q('-1704971.254'))]
    for name, low, high in advertised:
        x = result[name]
        require(low < x.low <= x.high < high, f'The advertised {name} enclosure failed.')
    require(D.high < 0 and E.high < 0 and F.high < 0 < G.low and J.low > 0,
            'A weighted degree-five coefficient sign is unresolved.')
    return result


def refined_contact(phase, data):
    """Rational Newton suggestions, then an independent contraction test.

    Midpoint Newton steps are never used as a proof. Only certify_box's
    strict interval contraction decides whether the proposed box succeeds.
    """
    center = candidate(float(phase), data)
    for _ in range(4):
        f, jac = equations([I.wrap(x) for x in center], phase)
        R = inverse([[x.midpoint() for x in row] for row in jac])
        center = [outward(x-sum(R[i][j]*f[j].midpoint() for j in range(3))).midpoint()
                  for i, x in enumerate(center)]
    return certify_box(center, phase, radius=Q(1, 10**20))


def check_contacts(data, correction):
    print('Four finite contacts, certified boxes of radius 1e-20. Error bounds below are rounded outward:')
    for phase in (Q(1, 1000), Q(1, 10000), Q(1, 100000), Q(1, 1000000)):
        record = refined_contact(phase, data)
        h = cuberoot(phase)
        height = correction['v0']*h+correction['v2']*h*h*h
        weight = data['weight']+correction['k0']*h*h+correction['k2']*h*h*h*h
        dy, da = record['height']-height, record['box'][2]-weight
        require(dy.low > 0 and da.low > 0, 'The finite two-term prediction errors have unresolved signs.')
        weight_scaled = da/(phase*phase)
        height_scaled = dy/(h*h*h*h*h)
        require(Q(3, 100) < weight_scaled.low <= weight_scaled.high < Q(5, 100)
                and 80 < height_scaled.low <= height_scaled.high < 90,
                'A finite prediction error is outside its stated scaled bounds.')
        print(f'  phase {float(phase):.0e}: weight error in {decimal_bounds(da, 19)}; '
              f'height error in {decimal_bounds(dy, 15)}; '
              f'contraction < {float(record["contraction"]):.2g}.')


def check_mirror_area(data, correction):
    a0, K0 = [float(data[k].midpoint()) for k in ('weight', 'mirror_pocket_coefficient')]
    K1 = float(correction['mirror_area'].midpoint())
    L = sqrt(float((-data['A_prime']/data['C']).midpoint()))
    previous = float('inf')
    print('Numerical mirror areas; these quadratures are not interval enclosures:')
    for delta in (1e-3, 3e-4, 1e-4, 3e-5):
        fn = lambda y: gap(y, a0+delta, 0)[0]
        prediction = L*sqrt(delta)
        endpoint = bisect(fn, prediction/2, prediction*1.5)
        area, refined = [integral(fn, 0, endpoint, n) for n in (128, 256)]
        require(abs(area-refined) < 1e-8*refined+1e-12, 'The corrected mirror quadrature did not stabilize.')
        ratio = refined/(K0*delta*delta+K1*delta**3)
        error = abs(ratio-1)
        require(error < previous and error < .0001, 'The corrected mirror-area law is not converging.')
        previous = error
        print(f'  delta={delta:.0e}: area/(K0 delta² + K1 delta³) ≈ {ratio:.10f}.')


def decimal_bounds(x, places):
    """Outward decimal printing: textual bounds retain their proof meaning."""
    scale = 10**places
    low, high = x.low*scale, x.high*scale
    low = low.numerator//low.denominator
    high = -(-high.numerator//high.denominator)

    def write(n):
        return f'{"−" if n < 0 else ""}{abs(n)//scale}.{abs(n)%scale:0{places}d}'

    return f'({write(low)}, {write(high)})'


def check_primitives():
    count = 0
    for x in (Q(-17, 3), Q(-1, 3), Q(0), Q(1, 7), Q(99, 10)):
        r = outward(x)
        require(r.low <= x <= r.high and r.high-r.low <= Q(1, DENOMINATOR),
                'Outward rounding failed.')
        count += 1
    for n in list(range(100))+[10**60-1, 10**60, 10**60+1]:
        r = integer_cuberoot(n)
        require(r**3 <= n < (r+1)**3, 'Integer cube-root control failed.')
        count += 1
    for power_a, power_b in [(1, 2), (1, 3), (2, 3)]:
        for alpha, beta in [(Q(0), Q(0)), (Q(-2), Q(3)), (Q(1, 3), Q(-2, 7))]:
            phase = [I.wrap(0) for _ in range(9)]
            phase[power_a], phase[power_b] = alpha, beta
            jet = exp_i_jet(phase, 8)
            # Independently multiply the two exponential series directly
            # from factorials, rather than the recurrence under test.
            for n in range(9):
                real, imag = Q(0), Q(0)
                for j in range(9):
                    for k in range(9):
                        if power_a*j+power_b*k != n:
                            continue
                        coefficient = alpha**j*beta**k/Q(factorial(j)*factorial(k))
                        real += coefficient*(1, 0, -1, 0)[(j+k) % 4]
                        imag += coefficient*(0, 1, 0, -1)[(j+k) % 4]
                for bound, exact in zip(jet[n], (real, imag)):
                    require(bound.low <= exact <= bound.high, 'Exponential-jet control failed.')
                    count += 1
    # An invalid constant phase must be rejected, rather than silently
    # yielding coefficients for a different exponential.
    try:
        exp_i_jet([Q(1), Q(0)], 1)
    except ValueError:
        count += 1
    else:
        raise ValueError('A nonzero constant phase was incorrectly accepted.')
    print(f'{count} primitive controls passed; chart inversions and cubic reconstruction also checked.')


def main():
    check_primitives()
    data = coefficients()
    correction = next_coefficients(data)
    print('Weighted degree-five and contact coefficients, exact rational enclosures:')
    for name in ('D', 'E', 'F', 'G', 'J', 'v0', 'k0', 'v2', 'k2', 'mirror_area'):
        places = 20 if name in ('D', 'E', 'J') else 12
        print(f'  {name}: {decimal_bounds(correction[name], places)}')
    check_contacts(data, correction)
    check_mirror_area(data, correction)


if __name__ == '__main__':
    main()
