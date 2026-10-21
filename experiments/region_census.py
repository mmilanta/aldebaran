"""Count every face of a sampled orbital polygon, using exact geometry.

Run: python3 experiments/region_census.py [--all] [--steps N]
Standard library only. Sines/cosines first generate binary floating-point
vertices; all subsequent intersection, face, and area arithmetic is exact for
those stored vertices. This does NOT certify the smooth curve's region count.
"""

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import cmp_to_key

from signed_area import orbit
from tangent_turning import certify_turning


class GeometryError(ValueError):
    """The polygon has a degeneracy this generic-curve census does not handle."""


def cross(p, q):
    return p[0]*q[1] - p[1]*q[0]


def subtract(p, q):
    return p[0]-q[0], p[1]-q[1]


def angle_order(p, q):
    """Order rays counterclockwise using exact signs, without atan2."""
    first_p = p[1] > 0 or p[1] == 0 and p[0] >= 0
    first_q = q[1] > 0 or q[1] == 0 and q[0] >= 0
    if first_p != first_q:
        return -1 if first_p else 1
    determinant = cross(p, q)
    if determinant == 0:
        raise GeometryError('Coincident rays at a crossing.')
    return -1 if determinant > 0 else 1


def census(outer, inner, steps=24000):
    if not (2 <= outer <= 15 and 3 <= inner <= 25 and steps >= 64):
        raise ValueError('Use supported rhythms and at least 64 samples.')
    if (outer, inner) == (8, 21):
        raise GeometryError('Needle has a cusp; this census concerns regular generic curves.')
    ratios = [(x.as_integer_ratio(), y.as_integer_ratio()) for x, y in orbit(outer, inner, steps)]
    # Every denominator is a power of two. A common scale makes all vertices
    # integers without rounding or changing their exact binary values.
    scale = max(max(x[1], y[1]) for x, y in ratios)
    points = [(x[0]*(scale//x[1]), y[0]*(scale//y[1])) for x, y in ratios]
    vectors = [subtract(points[(i+1) % steps], p) for i, p in enumerate(points)]
    if (0, 0) in vectors:
        raise GeometryError('A sampled edge has zero length.')
    for previous, current in zip(vectors[-1:] + vectors[:-1], vectors):
        if cross(previous, current) == 0 and previous[0]*current[0] + previous[1]*current[1] < 0:
            raise GeometryError('Adjacent edges reverse along the same line.')
    original_area = Fraction(sum(cross(points[i], points[(i+1) % steps])
                                 for i in range(steps)), 2*scale*scale)

    buckets = defaultdict(list)
    cell = 8 * scale
    occurrences = []
    nodes = {}
    for i, a in enumerate(points):
        b = points[(i+1) % steps]
        direction = vectors[i]
        visited = set()
        # Any two intersecting closed segments share at least one of these
        # closed bounding-box buckets, including intersections on bucket borders.
        for bx in range(min(a[0], b[0])//cell, max(a[0], b[0])//cell + 1):
            for by in range(min(a[1], b[1])//cell, max(a[1], b[1])//cell + 1):
                for j in buckets[bx, by]:
                    if j in visited or i-j == 1 or i-j == steps-1:
                        continue  # Neighboring edges share their ordinary vertex.
                    visited.add(j)
                    c, d = points[j], points[(j+1) % steps]
                    if (max(a[0], b[0]) < min(c[0], d[0]) or
                            max(c[0], d[0]) < min(a[0], b[0]) or
                            max(a[1], b[1]) < min(c[1], d[1]) or
                            max(c[1], d[1]) < min(a[1], b[1])):
                        continue
                    other = vectors[j]
                    denominator = cross(direction, other)
                    offset = subtract(c, a)
                    if denominator == 0:
                        if cross(offset, direction) == 0:
                            raise GeometryError('Nonadjacent collinear edges touch or overlap.')
                        continue
                    t = Fraction(cross(offset, other), denominator)
                    u = Fraction(cross(offset, direction), denominator)
                    if not (0 <= t <= 1 and 0 <= u <= 1):
                        continue
                    if t in (0, 1) or u in (0, 1):
                        raise GeometryError('A nonadjacent edge touches a sampled vertex.')
                    point = a[0] + t*direction[0], a[1] + t*direction[1]
                    if point in nodes:
                        raise GeometryError('More than two branches share a crossing.')
                    node = len(nodes)
                    nodes[point] = node
                    occurrences.extend([(i+t, node, i, t, point), (j+u, node, j, u, point)])
                buckets[bx, by].append(i)

    if not occurrences:
        if original_area == 0:
            raise GeometryError('A simple polygon cannot have zero area.')
        index = 1 if original_area > 0 else -1
        return {'crossings': 0, 'bounded_faces': 1, 'face_counts': {index: 1},
                'region_sum': index, 'crossing_sum': 0, 'graph_index': index}

    # Contract ordinary degree-two vertices. Consecutive crossing occurrences
    # along the original parameter give oriented arcs between graph vertices.
    occurrences.sort()
    outgoing = defaultdict(list)
    directions = []
    arc_areas = []
    for k, start in enumerate(occurrences):
        end = occurrences[(k+1) % len(occurrences)]
        _, a, i, t, p = start
        _, b, j, u, q = end
        outgoing[a].append(2*k)
        outgoing[b].append(2*k+1)
        directions.extend([vectors[i], (-vectors[j][0], -vectors[j][1])])
        # Twice the oriented area integral along this arc, before rescaling.
        if i == j and t < u:
            area = cross(p, q)
        else:
            area, current, vertex = Fraction(0), p, (i+1) % steps
            while True:
                area += cross(current, points[vertex])
                current = points[vertex]
                if vertex == j:
                    break
                vertex = (vertex+1) % steps
            area += cross(current, q)
        arc_areas.append(area)

    following = {}
    for edges in outgoing.values():
        if len(edges) != 4:
            raise GeometryError('A crossing does not have four incident rays.')
        edges.sort(key=cmp_to_key(lambda a, b: angle_order(directions[a], directions[b])))
        for k, edge in enumerate(edges):
            # At the arrival vertex, turn clockwise from the reversed incoming
            # ray. The traversed face stays to the left of the directed arc.
            following[edge ^ 1] = edges[k-1]

    face_for = {}
    face_areas = []
    for first in following:
        if first in face_for:
            continue
        face, edge, area = len(face_areas), first, Fraction(0)
        while edge not in face_for:
            face_for[edge] = face
            area += (-1 if edge % 2 else 1) * arc_areas[edge//2]
            edge = following[edge]
        assert edge == first
        face_areas.append(area / (2*scale*scale))
    outside = min(range(len(face_areas)), key=lambda i: face_areas[i])
    assert face_areas[outside] < 0
    assert all(area > 0 for i, area in enumerate(face_areas) if i != outside)
    assert len(face_areas) == len(nodes) + 2  # Euler's formula on the sphere.

    # Each oriented arc has count k+1 on its left and k on its right. Propagate
    # from the unbounded face, then check every arc for consistency.
    adjacency = defaultdict(list)
    for arc in range(len(arc_areas)):
        left, right = face_for[2*arc], face_for[2*arc+1]
        assert left != right
        adjacency[right].append((left, 1))
        adjacency[left].append((right, -1))
    labels = {outside: 0}
    pending = deque([outside])
    while pending:
        face = pending.popleft()
        for neighbor, delta in adjacency[face]:
            if neighbor in labels:
                assert labels[neighbor] == labels[face] + delta
            else:
                labels[neighbor] = labels[face] + delta
                pending.append(neighbor)
    assert len(labels) == len(face_areas)
    crossing_sum = Fraction(0)
    for edges in outgoing.values():
        corners = [labels[face_for[edge]] for edge in edges]
        mean = Fraction(sum(corners), 4)
        assert mean.denominator == 1
        assert sorted(corners) == [mean-1, mean, mean, mean+1]
        crossing_sum += mean
    # Every face's area is counted with its winding label. Interior arc
    # contributions cancel exactly to recover the original shoelace sum.
    assert sum(labels[i]*face_areas[i] for i in labels) == original_area
    region_sum = sum(labels.values())
    return {'crossings': len(nodes), 'bounded_faces': len(face_areas)-1,
            'face_counts': dict(sorted(Counter(labels[i] for i in labels if i != outside).items())),
            'region_sum': region_sum, 'crossing_sum': int(crossing_sum),
            'graph_index': int(region_sum-crossing_sum)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Survey all 321 regular pairs (about one minute).')
    parser.add_argument('--steps', type=int, default=24000)
    args = parser.parse_args()
    pairs = ([(m, n) for m in range(2, 16) for n in range(3, 26) if (m, n) != (8, 21)]
             if args.all else [(7, 13), (2, 25), (6, 9), (9, 23)])
    completed = 0
    for pair in pairs:
        result = census(*pair, args.steps)
        certificate = certify_turning(*pair)
        if args.steps == 24000:
            assert result['graph_index'] == certificate.turns
        print(f'{pair[0]:2}/{pair[1]:2}: {result}', flush=True)
        completed += 1
    print(f'{completed} exact sampled-polygon censuses completed. Use certify_intersections.py for the four smooth-curve certificates.')


if __name__ == '__main__':
    main()
