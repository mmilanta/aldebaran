"""The smaller pocket left after correcting the leading triple clock.

Exact second-order drift coefficients and independent Cartesian Taylor
jets. Numerical four-variable event solves and small curved polygons
check the asymptotics separately. No uniform finite-offset certificate
or full-drawing face census is claimed. Standard library only.
"""

from fractions import Fraction as Q
from itertools import permutations, product
from math import atan, cos, factorial, fsum, sin

from blend_cusps import require
from parabolic_triangle import inputs
from positive_front_projection import f, first, second
from radial_limit import FIRST, THIRD, triple_drift
from triple_area import coefficient, cross


def second_drift(slopes, rates, seconds, mixed, route_seconds, height):
    inputs(slopes, rates)
    require(all(type(v) in (tuple, list) and len(v) == 3
                and all(type(x) is Q for x in v) for v in (seconds, mixed, route_seconds))
            and type(height) is Q, "Use rational second derivatives and a rational common height.")
    first_order = triple_drift(slopes, rates)
    a, c = first_order["angle"], first_order["parameter"]
    p, b, k, d, e = slopes, rates, seconds, mixed, route_seconds
    residual = tuple(k[i]*(a+p[i])**2/2+d[i]*c*(a+p[i])+e[i]*c*c/2+height*p[i]**2/2
                     for i in range(3))
    j00, j01, j10, j11 = p[0]-p[1], b[0]-b[1], p[0]-p[2], b[0]-b[2]
    u, v = residual[1]-residual[0], residual[2]-residual[0]
    determinant = first_order["jacobian_determinant"]
    a2 = (u*j11-j01*v)/determinant
    c2 = (j00*v-u*j10)/determinant
    height2 = p[0]*a2+b[0]*c2+residual[0]
    normal2 = tuple(a2+k[i]*(a+p[i])+d[i]*c+height*p[i] for i in range(3))
    V = abs((p[0]-p[1])*(p[0]-p[2])*(p[1]-p[2]))
    K = determinant**2/(2*V)
    return {"first": first_order, "residuals": residual,
            "angle": a2, "parameter": c2, "height": height2,
            "normal_angles": normal2, "quadratic_area": K,
            "retimed_area": K*c2*c2}


def add(a, b):
    return {n: a.get(n, Q(0))+b.get(n, Q(0)) for n in a.keys() | b.keys()}


def scale(a, c):
    return {n: x*c for n, x in a.items()}


def multiply(a, b):
    out = {}
    for i, x in a.items():
        for j, y in b.items():
            if -1 <= i+j <= 6:
                out[i+j] = out.get(i+j, Q(0))+x*y
    return out


def power(a, n):
    out = {0: Q(1)}
    for _ in range(n):
        out = multiply(out, a)
    return out


def cartesian_jet(p, b, k, d, e, h0, normal1, normal2, c1, c2):
    """Compose Cartesian q directly, without the radial graph expansion."""
    theta, route = {1: normal1, 2: normal2}, {1: c1, 2: c2}
    h = add({0: h0}, add(scale(theta, p), scale(route, b)))
    h = add(h, add(scale(power(theta, 2), k/2),
                   add(scale(multiply(theta, route), d), scale(power(route, 2), e/2))))
    slope = add({0: p}, add(scale(theta, k), scale(route, d)))
    sine, cosine = {}, {}
    for j in range(3):
        sine = add(sine, scale(power(theta, 2*j+1), Q((-1)**j, factorial(2*j+1))))
    for j in range(4):
        cosine = add(cosine, scale(power(theta, 2*j), Q((-1)**j, factorial(2*j))))
    distance = add(h, {-1: Q(-1)})
    return (add(multiply(distance, cosine), scale(multiply(slope, sine), -1)),
            add(multiply(distance, sine), multiply(slope, cosine)))


PROFILES = (
    ((-2, 1, 2), (0, 1, 0)),
    ((-3, -1, 2), (1, 0, 2)),
    ((0, 2, 5), (-1, 3, 0)),
)


