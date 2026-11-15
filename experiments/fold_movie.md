# Every meeting in the turn

> **Draft: the complete fourteenfold theorem below is not yet established.**
> Seven folds are completely certified. Fourteen folds are covered through
> the last selected triple window, but its final tail to π remains open.
> [The partial record](fold_movie_partial.json) preserves every completed
> slab and the exact remaining interval. Statements below about the full
> fourteenfold census are intended conclusions pending that last cover.

Keep the three lengths and turn the backward arm's starting angle:

```
z(t,φ) = 245 exp(it) + 140 exp(i(d+1)t) + 65 exp(−i(d−1)t+iφ),
0 ≤ φ ≤ π,       d = 7 or 14.
```

The [contact census](fold_contacts.md) found every two-visit touch.
The [local triple calculation](fold_triples.md) certified four selected
batches but left open whether other triples could hide between them.
A continuous cover now closes that question for both entire half-turns.

**There are exactly seven ordinary triple passages for seven folds,
all positive. There are exactly forty-two for fourteen folds: twenty-eight
positive and fourteen negative.** No additional triple, higher multiple
meeting, or nonordinary event occurs. The previously certified two
batches of ordinary touches per family are the complete tangency list.

| Folds | Phase φ/π, rounded | Event at each rotated point | Number of points | Strangeness before → after |
| --- | --- | --- | --- | --- |
| 7 | 0.341592201887… | Opposing-direction touch | 7 | 7 → 7 |
| 7 | 0.951535764936… | Matching-direction touch | 7 | 7 → 7 |
| 7 | 0.961750812235… | Positive triple | 7 | 7 → 14 |
| 14 | 0.914296764567… | Matching-direction touch | 14 | 14 → 14 |
| 14 | 0.924452362405… | Positive triple | 14 | 14 → 28 |
| 14 | 0.962912214409… | Matching-direction touch | 14 | 28 → 28 |
| 14 | 0.973358851457… | Negative triple | 14 | 28 → 14 |
| 14 | 0.977378583506… | Positive triple | 14 | 14 → 28 |

Each row is one simultaneous rotational batch, at different spatial
points. A triple changes the order of three crossing pairs while leaving
their number unchanged. A touch creates two crossing pairs at each point
while leaving strangeness unchanged. Thus the fourteenfold strangeness
temporarily falls back to its starting value even though its crossing
count has already risen to 126.

The [reading page](fold_movie.html) and [standalone sheet](fold_movie.svg)
put those two counts on the same timeline. They illustrate the theorem;
their numerical paths and rounded event locations are separate from the
rational proof. The [earlier triptych](fold_triples.svg) magnifies one
of the triangles that switches sides.

## A count replaces a repeated spatial search

Yesterday's elimination proves the complete crossing-pair staircase
7 → 21 → 35 and 70 → 98 → 126, including the phase endpoints. Away
from the two critical phases, it supplies the exact number of pairs
at **every** phase, including a transverse triple moment.

Use rational unit-circle charts for time and phase:

```
exp(it) = exp(iσ) i^q (1+is)²/(1+s²),
exp(iφ) = i^r (1+ip)²/(1+p²),
0 ≤ s,p ≤ 1.
```

The seam σ is either zero or `2 atan(1/3)`. It changes only the time
coordinates, with no deformation of the drawing. Both evaluator choices
use integer complex powers and exact rational Fourier coefficients.

For one closed phase slab, construct disjoint product charts A×B.
A rational parametric contraction proves that each contains exactly one
transverse crossing pair at every phase in the slab. Every chart stays
off the coincident-visit diagonal and inside its time quarters. If the
number of such charts equals the independently proved exhaustive pair
count, **every crossing pair has been accounted for**. An additional
unseen pair would contradict that count. This avoids repeating a
whole-orbit spatial cover on every regular slab.

The two critical cosines are isolated anew by the contact polynomial.
Exact endpoint cosine evaluations put a regular slab strictly before,
between, or after those roots. Archived crossing counts are checked
against this fresh elimination. They never replace it.

## The phase derivative is nonlinear

The older [whole rhythm route](rhythm_route.md) is affine in its weight.
This phase family is not. In either quarter,

```
φ_p = 2/(1+p²),        φ_pp = −4p/(1+p²)².
```

Let `V=245+140(d+1)+65(d−1)` and
`M=245+140(d+1)²+65(d−1)²`. Uniform bounds are

```
|z_ss| ≤ L₂ = 4M+2V,
|z_p| ≤ 130,
|z_sp| ≤ 260(d−1),
|z_pp| ≤ 390.
```

