# A triangle switches sides

The [strangeness calculation](strangeness.md) distinguishes the first
two zero-turn drawings. Their existing regular arm detour has a
selected meeting of three visits near 46.4144% of its middle leg.
We can now isolate that event in the **complete** curve.

Throughout the closed weight interval

```
0.4641 ≤ a ≤ 0.4642,
```

the full curve is regular, every intersection belongs to the three
selected branches, and every pair of those branches meets exactly once.
There is **one ordinary triple passage and no other curve events**
in that interval. This is a census of a small continuous parameter
window, not of the full three-leg detour.

![Three magnified drawings show a clockwise triangle collapsing into a triple meeting, then opening on the other side as a counterclockwise triangle. Its winding count is minus one before and plus two after. Strangeness falls from zero to minus one. All panels have the same equal scales.](triple_passage.svg)

The displayed separation is tiny: the plotting window extends only
0.012 drawing units above and below the axis. This magnification uses
the same scale horizontally and vertically. The three curves are the
actual orbital branches, drawn with rounded numerical height inversions.
The continuous count and invariant claims use separate rational proofs.

## The curve and its three charts

On the first detour's middle leg, the first arm has length 300:

```
z(t,a) = 300 exp(it)
       + 140 [(1−a) exp(2it) + a exp(4it)]
       +  65 [(1−a) exp(−3it) + a exp(−7it)].
```

Write t = π+u. The three selected time charts are

```
earlier: −0.52 ≤ u ≤ −0.49,
halfway: −0.01 ≤ u ≤ +0.01,
later:   +0.49 ≤ u ≤ +0.52.
```

Rational trigonometric bounds show that each chart is a unique graph
of x against height across the entire window −1 ≤ y ≤ +1, for every
weight in the stated interval. The earlier and later visits travel
downward; the halfway visit travels upward. Their slope intervals obey

```
earlier:  −0.57 < dx/dy < −0.26,
halfway:  −0.09 < dx/dy < +0.09,
later:    +0.26 < dx/dy < +0.57.
```

These bounds hold on the complete time charts, rather than just their
pieces in the room. Thus the difference of any two height graphs is
strictly monotone on their full common height domain. Each pair can
meet **at most once**, and every meeting is transverse.

At height −1 the graphs' x coordinates have order later, halfway,
earlier. At +1 that order reverses. Small rational time brackets around
numerical hints prove both endpoint orders with the full weight interval
retained. Hence every pair meets **exactly once**, with height in (−1,1).

A spatial cover also certifies the rectangle

```
−229 ≤ x ≤ −221,
  −1 ≤ y ≤ +1.
```

Only these three charts can enter it. All three charts stay strictly
between its vertical walls. The proof excludes the rest of the orbit
with **42 rational arcs** and contains the charts horizontally with
**24 arcs**. It uses the same finite alternating upper bound on π as
the [earlier pocket room](pocket_room.md), so the exclusion covers a
complete orbit. Every accepted leaf is reevaluated independently.

This room alone would not exclude another crossing elsewhere. The next
step does that.

## Cover all possible crossings throughout the parameter interval

The rational-circle parameterization from the
[smooth atlas](smooth_census.md) applies to all five Fourier terms.
At the midpoint weight, `DetourCurve` evaluates positions and velocities
as exact fractions. Its endpoints agree with the frozen original
evaluator after adding 55 to the first arm; affine checks cover mixed
weights. There are **480 exact component comparisons**.

The original arc and contraction methods are imported unchanged.
For the continuous family cover, enlarge each midpoint position box.
Differentiation with respect to a gives the global bounds

```
|∂z/∂a| ≤ 140+140+65+65 = 410,
|∂z′/∂a| ≤ 280+560+195+455 = 1490.
```

The weight radius is exactly 1/20000. Each midpoint position box expands
by **0.0205** in both coordinates. A midpoint velocity varies by at
most **0.0745** from weight variation.

A uniform acceleration bound is

```
M = 300 + 4·140(1−a_low) + 16·140 a_high
        + 9·65(1−a_low) + 49·65 a_high.
```

