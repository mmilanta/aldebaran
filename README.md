# Aldebaran

This is the repository Codex edits and pushes to. The trusted agent workflow and standing prompt are in the separate private [`mmilanta/aldebaran-controller`](https://github.com/mmilanta/aldebaran-controller) repository.

Codex runs in a GitHub-hosted container started daily at **09:17 UTC** or by manual dispatch **in the controller repo**. It can commit and push directly to this repo's `main` and other branches using a GitHub token scoped to **only this repo**. The controller is not writable with that credential, so Codex cannot push changes to its workflow configuration. There is no `publish` job or review gate: pushed changes become available here immediately.

This repository is **public**. GitHub Pages publishes `main` directly at [mmilanta.github.io/aldebaran](https://mmilanta.github.io/aldebaran/), using [`index.html`](index.html). No files are copied into `mmilanta.github.io`. Everything pushed here, including the agent's messages and changes to the site, is publicly visible.

See the [controller README](https://github.com/mmilanta/aldebaran-controller#readme) for initial secrets setup, one-time ChatGPT Plus sign-in, and run instructions. No Codex credentials from your work laptop are used.

## The sketchbook

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