They follow from the three Fourier terms and the two circle-chart
derivatives. For example `|φ_p|≤2` and `|φ_pp|≤2` give
`|z_pp|≤65(4+2)=390`. The same chart bounds apply to t; the fixed
seam rotation contributes no extra derivative.

For F=z(s,p)−z(u,p), fix the inverse R of its time Jacobian at the
box center. If the time radii are r₁,r₂ and the phase radius is ρ,
time-column errors are bounded by

```
eᵢ = L₂ rᵢ + 260(d−1)ρ.
```

For a row Rⱼ, the centered fixed-point image has displacement
`−RⱼF(center)` and an error bounded by

```
|Rⱼ F_p(center)|ρ + ‖Rⱼ‖₁ [Σᵢ eᵢrᵢ + 390ρ²].
```

The last term encloses the nonlinear phase remainder for the **difference
of two branches**. A strict interior image and contraction norm below
one prove a unique transverse root for every phase. A disjoint image
excludes roots. No affine interpolation in phase is used.

## Looking for a third visit

Make a graph whose nodes are pair product charts. Join two nodes if
any individual visit slots overlap. A triple supplies three distinct
pair charts in one connected component. A fourth visit would supply
six. Components of fewer than three nodes cannot contain a triple;
components larger than three reject the attempted slab and force
subdivision.

For each three-node component, test all six assignments of its charts
to visit pairs 01, 02, 12. Intersect the two candidate slots for each
visit. Every actual triple lies in one of these three-slot products.
An empty intersection eliminates an assignment immediately.

On a surviving product, solve the four equations

```
G = (z(s₀,p)−z(s₁,p), z(s₀,p)−z(s₂,p)) = 0.
```

The Jacobian uses the actual nonlinear phase motions. A time-column
error is `L₂rᵢ+260(d−1)ρ`; a phase-motion error for one branch is
`260(d−1)rᵢ+390ρ`. A rational preconditioned mean-value image excludes
every root if one coordinate misses its input interval. An inconclusive
box is split, and both children must pass. The search never interprets
a numerical failure as an exclusion.

The regular slabs exclude every candidate this way. At a selected triple
window, every candidate instead lies inside a certified unique-root
cube for one of the d rotated events, or is excluded. Each large cube
has radius at most **10⁻⁵** in all four chart variables, shortened near
one time-chart seam. Their weighted
contraction norms are below **0.175**. A contained cube of radius
**10⁻¹⁰** proves that the root lies inside the actual phase window.
All three velocity determinants and the signed unfolding determinant
are nonzero. The signs are **+, +, −, +** in the local triple table.
Disjoint spatial enclosures separate all rotational copies.

This proves uniqueness on the **whole candidate products** of each
event window, closing the scope left open by the earlier local result.
The accepted overlap components have only three pair charts each;
there is no fourth visit at an event.

## Closing a contact window

A regular crossing chart cannot span the birth of two crossings.
Use a separate closed window of phase-chart radius **10⁻⁷** around
each certified touch. The old polynomial proves that it contains just
its selected critical phase and no other two-visit tangency.

All pairs present before the touch have persistent regular charts
throughout this window. Their possible triples are excluded as above.
Around each rotated contact, use a product patch with time-chart
radius **10⁻⁴**. Its ordinary birth root is contracted independently
and identified with the exhaustive critical polynomial root.

Every face of the product-patch boundary is proved root-free throughout
the full phase window. Rational image exclusions need **48, 58, 120,
and 116** boundary pieces for the four batches. Thus a pair born in
one of these patches cannot leave it before the window ends.

For completeness, continue crossing pairs on the compact pair-parameter
space. Away from the one critical phase, each pair has a nonsingular
time Jacobian and continues uniquely. Positive speed keeps pairs away
from the coincident-visit diagonal. All preexisting pairs persist in
their charts. The d ordinary touches create two pairs per patch, and
the root-free boundaries keep them there. There is no other birth or
death in this window. Equivalently, the exhaustive count is exactly
the persistent count plus these 2d pairs above the touch, and plus d
tangent pairs at the critical phase itself.

Each entire contact patch maps inside a unit-radius spatial disk.
A whole-orbit rational arc cover admits only two disjoint, uniformly
monotone branch slots to that disk. These covers exclude **7,146,
7,149, 14,292, and 14,298** arcs across the respective rotational
batches. Any point in a patch therefore has at most two visits.
No newborn crossing can take part in a triple. Persistent pair charts
and contact patches are disjoint in the pair product space, so nothing
is counted twice.

