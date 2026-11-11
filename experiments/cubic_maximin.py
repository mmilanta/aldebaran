"""Four cubic-intercept parabolas: the unique largest smallest pocket.

Exact rational polynomial identities prove global log-concavity of the
quadrilateral area. A cubic root selects the unique equal-area placement;
positive supporting weights prove its global optimality. No dependencies.
See cubic_maximin.md for the argument and the scope of the certificate.
"""

import argparse
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
from random import Random

from blend_cusps import require, add, product, remainder, scale, value
from shifted_maximin import check_arrangement, run_area
from shifted_parabolas import variance_area
from shifted_placement import partition

HERE = Path(__file__).resolve().parent
ROOT = (Q(54), Q(-87), Q(20), Q(8))


# Sparse bivariate polynomials, indexed by powers of x and y. Keeping this
# small arithmetic explicit makes the continuous certificate reproducible
# without a symbolic algebra package or a saved list of trusted coefficients.
def constant(c):
    return {(0, 0): Q(c)} if c else {}


def plus(*polys):
    out = {}
    for p in polys:
        for key, c in p.items():
            out[key] = out.get(key, Q(0))+c
    return {key: c for key, c in out.items() if c}


def times(*polys):
    out = constant(1)
    for p in polys:
        result = {}
        for (i, j), a in out.items():
            for (k, l), b in p.items():
                key = i+k, j+l
                result[key] = result.get(key, Q(0))+a*b
        out = {key: c for key, c in result.items() if c}
    return out


def scaled(p, c):
    return {key: a*c for key, a in p.items() if a*c}


def power(p, n):
    out = constant(1)
    for _ in range(n):
        out = times(out, p)
    return out


def diff(p, axis):
    out = {}
    for key, c in p.items():
        if key[axis]:
            new = list(key)
            new[axis] -= 1
            out[tuple(new)] = c*key[axis]
    return out


def at(p, x, y):
    return sum((c*x**i*y**j for (i, j), c in p.items()), Q(0))


def face_polynomials():
    x, y = {(1, 0): Q(1)}, {(0, 1): Q(1)}
    u, v, w = plus(x, constant(-1)), plus(y, scaled(x, -1)), plus(constant(3), scaled(y, -1))
    first = scaled(times(u, v, plus(y, constant(-1)), power(plus(x, y, constant(1)), 2)), Q(1, 18))
    last = scaled(times(v, w, plus(constant(3), scaled(x, -1)),
                        power(plus(x, y, constant(3)), 2)), Q(1, 18))
    single = scaled(times(u, plus(constant(3), scaled(x, -1)), power(plus(x, constant(4)), 2)), Q(1, 9))
    middle = plus(single, scaled(first, -1))
    other_single = scaled(times(plus(y, constant(-1)), w, power(plus(y, constant(4)), 2)), Q(1, 9))
    require(middle == plus(other_single, scaled(last, -1)),
            'The two overlapping three-curve pockets disagree on their common quadrilateral.')
    return first, middle, last


def homogeneous(p):
    """Identity on x=1+2u, y=3-2w, u+v+w=1, with u,v,w>0.

    Expand the affine substitution, then multiply each term of degree k
    by (u+v+w)^(d-k). Nonnegative coefficients prove nonnegativity on
    the *whole* triangle, rather than merely at finitely many points.
    """
    degree = max(i+j for i, j in p)
    affine = {}
    for (i, j), c in p.items():
        for a in range(i+1):
            for b in range(j+1):
                key = a, b
                affine[key] = affine.get(key, Q(0))+c*comb(i, a)*2**a*comb(j, b)*3**(j-b)*(-2)**b
    out = {}
    for (a, b), c in affine.items():
        if not c:
            continue
        n = degree-a-b
        for i in range(n+1):
            for j in range(n-i+1):
                k = n-i-j
                key = a+i, j, b+k
                out[key] = out.get(key, Q(0))+c*comb(n, i)*comb(n-i, j)
    return degree, {key: c for key, c in out.items() if c}


def concavity_certificate():
    C = face_polynomials()[1]
    cx, cy = diff(C, 0), diff(C, 1)
    A = plus(times(cx, cx), scaled(times(C, diff(cx, 0)), -1))
    B = plus(times(cy, cy), scaled(times(C, diff(cy, 1)), -1))
    E = plus(times(cx, cy), scaled(times(C, diff(cx, 1)), -1))
    D = plus(times(A, B), scaled(times(E, E), -1))
    records = []
    for name, p in (("negative_log_hessian_xx_numerator", A),
                    ("log_hessian_determinant_numerator", D)):
        degree, coeffs = homogeneous(p)
        require(coeffs and all(c > 0 for c in coeffs.values()),
                'A global log-concavity polynomial has a negative coefficient.')
        records.append({'polynomial': name, 'degree': degree,
                        'positive_terms': len(coeffs),
                        'coefficients': [{'powers': key, 'coefficient': str(c)}
                                         for key, c in sorted(coeffs.items())]})
    require([(r['degree'], r['positive_terms']) for r in records] == [(8, 28), (16, 91)],
            'The continuous concavity certificates changed degree or term count.')
    return records


