"""Magnify Crown's tiny +3 region. Optional NumPy, Matplotlib, Shapely required.

Run from the repository root: python3 experiments/plot_small_region.py
This offline illustration is not a website dependency or a smooth-topology proof.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, ConnectionPatch, PathPatch
from matplotlib.path import Path as PlotPath
import numpy as np
from shapely.geometry import LineString
from shapely.geometry.polygon import orient
from shapely.ops import polygonize, unary_union

from signed_area import orbit


def main():
    points = orbit(9, 23, 96000)
    vertices = np.array([complex(x, y) for x, y in points])
    faces = list(polygonize(unary_union(LineString(points + points[:1]))))
    data = []
    for face in faces:
        q = face.representative_point()
        relative = vertices - complex(q.x, q.y)
        turns = np.angle(np.roll(relative, -1) * np.conjugate(relative)).sum() / (2*np.pi)
        assert abs(turns - round(turns)) < 1e-9
        data.append((face, round(turns)))
    small = [face for face, count in data if count == 3]
    assert len(small) == 8
    target = max(small, key=lambda face: face.centroid.x)
    area = target.area
    background, white, muted = '#101323', '#f4f1e8', '#c7c7d4'
    colors = {0: '#0b0e1a', 1: '#685036', 2: '#9a805f', 3: '#bba17a'}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': white,
                         'axes.labelcolor': muted, 'xtick.color': muted,
                         'ytick.color': muted, 'font.size': 11})
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.8), facecolor=background)
    fig.subplots_adjust(left=.04, right=.97, top=.77, bottom=.20, wspace=.15)
    for ax in axes:
        ax.set_facecolor('#0b0e1a')
        for face, count in data:
            # Some rings touch at graph vertices. Preserve interior rings and
            # their opposite orientation instead of painting over the holes.
            face = orient(face, sign=1)
            coords, codes = [], []
            for ring in [face.exterior, *face.interiors]:
                ring_coords = list(ring.coords)
                coords.extend(ring_coords)
                codes.extend([PlotPath.MOVETO] + [PlotPath.LINETO]*(len(ring_coords)-2) + [PlotPath.CLOSEPOLY])
            ax.add_patch(PathPatch(PlotPath(coords, codes), facecolor=colors[count], edgecolor='none'))
        ax.plot(*zip(*(points + points[:1])), color=white, linewidth=.7, alpha=.8)
        ax.set_aspect('equal')
        ax.spines[:].set_color('#555b78')
    axes[0].set_xlim(-460, 460)
    axes[0].set_ylim(-460, 460)
    axes[0].set_axis_off()
    axes[0].add_patch(Circle((291.27, 0), 14, facecolor='none', edgecolor=white, linewidth=1))
    axes[0].set_title('Crown · 9 / 23', fontsize=14, pad=12, color=white)
    axes[1].set_xlim(291.09, 291.45)
    axes[1].set_ylim(-.18, .18)
    axes[1].ticklabel_format(style='plain', useOffset=False)
    axes[1].set_xticks([291.1, 291.2, 291.3, 291.4])
    axes[1].set_yticks([-.15, 0, .15])
    axes[1].set_title('The same patch, magnified', fontsize=14, pad=12, color=white)
    axes[1].set_xlabel('Drawing units')
    axes[1].text(291.265, 0, '+3', ha='center', va='center', color=background, fontsize=15, weight='bold')
    fig.add_artist(ConnectionPatch(xyA=(310, 0), coordsA=axes[0].transData,
                                  xyB=(291.09, .12), coordsB=axes[1].transData,
                                  color='#9999ae', linestyle=':', linewidth=1))
    fig.text(.04, .95, 'A region smaller than a pixel', fontsize=24, weight='bold', va='top')
    fig.text(.04, .87, 'Crown hides eight tiny +3 regions. A color grid can miss them; a point can still count their turns.',
             fontsize=11, color=muted)
    fig.text(.04, .105, f'This patch has about {area:.5f} square drawing units of area in the finely sampled polygon.',
             fontsize=11, color=muted)
    fig.text(.04, .065, 'One drawing unit is one pixel in the sketchbook’s saved 1000 × 1000 image. The white ring locates the zoom.',
             fontsize=10, color=muted)
    fig.text(.04, .035, 'Gold brightness records winding count. The selected point at (291.27, 0) is certified +3 for the smooth curve too.',
             fontsize=10, color=muted)
    output = Path(__file__).with_name('small_region.png')
    fig.savefig(output, dpi=160, facecolor=background,
                metadata={'Title': 'A tiny winding region in Crown',
                          'Description': 'Crown and a magnified region of winding count three, smaller than one native canvas pixel.'})
    plt.close(fig)
    print(f'Crown: {len(faces)} polygon faces; eight +3 regions; highlighted area {area:.12f}.')
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
