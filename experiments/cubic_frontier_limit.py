"""The short cubic-frontier branch near the constant-curvature limit.

Exact rational Taylor jets reconstruct the total optimizer and first
triangle tie. Nonsingular implicit systems justify their smooth local
branches; the written compactness/support argument gives global scope
for sufficiently small positive perturbations. No explicit perturbation
threshold or full arbitrary-endpoint frontier is claimed. Standard library.
See cubic_frontier_limit.md.
"""

from fractions import Fraction as Q
from math import comb

from blend_cusps import require

ORDER = 6


class Jet:
    """A rational polynomial modulo e^(ORDER+1), with exact arithmetic."""
    def __init__(self, coefficients):
        self.c = tuple(map(Q, coefficients))+((Q(0),)*(ORDER+1-len(coefficients)))
        require(len(self.c) == ORDER+1, 'The Taylor jet exceeds the working order.')

    @staticmethod
    def wrap(value):
        return value if isinstance(value, Jet) else Jet((Q(value),))

    def __add__(self, other):
        other = self.wrap(other)
        return Jet(tuple(a+b for a, b in zip(self.c, other.c)))

    __radd__ = __add__

    def __neg__(self):
        return Jet(tuple(-c for c in self.c))

    def __sub__(self, other):
        return self+-self.wrap(other)

    def __rsub__(self, other):
        return self.wrap(other)+-self

    def __mul__(self, other):
        other = self.wrap(other)
        return Jet(tuple(sum(self.c[k]*other.c[n-k] for k in range(n+1))
                         for n in range(ORDER+1)))

    __rmul__ = __mul__

    def __pow__(self, n):
        require(type(n) is int and n >= 0, 'Use a nonnegative integer jet power.')
        out = self.wrap(1)
        for _ in range(n):
            out = out*self
        return out


def monomial(n, coefficient=Q(1)):
    return Jet((Q(0),)*n+(coefficient,))


def quantities(x, y, e):
    """Areas scaled by 18/(L^5 q^2), and derivatives at fixed e."""
    r, z = 1+e*(x+y), 1+e*x
    u, v, w = y-x, 1-y, 1-x
    A = x*u*y*(1+e*(x+y-1))**2
    B = u*v*w*r*r
    F = x*(1-x)*z*z
    Bx = -v*w*r*r-u*v*r*r+2*e*u*v*w*r
    By = v*w*r*r-u*w*r*r+2*e*u*v*w*r
    Fx = (1-2*x)*z*z+2*e*x*(1-x)*z
    return {'A': A, 'C': F-A, 'B': B, 'T': F+B, 'Tx': Fx+Bx, 'Ty': By}


def equations(x, y, e, branch):
    p = quantities(x, y, e)
    require(branch in ('total', 'switch'), 'Choose the total or switch implicit system.')
    return (p['Tx'], p['Ty']) if branch == 'total' else (p['A']-p['B'], p['Ty'])


def root_jet(branch):
    x, y, e = Jet((Q(1, 3),)), Jet((Q(2, 3),)), monomial(1)
    jacobian = None
    for n in range(1, ORDER+1):
        zero = equations(x, y, e, branch)
        dx, dy = equations(x+monomial(n), y, e, branch), equations(x, y+monomial(n), e, branch)
        a, c = [dx[i].c[n]-zero[i].c[n] for i in (0, 1)]
        b, d = [dy[i].c[n]-zero[i].c[n] for i in (0, 1)]
        determinant = a*d-b*c
        current = ((a, b), (c, d))
        require(jacobian is None or jacobian == current, 'The implicit coefficient Jacobian changed.')
        jacobian = current
        require(determinant == (Q(4, 3) if branch == 'total' else Q(-2, 3)),
                'An implicit Taylor system lost its nonsingular Jacobian.')
        f, g = zero[0].c[n], zero[1].c[n]
        x += monomial(n, (-d*f+b*g)/determinant)
        y += monomial(n, (c*f-a*g)/determinant)
    require(all(c == 0 for p in equations(x, y, e, branch) for c in p.c),
            'An implicit root jet has a nonzero residual through order six.')
    return x, y, jacobian


def main():
    e = monomial(1)
    require(((1-e)*(1+e)).c == (Q(1), Q(0), Q(-1))+(Q(0),)*(ORDER-2),
            'The jet multiplication control failed.')
    require(((1+e)**ORDER).c == tuple(Q(comb(ORDER, i)) for i in range(ORDER+1)),
            'The exact binomial jet control failed.')
    tx, ty, hessian = root_jet('total')
    sx, sy, switch_jacobian = root_jet('switch')
    require(tx.c[:4] == (Q(1, 3), Q(2, 9), Q(-2, 81), Q(-14, 243))
            and ty.c[:4] == (Q(2, 3), Q(2, 9), Q(-16, 81), Q(28, 243))
            and sx.c[:4] == (Q(1, 3), Q(2, 9), Q(-2, 81), Q(-10, 81))
            and sy.c[:4] == (Q(2, 3), Q(2, 9), Q(-16, 81), Q(20, 243)),
            'A displayed cubic Taylor coefficient changed.')
    require(hessian == ((Q(-4, 3), Q(2, 3)), (Q(2, 3), Q(-4, 3)))
            and switch_jacobian == ((Q(1, 3), Q(1, 3)), (Q(2, 3), Q(-4, 3))),
            'A base-point derivative matrix is incorrect.')
    total, switch = quantities(tx, ty, e), quantities(sx, sy, e)
    asymmetry = total['A']-total['B']
    gain, cost = switch['B']-total['B'], total['T']-switch['T']
    require(asymmetry.c[:4] == (Q(0), Q(0), Q(0), Q(8, 243)),
            'The first unequal-triangle term changed.')
    require(gain.c[:4] == (Q(0), Q(0), Q(0), Q(16, 729)),
            'The cubic smallest-pocket gain changed.')
    require(cost.c == (Q(0),)*6+(Q(128, 59049),),
            'The total-area cost must vanish through order five.')
    require(gain.c[3]/total['B'].c[0] == Q(8, 27)
            and cost.c[6]/total['T'].c[0] == Q(16, 2187)
            and (cost.c[6]/total['T'].c[0])/(gain.c[3]/total['B'].c[0])**2 == Q(1, 12),
            'A relative asymptotic coefficient changed.')
    # The sixth-order loss is also the independent Hessian quadratic form.
    delta = (sx.c[3]-tx.c[3], sy.c[3]-ty.c[3])
    require(delta == (Q(-16, 243), Q(-8, 243))
            and -sum(delta[i]*hessian[i][j]*delta[j] for i in (0, 1) for j in (0, 1))/2 == cost.c[6],
            'The Hessian explanation of the sixth-order cost failed.')
    print('Two nonsingular implicit systems; 28 zero residual coefficients through order six.')
    for name, a, b in (('total', tx, ty), ('switch', sx, sy)):
        print(name+' x coefficients through cubic:', ', '.join(map(str, a.c[:4])))
        print(name+' y coefficients through cubic:', ', '.join(map(str, b.c[:4])))
    print('Relative minimum gain = (8/27) e^3 + O(e^4).')
    print('Relative total cost = (16/2187) e^6 + O(e^7).')
    print('Relative cost / squared relative gain -> 1/12.')
    print('These are local asymptotic theorems: no explicit positive-e threshold is asserted.')


if __name__ == '__main__':
    main()
