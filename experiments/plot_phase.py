"""Draw three stills of the mirror contact and its phase unfoldings.

Run: python3 experiments/plot_phase.py
Optional illustration only: requires Matplotlib. The certificates use the
standard library and do not depend on this figure or its numerical solves.
"""

from math import pi
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase_contact_probe import gap, orbit
from phase_unfolding import candidate, coefficients


def crossing(a, phase):
    lo, hi = (-32, -1) if phase > 0 else (1, 32)
    gl, gh = [gap(y, a, phase)[0] for y in (lo, hi)]
    if gl*gh >= 0:
        raise ValueError('The companion crossing is not bracketed.')
    for _ in range(48):
        mid = (lo+hi)/2
        if gap(mid, a, phase)[0]*gl > 0:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def main():
    data = coefficients()
    critical = float(data['weight'].midpoint())
    phases = [0, .001, -.001]
    heights = [-32+64*j/640 for j in range(641)]
    background, panel = '#101323', '#0b0e1a'
    gold, white, muted = '#e8b66e', '#f4f1e8', '#c7c7d4'
    plt.rcParams.update({'font.family': ['DejaVu Sans', 'sans-serif'], 'font.size': 11,
                         'text.color': white, 'axes.labelcolor': muted,
                         'xtick.color': muted, 'ytick.color': muted,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'aldebaran-phase'})
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 8.5), facecolor=background,
                             sharex=True, sharey=True)
    fig.subplots_adjust(left=.09, right=.965, top=.73, bottom=.25, wspace=.22)
    for j, (ax, phase) in enumerate(zip(axes, phases)):
        if phase:
            u, _, weight = candidate(phase, data)
            a = float(weight)
            y = orbit(pi+float(u), 0, a, phase).imag
            simple = crossing(a, phase)
            ax.plot(0, simple, 'o', color=gold, markeredgecolor=panel, markersize=6)
        else:
            a, y = critical, 0
        current = [gap(y, a, phase)[0] for y in heights]
        reference = [gap(y, a, 0)[0] for y in heights]
        ax.set_facecolor(panel)
        for spine in ax.spines.values():
            spine.set_color('#555b78')
        ax.axvline(0, color='#bcbccc', linewidth=1)
        ax.axhline(0, color='#555b78', linewidth=.7, linestyle=':')
        ax.plot(reference, heights, color='#b6b7c9', linewidth=1.3, dashes=(4, 4),
                label='Mirror at same blend')
        ax.plot(current, heights, color=gold, linewidth=2, label='Current turn')
        ax.plot(0, y, 'o', markerfacecolor=panel, markeredgecolor=white,
                markeredgewidth=1.6, markersize=8)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-32, 32)
        ax.set_xticks([-1.5, 0, 1.5])
        ax.set_yticks([-32, -16, 0, 16, 32])
        ax.tick_params(length=3)
        ax.set_title(['Mirror intact', 'Turn +0.001 rad', 'Turn −0.001 rad'][j],
                     color=gold, fontsize=13, pad=29)
        ax.text(.5, 1.025, f'Blend weight {100*a:.5f}%', transform=ax.transAxes,
                color=muted, ha='center', fontsize=10)
        ax.text(.5, -.17, ['One cubic contact', 'Touch above the axis', 'Touch below the axis'][j],
                transform=ax.transAxes, ha='center', color=white, fontsize=11)
    axes[0].set_ylabel('Height (drawing units)')
    fig.text(.07, .94, 'A small turn breaks the mirror', fontsize=26, weight='bold')
    fig.text(.07, .885, 'Two local branches, still moving. Plot their horizontal separation against height.',
             fontsize=12, color=muted)
    fig.text(.07, .845, 'A hollow ring marks a contact; a filled dot marks a crossing. Each panel follows its own contact weight.',
             fontsize=11, color=muted)
    fig.text(.52, .145, 'Horizontal separation  x₊(y) − x₋(y)  (drawing units)',
             ha='center', fontsize=11, color=muted)
    handles, labels = axes[2].get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc='lower left', bbox_to_anchor=(.062, .069),
               frameon=False, ncol=2, labelcolor=muted, fontsize=10)
    fig.text(.07, .035, 'The axes have separate scales. Numerical drawings; the rational event certificates are independent of the pixels.',
             color=muted, fontsize=10)
    destination = Path(__file__).with_name('phase.svg')
    fig.savefig(destination, facecolor=background, metadata={
        'Title': 'A small turn breaks the mirror', 'Date': None,
        'Description': 'Horizontal separation against height for a cubic mirror contact and its two '
                       'quadratic unfoldings after phases of plus and minus .001 radians. '
                       'Each nonzero phase has a crossing and an off-axis touch in this window. '
                       'Separate axis scales; both branches keep moving.'})
    plt.close(fig)
    source = destination.read_text()
    source = source.replace('<svg ', '<svg role="img" aria-labelledby="phase-title phase-description" ', 1)
    source = source.replace('<title>', '<title id="phase-title">', 1)
    start = source.index('>', source.index('<svg '))+1
    source = (source[:start]+'\n<desc id="phase-description">Three graphs of horizontal branch separation against '
              'height. At zero phase the cubic contact stays on the axis. Positive phase moves a quadratic '
              'touch above it; negative phase moves it below. Hollow rings mark contacts, filled dots '
              'mark crossings. The two axis scales differ. Both branches keep moving.</desc>'+source[start:])
    destination.write_text('\n'.join(line.rstrip() for line in source.splitlines())+'\n')
    print('Wrote', destination.name)


if __name__ == '__main__':
    main()
