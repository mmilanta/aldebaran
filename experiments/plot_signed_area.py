"""Draw the signed-area illustration. Optional: NumPy and Matplotlib required.

Run from the repository root: python3 experiments/plot_signed_area.py
The plot is an offline notebook artifact; the website does not load these tools.
"""

from math import ceil, pi
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgb
import numpy as np

from signed_area import exact_area_coefficient, orbit


EXTENT = 460
PIXELS = 1200


def winding_field(points):
    """Oriented scan-line crossings at pixel centers of a closed polygon."""
    cell = 2 * EXTENT / PIXELS
    rows = [[] for _ in range(PIXELS)]
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        if y0 == y1:
            continue
        first = max(0, ceil((min(y0, y1) + EXTENT) / cell - 0.5))
        end = min(PIXELS, ceil((max(y0, y1) + EXTENT) / cell - 0.5))
        sign = 1 if y1 > y0 else -1
        for row in range(first, end):
            y = -EXTENT + (row + 0.5) * cell
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            rows[row].append((x, sign))
    field = np.zeros((PIXELS, PIXELS), dtype=np.int16)
    for row, events in enumerate(rows):
        winding, previous = 0, 0
        for x, sign in sorted(events):
            col = min(PIXELS, max(0, ceil((x + EXTENT) / cell - 0.5)))
            field[row, previous:col] = winding
            winding -= sign
            previous = col
        field[row, previous:] = winding
        assert winding == 0
    return field


def check_field(points, field):
    """Independently check colors by summing argument changes about test points."""
    vertices = np.array([complex(x, y) for x, y in points])
    rng = np.random.default_rng(21)
    indices = list(rng.integers(0, PIXELS*PIXELS, size=512))
    # Include a representative of every color, even a very small region.
    for level in np.unique(field):
        indices.append(int(np.flatnonzero(field == level)[0]))
    for index in indices:
        row, col = divmod(index, PIXELS)
        q = complex(-EXTENT + (col+.5)*2*EXTENT/PIXELS,
                    -EXTENT + (row+.5)*2*EXTENT/PIXELS)
        relative = vertices - q
        angle = np.angle(np.roll(relative, -1) * np.conjugate(relative)).sum()
        winding = angle / (2*pi)
        assert abs(winding - round(winding)) < 1e-9
        assert round(winding) == field[row, col]
    return len(indices)


def main():
    shapes = [('Garden', 7, 13), ('A negative total', 2, 25)]
    data = [(name, m, n, orbit(m, n)) for name, m, n in shapes]
    fields = [winding_field(points) for _, _, _, points in data]
    assert all(field[PIXELS//2, PIXELS//2] == 1 for field in fields)
    for field, (_, m, n, points) in zip(fields, data):
        checked = check_field(points, field)
        print(f'{m}/{n}: {checked} independent winding-color checks passed.')
    low = min(int(field.min()) for field in fields)
    high = max(int(field.max()) for field in fields)
    assert low < 0 < high
    background = '#101323'
    colors = []
    for level in range(low, high + 1):
        if level == 0:
            colors.append(background)
        else:
            base = to_rgb('#9fc7eb' if level < 0 else '#e8b66e')
            fraction = min(0.7, (abs(level) - 1) * 0.25)
            colors.append(tuple(c + (1-c)*fraction for c in base))
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(np.arange(low - 0.5, high + 1.5), cmap.N)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': '#f4f1e8',
                         'axes.titlecolor': '#f4f1e8', 'font.size': 11})
    fig, axes = plt.subplots(1, 2, figsize=(11, 6), facecolor=background)
    fig.subplots_adjust(left=.04, right=.96, top=.80, bottom=.22, wspace=.12)
    fig.text(.04, .94, 'One turn around the center. Two very different areas.',
             fontsize=20, weight='bold', va='top')
    fig.text(.04, .87, 'Gold counts positive turns; blue counts negative turns. Overlaps count more than once.',
             fontsize=11, color='#c7c7d4')
    for ax, field, (name, m, n, points) in zip(axes, fields, data):
        im = ax.imshow(field, origin='lower', extent=[-EXTENT, EXTENT]*2,
                       cmap=cmap, norm=norm, interpolation='nearest')
        closed = points + points[:1]
        ax.plot(*zip(*closed), color='#f4f1e8', linewidth=.32, alpha=.7)
        ax.plot(0, 0, marker='o', color='#f4f1e8', markersize=2.5)
        ax.add_patch(plt.Circle((0, 0), 40, fill=False, edgecolor='#f4f1e8',
                                linewidth=.65, linestyle=(0, (2, 3)), alpha=.6))
        ax.set_title(f'{name} · {m} / {n}', fontsize=14, pad=8)
        ax.set_xlim(-EXTENT, EXTENT)
        ax.set_ylim(-EXTENT, EXTENT)
        ax.set_axis_off()
        coefficient = exact_area_coefficient(m, n)
        ax.text(.5, -.05, f'Signed area: {coefficient:,}π', ha='center',
                transform=ax.transAxes, fontsize=12)
        raster_area = int(field.sum()) * (2*EXTENT/PIXELS)**2
        print(f'{m}/{n}: winding levels {int(field.min())}..{int(field.max())}; '
              f'raster area {raster_area:.3f}; exact {coefficient*pi:.3f}')
    color_axis = fig.add_axes([.35, .09, .30, .028])
    bar = fig.colorbar(im, cax=color_axis, orientation='horizontal', ticks=range(low, high+1))
    bar.ax.tick_params(colors='#c7c7d4', labelsize=9)
    bar.outline.set_visible(False)
    fig.text(.5, .035, 'Local winding count · The center stays at +1 in both drawings.',
             ha='center', fontsize=10, color='#c7c7d4')
    output = Path(__file__).with_name('signed_area.png')
    fig.savefig(output, dpi=160, facecolor=background,
                metadata={'Title': 'Signed area and winding in two orbital curves',
                          'Description': 'Gold shows positive winding, blue negative winding. '
                          'Garden has signed area 142300 pi; rhythms 2/25 have signed area -6400 pi. '
                          'Both have winding number one around the center.'})
    plt.close(fig)
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
