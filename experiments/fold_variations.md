# An ellipse inside a turn

[Keep the folds. Turn one arm.](fold_variations.svg) is a sheet of six
orbital drawings. The top row has seven rotational folds, the bottom
fourteen. Moving across either row, the backward arm begins at zero,
a quarter turn, and a half turn. The arm lengths stay 245, 140, and 65.
Every panel has the same scale.

![Sevenfold and fourteenfold drawings at three starting angles, moving
from open petals to overlapping rings.](fold_variations.svg)

The half-turn version leaves a much wider space around the center.
There is a short explanation hiding in the original three arms.

## Pull out the first turn

Both rows have outer rhythm m=d+1 and backward rhythm n=d−1.
Here d is 7 or 14. With backward starting angle φ, the complex point is

```
z(t) = 245 exp(it) + 140 exp(i(d+1)t) + 65 exp(−i(d−1)t+iφ).
```

Write `θ=dt−φ/2`. Factoring gives

```
z(t) = exp(it) [245 + exp(iφ/2)(205 cos θ + 75i sin θ)].
```

The expression `205 cos θ + 75i sin θ` runs around an ellipse.
The starting angle rotates that ellipse by φ/2 around its center,
which is offset 245 from the origin. The outside factor exp(it) turns
the whole arrangement as the point travels around it.

At zero starting angle, the ellipse's long axis points toward the
origin; one end comes within `245−205=40`. At a half turn, the
long axis points sideways, and the ellipse stays much farther away.
The radius of z is just the distance to a point on this offset ellipse.
Seven or fourteen changes how the point is woven around the origin,
but θ still visits the entire ellipse. **Both rows therefore have
the same full radial range in each column.**

## The two end columns have exact radii

At φ=0, put u=cos θ. The squared radius is

```
|z|² = 65650 + 100450u + 36400u²,       −1≤u≤1.
```

Its derivative is `100450+72800u>0` throughout this interval.
Thus the first column has radii **40 through 450**, in both rows.

At φ=π, put s=sin θ. Now

```
|z|² = 102050 − 36750s − 36400s²,      −1≤s≤1.
```

This is a concave quadratic. Its smaller endpoint value is 28900,
and its maximum occurs at `s=−735/1456`. Consequently the last
column has radii

```
170 ≤ |z| ≤ sqrt(23155775/208) ≈ 333.6553.
```

That larger inner radius is the ring's open center. The three columns
are geometric illustrations, rather than certified crossing censuses.

## Why the folds stay

Increasing t by 2π/d leaves both `exp(idt)` and `exp(−idt)` unchanged,
while the outside factor gains `exp(2πi/d)`. Thus

```
z(t+2π/d) = exp(2πi/d) z(t)
```

for every starting angle. This is the original
`gcd(m−1,n+1)` rotation rule, with no restriction on φ. The shapes
change, and their stated rotational symmetry remains.

## The point keeps moving

The same ellipse trick works for the velocity:

```
z′(t) = i exp(it) [245 + exp(iφ/2)(A cos θ + iB sin θ)],
A = 205+75d,       B = 75+205d.
```

Here B≥A>245. Every point on this velocity ellipse is at least
A from its own center, so its distance from the origin is at least
`A−245=75d−40`. Speed therefore stays at least **485** in the
sevenfold row and **1,010** in the fourteenfold row, throughout
**every intermediate starting angle**, not only the three stills.
No stationary point appears while the arm turns.

The velocity ellipse surrounds the origin and is traversed d times
counterclockwise. The outside factor contributes one more turn.
The [tangent direction](tangent_turning.md) therefore makes **8 turns**
in the top row and **15 turns** in the bottom row, at every phase.
These are direction turns; the position itself winds once around
the center because the offset position ellipse stays to one side
of the origin before the outside rotation.

## The signed area stays too

Fourier orthogonality gives the same
[signed-area formula](signed_area.md) as for the original drawing:

```
signed area = π[245²+140²(d+1)−65²(d−1)]
            = π(83850+15375d).
```

Changing φ leaves it unchanged. The top row keeps area 191475π,
the bottom 299100π, even as their empty centers widen. Signed
area counts overlapping regions with their winding multiplicities.

## Save or redraw

The [standalone SVG](fold_variations.svg) works without scripts and
keeps links to the original zero-phase drawings. Regenerate it with

```sh
python3 experiments/fold_variations.py
```

The generator uses the standard library and 4,096 line segments per
curve. A bound on the second derivative gives chord interpolation
error at most `max|z″|·(2π/4096)²/8`. At the sheet's common scale,
even the fourteenfold row stays below **0.005 sheet units**, including
rounded vertex coordinates. These paths illustrate the smooth curves;
the small sampling bound is not an intersection certificate.

The follow-up [The folds stay. The crossings change.](fold_contacts.html)
now classifies every two-branch tangency during each complete half-turn.
There are two batches per row; their crossing-pair counts rise
7 → 21 → 35 and 70 → 98 → 126. Its [triangle reduction](fold_contacts.md)
uses exact polynomial root isolation, separately from these sampled
drawings. A complete triple-passage census along the turns remains open.
