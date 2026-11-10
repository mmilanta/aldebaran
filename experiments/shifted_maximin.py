"""The dense-placement law also maximizes the smallest pocket asymptotically.

Exact four-line face formulas and curvature bounds check every run.
The proof for arbitrary C^2 intercepts is in shifted_maximin.md.
Finite rational density controls are illustrations, not exact finite optima.
Only the standard library.
"""

from fractions import Fraction as Q
from random import Random

from blend_cusps import require
from parabolic_pockets import area
from shifted_parabolas import bounded_faces, crossing, ordered
from shifted_placement import density_nodes


def run_area(points, first, last):
    p = points
    require(type(first) is int and type(last) is int and 1 <= first <= last < len(p)-1,
            'Use a nonempty run of interior slope indices.')
    a = p[first][0]-p[first-1][0]
    b = p[last+1][0]-p[last][0]
    H = p[last][0]-p[first][0]
    require(a > 0 and b > 0 and H >= 0, 'Run boundaries must have positive outer gaps.')
    x = (p[first][1]-p[first-1][1])/a
    z = (p[last+1][1]-p[last][1])/b
    if first == last:
        actual = a*b*(z-x)**2/(2*(a+b))
    else:
        y = (p[last][1]-p[first][1])/H
        A, B = y-x, z-y
        require(A > 0 and B > 0, 'The intercepts must be strictly convex across the run.')
        actual = (a*a*b*A*A/(2*(a+H+b)*(a+H))
                  +a*b*A*B/(a+H+b)
                  +a*b*b*B*B/(2*(a+H+b)*(H+b)))
    return actual, a*b*(a+2*H+b)/8


def check_arrangement(points, curvature=None):
    p = ordered(points)
    fresh = {frozenset(v) for v in bounded_faces(p)}
    runs = set()
    count = 0
    for i in range(1, len(p)-1):
        for j in range(i, len(p)-1):
            pairs = ((i-1, i), (i-1, j+1), (i, j+1)) if i == j else (
                (i-1, j), (i-1, j+1), (i, j+1), (i, j))
            vertices = [crossing(p[a], p[b]) for a, b in pairs]
            actual, canonical = run_area(p, i, j)
            require(actual == area(vertices) > 0,
                    'The positive face polynomial misses its independently integrated polygon.')
            runs.add(frozenset(vertices))
            if curvature:
                c, C = curvature(p[i-1][0], p[j+1][0])
                require(0 < c <= C and c*c*canonical <= actual <= C*C*canonical,
                        'A complete face escapes its local curvature sandwich.')
            count += 1
    require(runs == fresh, 'The run list misses a freshly clipped bounded face.')
    return count


def controls():
    arrangements = faces = 0
    families = ((lambda p: p*p/2, lambda a, b: (Q(1), Q(1)), Q(1), Q(3)),
                (lambda p: p**3/3, lambda a, b: (2*a, 2*b), Q(1), Q(3)),
                (lambda p: p**4/4+p*p/16,
                 lambda a, b: (Q(1, 8)+(0 if a <= 0 <= b else 3*min(a*a, b*b)),
                               Q(1, 8)+3*max(a*a, b*b)), Q(-1), Q(1)))
    for h, curvature, left, right in families:
        for size in range(3, 10):
            # Uneven rational gaps exercise nonuniform four-line faces.
            slopes = [left+(right-left)*Q(j*j, (size-1)**2) for j in range(size)]
            points = [(p, h(p)) for p in slopes]
            faces += check_arrangement(points, curvature)
            arrangements += 1
    random = Random(20261110)
    for size in range(3, 10):
        points = [(Q(-2), Q(1))]
        secant = Q(-3)
        for _ in range(size-1):
            gap = Q(random.randrange(1, 9), 7)
            p, h = points[-1]
            points.append((p+gap, h+gap*secant))
            secant += Q(random.randrange(1, 10), 5)
        faces += check_arrangement(points)
        arrangements += 1
    rows = []
    density_faces = 0
    for gaps in (2, 3, 4, 8, 16, 32, 64, 128):
        nodes = [(a+b)/2 for a, b in density_nodes(gaps)]
        points = [(p, p**3/3) for p in nodes]
        minimum = None
        singleton_minimum = None
        for i in range(1, gaps):
            for j in range(i, gaps):
                actual, canonical = run_area(points, i, j)
                c, C = 2*nodes[i-1], 2*nodes[j+1]
                require(c*c*canonical <= actual <= C*C*canonical,
                        'A rational density face escapes its exact local curvature bounds.')
                minimum = actual if minimum is None else min(minimum, actual)
                if i == j:
                    singleton_minimum = actual if singleton_minimum is None else min(singleton_minimum, actual)
                density_faces += 1
        require(minimum == singleton_minimum,
                'A longer run unexpectedly undercuts the selected rational density triangles.')
        rows.append((gaps, minimum*gaps**3))
    invalid = 0
    points = [(Q(-1), Q(1, 2)), (Q(0), Q(0)), (Q(1), Q(1, 2))]
    for first, last in ((0, 1), (1, 2), (2, 1), (True, 1)):
        try:
            run_area(points, first, last)
        except ValueError:
            invalid += 1
        else:
            raise ValueError('An invalid run index was accepted.')
    return arrangements, faces, density_faces, invalid, rows


def main():
    arrangements, faces, density_faces, invalid, rows = controls()
    print(f'{arrangements} complete clipped arrangements, {faces} exact face polynomials, '
          f'{density_faces} rational density faces, and {invalid} invalid controls passed.')
    for gaps, scaled in rows:
        print(f'{gaps:3} gaps: rational density control m^3 * smallest area ≈ {float(scaled):.12f}.')
    print('The written theorem gives limit W^3/4, six times the leading total-deficit constant.')
    print('These finite density controls are not claimed to maximize the smallest pocket at finite count.')


if __name__ == '__main__':
    main()