def candidate_identities():
    # beta=(13 alpha-12)/(4 alpha-3) is also this polynomial in alpha.
    beta = (Q(-8), Q(13, 3), Q(4, 3))
    alpha = (Q(0), Q(1))
    def substitute(p):
        out = (Q(0),)
        for (i, j), c in p.items():
            term = (Q(1),)
            for _ in range(i):
                term = product(term, alpha)
            for _ in range(j):
                term = product(term, beta)
            out = add(out, scale(term, c))
        return remainder(out, ROOT)
    S = (Q(-101, 48), Q(487, 288), Q(47, 144))
    require(all(substitute(p) == S for p in face_polynomials()),
            'The cubic candidate does not make all three face areas equal.')
    require(remainder(add(product((Q(-3), Q(4)), beta), (Q(12), Q(-13))), ROOT) == (0,),
            'The rational and polynomial formulas for beta disagree.')
    return beta, S


def root_bounds(bits=96):
    require(type(bits) is int and bits >= 16, 'Use an integer precision of at least 16 bits.')
    lo, hi = Q(163, 100), Q(164, 100)
    require(value(ROOT, lo) < 0 < value(ROOT, hi), 'The cubic root lost its initial bracket.')
    while hi-lo > Q(1, 1 << bits):
        mid = (lo+hi)/2
        f = value(ROOT, mid)
        if f == 0:
            return mid, mid
        if f < 0:
            lo = mid
        else:
            hi = mid
    require(value(ROOT, lo) < 0 < value(ROOT, hi), 'The final root bracket has invalid signs.')
    return lo, hi


def interval_sum(*pairs):
    return sum((p[0] for p in pairs), Q(0)), sum((p[1] for p in pairs), Q(0))


def interval_product(a, b):
    values = [x*y for x in a for y in b]
    return min(values), max(values)


def interval_negative(a):
    return -a[1], -a[0]


def enclose(p, x, y):
    require(0 < x[0] <= x[1] and 0 < y[0] <= y[1], 'Polynomial boxes need positive coordinates.')
    terms = []
    for (i, j), c in p.items():
        lo, hi = c*x[0]**i*y[0]**j, c*x[1]**i*y[1]**j
        terms.append((min(lo, hi), max(lo, hi)))
    return interval_sum(*terms)


def determinant(a, b):
    return interval_sum(interval_product(a[0], b[1]), interval_negative(interval_product(a[1], b[0])))


def optimum(bits=96):
    beta, S = candidate_identities()
    alpha_box = root_bounds(bits)
    # Both polynomials increase on the initial root bracket.
    beta_box = tuple(value(beta, x) for x in alpha_box)
    area_box = tuple(value(S, x) for x in alpha_box)
    require(1 < alpha_box[0] <= alpha_box[1] < beta_box[0] <= beta_box[1] < 3,
            'The candidate slope enclosures must be interior and disjoint.')
    polys = face_polynomials()
    gradients = []
    for p in polys:
        area = enclose(p, alpha_box, beta_box)
        require(area[0] > 0, 'An optimal face area enclosure reaches zero.')
        inverse = 1/area[1], 1/area[0]
        gradients.append(tuple(interval_product(enclose(diff(p, k), alpha_box, beta_box), inverse)
                               for k in (0, 1)))
    weights = [determinant(gradients[1], gradients[2]),
               determinant(gradients[2], gradients[0]),
               determinant(gradients[0], gradients[1])]
    # A cyclic reversal chooses the common orientation of the null vector.
    if all(w[1] < 0 for w in weights):
        weights = [interval_negative(w) for w in weights]
    require(all(w[0] > 0 for w in weights), 'The global support needs three strictly positive weights.')
    return {'nodes': [(Q(1), Q(1)), alpha_box, beta_box, (Q(3), Q(3))],
            'smallest_area': area_box, 'total_area': tuple(3*x for x in area_box),
            'support_weights': weights, 'root_polynomial_ascending': ROOT,
            'precision_bits': bits}


