"""Certify the three zero-tangent-index rhythm pairs and all their regions.

Run: python3 experiments/zero_turns.py
Optional illustration: python3 experiments/zero_turns.py --figure
The checks use the standard library. Only --figure needs NumPy, Matplotlib,
and Shapely; none of them is a website dependency.
"""

from collections import Counter
from pathlib import Path
import sys

from certify_intersections import IntersectionCertificate
from region_census import census
from tangent_turning import atlas


CASES = [
    (2, 3, 1024, 1, {-1: 1, 1: 1}),
    (4, 7, 2048, 7, {0: 4, 1: 1, 2: 3}),
    (6, 11, 8192, 19, {-1: 1, 0: 8, 1: 6, 2: 5}),
]


def certify():
    certificates = atlas()
    zeros = {pair for pair, certificate in certificates.items() if certificate.turns == 0}
    assert zeros == {(m, n) for m, n, *_ in CASES}
    print('Exactly three of the 321 regular slider pairs have tangent index zero.')
    for m, n, partition, crossings, regions in CASES:
        solver = IntersectionCertificate(m, n, partition)
        solver.run()
        solver.refine()
        result = solver.graph()
        assert result == {'crossings': crossings, 'bounded_faces': crossings+1, 'face_counts': regions}
        polygon_result = census(m, n)
        assert all(result[key] == polygon_result[key] for key in result)
        assert polygon_result['graph_index'] == certificates[m, n].turns == 0
        print('CERTIFIED', m, n, result, flush=True)
        solver.evaluate.cache_clear()
    print('Rhythms 4 / 7 have only nonnegative winding regions, and tangent index zero.')


def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as PlotPath
    import numpy as np
    from shapely.geometry import LineString, Point
    from shapely.geometry.polygon import orient
    from shapely.ops import polygonize, unary_union
    from signed_area import orbit

    background, panel, white, muted = '#101323', '#0b0e1a', '#f4f1e8', '#c7c7d4'
    colors = {-1: '#3c6284', 0: panel, 1: '#685036', 2: '#b59c76'}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': white, 'axes.titlecolor': white})
    fig, axes = plt.subplots(1, 3, figsize=(15, 7.1), facecolor=background)
    fig.subplots_adjust(left=.035, right=.98, top=.76, bottom=.22, wspace=.06)
    for ax, (m, n, _, crossings, expected) in zip(axes, CASES):
        points = orbit(m, n, 48000)
        vertices = np.array([complex(x, y) for x, y in points])
        faces = list(polygonize(unary_union(LineString(points + points[:1]))))
        records = []
        for face in faces:
            q = face.representative_point()
            relative = vertices-complex(q.x, q.y)
            winding = np.angle(np.roll(relative, -1)*np.conjugate(relative)).sum() / (2*np.pi)
            assert abs(winding-round(winding)) < 1e-8
            count = round(winding)
            records.append((face, count))
            face = orient(face, sign=1)
            coords, codes = [], []
            for ring in [face.exterior, *face.interiors]:
                ring_coords = list(ring.coords)
                coords.extend(ring_coords)
                codes.extend([PlotPath.MOVETO] + [PlotPath.LINETO]*(len(ring_coords)-2) + [PlotPath.CLOSEPOLY])
            ax.add_patch(PathPatch(PlotPath(coords, codes), facecolor=colors[count], edgecolor='none'))
        assert dict(Counter(count for _, count in records)) == expected
        ax.set_facecolor(panel)
        ax.plot(*zip(*(points + points[:1])), color=white, linewidth=.65, alpha=.8)
        ax.plot(0, 0, '+', color='#e8b66e', markersize=6, markeredgewidth=1)
        ax.set_aspect('equal')
        ax.set_xlim(-470, 470)
        ax.set_ylim(-470, 470)
        ax.set_axis_off()
        ax.set_title(f'{m} / {n}', fontsize=17, pad=10)
        # One representative label per count, where the patch has room.
        # Tiny regions remain in the certified census even without a label.
        for count in expected:
            face = max((face for face, value in records if value == count), key=lambda face: face.area)
            q = face.representative_point()
            if m == 4 and count in (0, 2):
                side = 1 if q.y > 0 else -1
                ax.annotate(f'{count:+d}' if count else '0', xy=(q.x, q.y),
                            xytext=(300, side*(330 if count == 2 else 110)), ha='center', va='center',
                            fontsize=12, arrowprops={'arrowstyle': '-', 'color': muted, 'lw': .7})
                continue
            if q.distance(Point(0, 0)) < 65:
                for candidate in [Point(q.x-65, q.y), Point(q.x, q.y+65)]:
                    if face.contains(candidate) and candidate.distance(face.boundary) > 15:
                        q = candidate
                        break
            if q.distance(face.boundary) > 15:
                ax.text(q.x, q.y, f'{count:+d}' if count else '0', ha='center', va='center',
                        fontsize=12, color=white if count <= 1 else background)
        entries = ', '.join(f'{count:+d}: {number}' if count else f'0: {number}' for count, number in expected.items())
        ax.text(.5, -.05, f'{crossings} crossing{"s" if crossings != 1 else ""} · {crossings+1} bounded regions',
                transform=ax.transAxes, ha='center', color=muted, fontsize=10)
        ax.text(.5, -.12, f'Regions by count   {entries}', transform=ax.transAxes,
                ha='center', color=muted, fontsize=9)
    fig.text(.035, .95, 'When the direction’s turns cancel', fontsize=25, weight='bold', va='top')
    fig.text(.035, .875, 'All three curves have tangent index zero. Rhythms 4 / 7 enclose only regions with nonnegative winding counts.',
             fontsize=11, color=muted)
    fig.text(.035, .105, 'Blue counts −1. Gold counts +1; light gold counts +2. Dark gaps count 0. The small cross marks the center, which always counts +1.',
             fontsize=10, color=muted)
    fig.text(.035, .065, 'Counts are certified separately for the smooth curves. These 48,000-segment illustrations preserve proportions; tiny regions may be hard to see.',
             fontsize=10, color=muted)
    output = Path(__file__).with_suffix('.png')
    fig.savefig(output, dpi=150, facecolor=background,
                metadata={'Title': 'Three orbital curves with tangent index zero',
                          'Description': 'Rhythms 2/3, 4/7, and 6/11 have different winding regions but the same zero tangent index.'})
    plt.close(fig)
    print('Wrote', output.name)


if __name__ == '__main__':
    certify()
    if '--figure' in sys.argv:
        figure()
