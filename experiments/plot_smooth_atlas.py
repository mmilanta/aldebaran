"""Draw the recorded smooth crossing counts. Optional NumPy/Matplotlib.

Run: python3 experiments/plot_smooth_atlas.py
The JSON is a record; verify_smooth_atlas.py recomputes its exact proofs.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

from verify_smooth_atlas import read_atlas


def main():
    atlas = read_atlas(Path(__file__).with_name('smooth_atlas.json'))
    values = np.full((14, 23), np.nan)
    for case in atlas['verified']:
        values[case['outer']-2, case['inner']-3] = case['crossings']
    background, white, muted = '#101323', '#f4f1e8', '#c7c7d4'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': white, 'axes.labelcolor': white,
                         'xtick.color': muted, 'ytick.color': muted})
    fig, ax = plt.subplots(figsize=(15, 10), facecolor=background)
    fig.subplots_adjust(left=.08, right=.9, bottom=.16, top=.79)
    palette = plt.get_cmap('cividis').copy()
    palette.set_bad('#383b50')
    image = ax.imshow(values, cmap=palette, norm=Normalize(vmin=0, vmax=np.nanmax(values)), aspect='auto')
    for i in range(14):
        for j in range(23):
            value = values[i, j]
            text = str(int(value)) if np.isfinite(value) else '×' if (i+2, j+3) == (8, 21) else '?'
            rgb = palette(image.norm(value))[:3] if np.isfinite(value) else (0, 0, 0)
            linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb]
            luminance = sum(a*b for a, b in zip(linear, [.2126, .7152, .0722]))
            ax.text(j, i, text, ha='center', va='center', fontsize=8,
                    color='#000000' if luminance > .179 else '#ffffff')
    ax.set_xticks(range(23), [str(n) for n in range(3, 26)])
    ax.set_yticks(range(14), [str(m) for m in range(2, 16)])
    ax.set_xticks(np.arange(-.5, 23), minor=True)
    ax.set_yticks(np.arange(-.5, 14), minor=True)
    ax.grid(which='minor', color=background, linewidth=.7)
    ax.tick_params(which='both', length=0)
    ax.set_xlabel('Backward inner rhythm', labelpad=12)
    ax.set_ylabel('Forward outer rhythm', labelpad=12)
    ax.spines[:].set_visible(False)
    bar = fig.colorbar(image, ax=ax, fraction=.025, pad=.025)
    bar.set_label('Transverse double points', labelpad=12)
    bar.outline.set_visible(False)
    fig.text(.08, .95, 'Counting the sketchbook’s crossings', fontsize=25, weight='bold', va='top')
    fig.text(.08, .88, f'{len(atlas["verified"])} regular curves have complete smooth certificates. Each has one more bounded region than crossings.',
             color=muted, fontsize=11)
    status = ('× marks Needle’s cusp; ? marks an unresolved regular pair.' if atlas['unresolved']
              else 'All regular pairs are verified. × marks Needle’s cusp.')
    fig.text(.08, .085, f'Each number is a verified smooth crossing count. {status}',
             color=muted, fontsize=10)
    fig.text(.08, .045, 'Rational arc bounds and contraction tests certify the counts. Color measures crossings, independently of the signs of region winding counts.',
             color=muted, fontsize=10)
    output = Path(__file__).with_name('smooth_atlas.png')
    fig.savefig(output, dpi=150, facecolor=background,
                metadata={'Title': 'Certified smooth crossings across the orbital sketchbook',
                          'Description': f'{len(atlas["verified"])} exact smooth census certificates; unresolved pairs and the singular pair remain separate.'})
    plt.close(fig)
    print('Wrote', output.name)


if __name__ == '__main__':
    main()