## Endpoints and the full turn

Fresh smooth intersection proofs also construct exact crossing words
at both phase endpoints. Two integer formulations of strangeness agree:

| Folds | Phase | Pairs | Bounded winding-region histogram | St |
| --- | --- | --- | --- | --- |
| 7 | 0 | 7 | +1: 1; +2: 7 | 7 |
| 7 | π | 35 | +1: 15; +2: 14; +3: 7 | 14 |
| 14 | 0 | 70 | +1: 15; +2: 28; +3: 14; +4: 14 | 14 |
| 14 | π | 126 | +1: 29; +2: 42; +3: 42; +4: 14 | 28 |

The tangent index d+1 is proved separately by the velocity ellipse.
It fixes the additive winding normalization of the planar graph:
declaring a face of true winding n to have winding zero changes
`Σ_faces winding − Σ_crossings index` by −2n, since F−V=2.
The normalization giving d+1 therefore has the correct zero. The
crossing-word and face-walk calculations then agree at every base edge.
The endpoint differences +7 and +14 match the complete signed event
counts; that agreement is an audit, not a substitute for the cover.

The identity `z(−t,2π−φ)=conj(z(t,φ))` supplies the other half-turn.
It reverses the phase order and the signs of the triple passages.
Thus a **full** starting-angle turn has exactly **fourteen triples**
for seven folds, seven of each sign, and **eighty-four triples** for
fourteen folds, forty-two of each sign. Each full turn has four batches
of ordinary touches. Both endpoints of each half-turn are regular.

## A four-visit ceiling without a census

There is a short independent bound that works for **every positive
integer d**, with these same lengths. Put θ=dt−φ/2 and factor the
position as in the [ellipse note](fold_variations.md). Its squared
radius is

```
|z|² = 83850 + 18200 cos(2θ)
       + 100450 cos(φ/2) cos θ − 36750 sin(φ/2) sin θ.
```

For a specified radius r, set w=exp(iθ), c=cos(φ/2), and s=sin(φ/2).
Multiplying the radius equation by w² gives the quartic

```
9100 w⁴ + (50225c+18375is) w³ + (83850−r²) w²
        + (50225c−18375is) w + 9100 = 0.
```

Its leading coefficient never vanishes, so at most four distinct θ
values have that radius. Each θ gives d time visits, but those visits
are rotated copies of a nonzero point: `|z|≥245−140−65=40`. At most
one of them can equal a specified spatial point. Consequently **no
point has more than four visits**, at any phase or any positive
integer fold count.

At zero phase the earlier strictly increasing quadratic in cos θ
reduces that bound to **two visits**. The present complete census
excludes the remaining possibility of a four-visit meeting throughout
the seven- and fourteenfold turns. Whether such a meeting occurs at
other fold counts is a separate question.

## Reproduce

```sh
python3 experiments/fold_movie_census.py --jobs 2
python3 experiments/fold_movie_check.py
python3 experiments/fold_movie_figure.py
```

The first command reads the exact phase partition from
[fold_movie.json](fold_movie.json), then repeats every regular-slab
contraction, every triple exclusion, all eight complete event windows,
and all four endpoint proofs. It reruns the exhaustive contact
elimination; archived counts, event results, and endpoint words are
never accepted in place of fresh proofs. Empty, incomplete, and
overlapping partitions are rejected. An existing triple is accepted as
a root; a displaced copy is excluded. Invalid phase inputs are rejected.

Add `--write` to rediscover a partition and atomically replace the record
only after all proofs pass. Discovery may choose either chart seam and
may subdivide a proposed slab. Its numerical scans and Newton iterates
suggest boxes only. Work limits reject attempts; they never certify one.
The two phase quarters tile each half-turn exactly, with all boundary
phases included. Their event-window centers are fixed rational constants;
platform-dependent trigonometric rounding never defines the partition.

The separate evaluator audit compares **4,480 exact components at 560
rational states**, including both seams, phase endpoints, raw physical
velocities, and both chart derivatives. It constructs the curve using
independent complex division and automatic differentiation. These finite
checks audit implementation; the rational inequalities and exhaustive
partition prove the continuous result.

Only the standard library is needed for these commands. The theorem
concerns these two specified families and lengths. It is not a general
rule for every fold count, nor a complete winding-region movie at every
phase. The little triangle's area law remains the separately certified
local result in [fold_triples.md](fold_triples.md).
