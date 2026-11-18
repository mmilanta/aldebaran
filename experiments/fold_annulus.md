# The annulus tightens

In [One ellipse. Many folds.](fold_turn.html), the petals withdraw from
the center as the backward arm turns. This is more than a comparison
of the two end drawings: **the innermost radius increases strictly and
the outermost radius decreases strictly throughout the half-turn**.

This holds for every positive integer fold count d, with the original
lengths 245, 140, and 65. The smallest concentric annulus containing
the curve steadily tightens. It does not say that the curves themselves,
or their winding regions, are nested.

![The inner radial boundary rises from 40 to 170 while the outer falls
from 450 to about 333.66 over a half-turn.](fold_annulus.svg)

The graph joins numerical illustrations at integer degrees. The
following argument concerns every real phase, including between those
vertices. A separate rational calculation encloses the radii at all
181 degree settings in the interactive study.

## Trade an orbit for a point outside an ellipse

Put R=245, A=205, B=75, and ψ=φ/2. The
[ellipse factorization](fold_variations.md) gives

```
z(t,φ) = exp(it) [R + exp(iψ)(A cos θ + iB sin θ)],
θ = dt−ψ.
```

The outside rotation changes no distance. As t completes an orbit,
θ covers the entire ellipse. Thus d has no effect on either radial
extremum.

Rotate the axes by −ψ and use the ellipse's two reflection symmetries.
The possible radii are exactly the distances from

```
q = (R cos ψ, R sin ψ)
```

to points e on the fixed ellipse `(e₁/A)²+(e₂/B)²=1`.
For 0<ψ<π/2, both coordinates of q are positive. Since R>A,
q is always outside the filled ellipse.

## The nearest point has one positive multiplier

Write a₁=A, a₂=B. There is a unique λ>0 satisfying

```
Σ aⱼ² qⱼ² / (aⱼ²+λ)² = 1.
```

The left side decreases strictly from more than one to zero. The
nearest point is

```
eⱼ = aⱼ² qⱼ / (aⱼ²+λ).
```

This is a global assertion, not just a stationary-point test. Write
xⱼ=eⱼ/aⱼ and let x* be the proposed point. Both x and x* have unit
length. Expanding the squared distance F(x)=|q−(Ax₁,Bx₂)|² gives

```
F(x)−F(x*) = Σ (aⱼ²+λ)(xⱼ−x*ⱼ)².
```

Every coefficient is positive, so x* is the unique global minimum.
The strictly decreasing scalar equation also makes λ and e smooth
on the open quadrant.

Let m(ψ)=|q−e|. When differentiating its squared distance, the
contribution from e′ vanishes: q−e is normal to the ellipse and e′
is tangent to it. Consequently

```
d(m²)/dψ = 2(q−e)·q′
         = 2λR² sin ψ cos ψ
           [1/(B²+λ) − 1/(A²+λ)] > 0.
```

Thus the innermost radius moves strictly outward.

## The farthest point has a multiplier beyond A²

There is likewise a unique μ>A² satisfying

```
Σ aⱼ² qⱼ² / (μ−aⱼ²)² = 1.
```

The first term diverges as μ decreases toward A² because q₁>0.
The sum then decreases strictly to zero as μ tends to infinity.
The farthest point is

```
eⱼ = −aⱼ² qⱼ / (μ−aⱼ²).
```

For this stationary point the global difference identity is

```
F(x*)−F(x) = Σ (μ−aⱼ²)(xⱼ−x*ⱼ)².
```

Every coefficient is positive. This is therefore the unique global
maximum on the open quadrant, again smooth in ψ. If M(ψ)=|q−e|,

```
d(M²)/dψ = 2μR² sin ψ cos ψ
           [1/(μ−B²) − 1/(μ−A²)] < 0.
```

The outermost radius moves strictly inward. Because m and M are
positive, the signs for their squares give the same signs for the
radii themselves. Continuity of extrema on a compact ellipse extends
the strict inequalities to the closed half-turn: any two distinct
phases in [0,π] give strictly nested radial intervals.

## The symmetric endpoints need their own maximum

At ψ=0 the nearest and farthest points lie on the long axis, giving

```
m(0)=R−A=40,       M(0)=R+A=450.
```

At ψ=π/2, the nearest point lies on the short axis, so m=R−B=170.
The farthest point is different: it occurs twice, away from the axes.
The open-quadrant maximum formula reaches μ=A² at this endpoint.
Put D=A²−B²=36400. Its two maximizers have

```
x₂ = −BR/D = −735/1456,
x₁ = ±sqrt(1−x₂²).
```

They are valid because BR<D. The same global difference identity
still applies, now with a zero coefficient on the first square and
positive coefficient D on the second. Exactly these two points
maximize the distance. Their squared radius is

```
M(π/2)² = A²(1+R²/D) = 23155775/208,
M(π/2) ≈ 333.6552732180.
```

Treating the short-axis endpoint as the farthest point would give
320 and miss both true maxima. The browser calculation handles
this symmetric case explicitly; its ordinary scalar equation applies
to the open interval.

## Read the two views and repeat the calculation

In the interactive study, one circuit of the ellipse is one repeat of
the orbital curve. The white points have exactly the same radius in
their respective coordinate systems. A full orbital repeat takes
2π/d radians of the first arm's turn. At its end, the ellipse point
returns, while the orbital point is rotated by that amount.

The browser solves the two scalar equations by bisection and displays
both radial edges to two decimal places. The independent rational
calculator uses enclosed sine and cosine, strict endpoint signs, and
80 rational bisections for each multiplier. Its radius enclosures are
narrower than 10⁻¹⁶ drawing units at all 181 slider phases. It also
checks that each enclosure determines a unique two-decimal display.
The signs in the analytic argument above establish monotonicity
between those phases.

```sh
python3 experiments/fold_annulus.py
python3 experiments/fold_annulus.py --figure
node experiments/fold_turn_check.js
```

These commands use only standard runtimes. `--json` prints the exact
rational radius bounds for independent checks. The JavaScript check
compares every displayed radial edge with those bounds, and audits the
browser geometry against the original three-frequency formula.
Regenerate the default still, study preview, and illustrated sheet with
`node experiments/study_covers.js`.

The annulus says where the line can reach, not how often it visits a
point. The [crossing census](fold_movie.html) and the
[radial shoulder](fold_radial.md) answer separate questions.

The companion [A line approaches a band](fold_band.md) follows the fold
count instead of the starting angle. Every point of the annulus is
within `2M sin(π/(2d))` of the d-fold curve. The rotational copies alone
give this quantitative convergence to the whole band.
