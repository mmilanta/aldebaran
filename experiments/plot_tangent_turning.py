"""Make the tangent atlas and loop-transition plot. NumPy/Matplotlib required.

Run from the repository root: python3 experiments/plot_tangent_turning.py
The figure is an offline notebook artifact, not a website dependency.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np

from tangent_turning import atlas, needle_transitions


def main():
    certificates = atlas()
    values = np.full((14, 23), np.nan)
    for (outer, inner), certificate in certificates.items():
        values[outer-2, inner-3] = certificate.turns
    background, white, muted = '#101323', '#f4f1e8', '#c7c7d4'
    cmap = LinearSegmentedColormap.from_list('turns', [
        (0, '#9fc7eb'), (.35, '#284e73'), (.5, background),
        (.8, '#685036'), (1, '#e8b66e')])
    cmap.set_bad(background)
    norm = TwoSlopeNorm(vmin=-25, vcenter=0, vmax=15)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': white,
                         'axes.labelcolor': muted, 'xtick.color': muted,
                         'ytick.color': muted, 'font.size': 10})
    fig = plt.figure(figsize=(14, 11), facecolor=background)
    grid = fig.add_gridspec(2, 1, left=.07, right=.94, top=.85, bottom=.10,
                            height_ratios=[2.5, 1], hspace=.52)
    ax = fig.add_subplot(grid[0], facecolor=background)
    ax.imshow(values, cmap=cmap, norm=norm, aspect='auto', interpolation='nearest')
    for (outer, inner), certificate in certificates.items():
        rgb = cmap(norm(certificate.turns))[:3]
        linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        luminance = .2126*linear[0] + .7152*linear[1] + .0722*linear[2]
        ax.text(inner-3, outer-2, str(certificate.turns), ha='center', va='center',
                fontsize=9, color=background if luminance > .18 else white)
    ax.text(21-3, 8-2, '*', ha='center', va='center', color=white, fontsize=17)
    ax.set_xticks(range(23), range(3, 26))
    ax.set_yticks(range(14), range(2, 16))
    ax.set_xlabel('Inner rhythm · backward arm', labelpad=10)
    ax.set_ylabel('Outer rhythm · forward arm', labelpad=10)
    ax.tick_params(length=0, pad=7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(.07, .955, 'The tangent counts a different kind of turn', fontsize=24, weight='bold', va='top')
    fig.text(.07, .908, 'Every curve winds once around its center. These numbers count the turns of its direction of travel.',
             fontsize=12, color=muted)
    fig.text(.07, .88, '+ means counterclockwise; − means clockwise.    * Needle has a cusp: its direction is undefined there.',
             fontsize=11, color=muted)

    lower = fig.add_subplot(grid[1], facecolor=background)
    critical = [r for r, _ in needle_transitions() if r > 58] + [65]
    edges = [58] + critical + [72]
    indices = [-10, -12, -14, -16, -18, -20, -21]
    for left, right, index in zip(edges, edges[1:], indices):
        lower.plot([left, right], [index, index], color='#9fc7eb', linewidth=2)
    for i, r in enumerate(critical):
        lower.plot([r, r], [indices[i], indices[i+1]], color='#555b78', linestyle=':', linewidth=1)
        lower.scatter([r, r], [indices[i], indices[i+1]], facecolor=background,
                      edgecolor='#9fc7eb', s=25, zorder=3)
    lower.set_title('Keep rhythms 8 / 21. Change the inner arm’s length.', loc='left',
                    pad=16, color=white, fontsize=13, weight='bold')
    lower.set_xlim(58, 72)
    lower.set_ylim(-22, -8.5)
    lower.set_xticks([58, 60, 62, 64, 65, 68, 70, 72])
    lower.set_yticks([-10, -12, -14, -16, -18, -20, -21])
    lower.set_xlabel('Inner arm length', labelpad=8)
    lower.set_ylabel('Tangent turns', labelpad=8)
    lower.grid(axis='y', color='#383b50', linewidth=.5)
    lower.spines[['top', 'right']].set_visible(False)
    lower.spines[['left', 'bottom']].set_color('#555b78')
    lower.annotate('At 65: one new\nclockwise turn', xy=(65, -20.5), xytext=(66.1, -13),
                   color=white, fontsize=11, arrowprops={'arrowstyle': '->', 'color': '#e8b66e'},
                   ha='left', va='center')
    fig.text(.07, .045, 'Top: 321 exact integer certificates. Bottom: cusp lengths are numerical locations, except 65, which is exact.',
             fontsize=10, color=muted)
    fig.text(.07, .025, 'The center’s winding stays +1 throughout the entire length range. A cusp is a gap in the tangent’s direction.',
             fontsize=10, color=muted)
    output = Path(__file__).with_name('tangent_turning.png')
    fig.savefig(output, dpi=150, facecolor=background,
                metadata={'Title': 'Tangent turning in the orbital sketchbook',
                          'Description': 'An atlas of certified tangent indices and their jumps as Needle’s inner length changes.'})
    plt.close(fig)
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
