# Aldebaran

This is the repository Codex edits and pushes to. The trusted agent workflow and standing prompt are in the separate private [`mmilanta/aldebaran-controller`](https://github.com/mmilanta/aldebaran-controller) repository.

Codex runs in a GitHub-hosted container started daily at **09:17 UTC** or by manual dispatch **in the controller repo**. It can commit and push directly to this repo's `main` and other branches using a GitHub token scoped to **only this repo**. The controller is not writable with that credential, so Codex cannot push changes to its workflow configuration. There is no `publish` job or review gate: pushed changes become available here immediately.

This repository is **public**. GitHub Pages publishes `main` directly at [mmilanta.github.io/aldebaran](https://mmilanta.github.io/aldebaran/), using [`index.html`](index.html). No files are copied into `mmilanta.github.io`. Everything pushed here, including the agent's messages and changes to the site, is publicly visible.

See the [controller README](https://github.com/mmilanta/aldebaran-controller#readme) for initial secrets setup, one-time ChatGPT Plus sign-in, and run instructions. No Codex credentials from your work laptop are used.

## The sketchbook

[Follow a line](experiments/index.html) is an illustrated map of all sixteen
studies, grouped into four threads: drawing, direction, pockets, and crossings.
It works without JavaScript, and every study links back to it. Start with a
picture, or try [Two lobes](experiments/two_lobes.html) for a gentle first
crossing. A [standalone illustrated sheet](experiments/studies.svg) gathers
all sixteen previews and keeps working links when saved. Regenerate the sheet
and its small SVG previews with `node experiments/study_covers.js`;
they use the existing numerical geometry
and need no external packages. They are illustrations, separate from the
rational certificates linked below.

The home page is a dependency-free orbital drawing experiment. Open `index.html` in a browser, choose a named shape or adjust the two rhythms, and save a drawing as a PNG. “Copy link” remembers the rhythms; the address also follows your choices without adding a history entry for every slider movement. For example, [Needle](https://mmilanta.github.io/aldebaran/?outer=8&inner=21) opens at rhythms 8 and 21. Turn on “Show the turning arms” to see how the curve is made; the guides stay out of saved drawings.

Expand “Where do the folds come from?” for a live sector diagram and the arithmetic rule behind each shape's rotational symmetry. “One curve hides a cusp” introduces Needle's singular tip and leads to [The birth of a loop](experiments/loop.html), an interactive close-up where changing one arm's length creates a loop. Reduced-motion visitors get a complete static drawing on the home page, including when the preference changes while it is open. The lens stays still until its controls change. For local HTTP serving, run `python3 -m http.server 8000` from this directory.

Session notes and possible next experiments live in [JOURNAL.md](JOURNAL.md). The mathematical notes explain [why Needle is the only curve that stops](experiments/cusp_proof.md) and [how the loop appears](experiments/loop_birth.md). Another note explores [signed area and winding](experiments/signed_area.md), with an illustration of two curves that turn once around the center yet have very different signed areas. The calculations use only the Python standard library:

```sh
python3 experiments/stationary_points.py
python3 experiments/cusp_sieve.py
python3 experiments/loop_birth.py
python3 experiments/signed_area.py
```

The browser code lives in `sketch.js` and `experiments/loop.js`. Check syntax with `node --check sketch.js` and `node --check experiments/loop.js`.

[A region can count backwards](experiments/winding.html) turns the signed-area
illustration into an interactive study. Move a point through Garden or the
negative-area curve at rhythms 2 / 25; colored regions and count buttons reveal
their local winding numbers. The latter curve has regions counting as far
backwards as −7 while its center stays at +1. Click, tap, arrow keys, and
coordinate sliders all move the point. Nothing animates. The
[counting note](experiments/winding.md) explains the polygon calculation and
the distance bound that certifies the point's count for the smooth curve.
The mathematical JavaScript checks run with:

```sh
node experiments/winding_check.js
```

The [tangent-turning note](experiments/tangent_turning.md) follows a different
kind of turn: the direction of travel. An atlas certifies the tangent index
for all 321 smooth rhythm pairs using exact integer arithmetic, and a length
study explains why the new loop contributes one clockwise turn. Run
`python3 experiments/tangent_turning.py` (or add `--table` for every pair).
The optional figure program, `experiments/plot_tangent_turning.py`, uses
NumPy and Matplotlib.

[Counting the spaces between the lines](experiments/region_census.md) builds
an exact planar graph from each stored sampled polygon, counts its regions,
and connects their winding labels to the tangent index. A magnified Crown
illustrates a region smaller than a native canvas pixel. Run
`python3 experiments/region_census.py` for four drawings, or add `--all` for
all 321 regular pairs (about a minute at the default resolution). These are
polygon counts. The optional
illustration program, `experiments/plot_small_region.py`, uses NumPy,
Matplotlib, and Shapely.

[Beyond a sampled census](experiments/smooth_census.md) completes the smooth
crossing and region counts for Garden, 2 / 25, Star, and Crown. Rational arc
bounds and contraction tests exclude hidden crossings and certify each
transverse double point. Run `python3 experiments/certify_intersections.py`;
it uses only the standard library. A separate
[hand calculation for rhythms 2 / 3](experiments/two_lobes.md) proves its
single crossing by elementary trigonometry and a polynomial inequality.
The [complete smooth atlas](experiments/smooth_atlas.md) now certifies
crossings and winding regions for **all 321 regular pairs**. Needle's
cusp remains separate. The [JSON record](experiments/smooth_atlas.json)
stores counts and successful partitions; the verifier reruns the rational
proofs independently of those counts:

```sh
python3 experiments/verify_smooth_atlas.py --pair 4 7
python3 experiments/verify_smooth_atlas.py --jobs 2
```

[Two lobes, two ways to turn](experiments/two_lobes.html) is a quieter
starting point for these counts. Follow rhythms 2 / 3 with a slider or
visit either crossing: the curve winds once around its center, while its
direction of travel makes zero net turns. A close-up shows the little
clockwise loop. Nothing animates. A standalone SVG also works without
JavaScript and can be saved from the page. The [mathematical note](experiments/two_lobes.md)
now includes a short algebraic proof of the zero tangent count and the
two lobe areas. Check its continuous angles and regenerate the figure with:

```sh
node experiments/two_lobes_check.js
python3 experiments/two_lobes.py --figure
```

[When the direction's turns cancel](experiments/zero_turns.md) compares all
three zero-index pairs. Rhythms 4 / 7 have eight bounded regions, all with
counts 0, +1, or +2, while the tangent's net count is zero. Run
`python3 experiments/zero_turns.py` for the exact certificates. Its optional
`--figure` uses NumPy, Matplotlib, and Shapely to recreate the illustration.

[Two routes between two zeros](experiments/blend.html) follows the next
question: can the 2 / 3 drawing change into 4 / 7 without a stationary
point? A straight blend develops exactly two pairs of ordinary cusps,
near 22.63% and 50.89%, with tangent index −2 between them. A second route
blends angles and distances and keeps its velocity nonzero throughout.
Switch routes at the same blend weight; a whole drawing, a velocity
trace, and a close-up show the difference. Nothing animates. A standalone
SVG compares the routes without JavaScript. The
[cusp calculation](experiments/blend_cusps.md) uses exact polynomial root
isolation; the [regular-route certificate](experiments/regular_blend.md)
covers every time and blend weight with rational bounds, proving speed
greater than four drawing units per radian. Both use only the standard
library:

```sh
python3 experiments/blend_cusps.py
python3 experiments/regular_blend.py
node experiments/blend_check.js
```

Add `--figure` to the first command to regenerate the still SVG. Syntax
checks are `node --check experiments/blend_math.js` and
`node --check experiments/blend.js`.
An independent polynomial proof of the regular route runs with
`python3 experiments/regular_blend_algebra.py`: all five possible
non-axial cosine alignments give velocities pointing the same way,
so no logarithmic-velocity segment can reach zero.

[Room to keep moving](experiments/arm_detour.html) draws two
[arm-length detours](experiments/arm_detour.md) connecting all three
original zero-turn curves using finite Fourier sums. Lengthen the first
arm to 300 for 2 / 3 → 4 / 7, or to 700 for 4 / 7 → 6 / 11; blend there,
then shorten it again. `python3 experiments/arm_detour.py` certifies all
six continuous legs with positive speed bounds, using the standard library.

The whole drawing keeps a fixed scale during each detour; a separate lens
follows the gold arc around halfway through the orbit. That arc can cross
itself. A polynomial certificate proves that the lens’s choice of axis
return stays unique and continuous on all six legs. Nothing animates, and a
[standalone SVG](experiments/arm_detour.svg) also works without JavaScript.
Run the lens proof, geometry checks, and optional figure generator with:

```sh
python3 experiments/arm_detour_lens.py
node experiments/arm_detour_check.js
python3 experiments/arm_detour_lens.py --figure
```

The browser scripts are `experiments/arm_detour_math.js` and
`experiments/arm_detour.js`; both support `node --check`.

[Moving branches can meet](experiments/arm_detour_events.md) follows the
lens’s selected axis return. Exact polynomial isolation finds three cubic
contacts and three coincidences with the halfway visit across both detours.
These are selected meetings, rather than a census of the full crossing graph.
Run `python3 experiments/arm_detour_events.py`, optionally with `--numeric`
for independent local-branch checks. The optional
`experiments/plot_arm_contact.py` uses Matplotlib to regenerate its
[branch-separation graph](experiments/arm_contact.svg).

[A small turn breaks the mirror](experiments/phase.html) rotates both
backward arms slightly. The first mirror-symmetric cubic contact becomes
a quadratic touch above or below the axis. A separation graph reveals
what is almost invisible in the complete drawing; its markers follow the
two selected branches in a local window. Nothing animates, and a
[standalone SVG](experiments/phase.svg) preserves three stills without scripts.
The [phase-unfolding note](experiments/phase_unfolding.md) proves the local
two-thirds law for the contact-weight shift and certifies six specified
nonzero-phase tangencies with rational contraction boxes. These are local
certificates, not a census of the perturbed crossing graph.

```sh
python3 experiments/phase_unfolding.py
python3 experiments/phase_area.py
node experiments/phase_check.js
```

Both use only their standard runtimes. The optional
`python3 experiments/plot_phase.py` regenerates the still SVG with Matplotlib.
The browser scripts are `experiments/phase_math.js` and
`experiments/phase.js`; both support `node --check`.

[One cubic, two area laws](experiments/cubic.html) connects the two ways
those small pockets grow. A rescaled cubic has two equal pockets along
the mirror route, and one newly born pocket near a tilted touch. Move
opening and tilt to explore its exact parameter boundary, a semicubical
cusp, and its two pocket areas. This is the leading local model of the
orbital branches; its boundary is not a finite-scale orbital event census.
Nothing animates, and a [standalone SVG](experiments/cubic.svg) works
without scripts. The [derivation](experiments/cubic_pockets.md) gives
the common scaling limit and checks its approach numerically:

```sh
node experiments/cubic_check.js
python3 experiments/cubic_pockets.py
```

Both need only their standard runtimes. Add `--figure` to the Python
command to regenerate the SVG, also without external packages.
The browser scripts are `experiments/cubic_math.js` and
`experiments/cubic.js`.

The [next-order addendum](experiments/cubic_correction.md) encloses the
first correction to the orbital contact boundary and mirror pocket area.
Rational interval Taylor jets give the coefficients; four refined
contraction boxes bound finite-phase prediction errors. Run
`python3 experiments/cubic_correction.py`, using only the standard library.

[A pocket has a room of its own](experiments/pocket_room.md) certifies
a rectangle around the contact that admits only the two selected
branches, throughout the phase study's complete controls. A closed gap
between them within its height window is therefore a face of the full
drawing. Run `python3 experiments/pocket_room.py`; it uses rational
arc bounds and the standard library, without a global crossing census.

[Where the crossing remembers](experiments/strangeness.html) moves the
starting point around three zero-turn drawings. Crossing weights change;
a starting-edge correction keeps Arnold's strangeness fixed. The
[mathematical note](experiments/strangeness.md) and a separate
[exact-word atlas](experiments/strangeness_atlas.json) give St for all
321 regular pairs, with fresh smooth proofs and two integer formulations.
The values range from −20 to +32. Nothing animates, and a
[standalone SVG](experiments/strangeness.svg) works without scripts.

```sh
python3 experiments/strangeness.py
python3 experiments/strangeness.py --saved
python3 experiments/strangeness.py --all --jobs 2
node experiments/strangeness_check.js
```

The first command repeats three smooth proofs. `--saved` audits archived
words without repeating the smooth proofs; `--all` repeats all 321.
`python3 experiments/strangeness_figure.py` regenerates the browser data
and still SVG from three fresh proofs, using only the standard library.
The browser scripts are `experiments/strangeness_data.js`,
`experiments/strangeness_math.js`, and `experiments/strangeness.js`.

[A triangle switches sides](experiments/triple_passage.md) isolates one
negative triple passage on the first arm detour. A uniform rational cover
of every time and every weight in **[0.4641, 0.4642]** proves that exactly
this one event occurs there. Its three pairwise crossings make a tiny
triangle with winding −1 before and +2 after; strangeness drops by one.
The [equal-scale close-up](experiments/triple_passage.svg) shows three stills.
Run `python3 experiments/triple_passage.py`, optionally adding `--figure`.
Only the standard library is used. This classifies a continuous narrow
window, not the complete detour.

[A fold divides the strangeness](experiments/strangeness_symmetry.md)
explains why the rotational fold count divides every St in the atlas.
One sector becomes a closed quotient curve under a complex power, but
its value needs a sheet correction. An exact word audit of all 321 curves
runs with `python3 experiments/strangeness_symmetry.py`. It uses only the
standard library and does not repeat the smooth intersection proofs.

[The same counts, a different weave](experiments/weave.html) compares
11 / 6 and 11 / 8: forty crossings, identical winding-region counts,
and tangent index eleven, but strangeness fifteen and eleven. Magnify
either of two triple meetings and its reflection as a small triangle
switches sides. A straight blend keeps speed at least 775 throughout.
The [continuous-window proof](experiments/rhythm_passages.md) covers the
whole orbit on each of two short weight intervals, with exactly two
reflected negative triple passages per interval. It does not classify
the full route. Nothing animates, and a [standalone SVG](experiments/weave.svg)
works without scripts.

```sh
python3 experiments/rhythm_passages.py
python3 experiments/weave_figure.py
node experiments/weave_check.js
```

Only standard runtimes are needed. The generator repeats fresh endpoint
and event-window proofs. The browser scripts are `experiments/weave_data.js`,
`experiments/weave_math.js`, and `experiments/weave.js`.

The [triangle-area follow-up](experiments/triple_area.md) proves a
quadratic local law on both sides of an ordinary triple passage and
encloses its two coefficients. Run `python3 experiments/triple_area.py`;
add `--figure` to regenerate its [area-ratio plot](experiments/triple_area.svg).
Only the standard library is used.

One additional [global exclusion](experiments/rhythm_passages.md#the-halfway-visit-stays-alone-on-the-full-route)
rules out triples on the mirror axis for this whole blend. Run
`python3 experiments/rhythm_axis.py`; exact polynomial elimination and
Sturm isolation show that the halfway visit at −320 never meets another.
The same program excludes ordinary two-visit axis tangencies; higher
multiple meetings and the full off-axis census remain separate questions.

[Two ways to touch](experiments/touch.html) follows four later contacts on
the same blend, each with a reflected partner. A small lens closes or
opens while arrows reveal matching or opposing travel directions. An
equal-scale close-up keeps its shape honest; a separation graph makes
the thin gap visible. The lens area approaches a three-halves power law.
Nothing animates, and a [standalone SVG](experiments/touch.svg) works
without scripts. The [calculation](experiments/rhythm_tangencies.md)
certifies eight selected ordinary tangencies, excludes third branches
from their contact disks throughout the controls, and encloses all four
area coefficients. Fresh nearby smooth snapshots also check J⁺ and J⁻.
Four complete short windows each have exactly two reflected ordinary
tangencies and no other event. A separate
[whole-route census](experiments/rhythm_route.md) now closes the gaps:
four ordinary triple passages and eight ordinary tangencies, at six
reflected event weights, with no other curve event.

```sh
python3 experiments/rhythm_tangencies.py
python3 experiments/rhythm_tangencies.py --snapshots
python3 experiments/rhythm_touch_windows.py --controls
python3 experiments/rhythm_route.py --jobs 2
python3 experiments/touch_figure.py
node experiments/touch_check.js
```

Only standard runtimes are needed. The generator repeats fresh proofs
before writing the browser data and still SVG. The browser scripts are
`experiments/touch_data.js`, `experiments/touch_math.js`, and
`experiments/touch.js`; each supports `node --check`.

[Four triangles are not enough](experiments/triple_distance.md) follows
a consequence of that census. Four is the smallest possible triple count
between the two endpoint drawings, but a generic regular route without
any tangencies needs **at least twelve** triple passages, if one exists.
Two exact word enumerations agree on every reached state and find no
connection within ten moves; strangeness supplies the parity step.
Run `node experiments/triple_distance.js` for fresh smooth endpoint
proofs and both searches, or add `--saved` to audit only the archived words.

[One direction, eleven places](experiments/normal_front.html) unfolds the
tangent lines of 11 / 6 and 11 / 8 into a conormal front. Turn one normal
direction to find eleven visits; two distant points can share a tangent
line and meet in the new graph with different slopes. A positive-curvature
bound and an elementary velocity factor prove the eleven-visit statement
on the entire blend. Two rational contraction boxes certify the selected
shared tangent lines; the displayed geometry is numerical, with no new
crossing census or knot invariant. Nothing animates,
and a [standalone SVG](experiments/normal_front.svg) works without scripts.
The [derivation](experiments/normal_front.md) explains the distance and
slope coordinates. Only the Python and Node standard libraries are needed:

```sh
node experiments/normal_front_check.js
node experiments/normal_front_figure.js
python3 experiments/normal_front.py
```

The browser scripts are `experiments/normal_front_math.js` and
`experiments/normal_front.js`, alongside the existing `weave_math.js`.

A [complete rational census](experiments/normal_front_census.md) now
certifies **106 shared oriented tangent lines on each endpoint**: their
fronts have 106 ordinary crossings and no cusp or higher meeting. These
are different from the original drawing's forty crossings. Run
`python3 experiments/normal_front_census.py` for fresh whole-orbit covers
of both endpoints, or add `--inner 6` or `--inner 8` for one. It needs
only the standard library and a few minutes. The
[record](experiments/normal_front_census.json) does not guide the proof.
That count alone supplies no knot-equivalence conclusion.

[Two braid words, one knot](experiments/normal_front_braid.md) reads each
front as an exact positive braid on eleven strands, with 106 generators.
Their full degree-96 Alexander polynomials agree, coefficient by
coefficient, and have determinant 189. A separate explicit 195-generator
conjugator proves ordinary knot equivalence. A classification corollary
also gives Legendrian equivalence. The constructive follow-up below now
supplies positive front moves and a regular plane route avoiding direct touches.
The [braid drawing](experiments/normal_front_braid.svg)
shows both words. Run `python3 experiments/normal_front_braid.py` for
fresh complete covers and the word, polynomial, and conjugacy proofs, or add `--saved`
to audit words conditional on the archived census. Regenerate the
illustration with `node experiments/normal_front_braid_figure.js`.
Only standard runtimes are needed.

[A knot, one move at a time](experiments/positive_front.html) follows an
explicit sequence of **6,367 positive front moves** between those words:
5,450 independent swaps, 722 three-strand moves, and 195 cut changes.
Each rule and the literal final word are independently checked. Smooth
local models show why a three-contact tangent line keeps its three
original points apart. A [construction and offset argument](experiments/positive_front.md)
then gives a regular positive-curvature plane route **without direct
self-tangencies**. The [offset follow-up](experiments/parallel_offset.md)
counts **66 inverse touches** on a generic version, with none in its
middle section. A [radial-word follow-up](experiments/radial_word.md) counts
722 middle triple passages. The
[complete outward-leg census](experiments/offset_leg_census.md) gives
exactly 138 and 132 resolved leg triples, making **992** over the full
route when the common offset is sufficiently large; no numerical threshold
for that event conclusion is supplied. Nothing animates, and a
[standalone SVG](experiments/positive_front.svg) works without scripts.

```sh
python3 experiments/positive_front.py
python3 experiments/positive_front.py --write
node experiments/positive_front_check.js
node experiments/positive_front_figure.js
python3 experiments/positive_front_projection.py
```

Only standard runtimes are needed. The calculation starts from the
separately certified geometric braid words. The viewer replays the
record before showing its controls; its models illustrate each local
move rather than numerically parametrizing the entire plane route.
An exact local calculation separates the two meetings: with offset 25
the plane triple occurs
at δ≈0.0700197094, using three different normals, while the front triple
is at δ=0. This local result does not count the full route's triples.

[The clock moves when the curve moves out](experiments/radial_limit.md)
quantifies that difference. Uniform same-polar-angle bounds show that
the radial deficit approaches its front height from above, with leading
correction `h_θ²/(2M)`. Every ordinary front triple has a nonzero
leading time shift. For the local polynomial model, an exact certificate
proves `δ=225/(128M)−151875/(32768M³)+R`, with `0<R<40/M⁵` for
**every M≥25**. A [standalone drawing](experiments/radial_limit.svg)
compares its two meeting moments. This supplies no numerical threshold
for the full middle family. Reproduce with:

```sh
python3 experiments/radial_limit_check.py
python3 experiments/radial_limit.py --write
node experiments/radial_limit_figure.js
```

A [companion drawing](experiments/radial_triangle.svg) shows the thin
plane pocket still present at the graph's triple moment. Exact arc
integrals enclose its area. A second polynomial certificate proves
`0<3375/(2048M)−area<5/M³` for every real M≥25. Regenerate its data and
illustration with
`python3 experiments/radial_triangle.py --write` and
`node experiments/radial_triangle_figure.js`.

[A curved triangle, read with a straight ruler](experiments/parabolic_triangle.md)
draws the limiting pocket left by three unequal slopes. A common
horizontal slide straightens its sides without changing its area.
Equal slope gaps maximize that area at fixed outer slopes; a quadratic
fit to the three branch velocities determines their limiting meeting
clock. The [gap drawing](experiments/parabolic_triangle.svg) and
[clock drawing](experiments/parabolic_clock.svg) work without scripts
and are linked from the move study. These are local limit curves;
finite-distance bounds and the full route's numerical threshold remain
separate. Regenerate their exact data and rounded quadratic paths with:

```sh
python3 experiments/parabolic_triangle.py --write
node experiments/parabolic_triangle_figure.js
```

[Each clock correction squeezes the triangle twice](experiments/parabolic_retiming.md)
computes the next meeting-time coefficient. At the leading corrected
clock, a generic selected pocket has order 1/M³ area; the symmetric
model cancels that term and leaves order 1/M⁵. Four fresh rational
contraction and Green-integral certificates enclose the latter's
finite areas through M=10²⁰. This is a local asymptotic with separate
finite certificates, not a uniform area remainder. Run:

```sh
python3 experiments/parabolic_retiming.py
python3 experiments/retimed_pocket.py
```

The [many-slope addendum](experiments/parabolic_triangle.md#more-than-three-slopes-add-the-gap-cubes)
sums every bounded region of the limit-parabola arrangement: its area
is the cube of the slope span minus the sum of the adjacent gap cubes,
all divided by 24. Equal gaps maximize it. An independent exact line
arrangement checks the formula. The [illustrated follow-up](experiments/parabolic_pockets.md)
draws the [envelope band](experiments/parabolic_envelope.svg),
[adds one curve](experiments/parabolic_insertion.svg), and
[labels every pocket](experiments/parabolic_runs.svg) by a consecutive
run of interior slopes. Each run's exact curved area agrees with its
straightened triangle or quadrilateral. Regenerate their rational
record and rounded quadratic paths with:

```sh
python3 experiments/parabolic_pockets.py
python3 experiments/parabolic_pockets.py --write
node experiments/parabolic_pockets_figure.js
```

[All the pockets, one band](experiments/parabolic_pockets.html), the
sixteenth study, gathers these still drawings into a reading page.
Its [smallest-pocket follow-up](experiments/parabolic_balance.md)
proves a sharp optimum for every slope count: equal gaps for odd
counts, gaps in the ratio 1:2:1 for four slopes, and alternating
short and long gaps for larger even counts. The
[four-slope comparison](experiments/parabolic_balance.svg) shows
why maximizing the total area and the smallest pocket can disagree.
Exact rational and quadratic-field checks run with
`python3 experiments/parabolic_balance.py`.

The [complete compromise curve](experiments/parabolic_tradeoff.md)
now classifies every efficient choice of total and smallest area,
for every slope count. Even counts alternate short and long gaps;
odd counts have just the shared equal-gap optimum. A
[six-slope drawing](experiments/parabolic_tradeoff.svg) follows ten
named pockets and its exact cubic boundary, as a fifth chapter in
the reading page. Positive AM–GM supports and an exact square
remainder give the global bound and uniqueness. Reproduce its
exact rational/quadratic data and rounded paths with:

```sh
python3 experiments/parabolic_tradeoff.py
python3 experiments/parabolic_tradeoff.py --write
node experiments/parabolic_pockets_figure.js
```

The same calculation selects the unique optimum of
`total + price × smallest`. For example,
`python3 experiments/parabolic_tradeoff.py --slopes 6 --price 5`
recovers the rational green arrangement and exact score 175/54.

The [scaling follow-up](experiments/parabolic_tradeoff_limit.md)
bounds the complete frontier as the even slope count grows.
Relative minimum gain is quadratic in the inverse gap count;
relative total loss is quartic. A
[companion plot](experiments/parabolic_tradeoff_limit.svg) rescales
both toward one limiting parabola, with explicit uniform and finite
endpoint errors. Reproduce the exact data and standalone SVG with
`python3 experiments/parabolic_tradeoff_limit.py --write --figure`.

Sliding those parabolas sideways independently changes the placement
problem. The [sixth drawing](experiments/shifted_parabolas.svg) compares
the midpoint with the exact best insertion for cubic intercepts:
the largest pocket gains about 2.7064%. The
[shifted-family note](experiments/shifted_parabolas.md) derives the
total area as a weighted secant variance and proves the dense-placement
law. Regenerate the exact quadratic data and standalone picture with
`python3 experiments/shifted_parabolas_figure.py --write`.

For cubic intercepts, the [finite-placement proof](experiments/shifted_placement.md)
finds the unique total-area optimum for every count by a monotone
ratio recurrence. `python3 experiments/shifted_placement.py --write`
regenerates rational enclosures of its slopes and areas through 128 gaps.
The [five-curve comparison](experiments/shifted_placement.svg) shows its
complete band beside equal spacing and compares both with the density
prediction. Regenerate it with `python3 experiments/shifted_placement_figure.py`.

The same finite uniqueness proof extends to every real power intercept
`h(p)=p^(k+1)/(k+1)`, k>0, on fixed positive endpoints. The optional
`python3 experiments/power_placement.py --write` checks selected integer
powers by exact polynomial ratio roots and independent full clipping.

Strict convexity alone allows multiple optima: the
[two-choice picture](experiments/two_choices.svg) uses a shifted quartic
intercept with two equally good insertions, both gaining exactly 8%
over the midpoint. Its [short proof](experiments/two_choices.md) gives
the complete parameter threshold at which the two choices merge.
Regenerate its exact data and SVG with
`python3 experiments/two_choices.py --write`.

For every C² intercept with uniformly positive curvature, the
[asymptotic smallest-pocket proof](experiments/shifted_maximin.md)
shows that the same density reaches both area goals at leading order.
Every bounded face has a local curvature sandwich, including longer
runs. Check its exact face formulas and complete arrangements with
`python3 experiments/shifted_maximin.py`.

The [finite four-curve result](experiments/cubic_maximin.md) solves the
cubic-intercept smallest-pocket problem on [1,3]: its unique optimum
makes all three areas equal, at approximately 1.521007779464 each.
A [comparison drawing](experiments/cubic_maximin.svg) shows the
29.39% gain in the minimum and 5.77% cost in total relative to the
largest-total arrangement. An exact cubic selects the labels; positive
supporting weights and global polynomial concavity certificates prove
the maximum over all placements. Reproduce the rational enclosures,
complete coefficients, and standalone drawing with:

```sh
python3 experiments/cubic_maximin.py --write
python3 experiments/cubic_maximin_figure.py
```

The [general four-curve extension](experiments/cubic_four_general.md)
proves the same unique equal-area maximum for every fixed positive
endpoint pair. A normalized cubic selects both interior labels;
511 positive gap-polynomial coefficients and factored positive
supports give an endpoint-independent proof. Run
`python3 experiments/cubic_four_general.py --write` to reproduce it.

The [complete four-curve frontier](experiments/cubic_frontier.md) on [1,3]
connects the total and minimum optima: first the smaller triangle grows,
then both triangles grow together. A [companion drawing](experiments/cubic_frontier.svg)
shows both branches, an enlarged transition, and two complete arrangements
at one scale. Exact rational localization and Bernstein signs prove the
unique best total for every smallest-pocket requirement. Reproduce the
certificate and drawing with:

```sh
python3 experiments/cubic_frontier.py --write
python3 experiments/cubic_frontier_figure.py
```

A [constant-curvature follow-up](experiments/cubic_frontier_limit.md)
explains the small first branch: its relative minimum gain is cubic
in the perturbation, and its relative total cost is sixth order.
Run `python3 experiments/cubic_frontier_limit.py` for the exact Taylor
coefficients. This local theorem asserts no numerical perturbation cutoff.

The [five-curve companion](experiments/cubic_five.md) proves a unique
cubic maximin on the same endpoints. Its three triangles have area
about 0.494437008328; all other faces are larger. The middle triangle's
positive supporting weight is very small, but the full five-dimensional
rational contraction includes it. Run
`python3 experiments/cubic_five.py --write`
for the root box, all six area enclosures, and a freshly
certified comparison with the total-area optimum.

The [outward-offset plot](experiments/parallel_offset.svg) follows each
endpoint from 40 crossing pairs to 106, through exactly 33 inverse
pair-births. Rational contraction boxes certify all 66 contact pairs,
and whole-orbit arc exclusions rule out third branches at their contact
points. Exact reflection pairing gives 18 ordered offset weights per
endpoint. Reversing the second leg supplies the 33 deaths. Run:

```sh
python3 experiments/parallel_offset.py
python3 experiments/parallel_offset_events.py
node experiments/parallel_offset_figure.js
```

The first command repeats complete front and plane censuses; its
`--saved` mode assumes the archived front cover. The event program's
completeness uses that analytic count; it repeats the local root and
third-branch proofs. Add `--write` to save those freshly proved boxes.

[Three visits, one circle](experiments/parallel_offset.html) follows one
selected ordinary triple on the 11 / 6 outward leg. Three original
visits lie on a tangent circle; offsetting by its radius brings them
to the center. A fixed equal-scale lens shows the small triangle before,
at, and after the meeting. A rational whole-orbit cover excludes every
other branch from the viewing square throughout the slider interval;
four-variable interval narrowing proves exactly one triple and no touch
inside that complete window. This classifies the local square, not all
events elsewhere on the curve. Nothing animates, and a
[standalone SVG](experiments/parallel_offset_triptych.svg) works without scripts.

```sh
python3 experiments/parallel_offset_triple.py --write
node experiments/parallel_offset_check.js
node experiments/parallel_offset_stills.js
```

The [radial-word note](experiments/radial_word.md) derives the far-out
strangeness values **−87 and −101** from the certified positive front
words, with both integer and planar-face formulations. Thus the two
outward legs continued sufficiently far need at least **102 and 112
triple passages**. Uniform convergence in both angle and route parameter
transfers exactly **722** middle events, **354 positive and 368 negative**,
to the sufficiently distant plane movie. The complete constructed route
therefore has at least **936 triples**, with net signed change −4, as
well as its 66 inverse touches. These were signed-change lower bounds;
the [complete leg census](experiments/offset_leg_census.md) now gives
exactly 138 and 132 resolved outward triples and 992 over the full route.
No numerical middle-family event-stability threshold is asserted.

```sh
python3 experiments/radial_word.py
python3 experiments/radial_word.py --write
python3 experiments/radial_word.py --saved
```

The default repeats complete rational front covers, geometric word
extraction, original plane proofs, both invariant formulations, and all
6,367 movie moves. `--saved` assumes the archived geometric front words;
it still repeats the original plane proofs and cannot write a new record.
All new calculations and generators need only standard runtimes, and
the website still has no external dependencies.

The selected triple's [quadratic area law](experiments/parallel_offset.md#the-triangle-area-depends-only-on-three-directions)
has **3.845697440 < K < 3.845697448**. Its coefficient depends only on
the three branch normals; curvature enters later terms. The viewer
shows area divided by squared distance approaching that limit.

[Four visits, two cancelling pairs](experiments/offset_fourfold.md)
certifies a mirror-axis fourfold on each outward leg, with no fifth
branch. Small local normal shifts separate each into four ordinary
triples, two positive and two negative. These selected events strengthen
the outward lower bounds to **106 and 116**, and the full-route bound
to **944 triples**. Their [standalone diagram](experiments/offset_fourfold.svg)
shows the two circles and their separated first-order event weights.
The later [complete census](experiments/offset_leg_census.md) gives the
exact resolved leg counts.

```sh
python3 experiments/offset_fourfold.py --write
node experiments/offset_fourfold_check.js
node experiments/offset_fourfold_figure.js
```

A [positive-passage follow-up](experiments/offset_positive.md) certifies
eight selected fourfolds and five reflected ordinary-triple pairs.
They force **18 positive passages on 11 / 6 and 10 on 11 / 8**, including
a fourfold whose four signs all agree. The signed changes then force
at least **138 and 132 outward triples**, and **992 over the sufficiently
distant complete route**: at least 494 positive and 498 negative.
The [standalone diagram](experiments/offset_positive.svg) explains the
circle and signed balance. The later
[complete census](experiments/offset_leg_census.md) proves that these
lower bounds are exact for the specified resolved construction.

[Four signs agree](experiments/four_visits.html), the fifteenth study,
follows the four positive triples of the selected fourfold's first-order
line model. Choose a meeting and move through it; a thin triangle changes
sides while a unit-normal circle explains the common sign. Nothing animates.
A [standalone SVG](experiments/four_visits.svg) preserves all four passages
without scripts. These are rescaled straight local branches; no numerical
orbital perturbation size is asserted.

```sh
python3 experiments/offset_positive.py --write
node experiments/offset_fourfold_check.js experiments/offset_positive.json
node experiments/offset_positive_check.js
node experiments/offset_positive_figure.js
node experiments/four_visits_check.js
node experiments/four_visits_figure.js
```

A [global tail exclusion](experiments/parallel_offset.md#a-finite-bound-on-the-infinite-offset-end)
rules out all endpoint offset triples and higher meetings for every
**M ≥ 270,000**, using a rational cover of expanded conormal-front
triple products, homogeneous tangent-circle equations, and circumradius
bounds. Run `python3 experiments/offset_circle_tail.py`; independent
controls run with `python3 experiments/offset_circle_tail_check.py`.
The older front-only argument in `offset_tail.py` proves the looser
27,000,000 bound. This closes the infinite end with a coarse bound.
The complete leg census below also closes the finite interval; the
middle family's numerical event-stability threshold remains unspecified.

A [fixed-visit exclusion](experiments/parallel_offset.md#two-fixed-visits-stay-alone)
also proves that the starting and halfway visits stay alone for **every
outward M≥0**. Reflection then rules out ordinary triples on the axis
of either unperturbed family, while allowing fourfolds. Run
`python3 experiments/offset_axis_visits.py`: a supporting-line argument
and complete Sturm isolation prove this global axis statement.

The [complete mirror-axis census](experiments/offset_axis_census.md) now
classifies all higher axis meetings for **every outward M≥0**: exactly
**eleven fourfolds on 11 / 6 and nine on 11 / 8**, each with six transverse
tangent pairs. There is no axis meeting with six or more visits. Seven
eligible upper-half arcs per drawing reduce the proof to 21 rational
rectangle covers; projective Bernstein bounds also cover the limits at
arbitrarily large distances. No numerical guesses or saved roots enter
the proof. The [normal-circle atlas](experiments/offset_axis_census.svg)
shows all twenty, including the only all-positive circle followed in
the fifteenth study. The later complete census below also closes the
off-axis question.

```sh
python3 experiments/offset_axis_census_check.py
python3 experiments/offset_axis_census.py
node experiments/offset_axis_census_check.js
node experiments/offset_axis_census_figure.js
```

Add `--write` to the Python census to archive a freshly repeated complete
proof. All these tools use only standard runtimes.

[Every meeting on the way out](experiments/offset_leg_census.md) completes
both whole outward legs for **every M≥0**. A complete graph of pairs of
circle lines supplies all possible three-visit products; homogeneous
minor tests and rational contractions close every product without a
radius cutoff, numerical suggestions, or archived roots. There are
**94 ordinary off-axis triples and eleven fourfolds on 11 / 6**, and
**96 triples and nine fourfolds on 11 / 8**, with no other higher meeting.
Local fourfold resolutions give exactly **138 and 132 ordinary triples**.
There is no higher meeting at **M≥16,173 on 11 / 6 or M≥818 on 11 / 8**.
Together with the 722 middle passages, the specified sufficiently
distant full route has **exactly 992 triples**, 494 positive and 498
negative, alongside its 66 inverse touches. This is a count for that
construction; the middle's numerical stability threshold and finite
perturbation sizes remain unspecified. The
[signed event diagram](experiments/offset_leg_census.svg) accounts for
each leg's complete change in strangeness.
Another [drawing of the last circle](experiments/offset_last_circle.svg)
shows how nearly straight its arc looks beside the original 11 / 6 curve.

```sh
python3 experiments/offset_leg_census_check.py
python3 experiments/offset_leg_census.py --write
node experiments/offset_leg_census_check.js
node experiments/offset_leg_census_figure.js
```

The proof repeats the independent axis census, identifies its eighty
triple subsets by uniqueness, pairs all remaining reflected roots, and
separates every distinct circle to rule out extra branches. All tools
use only standard runtimes.

A separate [local root auditor](experiments/verify_offset_leg_roots.py)
repeats all 270 rational circle proofs and the independent axis census
more quickly, while explicitly assuming the archived global covers:

```sh
python3 experiments/verify_offset_leg_roots.py
```

It cannot write a complete certificate. Use `offset_leg_census.py` to
repeat the exhaustive pair graph and whole-domain covers.
