# One crossing, two lobes

[Draw rhythms 2 / 3](../index.html?outer=2&inner=3).

This is a quieter example after all the overlapping regions. The curve has
one transverse crossing and two bounded regions. The region labels are +1
and −1, and the tangent index is zero, while the center still counts as +1.
The region labels agree in the exact sampled census and in an independent
run of the rational intersection method with `IntersectionCertificate(2,3,1024)`.
Here is a separate hand proof of the **single crossing**.

## Locate the reflected crossing

For this pair,

```
z(t) = 245 exp(it) + 140 exp(2it) + 65 exp(−3it).
y(t) = 10 sin t [31 + 28 cos t − 26 cos²t].
```

The two reflected times `−t` and `t` meet when their imaginary coordinates
vanish. The only root of the bracket with `−1 < cos t < 1` is

```
c₀ = (14 − √1002)/26 ≈ −0.679014753.
```

It gives one pair of distinct times, with crossing coordinate

```
x = 260c₀³ + 280c₀² + 50c₀ − 140 ≈ −126.251131524,
y = 0.
```

The zeros from `sin t = 0` are the distinct ordinary points at times 0 and
π; each equals its own reflection and supplies no additional crossing.

## Exclude every off-axis crossing

Suppose `z(s+h) = z(s−h)` for distinct points of the parameter circle.
Choose lifts with `0 < h < π`, and put `c = cos h`. Subtract and divide by
`2i sin h`, then multiply by `exp(3is)`:

```
245 exp(4is) + 280c exp(5is) − 65(4c²−1) = 0.
```

When `sin s = 0`, this is the reflected pair just found. Otherwise
`sin 5s` cannot vanish: the imaginary part would force `sin 4s = 0` too,
which, since 4 and 5 are coprime, would give `sin s = 0`.

Put `a = cos s`, `b = a²`, and use

```
U₃ = sin 4s / sin s = 8a³ − 4a,
U₄ = sin 5s / sin s = 16b² − 12b + 1.
```

The imaginary and real parts give

```
c = −(7/8) U₃/U₄,
13(4c²−1)U₄ = 49.
```

Here `0 ≤ b ≤ 1`, `c² ≤ 1`, and `U₄ ≥ −5/4` by completing the square.
If `U₄ ≤ 0`, the second equation's left side is at most `65/4 < 49`.
If `0 < U₄ ≤ 1`, it is at most `39 < 49`. Therefore `U₄ > 1`, forcing
`b > 3/4` because `U₄−1 = 4b(4b−3)`.

Eliminating `c` from the two equations yields

```
P(b) = 3328b⁴ − 7540b³ + 5620b² − 1537b + 62 = 0.
```

But for `x = b−3/4` with `0 ≤ x ≤ 1/4`,

```
P(b) = 3328x⁴ + 2444x³ − 113x² − (859/4)x − 919/16.
```

In that interval, `3328x⁴ ≤ 52x` and `2444x³ ≤ (611/4)x`. Hence

```
P(b) ≤ −10x − 113x² − 919/16 < 0,
```

a contradiction. There is no off-axis crossing.

## Check transversality

At `t₀ = arccos c₀`, differentiating the factored vertical coordinate gives

```
y′(t₀) = 10 sin²t₀ (52c₀ − 28) < 0.
```

Writing `x(t) = X(cos t)`, the same quadratic relation simplifies

```
X′(c₀) = 1400c₀ + 980 > 0,
```

since `−7/10 < c₀ < −6/10`. Thus `x′(t₀) ≠ 0` too. The two branch
velocities at `−t₀` and `t₀` have opposite horizontal components and the
same nonzero vertical component, so they are transverse. One crossing gives
two bounded regions by the planar graph count.

This argument needs no numerical root isolation or enumeration of parameter
pairs. The decimals above locate the crossing; the algebra proves its
existence, uniqueness, and transversality. A small illustration of the two
opposite-turning lobes could make a friendly starting point for a future visit.
