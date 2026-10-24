"""Draw the branch-separation graph for the first cubic contact.

Run: python3 experiments/plot_arm_contact.py
Optional illustration only: requires Matplotlib, outside the website runtime.
All mathematical certificates in arm_detour_events.py use the standard library.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from arm_detour import BRIDGES
from arm_detour_events import branch_gap, events, orbit_derivative
from arm_detour_lens import central_radius
from math import ceil, pi


def main():
    first, second = BRIDGES[0][1:3]
    record, = events(first, second, 'tangent')
    critical = float(record['weight'].midpoint())
    weights = [critical-.001, critical, critical+.001]
    heights = [-20+40*j/400 for j in range(401)]
    traces = [[branch_gap(y, first, second, a) for y in heights] for a in weights]
    limit = ceil(max(abs(gap) for gaps in traces for gap in gaps)*10)/10
    background, panel, muted, white = '#101323', '#0b0e1a', '#c7c7d4', '#f4f1e8'
    colors = ['#9fc7eb', white, '#e8b66e']
    plt.rcParams.update({'font.family': ['DejaVu Sans', 'sans-serif'], 'font.size': 11,
                         'text.color': white, 'axes.labelcolor': muted,
                         'xtick.color': muted, 'ytick.color': muted,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'aldebaran-arm-contact'})
    fig, axes = plt.subplots(1, 3, figsize=(12, 6.5), facecolor=background, sharex=True, sharey=True)
    fig.subplots_adjust(left=.09, right=.965, top=.7, bottom=.24, wspace=.25)
    for j, (ax, a, gaps, color) in enumerate(zip(axes, weights, traces, colors)):
        ax.set_facecolor(panel)
        for spine in ax.spines.values():
            spine.set_color('#555b78')
        ax.axvline(0, color='#bcbccc', linewidth=1)
        ax.axhline(0, color='#555b78', linewidth=.7, linestyle=':')
        ax.plot(gaps, heights, color=color, linewidth=2)
        zeros = [0]
        if j == 2:
            low, high = .01, 20
            gl, gh = [branch_gap(y, first, second, a) for y in (low, high)]
            assert gl*gh < 0
            for _ in range(48):
                mid = (low+high)/2
                if branch_gap(mid, first, second, a)*gl > 0:
                    low = mid
                else:
                    high = mid
            root = (low+high)/2
            zeros += [-root, root]
        ax.plot([0]*len(zeros), zeros, 'o', color=color, markeredgecolor=panel, markersize=6)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-20, 20)
        ax.set_xticks([-limit, 0, limit])
        ax.set_yticks([-20, -10, 0, 10, 20])
        ax.tick_params(length=3)
        ax.set_title(['Just before', 'Cubic contact (rounded)', 'Just after'][j], color=color, fontsize=13, pad=28)
        ax.text(.5, 1.025, f'Leg weight {100*a:.5f}%', transform=ax.transAxes,
                color=muted, ha='center', fontsize=10)
        ax.text(.5, -.25, ['One meeting', 'Equal slope and curvature', 'Three meetings'][j],
                transform=ax.transAxes, ha='center', color=color, fontsize=11)
    axes[0].set_ylabel('Height above the horizontal axis\n(drawing units)')
    fig.text(.07, .93, 'The branches trade places', fontsize=25, weight='bold')
    fig.text(.07, .86, 'First detour, middle leg. Plot the horizontal separation between the two selected end branches.',
             fontsize=11, color=muted)
    fig.text(.07, .815, 'Each meeting is a zero of this separation: an intersection with the vertical line.',
             fontsize=11, color=muted)
    fig.text(.515, .15, 'Horizontal separation  x₊(y) − x₋(y)  (drawing units)', ha='center', fontsize=11, color=muted)
    radius = central_radius(first, second, critical)
    speed = abs(orbit_derivative(pi+radius, 1, first, second, critical))
    fig.text(.07, .085, f'At contact both branches still move at about {speed:.2f} drawing units per radian. Their separation first differs cubically.',
             color=muted, fontsize=10)
    fig.text(.07, .04, 'The axes have separate labeled scales. These are graphs of separation against height. Exact event isolation is a separate calculation.',
             color=muted, fontsize=9)
    destination = Path(__file__).with_name('arm_contact.svg')
    fig.savefig(destination, facecolor=background, metadata={
        'Title': 'The branches trade places at a cubic contact', 'Date': None,
        'Description': 'Before, at, and after the first central-axis contact of the 2/3 to 4/7 arm detour. '
                       'Graphs show horizontal separation against height, with separate labeled axis scales. '
                       'The axis meeting persists; two extra nearby crossings appear after contact. '
                       'Both branches have nonzero velocities throughout.'})
    plt.close(fig)
    source = destination.read_text()
    source = source.replace('<svg ', '<svg role="img" aria-labelledby="contact-title contact-description" ', 1)
    source = source.replace('<title>', '<title id="contact-title">', 1)
    start = source.index('>', source.index('<svg '))+1
    source = (source[:start]+'\n<desc id="contact-description">Graphs of horizontal branch separation against height before, '
              'at, and after a cubic contact. The axis meeting persists; two extra nearby crossings '
              'appear afterwards. Both branches keep moving. The axes have separate labeled scales.</desc>'
              +source[start:])
    destination.write_text('\n'.join(line.rstrip() for line in source.splitlines())+'\n')
    print('Wrote', destination.name)


if __name__ == '__main__':
    main()
