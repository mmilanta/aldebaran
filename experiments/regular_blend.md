# A route that keeps moving

Choose **Keep moving** in [Two routes between two zeros](blend.html).
It connects the original 2 / 3 and 4 / 7 drawings without a stationary
point anywhere in the family. The tangent’s net turn count stays **zero**;
the center’s winding count stays **+1**. Crossings are allowed.

The [straight blend](blend_cusps.md) between these same endpoints has two
critical weights with two cusps each, and an intermediate tangent count
of −2. Equal endpoint counts leave room for different routes. Here is
an explicit route with a certificate over its **entire continuous
parameter domain**, rather than a sampled sequence of regular drawings.

## Blend angles and distances

Write the endpoint curves as

```
z_A(t) = e^(it) f_A(t),     f_A(t) = 245 + 140 e^(it)  + 65 e^(−4it),
z_B(t) = e^(it) f_B(t),     f_B(t) = 245 + 140 e^(3it) + 65 e^(−8it).
```

Both `f` values have real part at least `245−140−65 = 40`. Their principal
complex logarithms are therefore smooth, periodic functions, without an
argument jump. Define

```
z_safe(t,a) = e^(it) exp[(1−a) Log f_A(t) + a Log f_B(t)],    0 ≤ a ≤ 1.
```

At `a = 0` this is exactly `z_A`; at `a = 1` it is exactly `z_B`.
Every intermediate curve is closed, with matching derivatives at the
cycle boundary. For each fixed time `t`, the point’s distance from the
center is the weighted geometric mean of the two original distances.
Its angle follows their shorter angular interval: both residual angles
lie strictly between −π/2 and π/2, so their difference is less than π.

In particular,

```
|z_safe| = |z_A|^(1−a) |z_B|^a ≥ 40.
```

Its angle is `t` plus a smooth periodic residual angle, so the center
has winding count +1 throughout. These facts alone do not prove a
nonzero velocity. That is the next check.

## A whole family becomes a family of straight segments

Logarithmic differentiation gives the useful identity

```
q_a(t) = z_safe′(t,a)/z_safe(t,a)
       = (1−a) z_A′(t)/z_A(t) + a z_B′(t)/z_B(t).
```

Thus for each orbit time, **every** blend’s logarithmic velocity is on
one straight segment from `q_A(t)` to `q_B(t)`. Prove that all those
segments avoid zero, with a uniform positive margin, and the entire
deformation is regular. The exponential and logarithm never need to
be enclosed or approximated in this proof.

The endpoint positions and velocities are rational at the familiar
rational unit-circle points

```
w_q(s) = i^q (1−s²+2is)/(1+s²),    q = 0,1,2,3,   0 ≤ s ≤ 1.
```

Their ratios `q_A` and `q_B` are rational too, since the positions are
nonzero. At each rational interval’s starting point, compute the exact
distance from zero to their segment. If `p = q_A` and `d = q_B−q_A`,
the closest point is

```
p + λd,     λ = clamp(−(p·d)/(d·d), 0, 1).
```

When `d = 0`, use `p` itself. Everything through the squared distance
uses rational arithmetic. An integer square root supplies a dyadic
lower bound for the distance: for `D = N/M ≥ 0`,

```
floor(sqrt(floor(2^80 N/M))) / 2^40 ≤ sqrt(D).
```

## Enclose all the segments between the anchors

For either original endpoint curve, retain the global angular bounds

```
|z′| ≤ V = 245 + 140m + 65n,
|z″| ≤ M = 245 + 140m² + 65n².
```

An interval of width `h` in `s` spans at most `2h` in angle. From its
rational starting position `p` and velocity `v`, the whole interval has
the radius and speed bounds

```
|z| ≥ r = max(40, max(|p_x|,|p_y|) − 2Vh),
|z′| ≤ b = |v_x| + |v_y| + 2Mh.
```

For its logarithmic velocity,

```
q′(t) = z″/z − (z′/z)²,
|dq/ds| ≤ 2(M/r + b²/r²) = L.
```

Compute this bound for both endpoints. At every time in the interval,
each endpoint of the moving segment stays within
`E = max(L_A,L_B) h` of its starting value. Every matched point on those
two segments therefore also stays within `E`, uniformly over **all**
blend weights.

Let `d₀` be the dyadic lower bound for the starting segment’s distance
from zero. Accept an interval only when the exact rational inequality

```
d₀ − E > 1/10
```

holds. Otherwise bisect it and cover both children. All four closed
quarters are covered. A depth limit causes explicit failure rather than
a claim of regularity. No floating-point decision participates in this
cover, in the closest-point calculation, or in its stopping inequalities.

Run the standard-library certificate:

```sh
python3 experiments/regular_blend.py
```

It completes with **1,235 intervals**, the deepest at subdivision 11.
The smallest accepted rational margin is approximately 0.100077071.
The resulting exact conclusion is

```
|z_safe′/z_safe| > 1/10,
|z_safe′| > 40/10 = 4
```

everywhere in the two-parameter family. The speed is measured in original
drawing units per radian of orbit time. The approximate reported margin
is only a convenient description of the exact inequalities already checked.

Since no tangent becomes undefined, its winding count cannot change
along this route. The [independent endpoint certificate](tangent_turning.py)
gives zero, so every intermediate curve also has tangent index zero.
This is an explicit regular deformation, not an assertion that all
equal-index curves are safely connected by this interpolation rule.

## Browser formulas and their separate checks

[blend_math.js](blend_math.js) evaluates the position with real logarithms
of the distances and continuous residual angles. It uses the identity
above for the analytic velocity. Analytic acceleration follows from

```
z_safe″ = z_safe (q_a² + q_a′),
q_a′ = (1−a)[z_A″/z_A − q_A²] + a[z_B″/z_B − q_B²].
```

Both endpoint weights return the original functions directly, preserving
their exact browser values. Switching routes preserves the selected
blend weight and parameter window. On this route, the two cusp presets
are labeled with their percentages instead; there is no cusp at either
weight. The lens keeps the straight-route event’s orientation for an
honest comparison, with one scale on both axes. Nothing animates.

```sh
node experiments/blend_check.js
```

The independent Node checks compare the positions to polar interpolation,
differentiate positions and velocities numerically, check periodicity,
reflection, and exact endpoint equality, and independently accumulate
tangent angles for 101 whole intermediate orbits. Separate straight-route
checks cover 1,001 blends, comparing angle sums and ray counts with the
certified classification and checking the sampled velocity polygon’s
clearance against its interpolation bound. These numerical checks validate
the browser formulas; the rational full-family cover proves regularity.