def controls():
    polys = face_polynomials()
    candidate_identities()
    arrangements = faces = challengers = identities = 0
    # Exact clipping checks all three actual faces, independently of the
    # polynomial representation used to prove the continuous upper bound.
    random = Random(20261111)
    selected = [(Q(5, 3), Q(7, 3)), (Q(3, 2), Q(5, 2))]
    selected += [tuple(sorted(random.sample([Q(i, 20) for i in range(21, 60)], 2))) for _ in range(30)]
    for x, y in selected:
        points = [(p, p**3/3) for p in (Q(1), x, y, Q(3))]
        faces += check_arrangement(points, lambda a, b: (2*a, 2*b))
        actual = [run_area(points, i, j)[0] for i, j in ((1, 1), (1, 2), (2, 2))]
        require(actual == [at(p, x, y) for p in polys] and sum(actual) == variance_area(points),
                'The cubic face polynomials miss independently clipped faces or band area.')
        arrangements += 1
    solution = optimum()
    alpha, beta = solution['nodes'][1:3]
    for i in range(1, 60):
        for j in range(i+1, 60):
            x, y = Q(1)+Q(i, 30), Q(1)+Q(j, 30)
            require(min(at(p, x, y) for p in polys) < solution['smallest_area'][0],
                    'A rational challenger meets the certified optimal lower area.')
            challengers += 1
    # Audit the actual homogeneous identities, not only their coefficient signs.
    C = polys[1]
    cx, cy = diff(C, 0), diff(C, 1)
    A = plus(times(cx, cx), scaled(times(C, diff(cx, 0)), -1))
    B = plus(times(cy, cy), scaled(times(C, diff(cy, 1)), -1))
    E = plus(times(cx, cy), scaled(times(C, diff(cx, 1)), -1))
    for p in (A, plus(times(A, B), scaled(times(E, E), -1))):
        degree, coeffs = homogeneous(p)
        for x, y in selected:
            u, w = (x-1)/2, (3-y)/2
            v = 1-u-w
            h = sum(c*u**i*v**j*w**k for (i, j, k), c in coeffs.items())
            require(h == at(p, x, y), 'A homogeneous global certificate misses its polynomial.')
            identities += 1
    # Node, area and support boxes survive three independent precisions.
    for bits in (64, 80, 128):
        other = optimum(bits)
        for key in ('nodes', 'support_weights'):
            for a, b in zip(solution[key], other[key]):
                require(max(a[0], b[0]) <= min(a[1], b[1]), 'Independent precision enclosures are disjoint.')
    total = partition(3)
    require(total['area'][0] > solution['total_area'][1], 'The total-area objective does not trade off here.')
    a, b = total['nodes'][1:3]
    total_min = enclose(polys[2], a, b)
    require(total_min[1] < solution['smallest_area'][0], 'The total optimizer already attains the maximin value.')
    invalid = 0
    for bits in (True, 0, 15, 32.0):
        try:
            root_bounds(bits)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid root precision was accepted.')
    return {'complete_arrangements': arrangements, 'clipped_faces': faces,
            'rational_challengers': challengers, 'homogeneous_identity_controls': identities,
            'invalid_controls': invalid}


def serialize(obj):
    if type(obj) is Q:
        return str(obj)
    if isinstance(obj, dict):
        return {key: serialize(v) for key, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]
    return obj


def record():
    total = partition(3)
    return {'scope': 'Four complete cubic-intercept parabolas, fixed outer labels 1 and 3. Unique finite maximin.',
            'equation': 'X_p(Y)=Y^2/2-pY+p^3/3', 'maximin': optimum(),
            'total_optimizer': {'nodes': total['nodes'], 'total_area': total['area'],
                                'face_areas': [enclose(p, total['nodes'][1], total['nodes'][2])
                                               for p in face_polynomials()]},
            'continuous_log_concavity': concavity_certificate()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate rational enclosures and the global polynomial certificate.')
    args = parser.parse_args()
    counts = controls()
    data = record()
    if args.write:
        (HERE/'cubic_maximin.json').write_text(json.dumps(serialize(data), indent=2)+'\n')
    print('Continuous global proof: 28 + 91 positive homogeneous polynomial coefficients.')
    print(', '.join(f'{v} {key.replace("_", " ")}' for key, v in counts.items())+'.')
    mid = lambda box: float(sum(box)/2)
    print('Unique maximin labels:', ', '.join(f'{mid(x):.12f}' for x in data['maximin']['nodes']))
    print(f'All three areas ≈ {mid(data["maximin"]["smallest_area"]):.12f}.')
    print('The global proof is the exact polynomial identities and positive supporting weights, not the challenger grid.')


if __name__ == '__main__':
    main()
