# Beyond a sampled census

The [sampled-polygon census](region_census.md) leaves a question: could the
smooth curve hide a crossing or region between the samples? For **Garden,
the negative-total curve, Star, and Crown**, there is now a computer-assisted
answer. The complete smooth curves have the same crossing counts and region
histograms as their sampled polygons:

| Rhythms | Transverse double crossings | Bounded regions |
| --- | ---: | ---: |
| 7 / 13 | 24 | 25 |
| 2 / 25 | 100 | 101 |
| 6 / 9 | 25 | 26 |
| 9 / 23 | 64 | 65 |

Run `python3 experiments/certify_intersections.py`. It uses Python's standard
library and takes roughly ten seconds here, mostly on Crown's fine
partition. The actual certificate is a completed set of rational exclusions,
unique-root tests, disjoint root-image boxes, and parameter-order checks.
If any of these checks fails, the program raises an error and produces no
completed census for that curve. The other 317 regular rhythm pairs are
outside this certificate.

## Parametrize the curve rationally

As in the [tangent certificate](tangent_turning.md), write

```
w_q(s) = i^q (1 − s² + 2is)/(1 + s²),     0 ≤ s ≤ 1, q = 0,1,2,3
Z_q(s) = 245w_q(s) + 140w_q(s)^m + 65 conjugate(w_q(s))^n.
```

Each quarter is traversed once, and `arg w_q` increases with derivative
`2/(1+s²)`. Rational values of `s` give exact rational positions and
derivatives. The code evaluates powers using pairs of integers, with positive
common denominators. No trigonometric approximation is needed.

The familiar bounds in the angular parameter are

```
|z′| ≤ V = 245 + 140m + 65n
|z″| ≤ M = 245 + 140m² + 65n².
```

Since `|dt/ds| ≤ 2` and `|d²t/ds²| ≤ 2` on a quarter,

```
|Z_q″(s)| ≤ L = 4M + 2V.
```

For an interval of width `h`, linear interpolation stays within `Lh²/8`
of the smooth arc. Expand its two endpoint bounding rectangle by that amount
in every coordinate. The resulting rational rectangle contains the whole
arc, not just the endpoints.

## Cover the whole parameter domain

Divide every quarter into `K` rational intervals. The selected values are
2048 for Garden, 512 for 2 / 25, 1024 for Star, and 32768 for Crown.
All same-interval pairs are excluded by a monotonicity check. At an interval's
start, require

```
|z′(start)| > 2M/K.
```

During that interval the velocity stays in the open half-plane facing its
starting velocity. Projection of the position onto that direction is strictly
increasing. The arc is injective and its velocity never vanishes. In
particular, this certifies regularity throughout each of the four curves.

Two different intervals can contain a crossing only if their enclosing
rectangles overlap. A spatial bucket search finds every such candidate.
Its bucket indices use exact rational rectangles. For fast rejection,
the implementation also uses enclosing binary floating-point rectangles,
but **checks their outward inclusions rationally**. Comparisons between these
verified outer bounds cannot discard an intersection of the actual arcs.

For nearby intervals, apply the same projection argument over their whole
intervening cyclic time window. If their grid indices are `d` intervals apart
along the shorter direction, that angular span is at most `2(d+1)/K`.
The exact squared inequality

```
|z′(window start)| > 2M(d+1)/K
```

excludes every distinct-time intersection between them. This also handles
neighboring intervals and the wrap from the fourth quarter back to the first;
their shared ordinary endpoint is one point of the parameter circle.
An uncertified neighboring pair causes explicit failure.

Every remaining pair is sent to the two-variable solver. Thus the coverage
is exhaustive: there is no region of the parameter domain left out because
it looked visually uninteresting or failed to contain a polygon crossing.

## An exact exclusion and uniqueness test

For two parameter intervals, solve

```
F(s,u) = Z_a(s) − Z_b(u) = 0.
```

Let `X` be their rectangle, `c` its center, and `r_1,r_2` its radii.
At the center, compute the exact rational Jacobian `J_0` and its inverse `C`.
If it is singular, subdivide instead. Each entry in column `j` of
`J(x) − J_0` has absolute value at most `B_j = L r_j`.

For the fixed-point map `T(x) = x − C F(x)`, row `i` of `I − C J(x)` has
entry bounds

```
E_ij = (|C_i1| + |C_i2|) B_j.
```

The mean-value integral shows that `T(X)` lies in the rectangle centered at
`c − C F(c)` with radius `R_i = Σ_j E_ij r_j`. Every zero in `X` must also
lie in this rectangle.

* If it is disjoint from `X` in any coordinate, there is no zero in `X`.
* If it lies strictly inside `X` and both row sums `Σ_j E_ij` are less than
  one, `T` is a strict contraction mapping `X` into itself. It has exactly
  one fixed point, hence exactly one zero of `F` there.
* Otherwise, bisect one interval and cover both resulting rectangles.

All these inequalities use `Fraction`, including every matrix entry and
radius. The strict contraction condition also makes `J` nonsingular everywhere
in a certified root box: `C J = I − (I − C J)` is invertible. The two curve
branches therefore meet transversely, and their determinant sign cannot change
within that box. Tangencies and overlapping arcs would prevent completion;
they cannot silently receive an ordinary crossing label.

Closed child boxes share boundaries, but accepted roots lie strictly inside
their boxes. Boundary roots that prevent certification cause further subdivision
and eventually an explicit failure at the depth limit, rather than a guess.

## Separate the crossings and read their graph

After obtaining the complete root cover, numerical Newton iterations suggest
smaller dyadic boxes. Those suggestions have no authority: each smaller box
must lie inside its previous certified box and pass the same exact contraction
test again. This proves that it contains that same unique root.

The smooth image rectangles of the refined roots are checked pairwise disjoint.
This excludes coincident intersection images and triple points. Their parameter
intervals are also checked disjoint along the parameter circle, so their cyclic
order is known exactly.

The four outgoing rays at a double point are the two branch velocities and
their negatives. Their cyclic order follows from the certified determinant
sign. Connect consecutive parameter occurrences into oriented arcs, then walk
face boundaries using this rotation order, just as in the sampled graph.
The entire smooth graph has now been specified without approximating a
crossing location by a pixel or a polygon intersection.

To identify the outside face, use `t = 0`: its `x = 450` is the unique global
maximum, because equality in
`245 cos t + 140 cos mt + 65 cos nt ≤ 450` forces `cos t = 1`.
The velocity there is vertical and nonzero. The east side of this arc is
outside, on its right when the velocity points up, and on its left when it
points down. Starting with label zero there, propagate the left-minus-right
rule through every oriented arc. The output is the full histogram of smooth
region winding counts. The code checks Euler's face count and consistency of
every winding relation, then compares the result with the independently
constructed sampled graph.

## What is certified, and what is still approximate

For these four curves, the counts and winding histograms are certified for
the smooth geometry. In particular, Garden has exactly two +3 regions, and
2 / 25 has exactly one −7 region. Crown has exactly eight +3 regions, despite
their absence from the 960-pixel color raster.

The illustrations still approximate boundaries and region **areas** by sampled
polygons. A certified region count does not make a polygon area the exact
smooth area of that region. The continuous total signed areas retain their
separate exact Fourier formula. Extending this complete crossing certificate
to other rhythms would require completing all of its checks for those pairs,
with a suitable partition; the 321-pair sampled survey alone does not do that.
