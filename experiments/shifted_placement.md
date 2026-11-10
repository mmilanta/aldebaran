# Where should a finite set of shifted parabolas go?

The [three-curve picture](shifted_parabolas.svg) moves the best insertion
away from the midpoint. What if several interior curves can move at once?
For the cubic intercept law, there is a unique answer for **every finite
count**, and one increasing scalar function finds it.

The family is

```
Xₚ(Y) = Y²/2 − pY + p³/3,       0 < a ≤ p ≤ b.
```

Fix the two outer slope labels a<b and choose m−1 interior labels, giving
m gaps and m+1 parabolas. The theorem here maximizes the **total area of
all bounded pockets**. It does not maximize the smallest pocket.

## The finite theorem

For every integer m≥1 and fixed positive a<b, precisely one placement
maximizes the total bounded area. For m≥2 all its interior labels satisfy

```
4pⱼ² − pⱼ(pⱼ₋₁+pⱼ₊₁) − pⱼ₋₁² − pⱼ₊₁² = 0.
```

The first ratio r₁=p₁/a determines the entire sequence:

```
T(r) = [−1 + √(17−4/r−4/r²)]/2,
rⱼ₊₁ = T(rⱼ),
pⱼ = a r₁r₂⋯rⱼ.
```

There is exactly one r₁ in (1,b/a) for which p_m=b. The gaps decrease
strictly from left to right: the higher-curvature end of the intercept
law gets more curves. These are exact statements at finite m, rather
than consequences inferred from the earlier density limit.

## A continuous objective, including collapsed gaps

