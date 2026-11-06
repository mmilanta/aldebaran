"""Independent algebra and geometry controls for radial_limit.md.

Exact rational controls check the identities, polynomial suprema, event
linearization, permutations, and invalid inputs. Floating-point controls
check independently reconstructed polar points and finite differences;
they do not make proof decisions. Standard library only.
"""

from fractions import Fraction as Q
from itertools import combinations, permutations, product
import json
from math import atan2, cos, hypot, pi, sin

from unittest.mock import patch

from blend_cusps import add, derivative, product as multiply, require, scale, trim, value
from positive_front_projection import certify
import radial_limit as limit
from radial_limit import Bounds, FIRST, THIRD, LOCAL, certify_drift_tail, scaled_triple, triple_drift


def exact_controls():
    checks = 0
    # Work in the orthonormal frame (N,N'), where q=(-u,p) and
    # q_theta=(0,a-u). Keep r² rational instead of introducing a square root.
    for u, p, a, b, mixed in product((Q(5), Q(17)),
                                   (Q(-3, 2), Q(0), Q(7, 3)),
                                   (Q(-2), Q(3)), (Q(-1), Q(4)),
                                   (Q(-5), Q(2))):
        r2 = u*u + p*p
        alpha_theta = u * (u-a) / r2
        alpha_s = (-u*mixed-p*b) / r2
        theta_s = -alpha_s / alpha_theta
        # These are r times D_theta and r times D_s at fixed theta.
        dtheta_r = p * (u-a)
        ds_r = u*b-p*mixed
        require(ds_r + dtheta_r*theta_s == r2*b/u,
                "The fixed-polar-angle route derivative identity failed.")
        require(dtheta_r / alpha_theta == p*r2/u,
                "The fixed-polar-angle angular derivative identity failed.")
        theta_m = -(p/r2)/alpha_theta
        require(-u + dtheta_r*theta_m == -r2/u,
                "The fixed-polar-angle offset derivative identity failed.")
        checks += 3

    # Exact polynomial suprema on [-1,1], with u=x² in [0,1].
    # d/du [u(1-u)^4] has its sole interior maximum at 1/5.
    shape = (Q(0), Q(1), Q(-4), Q(6), Q(-4), Q(1))
    require(derivative(shape) == multiply((Q(1), Q(-5)), (Q(1), Q(-3), Q(3), Q(-1))),
            "The mixed-derivative maximum factorization failed.")
    require(36 * value(shape, Q(1, 5)) == Q(9216, 3125) < 4,
            "The bound B=2 is too small.")
    # 4/27-u(1-u)² = (1-3u)²(4-3u)/27 >= 0.
    require(multiply((Q(1), Q(-6), Q(9)), (Q(4, 27), Q(-1, 9)))
            == (Q(4, 27), Q(-1), Q(2), Q(-1)),
            "The outer second-derivative bound factorization failed.")
    require(Q(225, 4) * Q(4, 27) == Q(25, 3) < 9,
            "The bound A=3 is too small.")
    require(trim((Q(-6), Q(36), Q(-30)))
            == trim((Q(24, 5)-30*Q(3, 5)**2, Q(36), Q(-30))),
            "The middle second derivative's completed square failed.")
    require(Q(6, 4) < 3 and Q(15, 8) > Q(2, 4),
            "The middle branch exceeds the common derivative bounds.")
    checks += 6

    # Formal epsilon jets independently verify the coordinate inversion and
    # the second-order height term at arbitrary signed height/slope jets.
    epsilon = (Q(0), Q(1))
    for h, p, a in product((Q(-3), Q(0), Q(2)), (Q(-2), Q(0), Q(3, 2)), (Q(-5), Q(1))):
        shift = (Q(0), p, p*(h+a))
        composed_h = add(add((h,), scale(shift, p)), scale(multiply(shift, shift), a/2))
        composed_p = add((p,), scale(shift, a))
        inversion = add(multiply(epsilon, composed_p), multiply(multiply(epsilon, epsilon), multiply(composed_h, composed_p)))
        require(trim(inversion[:3]) == trim(shift), "The inverse-angle epsilon jet changed.")
        square = multiply(composed_p, composed_p)
        deficit = add(add(composed_h, scale(multiply(epsilon, square), Q(-1, 2))),
                      scale(multiply(multiply(epsilon, epsilon), multiply(composed_h, square)), Q(-1, 2)))
        require(trim(deficit[:3]) == trim((h, p*p/2, p*p*(h+a)/2)),
                "The same-coordinate second-order height correction changed.")
        checks += 2

    # Independently solve the two equations by subtracting after division
    # by the slope differences; compare with the determinant solution.
    for integers in combinations(range(-3, 4), 3):
        p = tuple(map(Q, integers))
        for integers_b in product((-2, 0, 1), repeat=3):
            b = tuple(map(Q, integers_b))
            d01, d02 = (b[0]-b[1])/(p[0]-p[1]), (b[0]-b[2])/(p[0]-p[2])
            if d01 == d02:
                try:
                    triple_drift(p, b)
                except ValueError:
                    checks += 1
                else:
                    raise ValueError("A singular front event was accepted.")
                continue
            parameter = (p[2]-p[1])/(2*(d01-d02))
            angle = -(p[0]+p[1])/2-d01*parameter
            result = triple_drift(p, b)
            require(result["parameter"] == parameter and result["angle"] == angle,
                    "Independent divided-difference solution disagrees.")
            require(parameter == (p[0]-p[1])*(p[0]-p[2])*(p[1]-p[2])
                    / (2*result["jacobian_determinant"]),
                    "The parameter-drift determinant sign changed.")
            checks += 2
            for order in permutations(range(3)):
                permuted = triple_drift(tuple(p[i] for i in order), tuple(b[i] for i in order))
                require(all(permuted[key] == result[key] for key in ("parameter", "angle", "height")),
                        "Relabeling the three visits changed the drift.")
                checks += 1
            shifted = triple_drift(tuple(x+Q(9, 7) for x in p), b)
            require(shifted["parameter"] == parameter
                    and shifted["angle"] == angle-Q(9, 7),
                    "A common slope shift changed the parameter drift.")
            reversed_angle = triple_drift(tuple(-x for x in p), b)
            require(reversed_angle["parameter"] == parameter and reversed_angle["angle"] == -angle,
                    "Reversing the angular coordinate changed the parameter drift.")
            reversed_time = triple_drift(p, tuple(-x for x in b))
            require(reversed_time["parameter"] == -parameter and reversed_time["angle"] == angle,
                    "Reversing the route parameter changed the drift incorrectly.")
            checks += 3

    # Input controls distinguish exact rationals from booleans and floats.
    good = (Q(1), Q(2), Q(3), Q(4), Q(5))
    invalid = [lambda: Bounds(*((Q(-1),)+good[1:])),
               lambda: Bounds(*(good[:3]+(1.0, Q(5)))),
               lambda: Bounds(*(good[:3]+(True, Q(5)))),
               lambda: LOCAL.at(Q(4)), lambda: LOCAL.at(Q(-25)),
               lambda: LOCAL.at(25), lambda: LOCAL.at(25.0),
               lambda: triple_drift((Q(0), Q(0), Q(1)), (Q(1), Q(0), Q(0))),
               lambda: triple_drift((Q(0), Q(1)), (Q(1), Q(0))),
               lambda: triple_drift((Q(0), Q(1), Q(2)), (Q(1), 0, Q(0)))]
    for callback in invalid:
        try:
            callback()
        except ValueError:
            checks += 1
        else:
            raise ValueError("Malformed bounds or triple jets were accepted.")
    zero = Bounds(*(Q(0) for _ in range(5))).at(Q(1))
    require(all(x == 0 for x in zero.values()), "Constant zero height must have zero errors.")
    checks += 1
    proof = certify_drift_tail()
    for row in proof:
        expected = 1 if row["side"] == "lower" else -1
        require(row["root_residual"].sign() == row["parameter_residual"].sign() == expected,
                "An all-offset residual sign was lost.")
        checks += 1
    for name, wrong in (("FIRST", FIRST+Q(1, 10**12)), ("THIRD", THIRD-Q(1, 10**12))):
        with patch.object(limit, name, wrong):
            try:
                certify_drift_tail()
            except ValueError:
                checks += 1
            else:
                raise ValueError("A corrupted drift coefficient passed the uniform proof.")
    # Independently bracket actual roots, then compare exact rational errors
    # at ordinary offsets and a large distance where floats lose this term.
    for offset in (25, 26, 30, 50, 100, 1000, 10000, 10**6):
        angle, delta = certify(offset, bits=160)
        approximation = FIRST/offset+THIRD/offset**3
        require(approximation < delta.low < delta.high < approximation+Q(40, offset**5),
                "A fresh independent root bracket left the uniform corrected law.")
        require(0 < delta.low < delta.high < FIRST/offset,
                "The local clock is not below its first-order prediction.")
        checks += 2
    # Exact rescaling and height-origin controls. All three models share
    # the same dimensionless equations, so compare complete root intervals.
    for width in (Q(1), Q(1, 2), Q(3, 53), Q(1, 1000)):
        normalized = 25/width**2
        original = scaled_triple(width, Q(1), Q(0), normalized)
        shifted = scaled_triple(width, Q(1), Q(10), normalized+10)
        enlarged = scaled_triple(width, Q(3), Q(0), normalized*3)
        require(original == shifted == enlarged, "An exact local scale or height-origin change moved the root.")
        require(0 < original[0].low < original[0].high < Q(1, 8), "A scaled root left its local window.")
        slopes = (Q(15, 8)/width, Q(0), Q(-15, 8)/width)
        require(triple_drift(slopes, (Q(0), Q(1), Q(0)))["parameter"] == FIRST/width**2,
                "The local drift lost its squared-width scaling.")
        checks += 3
    canonical = scaled_triple(Q(3, 53), Q(1), Q(10), Q(7813))
    require(Q(7813)-10 >= 25/Q(3, 53)**2 and 0 < canonical[1].low < canonical[1].high < Q(1, 4),
            "The isolated canonical block's explicit threshold failed.")
    checks += 1
    for width, height, base, offset in [
        (Q(0), Q(1), Q(0), Q(25)), (Q(2), Q(1), Q(0), Q(25)),
        (Q(1), Q(0), Q(0), Q(25)), (Q(1), Q(1), Q(0), Q(24)),
        (Q(1, 2), Q(1), Q(10), Q(109)), (Q(1), Q(1), Q(0), 25.0),
    ]:
        try:
            scaled_triple(width, height, base, offset)
        except ValueError:
            checks += 1
        else:
            raise ValueError("An invalid rescaled local model was accepted.")
    return checks