def exact_controls():
    count = 0
    for profile, h0, k0, d0, e0 in product(PROFILES, (Q(-3, 2), Q(0), Q(3, 5)),
            ((0, 0, 0), (1, -2, 3), (-2, 1, -1)),
            ((0, 0, 0), (-1, 2, 0), (3, -2, 1)),
            ((0, 0, 0), (2, 1, -1), (-1, 0, 2))):
        p, b = [tuple(map(Q, v)) for v in profile]
        k, d, e = [tuple(map(Q, v)) for v in (k0, d0, e0)]
        result = second_drift(p, b, k, d, e, h0)
        old = result["first"]
        a, c, a2, c2 = old["angle"], old["parameter"], result["angle"], result["parameter"]
        require(all(p[i]*a2+b[i]*c2+result["residuals"][i] == result["height"] for i in range(3)),
                "The three second-order graph heights disagree.")
        require(coefficient([(Q(1), x) for x in p], [(Q(0), x) for x in result["residuals"]])
                == result["retimed_area"], "The second blow-up area disagrees with its independent determinant formula.")
        count += 1
        for i in range(3):
            x, y = cartesian_jet(p[i], b[i], k[i], d[i], e[i], h0,
                                 a+p[i], result["normal_angles"][i], c, c2)
            expected_x = {-1: Q(-1), 0: h0, 1: old["height"]+a*a/2,
                          2: result["height"]+a*a2-h0*a*a/2}
            expected_y = {0: -a, 1: h0*a-a2}
            require(all(x.get(n, Q(0)) == v for n, v in expected_x.items())
                    and all(y.get(n, Q(0)) == v for n, v in expected_y.items()),
                    "Independent Cartesian Taylor jets do not meet to second order.")
            count += 1
        if not any((*k, *d, *e)):
            require(a2 == h0*a and c2 == h0*c, "A pure height change did not replace M by M-h0.")
            count += 1

    p, b = [tuple(map(Q, v)) for v in PROFILES[0]]
    k, d, e = [tuple(map(Q, v)) for v in ((1, -2, 3), (-1, 2, 0), (2, 1, -1))]
    result = second_drift(p, b, k, d, e, Q(3, 5))
    require(result["angle"] == Q(19, 32) and result["parameter"] == Q(519, 160)
            and result["height"] == Q(581, 80) and result["retimed_area"] == Q(89787, 12800),
            "The displayed asymmetric second-order coefficients changed.")
    count += 1
    for order in permutations(range(3)):
        values = [tuple(v[i] for i in order) for v in (p, b, k, d, e)]
        other = second_drift(*values, Q(3, 5))
        require(all(other[name] == result[name] for name in ("angle", "parameter", "height", "quadratic_area", "retimed_area")),
                "Relabeling changed the second-order drift or area.")
        count += 1
    # A nonlinear change s=lambda*r+nu*r^2/2 changes clock coefficients,
    # while the physical event's angle, height, and normals are unchanged.
    c1 = result["first"]["parameter"]
    for lam, nu in product((Q(-2), Q(1, 2), Q(3)), (Q(-3), Q(0), Q(4))):
        changed = second_drift(p, tuple(lam*x for x in b), k, tuple(lam*x for x in d),
                               tuple(lam*lam*x+nu*y for x, y in zip(e, b)), Q(3, 5))
        expected_clock = result["parameter"]/lam-nu*c1*c1/(2*lam**3)
        require(changed["first"]["parameter"] == c1/lam
                and changed["parameter"] == expected_clock
                and all(changed[name] == result[name] for name in ("angle", "height", "normal_angles")),
                "The second-order event coefficients do not respect route reparameterization.")
        require(changed["retimed_area"] == result["quadratic_area"]
                *(result["parameter"]-nu*c1*c1/(2*lam*lam))**2,
                "The leading-clock area does not respect nonlinear retiming.")
        count += 1
    nu = 2*result["parameter"]/(c1*c1)
    retimed = second_drift(p, b, k, d, tuple(x+nu*y for x, y in zip(e, b)), Q(3, 5))
    require(retimed["parameter"] == retimed["retimed_area"] == 0,
            "Matching the second clock coefficient did not cancel the inverse-cube area term.")
    count += 1
    a = Q(15, 8)
    zeros = (Q(0),)*3
    symmetric = second_drift((a, Q(0), -a), (Q(0), Q(1), Q(0)), zeros, zeros, zeros, Q(0))
    require(symmetric["parameter"] == symmetric["retimed_area"] == 0
            and symmetric["quadratic_area"] == 1/a, "The symmetric model should have no second-order clock correction.")
    require(symmetric["quadratic_area"]*THIRD**2 == Q(1537734375, 134217728),
            "The symmetric fifth-order retimed area coefficient changed.")
    count += 1
    for bad in (0, 0.0, True):
        try:
            second_drift(p, b, k, d, e, bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("A non-rational height was accepted.")
    return count


def solve(matrix, rhs):
    a = [list(row)+[x] for row, x in zip(matrix, rhs)]
    for j in range(len(a)):
        pivot = max(range(j, len(a)), key=lambda i: abs(a[i][j]))
        a[j], a[pivot] = a[pivot], a[j]
        require(abs(a[j][j]) > 1e-10, "A numerical event matrix lost rank.")
        divisor = a[j][j]
        a[j] = [x/divisor for x in a[j]]
        for i in range(len(a)):
            if i != j:
                factor = a[i][j]
                a[i] = [x-factor*y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


class QuadraticModel:
    def __init__(self, profile, height, seconds, mixed, route_seconds):
        self.p, self.b = [tuple(map(float, v)) for v in profile]
        self.height = float(height)
        self.k, self.d, self.e = [tuple(map(float, v)) for v in (seconds, mixed, route_seconds)]
        self.proof = second_drift(*[tuple(map(Q, v)) for v in profile],
                                 *[tuple(map(Q, v)) for v in (seconds, mixed, route_seconds)], Q(height))

    def support(self, i, theta, route):
        p, b, k, d, e = (v[i] for v in (self.p, self.b, self.k, self.d, self.e))
        change = p*theta+b*route+k*theta*theta/2+d*theta*route+e*route*route/2
        return change, p+k*theta+d*route, k, b+d*theta+e*route, d

    def point(self, i, sigma, mu, offset):
        theta, route = sigma/offset, mu/offset
        h, p, k, rate, mixed = self.support(i, theta, route)
        half, sine, cosine = sin(theta/2)**2, sin(theta), cos(theta)
        point = (offset*(2*(offset-self.height)*half+h*cosine-p*sine),
                 (self.height+h-offset)*sine+p*cosine)
        radius = self.height+h+k-offset
        velocity = (-radius*sine, radius*cosine/offset)
        motion = (rate*cosine-mixed*sine, (rate*sine+mixed*cosine)/offset)
        return point, velocity, motion

    def event(self, offset):
        initial = self.proof["first"]
        x = [float(v) for v in (*initial["normal_angles"], initial["parameter"])]
        for _ in range(12):
            values = [self.point(i, x[i], x[3], offset) for i in range(3)]
            residual, matrix = [], []
            for j in (1, 2):
                for axis in (0, 1):
                    row = [0.]*4
                    row[0], row[j] = values[0][1][axis], -values[j][1][axis]
                    row[3] = values[0][2][axis]-values[j][2][axis]
                    matrix.append(row)
                    residual.append(values[0][0][axis]-values[j][0][axis])
            delta = solve(matrix, [-r for r in residual])
            x = [u+v for u, v in zip(x, delta)]
            if max(map(abs, delta)) < 1e-13:
                break
        points = [self.point(i, x[i], x[3], offset)[0] for i in range(3)]
        require(max(abs(a-b) for p in points[1:] for a, b in zip(p, points[0])) < 2e-12,
                "The four-variable numerical triple residual is unresolved.")
        change, p, *_ = self.support(0, x[0]/offset, x[3]/offset)
        polar = x[0]-offset*atan(p/(offset-self.height-change))
        return x, polar


def pocket(model, offset, mu, steps):
    initial = model.proof["first"]
    intersections = []
    for i, j in ((0, 1), (1, 2), (0, 2)):
        s, t = (float(initial["normal_angles"][a]) for a in (i, j))
        for _ in range(12):
            p, v, _ = model.point(i, s, mu, offset)
            q, w, _ = model.point(j, t, mu, offset)
            difference = (p[0]-q[0], p[1]-q[1])
            determinant = cross(v, w)
            require(abs(determinant) > .1, "A numerical pocket pair lost transversality.")
            ds, dt = -cross(difference, w)/determinant, -cross(difference, v)/determinant
            s, t = s+ds, t+dt
            if max(abs(ds), abs(dt)) < 1e-13:
                break
        a = model.point(i, s, mu, offset)[0]
        b = model.point(j, t, mu, offset)[0]
        require(max(abs(u-v) for u, v in zip(a, b)) < 2e-12,
                "A numerical pocket crossing is unresolved.")
        intersections.append((s, t))
    ab, bc, ac = intersections
    center = model.point(0, ac[0], mu, offset)[0]
    points = []
    for which, start, end in ((1, ab[1], bc[0]), (2, bc[1], ac[1]), (0, ac[0], ab[0])):
        for j in range(steps):
            p = model.point(which, start+(end-start)*j/steps, mu, offset)[0]
            points.append((p[0]-center[0], p[1]-center[1]))
    return abs(fsum(cross(p, q) for p, q in zip(points, points[1:]+points[:1]))/2)


class SymmetricModel(QuadraticModel):
    def __init__(self):
        a, zero = Q(15, 8), (Q(0),)*3
        super().__init__(((a, Q(0), -a), (Q(0), Q(1), Q(0))), Q(0), zero, zero, zero)

    def support(self, i, theta, route):
        if i == 1:
            g = (1-theta*theta)**3
            gp = -6*theta*(1-theta*theta)**2
            gpp = -6+36*theta*theta-30*theta**4
            return route*g, route*gp, route*gpp, g, gp
        sign = 1 if i == 0 else -1
        return sign*f(theta), sign*first(theta), sign*second(theta), 0., 0.


def numerical_controls():
    count = 0
    models = [QuadraticModel(profile, Q(3, 5), (1, -2, 3), (-1, 2, 0), (2, 1, -1)) for profile in PROFILES]
    for model in models:
        proof, first_order = model.proof, model.proof["first"]
        c, a = float(first_order["parameter"]), float(first_order["angle"])
        target = float(proof["retimed_area"])
        require(target > 0, "Choose a nonzero generic retimed-area control.")
        previous = (float("inf"),)*3
        for offset in (64, 128, 256, 512, 1024, 2048, 4096, 8192):
            actual, polar = model.event(offset)
            clock_error = abs(offset*(actual[3]-c)-float(proof["parameter"]))
            angle_error = abs(offset*(polar-a)-float(proof["angle"]))
            require(clock_error < 100/offset and angle_error < 100/offset,
                    "A numerical event misses the second-order clock or polar-angle limit.")
            for i in range(3):
                require(abs(offset*(actual[i]-float(first_order["normal_angles"][i]))
                            - float(proof["normal_angles"][i])) < 300/offset,
                        "A numerical normal angle misses its second-order limit.")
            area = pocket(model, offset, c, 64)*offset**2
            finer = pocket(model, offset, c, 256)*offset**2
            require(abs(area-finer) < target*2e-5 and abs(finer-target) < target*200/offset,
                    "The retimed pocket misses its inverse-cube physical area law.")
            errors = clock_error, angle_error, abs(finer-target)
            require(all(x < y for x, y in zip(errors, previous)),
                    "The finite second-clock and area errors did not decrease.")
            previous = errors
            count += 1
        print(f"Generic model: c2={float(proof['parameter']):.9g}, M^3*area -> {target:.9g}; at M={offset}: {finer:.9g}.")
    symmetric = SymmetricModel()
    target = float(Q(1537734375, 134217728))
    for offset in (25, 50, 100, 200):
        event, _ = symmetric.event(offset)
        third = offset**2*(event[3]-float(FIRST))
        require(0 < third-float(THIRD) < 40/offset**2,
                "The independent four-variable symmetric event misses the known third-order clock bound.")
        area = pocket(symmetric, offset, float(FIRST), 64)*offset**4
        finer = pocket(symmetric, offset, float(FIRST), 256)*offset**4
        require(abs(area-finer) < target*2e-5 and abs(finer-target) < target*100/offset**2,
                "The symmetric retimed pocket misses its fifth-order physical area law.")
        count += 1
        print(f"Symmetric model M={offset}: M^5*area about {finer:.10g}; limit {target:.10g}.")
    return count


def main():
    print(f"{exact_controls()} exact controls: direct Cartesian Taylor jets, second-order clocks, determinant areas, relabelings, height shifts, and symmetric cancellation.")
    print(f"{numerical_controls()} numerical event/pocket controls passed, each with independent crossings and two boundary resolutions.")
    print("At the leading corrected clock, a generic selected pocket has area K*c2^2/M^3+O(M^-4).")
    print("The symmetric polynomial model has c2=0 and M^5*area -> 1537734375/134217728.")
    print("These local asymptotics give neither finite-offset error bounds nor a full-drawing face census.")


if __name__ == "__main__":
    main()
