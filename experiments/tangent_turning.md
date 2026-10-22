# The direction takes its own turns

A point on one of these orbital curves makes one net turn around the center.
But its **direction of travel** can turn a very different number of times.

| Curve | Rhythms | Turns around the center | Turns of the tangent |
| --- | --- | --- | --- |
| Garden | 7 / 13 | +1 | +1 |
| Clover | 7 / 14 | +1 | +1 |
| Star | 6 / 9 | +1 | +6 |
| Crown | 9 / 23 | +1 | −15 |
| A negative total | 2 / 25 | +1 | −25 |
| Needle | 8 / 21 | +1 | Undefined at its cusp |

Signs use mathematical coordinates, with positive imaginary coordinates up.
Positive turns run counterclockwise. The direction is the nonzero velocity
`z′(t)` divided by its length. Its net turn count is the winding number of
the **velocity curve** around zero. Dividing by length does not change angles.
A cusp interrupts that direction because the velocity is zero.
For the general definition and its connection to region winding numbers,
see [Damián Wesenberg, *A new formula for rotation number*](https://arxiv.org/abs/2010.01422).

![Atlas of tangent turns for all supported rhythms. Large outer rhythms mostly give positive counts; large inner rhythms give negative counts. Needle is omitted at its cusp. A second plot shows the tangent count falling from −10 to −21 as Needle's inner arm length increases from 58 to 72, with paired jumps of two before a single jump at 65.](tangent_turning.png)

The counts above are certified with exact integer arithmetic by
[tangent_turning.py](tangent_turning.py). Run it with Python's standard
library; add `--table` to print the whole atlas. The figure can be recreated
with [plot_tangent_turning.py](plot_tangent_turning.py), using optional NumPy
and Matplotlib. None of these tools run on the website.

## A polygon whose answer is provably the same

For fixed arm lengths, the curve and its velocity are

```
z(t)  = 245 exp(it) + 140 exp(imt) + r exp(−int)
z′(t) = i [245 exp(it) + 140m exp(imt) − rn exp(−int)].
```

Write `v(t) = z′(t)/i`; rotating every velocity by the same quarter-turn
does not change its winding. Its derivative has the uniform bound

```
|v′(t)| ≤ L = 245 + 140m² + rn².
```

Parametrize each quarter of the unit circle by a rational number `s`:

```
w(s) = i^q (1 − s² + 2is)/(1 + s²),     0 ≤ s ≤ 1, q = 0, 1, 2, 3.
```

The angle changes at speed `2/(1+s²) ≤ 2`. If an interval has rational width
`Δs`, its whole velocity arc stays within distance `2L Δs` of its starting
velocity. Subdivide until

```
|v(start)| > 2L Δs.
```

The resulting disk excludes zero. Both the smooth velocity arc and its
straight chord lie in that convex disk, so they can deform into one another
without touching zero. Apply this to every interval. The resulting rational
polygon has exactly the same winding number as the smooth velocity curve.

All the samples are rational: integer powers of a rational point on the unit
circle remain rational, and negative powers use its conjugate. With rational
`r`, the disk inequality can be squared and its positive denominators cleared.
The implementation checks an inequality between integers. Signed crossings
of the final polygon use integer determinants too. No sine, cosine, floating
point, or numerical root solver enters these certificates.

Across the original slider ranges, **321 certificates use 86,702 edges** in
total. The deepest subdivision is 16. Needle's exact zero velocity is detected
at the first endpoint; it receives no tangent index. If a requested partition
cannot be certified within its depth limit, the program fails explicitly and
returns no count. Independent 24,000-sample floating-point angle sums agree
with all 321 integer answers, but those sums are only a cross-check.

The disk argument is the same principle used in the
[interactive winding study](winding.md): a deformation that avoids the
chosen point preserves winding. Here the chosen point is zero in velocity
space, and rational samples make the certification exact.

## Two checks that do not need the whole calculation

If one velocity term is longer than the sum of the others, shrink the shorter
terms to zero. The velocity cannot vanish during that deformation. Thus

```
140m > 245 + rn  implies tangent index m;
rn > 245 + 140m  implies tangent index −n.
```

For 2 / 25 at length 65, the backward speed is 1625, larger than
`245 + 280 = 525`, so its tangent index is −25 directly.

Also let `d = gcd(m−1, n+1)`, the number of rotational sectors. The velocity
satisfies the same rotation identity as the position:

```
z′(t + 2π/d) = exp(2πi/d) z′(t).
```

For a regular curve, a continuous choice of its direction angle gains
`2π/d + 2πk` across one sector, for some integer `k`. Repeating all `d`
sectors gives an index of **1 modulo d**. Crown's −15 is indeed 1 modulo 8;
Star's +6 is 1 modulo 5. The program checks this congruence for every regular
pair. Three supported regular pairs have tangent index zero: winding around
the center is still +1.

Those three pairs are **2 / 3, 4 / 7, and 6 / 11**. The
[two-lobe study](two_lobes.html) follows the first with a slider and compares
both angles. The [zero-turns note](zero_turns.md) certifies all three smooth
region censuses. In particular, 4 / 7 has tangent index zero while all its
region counts are nonnegative.

## The loop adds one clockwise turn

For Needle, keep `m = 8` and `n = 21`, and vary the inner length `r`. The exact
certificates give

```
r = 64.9: tangent index −20
r = 65:   velocity zero at the tip; no tangent index
r = 65.1: tangent index −21.
```

The [local lens](loop_birth.md) proves that a new loop is born at the tip as
the length passes 65. The tangent makes one extra clockwise turn after that
transition. This is a whole-curve index; it is not the center's winding,
which stays +1 throughout the lens's length range.

There are other cusp lengths farther below 65. To find them, multiply `v`
by `exp(21it)`:

```
v(t) = exp(−21it) [F(t) − 21r]
F(t) = 245 exp(22it) + 1120 exp(29it)
     = exp(29it) [1120 + 245 exp(−7it)].
```

The bracket stays in the right half-plane. A continuous argument is

```
Φ(t) = 29t + arg[1120 + 245 exp(−7it)].
```

Its derivative is strictly positive: the correction has absolute derivative
at most `7 × 245 / (1120−245) = 1.96 < 29`. Consequently `F` crosses the
positive real ray exactly 29 times in a full cycle, always upwards. One
crossing is at `t = 0`, with `F = 1365` and `r = 65`. The other 28 occur in
conjugate pairs, giving **14 other critical lengths**, strictly between
`125/3` and 65.

These lengths are distinct. Equal moduli force equal cosines of `7t`.
Combining `7s ≡ ±7t` with the fact that both `F(s)` and `F(t)` are positive
real gives `29s ≡ ±29t`, all modulo `2π`. Since 7 and 29 are coprime, only
the same time or its conjugate can share a critical length.

For regular `r`, count the upward crossings of `F` to the right of `21r`:

```
tangent index = (number of positive-real crossings with F(t) > 21r) − 21.
```

Thus the index starts at +8 for small lengths, drops by two at every paired
critical length, and drops by one at 65 to reach −21. Within the lens's
range, the earlier paired transitions are approximately

```
59.291961952, 61.247884511, 62.846157947, 64.029008367, 64.755194152.
```

These decimal locations use numerical bisection of the strictly increasing
phase. The exact integer method independently checks a rational length in
every predicted interval. The statement about all 14 paired transitions
comes from the phase argument, not a finite sample of lengths.

Every stationary point here is an ordinary cusp. At a zero velocity,

```
z″ = i exp(−21it) F′
z‴ = i exp(−21it) (F″ − 42iF′).
```

Now `F′ = i exp(29it)[32480 + 5390 exp(−7it)]` never vanishes, and its
argument derivative is at most `29 + 7 × 5390/(32480−5390) < 42`.
Therefore `Im(conjugate(z″) z‴) < 0`: the second and third derivatives are
independent. These statements classify stationary points as length varies;
they do not count all intersections of the position curve.

## Why the last transition really is isolated

The paired length nearest 65 is numerically about 64.755, but a short rational
bound already excludes every other stationary point for **64.9 ≤ r ≤ 65.1**.
Above 65 the backward velocity dominates, so consider `64.9 ≤ r ≤ 65`.

At a stationary point, `F(t) = 21r > 0`. Reduce `7t` modulo `2π` to
`θ ∈ [−π, π]`. The modulus identity gives

```
1 − cos θ = [1365² − (21r)²] / (2 × 245 × 1120).
```

For `r ≥ 64.9`, this is smaller than
`(0.15)²/2 − (0.15)⁴/24 ≤ 1 − cos(0.15)`, so `|θ| < 0.15`.
The bracket argument `φ = arg(1120 + 245 exp(−iθ))` then satisfies

```
|φ| ≤ 245 × 0.15 / [1120 + 245(1 − 0.15²/2)] < 0.03.
```

Write `7t = 2πk + θ` and `29t = 2πj − φ`. Eliminating `t` gives

```
|2π(7j − 29k)| = |7φ + 29θ| < 4.56 < 2π.
```

Hence `7j = 29k`, so `j = 29l`, `k = 7l`, and
`|t − 2πl| < 0.03/29`. Throughout this tiny interval,
`Im F′ = 5390 cos(22t) + 32480 cos(29t) > 0`. Its only real-axis crossing
is at `t = 2πl`, giving exactly `r = 65`.

The script checks the rational inequalities in this bound exactly. It
establishes one stationary event in this last length window; the original
lens proof remains a local statement about its one displayed crossing.