def branch(theta, delta, which):
    """Independent numerical polynomial jets, in descending powers."""
    x = theta
    if which == 1:
        return (delta*(1-3*x*x+3*x**4-x**6),
                delta*(-6*x+12*x**3-6*x**5),
                delta*(-6+36*x*x-30*x**4),
                1-3*x*x+3*x**4-x**6, -6*x+12*x**3-6*x**5)
    sign = 1 if which == 0 else -1
    return (sign*(3*x**5-10*x**3+15*x)/8,
            sign*(15*x**4-30*x*x+15)/8,
            sign*(60*x**3-60*x)/8, 0, 0)


def polar(alpha, delta, which, offset):
    """Invert atan2 of independently constructed Cartesian points."""
    lo, hi = -1., 1.
    for _ in range(52):
        theta = (lo+hi)/2
        h, p, a, b, mixed = branch(theta, delta, which)
        q = ((h-offset)*cos(theta)-p*sin(theta),
             (h-offset)*sin(theta)+p*cos(theta))
        if atan2(-q[1], -q[0]) < alpha:
            lo = theta
        else:
            hi = theta
    theta = (lo+hi)/2
    h, p, a, b, mixed = branch(theta, delta, which)
    u = offset-h
    r = hypot(u, p)
    # Stable deficit; the Cartesian radius is checked separately below.
    deficit = h-p*p/(r+u)
    return deficit, theta, r, p*r/u, b*r/u