The [secant-variance formula](shifted_parabolas.md#total-area-is-a-weighted-secant-variance)
writes the total area as

```
B = [Σ (v−u) s(u,v)² − (h(b)−h(a))²/(b−a)]/2,
s(u,v) = (u²+uv+v²)/3.
```

Equivalently, maximize B by minimizing the deficit

```
D = B∞−B = Σ E(u,v),
B∞ = [(b⁵−a⁵)/5 − (b³−a³)²/(9(b−a))]/2,
E(u,v) = q²g³/6 + g⁵/360,
g = v−u,       q = (u+v)/2.
```

The polynomial E extends continuously to zero-length gaps, with value
zero. Thus a minimum exists on the compact closed ordered simplex
`a=p₀≤p₁≤⋯≤p_m=b`.

A minimizer cannot have a collapsed gap. If it did, use one redundant
label to split any positive gap into lengths α,β. Strict convexity of
h(p)=p³/3 on this positive interval makes its two new secants different.
The [insertion identity](shifted_parabolas.md#insert-one-slope) increases
the total area by

```
αβ(s_right−s_left)² / [2(α+β)] > 0.
```

The new configuration has the same number of labels, a contradiction.
Consequently every minimizing partition has positive gaps and satisfies
the interior stationarity equations. This boundary argument matters:
uniqueness of a stationary solution alone would not prove existence of
an interior global optimum.

## Derive the stationarity equation

For a general C² strictly convex intercept h, write f=h′ and let s be
its average over [u,v]. The variance integral gives

```
E(u,v) = (1/2)∫[u,v] (f−s)²,
∂E/∂v = (f(v)−s)²/2,
∂E/∂u = −(f(u)−s)²/2.
```

The terms from differentiating s vanish because the residual has zero
integral. At an interior partition point p between neighbors u,v,
stationarity therefore says

```
(f(p)−s_left)² = (f(p)−s_right)².
```

Strict convexity gives `s_left<f(p)<s_right`, so this is equivalent to
`2f(p)=s_left+s_right`. With f(p)=p², substitution yields exactly
`4p²−p(u+v)−u²−v²=0`.

Divide by p², set r=p/u and t=v/p, and solve the quadratic in t.
Only its positive root can be an increasing next label. It is t=T(r)
as displayed above.

## One scalar root proves global uniqueness

For r≥1, the expression under the square root increases strictly with
r. Hence T is continuous and strictly increasing. Also T(1)=1 and
T(r)>1 when r>1. Thus each iterate Tʲ(r) increases strictly with r,
as does their positive product

```
P_m(r) = r T(r) ⋯ T^(m−1)(r).
```

At r=1, P_m=1. For m≥2, at r=b/a the first factor already equals b/a
and all remaining factors exceed one, so P_m>b/a. The intermediate
value theorem and strict monotonicity give exactly one root of
`P_m(r)=b/a` in (1,b/a).

Every global maximizer is interior and stationary, and every stationary
placement must follow that same unique recurrence. A global maximizer
exists, so this solution is the unique global maximizer. The m=1 case
has only its fixed endpoints and no bounded area.

No claim of convexity of the entire multivariable objective is needed.
The proof also does not transfer this special recurrence to an arbitrary
strictly convex intercept law.

## Why the physical gaps get smaller

For r>1,

```
1 < T(r) < 2−1/r < r.
```

To check the middle bound, compare the positive square roots:

```
(5−2/r)² − (17−4/r−4/r²) = 8(1−1/r)² > 0.
```

The preceding gap is `pⱼ₋₁(rⱼ−1)`. The next is
`pⱼ₋₁ rⱼ(T(rⱼ)−1)`, which is strictly smaller by that bound.
The ratios decrease too. This is consistent with the asymptotic
density `h″^(2/3)=(2p)^(2/3)`, but here follows directly at every finite
count.

The [companion drawing](shifted_placement.svg) compares the complete
five-curve bands and gives all three placements on common slope rulers.
The density quantiles and finite optimum almost coincide at that scale;
the table retains their visible decimal differences.

## Numbers with a rational certificate

For [a,b]=[1,3], the two-gap case recovers the independently known
`p₁=(1+√11)/2`. With four gaps, the three optimal interior labels are
approximately

```
1.650240766475,  2.162146131438,  2.603606875834.
```

Equal spacing would give 1.5, 2, 2.5. The density quantiles are much
closer, but still differ from the finite optimum. Their formula is

```
p_j^density = [1+(243^(1/3)−1)j/m]^(3/5).
```

Both optimal and density placements have the same asymptotic scaled
deficit `m²D→γ≈5.180347411652`. Finite placement improves the higher
terms. The exact enclosures distinguish all three choices through
128 gaps:

| Gaps m | Optimal m²D, approximately | Equal-gap m²D, approximately |
| ---: | ---: | ---: |
| 2 | 5.255862648505 | 5.688888888889 |
| 4 | 5.201605596809 | 5.755555555556 |
| 8 | 5.185926415981 | 5.772222222222 |
| 16 | 5.181764024150 | 5.776388888889 |
| 32 | 5.180703079464 | 5.777430555556 |
| 128 | 5.180369671440 | 5.777756076389 |

The last column uses the exact identity `52/9−16/(45m²)`.
The table's decimals are illustrative, not outward-rounded intervals.
The [JSON record](shifted_placement.json) retains rational lower and
upper endpoints for every slope, total area, and deficit. Every selected
area enclosure has width below 5×10⁻²⁴ square drawing units.

## Reproduce and audit

```sh
python3 experiments/shifted_placement.py
python3 experiments/shifted_placement.py --write
python3 experiments/shifted_placement_figure.py
```

The program uses only the standard library. Integer square roots give
dyadic square-root bounds, checked by exact squaring. Monotonicity of T
propagates ratio intervals and products. Bisection accepts a side only
when its **whole endpoint interval** is strictly below or above b/a.
An overlapping interval triggers refinement or a newly certified bracket;
neither a floating point sign nor a midpoint decides a proof predicate.

The final two rational shooting endpoints have strictly proved opposite
signs. Propagating their interval encloses every optimal node; the last
node is the fixed endpoint b. The positive interval polynomial for E
then encloses D and hence B. Endpoint precision in the saved record is
80 bits for the initial ratio in the saved [1,3] examples, with extra
working bits for accumulated roundoff. A very narrow endpoint span
also scales down the tolerance and increases working precision.
Root enclosures for the density quantiles use cube and fifth
powers, independently of the shooting recurrence.

Controls compare the known quadratic two-gap solution, the stationarity
polynomial at every enclosed interior point, independent full-band and
interval-variance integrals, freshly clipped complete arrangements, and
rational challengers. Positive endpoint changes and the exact scaling
`p→cp`, `B→c⁵B` supply further checks. These finite audits accompany the
all-count proof above; they do not replace it.

An additional exact-rational solution, a=2, p₁=17, b=26, exercises
the overlapping-midpoint branch of the bisection. Another endpoint
span of only 2⁻¹²⁰ exercises the precision adjustment.

The [earlier note](shifted_parabolas.md) continues to cover general
discrete-convex intercepts and the general asymptotic density theorem.
General finite placement, smallest-pocket optima, and a shifted-family
compromise frontier remain separate questions.
