# Why the triangles wait

The [complete phase census](fold_movie.md) puts all its triple passages
near the end of a half-turn. The ellipse gives a reason that does not
depend on seven or fourteen folds.

For **every positive integer d**, with the same lengths 245, 140, and 65,
there is **no triple or higher meeting** while

```
0 ≤ φ ≤ φ*,       0.894940827171 < φ*/π < 0.894940827172.
```

Before and at that threshold, a circle centered at the origin meets the
offset ellipse in at most two distinct points. A spatial meeting on the
orbital drawing can use at most one visit from each of those ellipse
points. Three visits therefore have to wait.

![The same circle meets a tilted ellipse twice before the threshold and
four times after it. A magnified radial profile shows the shoulder that
creates the two extra intersections.](fold_radial.svg)

The threshold is sharp **for this radial argument**. Every later phase
admits some radius with four ellipse points. Those points usually have
different spatial directions in the orbital drawing: this does not
assert a four-visit meeting, or a triple at the threshold. The sevenfold
and fourteenfold triple phases remain the separately proved census.

A separate [analytic follow-up](fold_shoulder.md) does prove that actual
three-or-more-visit meetings approach φ* as the fold count grows:
their phase excess is `C/d²+O(d⁻³)`, with C/π≈20.284022161535.
It asserts neither a numerical fold cutoff nor ordinary-passage signs.

## One radius, at most one visit from each ellipse point

Set ψ=φ/2 and θ=dt−ψ. The [ellipse factorization](fold_variations.md) is

```
z(t,φ) = exp(it) [245 + exp(iψ)(205 cos θ + 75i sin θ)].
```

The bracket is never zero: its modulus is at least 40. Fixing θ gives
d time visits, separated by 2π/d. Their positions are distinct rotated
copies of that nonzero bracket. Consequently a specified spatial point
can use **at most one time visit per distinct θ**. An upper bound on
ellipse points at its radius is also an upper bound on its visits.

Rotate the coordinate axes by −ψ. The squared radius becomes

```
f(θ) = (x₀ + A cos θ)² + (y₀ + B sin θ)²,
A=205,       B=75,
x₀=245 cos ψ,       y₀=−245 sin ψ,
D=A²−B²=36400.
```

At φ=0 it is a strictly increasing quadratic in cos θ. Thus f has just
one maximum and one minimum on the parameter circle, and each level
has at most two distinct preimages. That property can change only when
two radial critical points meet.

## Find every possible change

Write g=f′/2. Direct differentiation gives

```
g  = −A x₀ sin θ + B y₀ cos θ − D sin θ cos θ,
g′ = −A x₀ cos θ − B y₀ sin θ − D(cos² θ−sin² θ).
```

Solving g=g′=0 for the center coordinates gives

```
A x₀ = −D cos³ θ,       B y₀ = D sin³ θ.
```

On our phase half-turn x₀≥0 and y₀≤0. A simultaneous solution therefore
has both cos θ and sin θ negative, unless it lies at an axis endpoint.
The axis endpoints would require 245=D/A or 245=D/B, neither of which
holds. Every interior degeneracy is equivalent to

```
X^(2/3) + Y^(2/3) = 1,
X = (245 A/D) cos ψ,       Y = (245 B/D) sin ψ.
```

This is the astroid that describes the ellipse's centers of curvature,
but the two derivative equations above supply the entire calculation.

Let c=cos φ. Then

```
X² = (82369/43264)(1+c)/2,
Y² = (11025/43264)(1−c)/2.
```

Eliminating the positive cube roots gives
`(X²+Y²−1)³+27X²Y²=0`. Clearing denominators produces the cubic

```
45392319784448 c³ − 252094190659584 c²
    + 1261235890824 c + 265240041066937 = 0.
```

Complete rational Sturm isolation gives **exactly one root in (−1,1)**,
near −0.9460251272294891. It is simple. There are no discarded candidates:
for nonnegative X,Y the implicit equation is equivalent to the astroid.
Indeed, put u=X^(2/3), v=Y^(2/3). The implicit equation gives
`1−u³−v³=3uv`, hence

```
(u+v−1)(u²+v²−uv+u+v+1) = 0.
```

The second factor is strictly positive. Thus u+v=1.
The unique cosine root determines φ*. Rational square-root and arctangent
bounds give the stated phase bracket; the [exact record](fold_radial.json)
keeps tighter bounds.

Uniqueness also has a short calculus proof. Write
`H(ψ)=X^(2/3)+Y^(2/3)`. On the open quadrant, the sign of H′ is the
sign of `B^(2/3)cos(ψ)^(4/3)−A^(2/3)sin(ψ)^(4/3)`. It is positive
until `tan ψ=√(B/A)` and negative afterward. Moreover H(0)>1 because
245A>D, while H(π/2)<1 because 245B<D. The level one is therefore
crossed exactly once, on the decreasing part. The cubic isolation
independently verifies that count and encloses its location.

## At the threshold, two points still suffice

Away from φ*, no radial critical point is degenerate. On the compact
parameter circle the number of simple critical points is consequently
constant on each side. It is two at φ=0, and four at φ=π: at the latter
endpoint

```
f(θ) = 102050 − 36750 sin θ − 36400 sin² θ,
```

whose derivative vanishes at cos θ=0 and at
`sin θ=−735/1456`. All four points are simple. The independent exact
quartic checks also give two and four critical points at rational phase
charts on the respective sides.

At φ*, the degeneracy is unique because both negative cubes determine
cos θ and sin θ uniquely. Substituting its two equations gives

```
g″ = 3D sin θ cos θ > 0.
```

Thus f has a stationary inflection there, with a nonzero third derivative.
It stays strictly monotone through that flat point. Its other two critical
points remain the simple maximum and minimum inherited from earlier
phases. Every level still has at most two distinct preimages, including
the flat level itself. This proves the **closed** interval through φ*.

After φ*, the four simple critical points alternate between two maxima
and two minima. Each maximum exceeds both neighboring minima. A level
between the larger minimum and the smaller maximum therefore has four
distinct preimages. A quartic radius equation rules out more than four
at every phase, as shown in the [census note](fold_movie.md#a-four-visit-ceiling-without-a-census).

## Reproduce

```sh
python3 experiments/fold_radial.py --write
python3 experiments/fold_radial_check.py
python3 experiments/fold_radial_figure.py
```

All three use only the standard library. The proof program reconstructs the
integer cubic, isolates every root on the complete cosine interval,
bounds the phase, and independently counts radial critical points using
their quartic in tan(θ/2). It also proves that the illustrated circle
of radius 321 has exactly two or four distinct ellipse points at the
two selected rational half-phase charts, 4/5 and 19/20.

The separate algebra audit constructs the full 7×7 Sylvester determinant
of the radial-critical quartic and its derivative. All ten coefficients
agree with `256v[(u²+v²−D²)³+27D²u²v²]`, where u=Ax₀ and v=By₀.
Substituting the rational half-phase chart directly also gives a
degree-twelve polynomial with exactly one root in [0,1]. Its independently
bounded phase lies inside the cubic route's saved enclosure.

The SVG uses rounded numerical paths. Its ellipse points sharing a
radius are **not** marked as coincident spatial visits. The complete
triple census and its signs require the separate moving-crossing proof.
