# A line approaches a band

Increasing the folds makes a finer weave inside the same annulus.
There is a direct quantitative statement: **every point in that annulus
is within `2M sin(π/(2d))` of the smooth curve**, where d is the fold
count and M is the outer radius.

At a half-turn starting angle, M≈333.6552732180. The following
three drawings keep one scale. Their printed distances are guaranteed
upper bounds, rounded upward; they are not measurements of the largest
gaps in the pictures.

![Fourteen, sixty, and two hundred forty folds at a half-turn starting
angle, with the same two radial boundaries and successively finer lines.](fold_band.svg)

[Turn one arm and follow a repeat ↗](fold_turn.html)

## A circle of d visits at every radius

Keep any fixed starting angle φ. In the first arm's frame, write

```
B(u) = 245 + 140 exp(iu) + 65 exp(i(φ−u)),
z_d(t) = exp(it) B(dt).
```

Let m and M be the minimum and maximum of |B(u)|. The
[annulus calculation](fold_annulus.md) determines these edges and shows
that they are independent of d. As B goes around its ellipse, its
continuous radius takes every value r between m and M.

Choose one ellipse point B(u) of radius r. The d times

```
t_k = (u+2πk)/d,       k=0,…,d−1,
```

all give the same ellipse point. Their orbital positions are

```
z_d(t_k) = exp(iu/d) B(u) exp(2πik/d).
```

These are d equally spaced points on the circle of radius r.
Any target on that circle is at most π/d radians from one of them.
The chord between the target and that visit is therefore at most

```
2r sin(π/(2d)) ≤ 2M sin(π/(2d)).
```

Every point of the annulus lies on one such circle. This proves the
claim for the entire two-dimensional annulus, without a grid or a
crossing calculation. In general the curve also has other points
closer to the target, so the bound can be conservative.

## A limit with a concrete distance

The curve lies inside its annulus. The result bounds the reverse
approximation: every annulus point is close to some curve point.
Together these statements bound their *Hausdorff distance*, the
largest nearest-set distance in either direction:

```
d_H(curve_d, annulus) ≤ 2M sin(π/(2d)) ≤ πM/d.
```

Consequently the images of the curves converge to the whole annulus
as d tends through the positive integers, at least as fast as 1/d in
this distance. Each finite ideal curve remains a line. Its limiting
set can have positive area.

At the half-turn, **1,049 folds suffice** to put every annulus point
within one drawing unit of the line. Since every phase has M≤450
by the triangle inequality, **1,414 folds suffice at every starting
angle**. These are sufficient counts supplied by the bound, without
an assertion that they are the smallest possible counts. The limits
refer to the smooth centerline before adding a visible stroke width.

The annulus itself tightens as φ goes from zero to π, but this limit
keeps φ fixed and increases d. There is no nesting claim for the
individual curve images.

## The order 1/d cannot be improved

There is a lower bound too. If a connected curve has length L, the area
within distance ε of it is at most

```
2Lε + πε².
```

For a polygonal path, begin with a disk of radius ε at its first vertex.
Moving that disk along a segment of length ℓ adds at most the area
`2εℓ`: the segment's stadium has area `2εℓ+πε²`, and its starting disk
was already present. Add the segments. Smooth curves follow by uniform
polygonal approximation, whose chord lengths sum to at most L, and
then letting the approximation error tend to zero.

The orbital speed is at most `245+140(d+1)+65(d−1)`, so

```
L_d ≤ 2π(320+205d).
```

The annulus has area `π(M²−m²)`. If every annulus point is within δ
of the curve, the tube must cover that area. Therefore

```
M²−m² ≤ 4(320+205d)δ + δ²,

δ ≥ (M²−m²) /
    [sqrt(4(320+205d)²+M²−m²) + 2(320+205d)].
```

This supplies a lower bound proportional to 1/d at each phase. There
is even a simple uniform constant. Throughout 0≤φ≤π the tightening
annulus has `M²−m²≥17144575/208`. A hypothetical `δ≤38/d`, with d≥1,
would give

```
4(320+205d)δ+δ² ≤ 4·38·525+38²
                           = 81244 < 17144575/208.
```

That contradicts the necessary area inequality. Combining the two sides,

```
38/d < d_H(curve_d, annulus) ≤ 450π/d
```

for every positive integer d and every phase in the half-turn. Thus
the order 1/d is sharp; the constants are conservative. This lower
bound concerns the largest gap somewhere in the entire annulus,
without locating that gap or asserting clearance near a crossing.

## A radial statistic that stays exactly the same

There is also an exact finite-fold identity. If g is any continuous
function of radius, uniform time over a complete orbit gives

```
(1/(2π)) ∫₀²π g(|z_d(t)|) dt
  = (1/(2π)) ∫₀²π g(|B(u)|) du.
```

Substitute u=dt and split the resulting integral into d periods.
Thus every fold count has the same distribution of radii when sampled
at uniform times. The distribution of *directions* changes as the
folds become finer. Sampling by equal arc length would give a different
weight and is not what this identity measures.

The [length follow-up](fold_length.md) finds
`L_d=dP+C+O(1/d)`, with P the ellipse perimeter and a phase-independent
constant C. It gives an explicit uniform remainder and the limiting
radial weight for equal amounts of ink.

## Reproduce

```sh
python3 experiments/fold_band.py
python3 experiments/fold_band.py --figure
```

The standard-library program encloses the illustrated distance bounds
with rational sine and square-root estimates. It checks both one-unit
statements with a rational enclosure of π and verifies the exact strict
area inequality for the lower bound. The figure uses 256 segments
per repeat; its second-derivative and coordinate-rounding bound stays
below 0.01 sheet units at the common scale 0.42. The graph is an
illustration of the smooth curves, separate from the covering proof.

This does not give whole-branch clearance at a selected crossing or
classify any event. Those questions have their own
[local certificates](fold_shoulder_events.html) and
[seven-/fourteenfold census](fold_movie.html).
