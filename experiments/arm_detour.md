# Give the first arm more room

There is another way to connect the [three zero-turn drawings](zero_turns.md)
without stopping. It uses only finite sums of circular motions: lengthen
the first arm, blend the drawings, then shorten the arm again. Two such
three-leg routes connect the original **2 / 3, 4 / 7, and 6 / 11** curves.
Every intermediate curve has tangent index **0** and center winding **+1**.

[Room to keep moving](arm_detour.html) draws both detours, with a fixed
scale for the whole drawing and a separate lens around the orbit’s halfway
point. A [standalone SVG](arm_detour.svg) shows five stills from each route.
The [earlier two-route study](blend.html) uses angles and distances for its
second route; these detours use only finite sums of circles.

Write

```
z_(m,n,R)(t) = R e^(it) + 140 e^(imt) + 65 e^(−int).
```

The original first length is `R = 245`. The two routes are:

| Route | First leg | Middle leg | Last leg |
| --- | --- | --- | --- |
| 2 / 3 → 4 / 7 | At 2 / 3, increase R from 245 to 300 | Hold R = 300; linearly blend 2 / 3 into 4 / 7 | At 4 / 7, decrease R from 300 to 245 |
| 4 / 7 → 6 / 11 | At 4 / 7, increase R from 245 to 700 | Hold R = 700; linearly blend 4 / 7 into 6 / 11 | At 6 / 11, decrease R from 700 to 245 |

In each middle leg, match points at the same orbit time and interpolate
their positions. The frequencies themselves remain integers; this is
not a continuously changing frequency, which could break closure. The
three legs join at exactly identical parametrized curves. Crossings are
allowed, while zero velocities are excluded throughout.

The round lengths 300 and 700 are convenient choices. No claim of a
minimal required arm length is made.

## Certify the complete legs

For any two endpoint curves `z_A,z_B`, the straight position blend has
velocity

```
v_a(t) = (1−a) z_A′(t) + a z_B′(t).
```

At each fixed time, every blended velocity lies on one segment. Evaluate
its endpoints exactly at rational unit-circle points. On an interval of
width `h` in the rational quarter parameter, the angle spans at most `2h`.
If

```
M = max(R_A + 140m_A² + 65n_A², R_B + 140m_B² + 65n_B²),
```

both endpoint velocities vary by at most `E = 2Mh`. So does every matched
point on their segments, uniformly over all blend weights. Compute the
starting segment’s exact squared distance from zero and a dyadic lower
bound `d₀` for its square root, using the same rational projection as
the [angle-and-distance certificate](regular_blend.md). Accept only when

```
d₀ − E > 1.
```

Otherwise bisect the interval. All four quarters must complete; a depth
limit raises an error. The six completed covers give:

| Leg | Accepted intervals | Deepest split |
| --- | ---: | ---: |
| 2 / 3, R: 245 → 300 | 65 | 6 |
| At R = 300, 2 / 3 → 4 / 7 | 436 | 10 |
| 4 / 7, R: 300 → 245 | 146 | 9 |
| 4 / 7, R: 245 → 700 | 181 | 9 |
| At R = 700, 4 / 7 → 6 / 11 | 394 | 10 |
| 6 / 11, R: 700 → 245 | 321 | 12 |

All six continuous two-parameter legs therefore have speed **greater
than one drawing unit per radian**. The original endpoints independently
have tangent index zero, which cannot change on a regular route. Also,
after factoring out `e^(it)`, every intermediate position has residual
real part at least `min(R_A,R_B)−140−65 ≥ 40`. The curve never reaches
the center, whose winding count stays +1 throughout both routes.

Run the standard-library program:

```sh
python3 experiments/arm_detour.py
```

It certifies **1,543 intervals** in total. As a negative control, the
same procedure is applied to the original 2 / 3 → 4 / 7 straight blend
at length 245. That route has the [two known cusp events](blend_cusps.md),
and the verifier rejects it at the depth limit. A failed cover on its
own does not prove singularity; the separate cusp classification does.

## The lens has a continuous subject

The gold arc surrounds `t = π`. Its ends are `π−u` and `π+u`, where
`0 < u < π/2` is the next return to the horizontal axis after `π`.
Reflection makes these two ends the same point in the drawing. The gold
arc is **not necessarily a simple loop**: it can cross itself in between,
and a third visit can meet its ends. The lens follows an arc of the
parameter, rather than claiming to track one unchanged region.

There is exactly one such positive `u` on every intermediate drawing of
both detours. To check this without trusting a numerical search, write
`c = cos u` and use the Chebyshev polynomials of the second kind:

```
U₀(c) = 1,  U₁(c) = 2c,  Uₖ(c) = 2c Uₖ₋₁(c) − Uₖ₋₂(c).
sin(ku) = sin(u) Uₖ₋₁(c).
```

All forward rhythms here are even and all backward rhythms are odd.
For one endpoint drawing,

```
y(π+u) = sin(u) G(c),
G(c) = −R + 140 Uₘ₋₁(c) + 65 Uₙ₋₁(c).
```

On a leg, `G` is the weighted sum of the endpoint polynomials. Its
coefficients are affine in the leg weight, including on the legs that
change only the first arm. Throughout each leg, `G(0) < 0 < G(1)`.
The certificate covers the complete cosine/weight square with rectangles
and proves on each rectangle either **G < 0** or **∂G/∂c > 0**.
Consequently every zero is an upward simple zero. Opposite endpoint signs
give at least one; two upward simple zeros would require a downward or
nonsimple zero between them. There is therefore exactly one.

The bounds use exact rational Bernstein coefficients. On an interval,
the polynomial is a convex combination of these coefficients, so their
minimum and maximum bound it. For the weight direction, it is enough to
use both ends of the weight interval because dependence on weight is
affine. Ambiguous rectangles are bisected; reaching the depth limit
fails the certificate.

| Leg | Rectangles | Deepest split |
| --- | ---: | ---: |
| 2 / 3, R: 245 → 300 | 1 | 0 |
| At R = 300, 2 / 3 → 4 / 7 | 4 | 3 |
| 4 / 7, R: 300 → 245 | 5 | 3 |
| 4 / 7, R: 245 → 700 | 5 | 3 |
| At R = 700, 4 / 7 → 6 / 11 | 7 | 5 |
| 6 / 11, R: 700 → 245 | 13 | 5 |

The simple root varies continuously on each leg. At the joins the whole
polynomial is identical, so the unique roots agree too. Thus the lens’s
choice follows a continuous arc on both complete detours. At an endpoint
of this arc,

```
d/du y(π+u) = −sin²(u) G′(cos u) < 0.
```

This proves a transverse **return to the axis**. It does not prove that
the two reflected branches cross each other transversely: their
horizontal velocities may vanish while their vertical velocities remain
nonzero. Those meetings can change without a stationary point.

Run the standard-library proof and regenerate the still drawing with:

```sh
python3 experiments/arm_detour_lens.py
python3 experiments/arm_detour_lens.py --figure
node experiments/arm_detour_check.js
```

The Python program checks the shifted sine factorization against an
independent exact unit-circle evaluator, reconstructs the Bernstein
polynomials exactly, and rejects incompatible parity and endpoint signs.
All six covers use **35 rectangles**. The browser bisects the unique
axis return numerically; neither the mathematical claim nor the arc’s
continuity relies on the sampled drawing.
