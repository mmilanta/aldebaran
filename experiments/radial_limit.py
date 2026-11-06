"""Quantitative radial limits and the drift of an ordinary front triple.

Standard library only. The analytic argument is in radial_limit.md.
All reported envelopes and local root brackets are rational. Numerical
drawings and sampled checks are kept separate from proof decisions.
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction as Q
import json
from math import factorial
from pathlib import Path

from blend_cusps import Interval as I, add, bound, product, require, scale
from positive_front_projection import certify, decimal_enclosure, f, first, second, trig

HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Bounds:
    """Suprema of |h|, |h_theta|, |h_theta_theta|, |h_s|, |h_theta_s|."""

    height: Q
    slope: Q
    second: Q
    rate: Q
    mixed: Q

    def __post_init__(self):
        require(all(type(x) is Q and x >= 0 for x in self.__dict__.values()),
                "Use nonnegative rational derivative bounds.")

    def at(self, offset):
        require(type(offset) is Q and offset > self.height + self.second,
                "The rational offset must exceed H+A.")
        H, P, A, S, B = self.height, self.slope, self.second, self.rate, self.mixed
        R = offset - H
        return {
            "angle": P / R,
            "height": P * P / (2 * R),
            "angle_derivative": A * P / R + P**3 / (2 * R**2),
            "route_derivative": B * P / R + S * P**2 / (2 * R**2),
            "first_order_remainder": (H + A) * P**2 / (2 * R**2) + P**4 / (24 * R**3),
        }


def triple_drift(slopes, rates):
    """First-order (polar angle, route parameter, height) at a front triple.

    The coefficient of 1/M is exact. Distinct slopes and a nonsingular
    two-equation event Jacobian are necessary; degenerate input rejects.
    This is a local asymptotic, not a finite-M event certificate.
    """
    require(type(slopes) in (tuple, list) and type(rates) in (tuple, list)
            and len(slopes) == len(rates) == 3
            and all(type(x) is Q for x in (*slopes, *rates)),
            "Use three rational slopes and three rational route rates.")
    require(len(set(slopes)) == 3, "An ordinary triple needs three distinct slopes.")
    p, b = slopes, rates
    j00, j01 = p[0] - p[1], b[0] - b[1]
    j10, j11 = p[0] - p[2], b[0] - b[2]
    determinant = j00 * j11 - j01 * j10
    require(determinant != 0, "The front event Jacobian is singular.")
    f0, f1 = -(p[0]**2 - p[1]**2) / 2, -(p[0]**2 - p[2]**2) / 2
    angle = (f0 * j11 - j01 * f1) / determinant
    parameter = (j00 * f1 - f0 * j10) / determinant
    height = p[0] * angle + b[0] * parameter + p[0]**2 / 2
    require(parameter != 0, "Distinct ordinary slopes cannot have zero leading parameter drift.")
    require(all(p[i] * angle + b[i] * parameter + p[i]**2 / 2 == height
                for i in range(3)), "The three leading heights disagree.")
    return {"angle": angle, "parameter": parameter, "height": height,
            "normal_angles": tuple(angle + x for x in p),
            "jacobian_determinant": determinant}


LOCAL = Bounds(Q(1), Q(15, 8), Q(3), Q(1), Q(2))
FIRST = Q(225, 128)
THIRD = Q(-151875, 32768)


def power(polynomial, exponent):
    result = (Q(1),)
    for _ in range(exponent):
        result = product(result, polynomial)
    return result


def trig_polynomial(squared_angle, sinc=False):
    """Five even Taylor terms, in a polynomial squared angle."""
    result = (Q(0),)
    for k in range(5):
        coefficient = Q((-1)**k, factorial(2*k+(1 if sinc else 0)))
        result = add(result, scale(power(squared_angle, k), coefficient))
    return result


def certify_drift_tail():
    """Prove 0 < delta-FIRST/M-THIRD/M³ < 40/M⁵ for every M>=25.

    Set tau=1/M² and x=sqrt(tau) U(tau). Sign tests after exact
    cancellation of tau² cover the closed interval [0,1/625], including
    its limit at infinity. Taylor remainders are bounded analytically.
    The proof reads no root archive and needs no floating-point hints.
    """
    domain = I(Q(0), Q(1, 625))
    tau = (Q(0), Q(1))
    a, b, c = Q(15, 8), Q(-5, 4), Q(3, 8)
    lower = (a, Q(-1125, 128), Q(102))
    upper = (a, Q(-1125, 128), Q(106), Q(-1500))
    require(4-1500*domain.high > 0, "The global scaled root brackets cross.")
    output = []

    def magnitude(polynomial):
        interval = bound(polynomial, domain)
        return max(abs(interval.low), abs(interval.high))

    def residual(polynomial, error):
        require(polynomial[:2] == (0, 0), "The drift coefficients do not cancel exactly.")
        interval = bound(polynomial[2:], domain)
        return I(interval.low-error, interval.high+error)

    for side, U in (("lower", lower), ("upper", upper)):
        enclosure = bound(U, domain)
        require(0 < enclosure.low <= enclosure.high < 2 and Q(2, 25) < Q(1, 8),
                "The all-offset root bracket left the Taylor window.")
        U2 = power(U, 2)
        z = product(tau, U2)
        # f(x)=sqrt(tau)*odd; f'(x)=first.
        odd = add(add(scale(U, a), scale(product(tau, power(U, 3)), b)),
                  scale(product(power(tau, 2), power(U, 5)), c))
        first = add(add((a,), scale(product(tau, U2), 3*b)),
                    scale(product(power(tau, 2), power(U, 4)), 5*c))
        coefficient = add(product(tau, product(odd, U)), scale(U, -1))
        equation = add(product(coefficient, trig_polynomial(z, sinc=True)),
                       product(first, trig_polynomial(z)))
        # z<=4*tau. The first omitted terms are z^5/11! and z^5/10!.
        error = (magnitude(coefficient)*Q(4**5, factorial(11))
                 + magnitude(first)*Q(4**5, factorial(10))) * domain.high**3
        root_sign = residual(equation, error)
        require(root_sign.low > 0 if side == "lower" else root_sign.high < 0,
                "The all-offset root residual has no strict sign.")

        target = (FIRST, THIRD, Q(0 if side == "lower" else 40))
        coefficient = add(odd, scale(target, -1))
        other = scale(product(first, U), Q(-1, 2))
        half_z = scale(z, Q(1, 4))
        equation = add(product(coefficient, trig_polynomial(half_z)),
                       product(other, trig_polynomial(half_z, sinc=True)))
        # (delta(x)/sqrt(tau)-target)*cos(x/2), with half_z<=tau.
        error = (magnitude(coefficient)/factorial(10)
                 + magnitude(other)/factorial(11)) * domain.high**3
        parameter_sign = residual(equation, error)
        require(parameter_sign.low > 0 if side == "lower" else parameter_sign.high < 0,
                "The all-offset parameter residual has no strict sign.")
        output.append({"side": side, "scaled_root": U,
                       "root_residual": root_sign, "parameter_residual": parameter_sign})

    require(FIRST+THIRD*domain.high > 0, "The lower parameter bound is not positive.")
    require((FIRST+40*domain.high**2)/25 < Q(1, 4), "The upper parameter left its controls.")
    require(40*domain.high < -THIRD, "The corrected bound no longer lies below the leading term.")
    return output


def outward(interval, bits=40):
    """Small outward dyadic bounds for displaying exact residual signs."""
    denominator = 2**bits
    lo = (interval.low*denominator).__floor__()
    hi = (interval.high*denominator).__ceil__()
    return [str(Q(lo, denominator)), str(Q(hi, denominator))]


def scaled_triple(width, height, base, offset, bits=120):
    """Certify the three-arc model h=C+L(f,delta*g,-f), theta=w*x.

    0<w<=1, L>0 and M-C>=25L/w² suffice. This says nothing about
    unused strands or the coordinate-aligning stages of the whole movie.
    The local x bracket is in [0,1/8]; actual normal angles are +/-w*x.
    """
    require(all(type(x) is Q for x in (width, height, base, offset))
            and 0 < width <= 1 and height > 0 and offset > 0,
            "Use rational 0<w<=1, L>0, C and M>0.")
    require(offset-base >= 25*height/width**2,
            "The local model needs M-C>=25L/w².")
    require(type(bits) is int and bits >= 80, "Use at least eighty rational bisections.")
    effective = (offset-base)/height

    def equation(x):
        return (f(x)-effective)*trig(width*x) + first(x)*trig(width*x, True)/width

    lo, hi = Q(0), Q(1, 8)
    require(equation(lo).low > 0 and equation(hi).high < 0,
            "The rescaled root bracket has no sign change.")
    for _ in range(bits):
        mid = (lo+hi)/2
        enclosure = equation(mid)
        if enclosure.low > 0:
            lo = mid
        else:
            require(enclosure.high < 0, "Taylor error obscures a scaled root sign.")
            hi = mid
    require(equation(lo).low > 0 and equation(hi).high < 0,
            "The final rescaled root bracket lost its signs.")
    h = I(f(lo), f(hi))
    p = I(first(hi), first(lo))
    half_sin = I(trig(width*lo/2).low, trig(width*hi/2).high)
    half_cos = I(trig(width*hi/2, True).low, trig(width*lo/2, True).high)
    delta = h-p*half_sin/half_cos/width
    require(0 < delta.low <= delta.high < Q(1, 4), "The rescaled triple left its parameter controls.")
    radius_outer = effective-h-I(second(hi), second(lo))/width**2
    radius_middle = effective-delta*(1-6/width**2)
    sine = I(trig(width*lo).low, trig(width*hi).high)
    cosine = I(trig(width*hi, True).low, trig(width*lo, True).high)
    determinant = radius_outer*radius_outer*radius_middle*2*sine*cosine
    require(radius_outer.low > 0 and determinant.low > 0,
            "The rescaled ordinary-triple determinant was not separated.")
    return I(lo, hi), delta


def record():
    drift = triple_drift((Q(15, 8), Q(0), Q(-15, 8)), (Q(0), Q(1), Q(0)))
    examples = []
    for offset in (25, 100, 1000, 10000):
        angle, delta = certify(offset, bits=120)
        examples.append({
            "offset": offset,
            "angle": outward(angle, bits=128),
            "parameter": outward(delta, bits=128),
            "envelopes": {k: str(v) for k, v in LOCAL.at(Q(offset)).items()},
        })
    tail = certify_drift_tail()
    return {
        "scope": "Uniform analytic envelopes, an all-M>=25 local drift certificate, and four local triple brackets; no whole-movie threshold.",
        "local_bounds": {k: str(v) for k, v in LOCAL.__dict__.items()},
        "local_drift": {k: [str(x) for x in v] if isinstance(v, tuple) else str(v)
                        for k, v in drift.items()},
        "uniform_local_drift": {
            "offset_from": 25,
            "first_coefficient": str(FIRST), "third_coefficient": str(THIRD),
            "positive_fifth_order_remainder_upper": "40",
            "tau_domain": ["0", "1/625"],
            "proof": [{"side": row["side"],
                       "scaled_root": list(map(str, row["scaled_root"])),
                       "root_residual": outward(row["root_residual"]),
                       "parameter_residual": outward(row["parameter_residual"])} for row in tail],
        },
        "examples": examples,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write fresh rational local brackets and bounds")
    args = parser.parse_args()
    result = record()
    print("At the same polar angle: 0 <= D_M-h <= P^2/[2(M-H)].")
    print("Local triple drift: alpha_1=0, delta_1=225/128; the three normals drift by 15/8, 0, -15/8.")
    print("Every M>=25: delta=225/(128M)-151875/(32768M^3)+R, with 0<R<40/M^5.")
    for row in result["examples"]:
        low, high = map(Q, row["parameter"])
        print(f"M={row['offset']}: delta in {decimal_enclosure(I(low, high))}; "
              f"uniform height error <= {float(Q(row['envelopes']['height'])):.9g}.")
    if args.write:
        (HERE / "radial_limit.json").write_text(json.dumps(result, indent=2) + "\n")
        print("Wrote radial_limit.json from fresh rational brackets.")
    print("Analytic bounds assume the displayed derivative suprema; no global event count or middle threshold is inferred.")


if __name__ == "__main__":
    main()
