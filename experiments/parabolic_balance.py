"""Make the smallest bounded pocket as large as possible.

Exact rational and quadratic-field controls for parabolic_balance.md.
The all-count proof uses adjacent triangles and weighted AM-GM;
these finite controls verify its algebra and all selected face areas.
Only the standard library is needed. Decimal readouts are illustrative.
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import total_ordering
from math import isqrt, sqrt
from random import Random

from blend_cusps import require
from parabolic_pockets import compromise, compromise_record, run_faces


@total_ordering
@dataclass(frozen=True, eq=False)
class Quadratic:
    """a+b*sqrt(d), with exact arithmetic and exact order."""
    d: int
    a: Q = Q(0)
    b: Q = Q(0)

    def __post_init__(self):
        require(type(self.d) is int and self.d > 0 and isqrt(self.d)**2 != self.d,
                "The quadratic field needs a positive nonsquare integer.")
        object.__setattr__(self, "a", Q(self.a))
        object.__setattr__(self, "b", Q(self.b))

    def other(self, value):
        if isinstance(value, Quadratic):
            require(value.d == self.d, "Do not mix quadratic fields.")
            return value
        require(type(value) in (int, Q), "Use an exact rational or quadratic number.")
        return Quadratic(self.d, Q(value))

    def __add__(self, value):
        v = self.other(value)
        return Quadratic(self.d, self.a+v.a, self.b+v.b)

    __radd__ = __add__

    def __neg__(self):
        return Quadratic(self.d, -self.a, -self.b)

    def __sub__(self, value):
        return self+-self.other(value)

    def __rsub__(self, value):
        return -self+value

    def __mul__(self, value):
        v = self.other(value)
        return Quadratic(self.d, self.a*v.a+self.d*self.b*v.b, self.a*v.b+self.b*v.a)

    __rmul__ = __mul__

    def __truediv__(self, value):
        v = self.other(value)
        norm = v.a*v.a-self.d*v.b*v.b
        require(norm != 0, "Cannot divide by zero in a quadratic field.")
        return self*Quadratic(self.d, v.a/norm, -v.b/norm)

    def __rtruediv__(self, value):
        return self.other(value)/self

    def __pow__(self, power):
        require(type(power) is int and power >= 0, "Use a nonnegative integer power.")
        out = Quadratic(self.d, Q(1))
        for _ in range(power):
            out = out*self
        return out

    def sign(self):
        sign = lambda x: (x > 0)-(x < 0)
        if not self.b:
            return sign(self.a)
        if not self.a or sign(self.a) == sign(self.b):
            return sign(self.b)
        return sign(self.a)*sign(self.a*self.a-self.d*self.b*self.b)

    def __eq__(self, value):
        if type(value) not in (Quadratic, int, Q):
            return False
        v = self.other(value)
        return self.a == v.a and self.b == v.b

    def __lt__(self, value):
        return (self-self.other(value)).sign() < 0

    def __float__(self):
        return float(self.a)+float(self.b)*sqrt(self.d)


def optimum(size, span=Q(4)):
    require(type(size) is int and size >= 3 and type(span) is Q and span > 0,
            "Use at least three slopes and a positive rational span.")
    if size % 2:
        return [span/(size-1)]*(size-1)
    if size == 4:
        return [span/4, span/2, span/4]
    k = (size-2)//2
    t = Quadratic(k*k+k+1, Q(1, k), Q(1, k))
    a = span/(k+1+k*t)
    return [a if i % 2 == 0 else t*a for i in range(size-1)]


def face_areas(gaps):
    """One area for every nonempty run of interior slopes."""
    return [gaps[i-1]*gaps[j]*(gaps[i-1]+2*sum(gaps[i:j])+gaps[j])/8
            for i in range(1, len(gaps)) for j in range(i, len(gaps))]


def certificate(size, span=Q(4)):
    gaps = optimum(size, span)
    require(sum(gaps) == span and all(g > 0 for g in gaps), "The optimal gaps miss their span.")
    areas = face_areas(gaps)
    require(len(areas) == (size-1)*(size-2)//2, "A bounded face was omitted.")
    smallest = min(areas)
    if size % 2:
        require(smallest == (span/(size-1))**3/4, "The odd-count minimum is incorrect.")
    elif size == 4:
        require(all(x == 3*span**3/256 for x in areas), "The three balanced pockets differ.")
    else:
        k = (size-2)//2
        a, b = gaps[:2]
        t = b/a
        require(k*t*t-2*t-k-1 == 0 and 1 < t < 2, "The alternating ratio has the wrong exact root.")
        require(smallest == a*b*(a+b)/8, "A longer run undercuts the adjacent triangles.")
        # The two AM-GM tangent coefficients simplify to (k+1)/span, k/span.
        require((1/a+1/(a+b))/3 == Q(k+1)/span
                and (1/b+1/(a+b))/3 == Q(k)/span, "The AM-GM supporting line misses its candidate.")
        coefficients = [0]*(2*k+1)
        weights = []
        for i in range(2*k):
            weight = k-i//2 if i % 2 == 0 else (i+1)//2
            weights.append(weight)
            coefficients[i] += weight*(k+1 if i % 2 == 0 else k)
            coefficients[i+1] += weight*(k if i % 2 == 0 else k+1)
        require(all(w > 0 for w in weights) and sum(weights) == k*(k+1)
                and coefficients == [k*(k+1)]*(2*k+1),
                "The positive AM-GM weights fail to account for the full span.")
        require(smallest > (span/(size-1))**3/4, "Even counts should improve on equal gaps.")
        root = Quadratic(k*k+k+1, Q(0), Q(1))
        require(root*root == k*k+k+1 and (1/root)*root == 1
                and k < root < k+1, "The exact field arithmetic failed a root control.")
    return gaps, smallest


def rational_controls(maximum):
    random = Random(20261108)
    count = 0
    for size in range(3, maximum+1):
        _, upper = certificate(size)
        for _ in range(12):
            integers = [random.randrange(1, 33) for _ in range(size-1)]
            gaps = [Q(4*x, sum(integers)) for x in integers]
            require(min(face_areas(gaps)) <= upper, "A rational arrangement beats the proposed optimum.")
            if size >= 6 and size % 2 == 0:
                k = (size-2)//2
                for i, (x, y) in enumerate(zip(gaps, gaps[1:])):
                    linear = ((k+1)*x+k*y)/4 if i % 2 == 0 else (k*x+(k+1)*y)/4
                    require(x*y*(x+y) <= 8*upper*linear**3, "An exact AM-GM cubic inequality failed.")
            count += 1
    for l in range(1, 23):
        for m in range(1, 24-l):
            r = 24-l-m
            gaps = [Q(l, 6), Q(m, 6), Q(r, 6)]
            balanced = [(gaps[0]+gaps[2])/2, gaps[1], (gaps[0]+gaps[2])/2]
            require(min(face_areas(gaps)) <= min(face_areas(balanced)) <= Q(3, 4),
                    "Four-slope symmetrization or its sharp bound failed.")
            slopes = [Q(-2)]
            for g in gaps:
                slopes.append(slopes[-1]+g)
            require(sorted(face_areas(gaps)) == sorted(face["area"] for face in run_faces(slopes)),
                    "The gap-only areas miss the independently integrated four-slope faces.")
            count += 1
    for size, span in ((2, Q(4)), (True, Q(4)), (4, Q(0)), (4, Q(-1)), (4, 4)):
        try:
            optimum(size, span)
        except ValueError:
            count += 1
        else:
            raise ValueError("An invalid balance problem was accepted.")
    return count


def compromise_controls():
    count = 0
    for step in range(1, 25):
        # Any asymmetric three-gap arrangement improves in both measures
        # when the two outside gaps are replaced by their average.
        left, middle, right = Q(step, 20), Q(3, 2), Q(5, 4)
        original = [left, middle, right]
        symmetric = [(left+right)/2, middle, (left+right)/2]
        span = sum(original)
        total = lambda gs: (span**3-sum(g**3 for g in gs))/24
        require(total(symmetric) >= total(original)
                and min(face_areas(symmetric)) >= min(face_areas(original)),
                "Symmetrization misses one of the two objectives.")
        count += 1
    previous = None
    for step in range(37):
        z = Q(1, 4)+Q(step, 432)
        point = compromise(z)
        if previous:
            require(point[0] > previous[0] and point[1] < previous[1],
                    "The compromise curve does not exchange total and smallest area.")
        previous = point
        count += 1
    record = compromise_record()
    require(record["bezier"][0] == (Q(9, 4), Q(3, 4))
            and record["bezier"][-1] == (Q(64, 27), Q(16, 27))
            and record["middle"]["areas"] == (Q(294, 125), Q(84, 125)),
            "The illustrated compromises miss their exact coordinates.")
    count += 1
    for z in (Q(0), Q(1, 2), Q(1, 3)+Q(1, 1000), .3):
        try:
            compromise(z)
        except ValueError:
            count += 1
        else:
            raise ValueError("An invalid compromise parameter was accepted.")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-slopes", type=int, default=20, help="Largest slope count in the finite exact controls (at least 6).")
    args = parser.parse_args()
    require(args.max_slopes >= 6, "Check through at least six slopes.")
    for size in range(3, args.max_slopes+1):
        gaps, smallest = certificate(size)
        print(f"{size} slopes: smallest area ≈ {float(smallest):.12f}; gaps start {float(gaps[0]):.9f}, {float(gaps[1]):.9f}.")
        other, scaled = certificate(size, Q(7, 3))
        require(all(y == Q(7, 12)*x for x, y in zip(gaps, other)) and scaled == Q(7, 12)**3*smallest,
                "The optimum does not scale cubically with the slope span.")
    controls = rational_controls(args.max_slopes)
    compromise_count = compromise_controls()
    print(f"{2*(args.max_slopes-2)} exact optimal-arrangement controls and {controls} rational challenger/symmetrization/invalid controls passed.")
    print(f"{compromise_count} exact compromise controls and 37 cubic-path matches passed.")
    print("The all-count argument is weighted AM-GM; the decimal readouts are not proof predicates.")


if __name__ == "__main__":
    main()
