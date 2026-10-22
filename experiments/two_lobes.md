# One crossing, two lobes

[Follow the point in the interactive study](two_lobes.html), or
[draw rhythms 2 / 3 in the sketchbook](../index.html?outer=2&inner=3).

![Rhythms 2 / 3 have a large counterclockwise gold lobe and a small clockwise blue loop. Their region winding counts are plus one and minus one. A close-up preserves the narrow loop's proportions. The whole curve winds once around the center, while its tangent makes zero net turns.](two_lobes.svg)

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
existence, uniqueness, and transversality.

## Why the direction makes zero net turns

The interactive study compares two angles. One is the direction from the
fixed center to the point. The other is the tangent: the direction of the
point's nonzero velocity. Both are counted continuously from the start,
allowing clockwise motion to subtract earlier counterclockwise motion.
Their net counts over a full orbit are **+1 and 0**, respectively.

The center's +1 follows from factoring

```
z(t) = exp(it) [245 + 140 exp(it) + 65 exp(−4it)].
```

The bracket's real part is at least `245 − 140 − 65 = 40 > 0`. Its argument
has a continuous choice between −π/2 and π/2 and returns to zero. Therefore
the continuous direction of `z(t)` is `t` plus that argument, a total of
one full turn. This explains the first browser counter without summing
sampled angles.

For the tangent, use `c = cos t`. Direct differentiation gives

```
x′(t) = −10 sin t P(c),     P(c) = 78c² + 56c + 5,
y′(t) = 10 R(c),           R(c) = −78c³ + 56c² + 83c − 28.
```

To count turns of the velocity, count its signed crossings of the upward
ray: `x′ = 0, y′ > 0`. Besides `sin t = 0`, the only possible times satisfy

```
c = (−28 ± √394)/78.
```

Both roots lie between −1 and 0. At a root of `P`, the identity

```
39 R(c) − (296c − 1372) = (−39c + 56) P(c)
```

gives `R(c) = (296c − 1372)/39 < 0`. These velocities point down, so they
do not meet the upward ray. They are nonzero as well.

There are consequently just two upward-ray crossings per orbit:

| Time | Velocity | Horizontal acceleration | Signed crossing |
| --- | --- | --- | --- |
| 0, counted once modulo 2π | (0, 330) | −1390 | +1, counterclockwise |
| π | (0, 230) | +270 | −1, clockwise |

Their sum is **zero**. This calculation also proves that the velocity never
vanishes: all possible zeros of its horizontal component have nonzero
vertical component. No cusp interrupts the angle count.

It gives a particularly simple continuous angle choice for the browser.
Let `a(t) = atan2(−x′(t), y′(t))`, the principal tangent angle measured from
up. In `0 < t < π`, choose its representative in `(0, 2π)`; in
`π < t < 2π`, choose its representative in `(−2π, 0)`. At 0, π, and 2π the
angle is zero. There are no interior upward-ray crossings to interrupt
either choice. Dividing by `2π` gives the displayed tangent counter. The
readouts round to two decimal places. The arrow itself uses the analytic
velocity, not a finite difference.

The whole curve's tangent count is not obtained by assigning +1 and −1 to
two smooth closed tangent paths. Closing either lobe at the crossing joins
different velocity directions, introducing a corner. The interactive
point always follows the original smooth branch through the crossing.

## The two lobe areas

For this curve, the signed-area density is

```
(x y′ − y x′)/2
  = [86550 + 102900 cos t − 31850 cos 4t − 9100 cos 5t]/2.
```

An antiderivative is

```
F(t) = 43275t + 51450 sin t − (15925/4) sin 4t − 910 sin 5t.
```

The little loop is traced between `t₀ = arccos c₀` and `2π−t₀`. Its
signed area is `F(2π−t₀) − F(t₀) ≈ −4466.989530` square drawing units.
The large lobe contributes approximately `+276371.833698`. Their sum is
exactly `86550π`. The large lobe has about 61.87 times the ordinary area
of the little one. Its positive contribution outweighs the small loop's
negative contribution even though the tangent's turns cancel.

## Reproducing the illustration and counters

The website remains dependency-free. Its mathematical functions are in
[two_lobes_math.js](two_lobes_math.js); the view is in
[two_lobes.js](two_lobes.js). The plot has equal scales on both axes, with
a separate magnified window onto the loop. The point starts at home, with
the full curve visible. The slider and five stops retrace it without an
animation. Start and Home occupy the same position but have different
center counts. Without JavaScript, a static SVG replaces the controls.

Run these independent checks:

```sh
python3 experiments/two_lobes.py
node experiments/two_lobes_check.js
```

The Python calculation checks the integer polynomial identity above,
the crossing's location and transversality, both lobe areas against
polygonal shoelace sums, and region labels against angle sums. Clearance
bounds transfer the three checked labels to the smooth curve. The Node
calculation compares both continuous browser angles with 100,001
independent accumulated-angle samples, tests either side of every tangent
argument cut, and independently integrates the little loop's area. These
are checks of the formulas; the complete crossing count is the algebraic
argument above. The earlier [integer tangent certificate](tangent_turning.py)
provides another independent proof of the zero tangent index.

To regenerate the standalone SVG using only Python's standard library:

```sh
python3 experiments/two_lobes.py --figure
```

The still drawing can be saved directly from the study. No browser tools,
plotting packages, or external network requests enter the website runtime.