def numeric_controls():
    checks, worst_angle, worst_route = 0, 0., 0.
    for offset, delta, which in product((25, 100, 1000), (-.25, -.07, 0., .13, .25), range(3)):
        bounds = {k: float(v) for k, v in LOCAL.at(Q(offset)).items()}
        for k in range(41):
            alpha = -.96+k*.048
            deficit, theta, radius, d_alpha, d_s = polar(alpha, delta, which, offset)
            h, p, a, b, mixed = branch(alpha, delta, which)
            require(-2e-14 <= deficit-h <= bounds["height"]+2e-14,
                    "A sampled same-coordinate height left the analytic envelope.")
            require(abs(theta-alpha) <= bounds["angle"]+2e-14,
                    "A sampled normal angle left the analytic envelope.")
            require(abs(d_alpha-p) <= bounds["angle_derivative"]+2e-14
                    and abs(d_s-b) <= bounds["route_derivative"]+2e-14,
                    "A sampled derivative left the analytic envelope.")
            require(abs(deficit-h-p*p/(2*offset)) <= bounds["first_order_remainder"]+2e-14,
                    "A sampled first-order correction left its analytic envelope.")
            ht, pt, *_ = branch(theta, delta, which)
            q = ((ht-offset)*cos(theta)-pt*sin(theta), (ht-offset)*sin(theta)+pt*cos(theta))
            require(abs(hypot(*q)-radius) < 3e-12 and abs(offset-hypot(*q)-deficit) < 3e-12,
                    "Cartesian reconstruction disagrees with the radial deficit.")
            step = 1e-5
            da = (polar(alpha+step, delta, which, offset)[0]
                  - polar(alpha-step, delta, which, offset)[0])/(2*step)
            ds = (polar(alpha, delta+step, which, offset)[0]
                  - polar(alpha, delta-step, which, offset)[0])/(2*step)
            worst_angle = max(worst_angle, abs(da-d_alpha))
            worst_route = max(worst_route, abs(ds-d_s))
            require(abs(da-d_alpha) < 2e-8 and abs(ds-d_s) < 2e-8,
                    "Independent finite differences disagree with the derivative identities.")
            larger = polar(alpha, delta, which, 2*offset)[0]
            require(h-2e-14 <= larger <= deficit+2e-14,
                    "Increasing the offset violated one-sided convergence.")
            checks += 8

    # Follow the certified point through the three actual plane branches.
    for offset in (25, 100, 1000, 10000):
        angle, delta = certify(offset, bits=120)
        x, d = float(angle.midpoint()), float(delta.midpoint())
        for theta, which in ((x, 0), (0, 1), (-x, 2)):
            h, p, *_ = branch(theta, d, which)
            point = ((h-offset)*cos(theta)-p*sin(theta), (h-offset)*sin(theta)+p*cos(theta))
            require(hypot(point[0]-(d-offset), point[1]) < 4e-12,
                    "A certified local triple failed Cartesian reconstruction.")
            checks += 1
    return checks, worst_angle, worst_route