Divide every quarter-circle parameter into K = 4096 arcs, for **16,384
arcs** in all. Since dt/ds ≤ 2, an interval spanning d+1 such arcs has
time length at most `2(d+1)/K`. If v₀ is the midpoint-weight velocity
at its first endpoint and

```
|v₀| > 2 M (d+1)/K + 0.0745,
```

then every velocity throughout that time interval and every allowed
weight lies in the open half-plane facing v₀. Projection along v₀ is
strictly increasing, so there is no self-intersection within it.
Squared rational norms decide this inequality without square roots.
The single-arc version also proves regularity everywhere in the family.

Closed spatial buckets enumerate all overlapping enlarged arc boxes.
Binary floating bounds serve only as a filter after exact checks that
they enclose the rational boxes. Any possible crossing pair must then
pass either the uniform monotonicity exclusion or a strict test placing
both complete arcs inside two different selected charts.

The cover makes **18,374 monotonicity exclusions**. Only **14 arc pairs**
remain: six earlier/halfway, five halfway/later, and three earlier/later.
Those are overlapping parameter boxes, not extra intersections. The
height-graph argument already proves each chart pair has exactly one
meeting. Thus **the entire curve has precisely those three pairwise
meetings for every weight**. No other crossing or tangency is hidden
outside the spatial room.

## Exactly one triple meeting

Reflection exchanges the earlier and later graphs. Since their
difference is strictly monotone, their meeting is always on y = 0.
The halfway graph has x(0) = −225 exactly, independently of a.
For the reflected pair to share that point, the already isolated
[three-visit event polynomial](arm_detour_events.md) must vanish.
Its Sturm proof gives exactly one selected event on the complete leg:

```
a ≈ 0.4641442243614488,
u ≈ ±0.5052722066581221,
z = −225.
```

Rational bounds place its algebraic cosine and weight strictly inside
these charts and the certified parameter interval. Its event Jacobian
is nonzero. The pairwise separated slopes establish three transverse
branches, and the room and complete crossing cover exclude any fourth
visit or simultaneous event. There is consequently one ordinary triple
passage in the whole interval, with regular generic curves elsewhere.

## The invariant and the little triangle

Fresh contraction proofs at the two exact endpoint weights provide the
words below, relabeled in travel order from t = 0:

| Weight | Signed cyclic word | St | Bounded regions by winding |
| --- | --- | ---: | --- |
| 0.4641 | 1⁻ 2⁺ 3⁻ 1⁺ 2⁻ 3⁺ | 0 | −1: one, 0: two, +1: one |
| 0.4642 | 1⁺ 2⁻ 2⁺ 3⁻ 3⁺ 1⁻ | −1 | 0: two, +1: one, +2: one |

Both endpoint curves have three crossings, four bounded faces, and
tangent index zero. Starting at the uniquely rightmost point gives
edge index +½, with no correction. Both invariant formulations, all
starting edges, reflection, and traversal reversal agree.

Because the interval has only one curve event, its **strangeness jump
is −1**. With the paper's convention this is a negative triple passage.
There is no inference from the endpoint difference alone about how many
events lie between: the continuous cover supplies that missing information.

The little triangle is one face of the full drawing, since its three
graph arcs and enclosed gap lie inside the isolated room. Before the
meeting its boundary is traveled clockwise, placing its interior on
the right of both incident branches at each corner. All three vertex
mean counts are 0 there, so that minimum sector has winding −1.
After the meeting the triangle lies on the other side, with boundary
traveled counterclockwise. Vertex means are now 1, and its maximum
sector has winding +2. The drawings preserve the travel arrows.

Strangeness changes by −1 while this region's winding changes from
−1 to +2. These are different integers. Region winding concerns points
in the complement; strangeness concerns the immersed curve as a whole.

## Reproduce

```sh
python3 experiments/triple_passage.py
python3 experiments/triple_passage.py --figure
```

Only the Python standard library is used. The proof takes about four
seconds here. The optional figure repeats the proof, then uses numerical
height inversions only for its paths and fills. Its output is deterministic
on this machine; the middle weight is a rounded approximation to the
algebraic event. No pixel or floating-point drawing predicate decides
the certificate.

This strengthens one selected event from the earlier detour note to a
complete continuous-window result. It does not classify the other weights
or legs, and it does not prove that this is the detour's only triple event.
