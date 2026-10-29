# The whole route between two weaves

The straight blend from rhythms **11 / 6** to **11 / 8** has exactly
**four ordinary triple passages and eight ordinary tangencies**, grouped
into **six reflected pairs**. There are no other curve events on the
entire route, including its endpoints.

This completes the gaps left by [the two triple windows](rhythm_passages.md)
and [the four touch windows](rhythm_tangencies.md#four-complete-continuous-windows).
The interactive studies show [the triangles](weave.html) and
[the lenses](touch.html). The whole family keeps speed at least **775**;
its tangent index is eleven throughout.

Each row below is a weight at which **two reflected events occur
simultaneously**. Weights are rounded locations of separately enclosed
exact events. Counts and integer invariants are exact, on the adjacent
open intervals of generic curves.

| Weight | Two reflected events | Crossings | St | J⁺ | J⁻ |
| --- | --- | --- | --- | --- | --- |
| 0.047120044569… | Negative triple passages | 40 → 40 | 15 → 13 | −14 → −14 | −54 → −54 |
| 0.075511676380… | Negative triple passages | 40 → 40 | 13 → 11 | −14 → −14 | −54 → −54 |
| 0.103860136179… | Direct tangencies, lenses die | 40 → 36 | 11 → 11 | −14 → −18 | −54 → −54 |
| 0.322975096577… | Inverse tangencies, lenses open | 36 → 40 | 11 → 11 | −18 → −18 | −54 → −58 |
| 0.393710135492… | Inverse tangencies, lenses die | 40 → 36 | 11 → 11 | −18 → −18 | −58 → −54 |
| 0.863940915397… | Direct tangencies, lenses open | 36 → 40 | 11 → 11 | −18 → −14 | −54 → −54 |

The bounded-region count is one more than the crossing count away from
the event weights. The two endpoint drawings agree on both J-invariants,
crossing and winding-region counts, and tangent index. Their strangeness
differs by four. This particular route realizes those four negative triple
passages, together with cancelling pairs of both kinds of tangency.

## Covering every remaining weight

[rhythm_route.json](rhythm_route.json) stores an exact partition into
**424 regular weight slabs**. Together with the six event windows it tiles
**[0,1] exactly**, with disjoint interiors and matching rational endpoints.
No floating-point tolerance is used to check that the partition has no gap.

The verifier [rhythm_route.py](rhythm_route.py) repeats fresh rational
proofs on every archived slab. On each one:

1. A fresh smooth proof at its low weight suggests the crossing charts.
   Numerical Newton iterations only place rational candidate boxes.
2. A parametric contraction proves exactly one transverse crossing in
   each product chart at **every weight in the slab**.
3. A cover by **4096 rational circle arcs** excludes every crossing
   outside those charts, including arbitrarily close pairs of visits.
4. Every possible third visit is excluded by the test below. Thus there
   is no triple, higher multiple point, or tangency anywhere on the slab.

All six continuous event-window proofs run afresh too. They cover every
orbit time and every weight in their respective windows. Their exact
classifications, together with the regular slabs, yield the complete
event list. The archived crossing counts and statistics are never used
as substitutes for these proofs.

The Fourier family is finite and analytic. A nonzero global speed bound,
transverse double crossings off the six event moments, and the local
ordinary-event certificates account for every way its crossing graph can
change here. This is a census of this specified one-parameter blend;
it makes no assertion about all possible routes between the drawings.

## Moving the chart seam

A visit can pass a boundary between parameter charts without any curve
event. One fixed set of quarter-circle charts need not work throughout
every regular slab. The verifier can start its charts at either zero or
the rational-circle angle **φ = 2 atan(1/3)**.

For c equal to 0 or 1/3, tangent addition gives

```
u = (s+c)/(1−cs),
exp(i(t+φ)) = i^q (1+iu)²/(1+u²),
dt/ds = 2/(1+s²).
```

The shifted evaluator composes this map with the existing rational
Fourier evaluator, multiplying its s-velocity by
`(1+u²)/(1+s²)`. This reparametrizes the same closed curve; it does not
rotate or deform the drawing. The derivative bounds and affine weight
dependence remain valid. A separate rational complex-power evaluation
passes **576 exact component comparisons** for both seams, all four
quarters, positions, s-velocities, and raw t-velocities.

Every accepted chart stays strictly inside its circle quarter. A full
orbit cover still checks the seams themselves. If a slab cannot be
certified with either choice, discovery subdivides the weight interval;
it never treats a seam problem as evidence of a curve event.

## Excluding a triple without separating all visit ranges

Two nearby crossing visits can move together through a slab. Their
individual time enclosures can overlap even though the visits never
coincide. Requiring all visit ranges to be disjoint creates many needlessly
small slabs near the already known triple passages.

Instead, make a graph whose nodes are crossing charts. Join two nodes if
any of their visit slots overlap. An actual triple uses three distinct
crossing charts, all in one connected component of this graph. Components
of one or two nodes cannot contain a triple. An accepted slab has no
component larger than three; larger uncertain groups cause subdivision.

For a three-chart component, try all six assignments of its charts to
the visit pairs **01, 02, 12**. Intersect the corresponding two slots for
each visit. Empty intersections eliminate that assignment. Otherwise
every putative triple lies in the resulting three-slot product and the
full weight interval. On that four-dimensional box, set

```
G = (z(s₀,a)−z(s₁,a), z(s₀,a)−z(s₂,a)).
```

Let m be its rational center, r its radii, [J] a rational enclosure of
the Jacobian, and R an invertible rational preconditioner. Every zero
must satisfy

```
x−m ∈ −R G(m) + (Id−R[J]) ∏_j [−r_j,r_j].
```

If one coordinate of this image misses its original interval, the box
contains no zero. This is an exclusion by the mean value theorem; it
does not need a contraction norm below one. An inconclusive image is
subdivided, and **both** child boxes must be excluded. All possible chart
assignments are tested. A fourth or higher visit would contain a triple,
so it is excluded as well.

The Jacobian uses the same Fourier bounds as the earlier triple proof.
On the entire route, a change of s by radius r_s and weight by radius r_a
changes an s-velocity component by at most

```
89990 r_s + 1820 r_a.
```

A weight derivative of position changes by at most `1820 r_s`. These
bound all Jacobian entries. Center values, inverse matrices, interval
images, and exclusion comparisons use rational arithmetic. The only
binary spatial filters have their outward enclosures checked rationally,
as in the original frozen solver.

A control first certifies an existing triple independently, then asks
this exclusion routine to try its actual root box. It must fail to report
that box empty. Empty, incomplete, and overlapping partition archives are
also rejected. Search time and subdivision limits only reject attempts;
they cannot turn an unresolved box into a successful proof.

## Reproduce the complete census

Only the Python standard library is needed:

```sh
python3 experiments/rhythm_route.py --jobs 2
```

This repeats all **430 proof tasks**: every regular-slab proof and all six event-window proofs.
The archive saves a successful partition, not a trusted verdict. To
rediscover a partition, then verify it afresh before replacing the archive:

```sh
python3 experiments/rhythm_route.py --write --jobs 2
```

Discovery is slower than replaying the saved partition. A failed search
does not overwrite the previous archive. No frozen certificate source
was edited. In particular, the earlier
[global axis exclusions](rhythm_passages.md#the-halfway-visit-stays-alone-on-the-full-route)
remain an independent check on part of this census.