def periodic_controls():
    """Exercise a different support family across an eleven-turn seam."""
    bounds = Bounds(Q(7, 2), Q(15, 22), Q(47, 242), Q(1), Q(5, 11))
    period = 22*pi

    def jet(theta, s):
        t = theta/11
        return (2*sin(t)+cos(3*t)+s*cos(5*t),
                (2*cos(t)-3*sin(3*t)-5*s*sin(5*t))/11,
                (-2*sin(t)-9*cos(3*t)-25*s*cos(5*t))/121,
                cos(5*t), -5*sin(5*t)/11)

    def invert(alpha, s, offset):
        lo, hi = alpha-pi/2, alpha+pi/2
        for _ in range(55):
            theta = (lo+hi)/2
            h, p, *_ = jet(theta, s)
            if theta-atan2(p, offset-h) < alpha:
                lo = theta
            else:
                hi = theta
        theta = (lo+hi)/2
        h, p, a, b, mixed = jet(theta, s)
        radius = hypot(offset-h, p)
        return (h-p*p/(radius+offset-h), theta,
                p*radius/(offset-h), b*radius/(offset-h))

    checks, worst_a, worst_s = 0, 0., 0.
    angles = [k*2*pi+delta for k in (-12, -1, 0, 1, 10, 11, 12, 22)
              for delta in (-1e-6, 0., 1e-6)]
    for offset, s, alpha in product((4, 10, 1000), (-.5, -.13, 0., .31, .5), angles):
        envelope = {k: float(v) for k, v in bounds.at(Q(offset)).items()}
        d, theta, da, ds = invert(alpha, s, offset)
        h, p, a, b, mixed = jet(alpha, s)
        require(-1e-13 <= d-h <= envelope["height"]+1e-13, "A periodic strand violated one-sided convergence.")
        require(abs(theta-alpha) <= envelope["angle"]+1e-13, "The periodic coordinate change left its bound.")
        require(abs(da-p) <= envelope["angle_derivative"]+1e-13
                and abs(ds-b) <= envelope["route_derivative"]+1e-13, "A periodic derivative left its bound.")
        require(abs(d-h-p*p/(2*offset)) <= envelope["first_order_remainder"]+1e-13,
                "A periodic first correction left its remainder bound.")
        shifted = invert(alpha+period, s, offset)
        require(abs(shifted[0]-d) < 5e-14 and abs(shifted[1]-theta-period) < 5e-14,
                "The eleven-turn coordinate seam changed the deficit or inverse.")
        step = 1e-5
        fd_a = (invert(alpha+step, s, offset)[0]-invert(alpha-step, s, offset)[0])/(2*step)
        fd_s = (invert(alpha, s+step, offset)[0]-invert(alpha, s-step, offset)[0])/(2*step)
        worst_a, worst_s = max(worst_a, abs(fd_a-da)), max(worst_s, abs(fd_s-ds))
        require(abs(fd_a-da) < 2e-8 and abs(fd_s-ds) < 2e-8, "Periodic derivative finite differences disagree.")
        checks += 6
    return checks, worst_a, worst_s


def main():
    exact = exact_controls()
    require(json.loads((limit.HERE / "radial_limit.json").read_text()) == limit.record(),
            "The archived illustration record differs from fresh rational proofs.")
    exact += 1
    numeric, angle_error, route_error = numeric_controls()
    periodic, seam_angle, seam_route = periodic_controls()
    print(f"{exact:,} exact controls: derivative cancellations, local polynomial suprema, independent drift solutions, relabeling, coordinate changes, and invalid inputs.")
    print(f"{numeric:,} numerical controls: Cartesian polar inversion, analytic envelopes, both derivatives, monotonicity, and local plane triples.")
    print(f"Largest finite-difference errors: angular {angle_error:.4g}, route {route_error:.4g}.")
    print(f"{periodic:,} additional periodic controls cross the eleven-turn seam; finite-difference errors {seam_angle:.4g}, {seam_route:.4g}.")
    print("Uniform estimates and the general event-shift theorem are analytic; sampled checks do not establish a full-movie threshold.")


if __name__ == "__main__":
    main()
