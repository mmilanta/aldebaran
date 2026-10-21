# A point, a curve, and a count

[Open the interactive study](winding.html).

The original drawing colors time along the path. Here, color belongs to the
regions between the lines. A point in a gold region sees a positive net number
of counterclockwise turns. A point in a blue region sees a negative count.
Opposite turns cancel. A point directly on the curve has no winding number.

The study reflects the sketchbook vertically: positive imaginary coordinates
point up, so positive turns look counterclockwise. It uses the same lengths,
rhythms, and curve, with no animation.

Garden contains regions with counts +1, +2, and +3. Its +3 regions are thin;
the count buttons make them easier to find. The curve at rhythms 2 / 25 has
blue regions with counts down to −7, even though its center still has count
+1. Each button visits a point checked against the actual trigonometric curve,
using the distance argument below. The rendered grid finds no counts beyond
these, but a raster alone cannot exclude a smaller undetected region.
The zero-count buttons visit bounded gaps inside the drawing, illustrating
that zero need not mean the unbounded region outside the whole picture.

The signed area adds each region's area multiplied by its winding count.
The exact totals, **142300π** for Garden and **−6400π** for 2 / 25, come from
[Fourier orthogonality](signed_area.md), rather than counting colored pixels.

## Counting without following the whole argument

The website draws 24,000 uniformly sampled segments, including the closing
segment. For a point `q = (x, y)`, cast a horizontal ray to the right. An
upward edge crossing this ray adds one; a downward crossing subtracts one.
Ignore horizontal edges. Include the low endpoint's height and exclude the
high endpoint's height, so a shared vertex cannot be counted twice.

The point calculation uses oriented determinants to test which side of an
edge the point lies on. The color field uses a separate scanline calculation:
collect all edge crossings of each row of pixel centers, sort them from left
to right, and change the count on crossing each edge. Start at zero to the
left of the whole polygon. An upward edge decreases the count when the
*point* passes it from left to right, since that edge leaves the rightward ray.
These two signs describe different movements and agree.

See [Jeff Erickson's winding-number notes](https://jeffe.cs.illinois.edu/teaching/comptop/2023/notes/02-winding-number.html)
for the signed-crossing definition, its angle-sum equivalent, and the
connection to signed area. The JavaScript implementation lives in
[winding_math.js](winding_math.js); the browser controls live in
[winding.js](winding.js). Neither uses a library.

## When the polygon's count is the smooth curve's count

Write the smooth curve as

```
z(t) = 245 exp(it) + 140 exp(imt) + 65 exp(−int).
```

Its second derivative satisfies

```
|z″(t)| ≤ M = 245 + 140m² + 65n².
```

On an interval of length `h`, let `p(t)` interpolate its two endpoints by a
straight line. The elementary linear-interpolation bound for this vector
curve is

```
|z(t) − p(t)| ≤ M (t − a)(b − t) / 2 ≤ M h² / 8.
```

One way to obtain it is to integrate `z″` against the Green function for
zero endpoint values. That scalar kernel has one sign, and its absolute
integral is `(t − a)(b − t) / 2`. Taking the vector norm gives the displayed
bound without an extra factor from treating the coordinates separately.

For `N = 24000` samples, `h = 2π/N`. The uniform distance bound `ε = Mh²/8`
is less than **0.000155** drawing units for Garden and **0.000355** for 2 / 25.

Suppose a chosen point is at distance greater than `ε` from every segment of
the polygon. The straight homotopy

```
H(s, t) = (1 − s) p(t) + s z(t),     0 ≤ s ≤ 1,
```

stays within `ε` of the polygon at the corresponding parameter, so it never
touches that point. The winding count is unchanged through this deformation.
Therefore the polygon and the smooth curve have the same count there.

The website computes the shortest distance from the chosen point to every
segment. It shows a count only beyond a **one-unit** boundary margin, which
comfortably exceeds both error bounds. Inside that margin it says “Near
curve,” without reporting an integer. This is also a visual aid: points too
close to the displayed line are hard to distinguish on a small screen.
The calculation uses floating-point arithmetic; the wide margin avoids
depending on nearly equal comparisons at the theoretical error threshold.

The colors approximate boundaries at pixel resolution. A colored pixel's
center receives the polygon's count; its whole square need not lie in one
smooth region. The point readout checks distance independently of the image.
The count buttons are examples, not a proof that every possible region is
represented. The exact area formula has no raster approximation.
An [exhaustive rational intersection certificate](smooth_census.md) now
independently proves the complete region counts for both displayed shapes,
as well as Star and Crown. It supplies the exclusion argument that a raster
or a handful of point checks cannot give.

## Reproducible checks

Run `node experiments/winding_check.js`. It uses only Node's built-in
assertions. It checks clockwise, counterclockwise, doubled, self-crossing,
and repeated-vertex polygons, horizontal rays through vertices, raster
clipping, and polygon distances. For all 322 supported rhythm pairs, it
compares selected raster pixels and direct crossing counts with an independent
sum of argument changes. It checks a point of every raster color, the inner
disk's +1 count, and sampled interpolation errors against the bound.

For the two displayed shapes it also checks every count-button position,
its clearance from the curve, and agreement with a twice-refined polygon.
Those numerical checks complement the bound and homotopy argument; sampling
alone is not a proof about an entire continuous region.
