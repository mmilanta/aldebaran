# A cusp becomes a loop

[Open the interactive lens](loop.html).

Needle has rhythms 8 and 21 and arm lengths 245, 140, and 65. Its only cusp
occurs at the rightmost tip, where the point's velocity is zero. The
[classification note](cusp_proof.md) explains why this is the only stationary
point among the original sketchbook's rhythm pairs.

What happens if the innermost arm's length changes continuously?

## A local view, with one varying length

Call the inner length `r`. Move the origin to the rightmost tip for each value
of `r`, so all the tips line up. The coordinates in the lens are

```
X(t) = 245(cos t − 1) + 140(cos 8t − 1) + r(cos 21t − 1)
Y(t) = 245 sin t + 140 sin 8t − r sin 21t.
```

The lens shows `−0.05 ≤ t ≤ 0.05` and `58 ≤ r ≤ 72`, using the same scale in
both directions. `X` is even; `Y` is odd. At the tip,

```
X′(0) = 0
Y′(0) = 1365 − 21r = −21(r − 65).
```

The direction of travel therefore reverses as the inner length passes 65.
This is a change in velocity at the tip, not a reversal of time or of any arm.

## Why a crossing really appears

For `0 < t ≤ 0.05`, all three sine terms in

```
X′(t) = −245 sin t − 1120 sin 8t − 21r sin 21t
```

are positive before their minus signs. Thus `X` strictly decreases on the
positive half of the interval. There are no crossings within either half;
a crossing between halves must join the two times `−t` and `t`, at `Y(t) = 0`.

Also,

```
Y″(t) = −245 sin t − 8960 sin 8t + 441r sin 21t.
```

On this interval, use `sin u ≤ u` and `sin u ≥ u − u³/6`. Since `21t ≤ 1.05`
and `r ≥ 58`,

```
Y″(t) ≥ [−245 − 71680 + 441 × 58 × 21 × (1 − 1.05²/6)] t
       = (146605557 / 400) t > 0.
```

So `Y` is strictly convex for positive `t`.

- If **r < 65**, `Y′(0) > 0`. The point passes through a smooth, rounded tip,
  and `Y(t) > 0` for positive `t`; no crossing occurs in this lens.
- If **r = 65**, the first derivative vanishes but `Y(t) > 0` for positive
  `t`. The second and third derivatives of the curve are independent,
  giving the ordinary cusp.
- If **r > 65**, `Y′(0) < 0`, so `Y(t)` is initially negative. But `Y(0.05)`
  is positive throughout the slider range. Strict convexity gives exactly one
  positive root `τ` and hence one crossing between the times `−τ` and `τ`.
  Those two branches meet transversely: `X′(τ) < 0` and `Y′(τ) > 0`. The
  intervening arc forms one little loop.

For the endpoint claim, `Y(0.05)` decreases as `r` increases. At `r = 72`,
Taylor bounds for sine give the exact lower bound

```
245(0.05 − 0.05³/6) + 140(0.4 − 0.4³/6)
  − 72(1.05 − 1.05³/6 + 1.05⁵/120)
= 68436697 / 16000000 > 0.
```

Thus bisection on the positive half of the interval can reliably locate the
crossing. The website uses 50 iterations. It does not infer the existence of a
loop from sampled pixels.

## How the loop starts growing

Write `δ = r − 65`. Near the transition,

```
X(t) = −18935 t² + O(δt² + t⁴)
Y(t) = −21δt + 88340 t³ + O(δt³ + t⁵).
```

For small positive `δ`, the crossing time and the width from the tip to the
crossing therefore satisfy

```
τ ~ sqrt(21δ / 88340)
−X(τ) ~ (397635 / 88340) δ ≈ 4.501189 δ.
```

The greatest vertical distance from the horizontal axis, within the little
loop, grows more slowly:

```
height ~ 14 sqrt(7 / 88340) δ^(3/2).
```

The enclosed area grows as `δ^(5/2)`. To find its leading coefficient, put
`A = 18935`, `D = 21`, and `B = 88340` in the local form
`X = −At²`, `Y = −Dδt + Bt³`. Taking the absolute value of the integral
of `X dY` from `−τ` to `τ` gives

```
area ~ (8/15) A D^(5/2) / B^(3/2) × δ^(5/2)
     ≈ 0.777278 δ^(5/2).
```

The loop starts long and very thin. This is why it can look like a single
point at small lengths or on a small screen even though the crossing already
exists mathematically. These are asymptotic statements as `δ → 0+`, not exact
formulas for the whole slider range.

[loop_birth.py](loop_birth.py) checks the rational bounds, samples all 141
slider values, and compares the shrinking loops with the local width and area laws.
The script uses the Python standard library and is independent of the lens's
JavaScript. The site samples the actual trigonometric curve, not the cubic
approximation above. This argument describes only the displayed interval;
it does not classify intersections elsewhere on the full orbit.
