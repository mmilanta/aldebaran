# One density, two asymptotic goals

For shifted parabolas, the placement with the largest total pocket area
need not make its smallest pocket as large as possible. The exact
[finite compromise](parabolic_tradeoff.md) already shows that even
for quadratic intercepts. But as more curves fill a fixed interval,
the same curvature density asymptotically optimizes **both** goals.

This extends the [total-area density theorem](shifted_parabolas.md#a-dense-arrangement-favors-stronger-curvature)
to the smallest of **all** bounded faces, including the longer-run
quadrilaterals. It is an asymptotic result, not a general finite
maximin or compromise classification.

## Statement and hypotheses

Let h be C² on [a,b], with

```
0 < c ≤ h″(p) ≤ C.
```

Choose m+1 distinct slope labels, including fixed endpoints a,b, for
`Xₚ(Y)=Y²/2−pY+h(p)`. They make m gaps and m(m−1)/2 bounded
pockets. For m≥2, let S_m be their smallest area and S_m* the largest
possible value over placements. Set

```
L = b−a,
w(p) = h″(p)^(2/3),       W = ∫[a,b] w(p) dp.
```

Then

```
lim[m→∞] m³ S_m* = W³/4.
```

The equal-w-mass placement, `∫[p_j,p_{j+1}]w=W/m` for every gap,
attains this leading constant. The earlier total-area result says
the same placement has deficit `W³/(24m²)+o(m⁻²)`. Thus the smallest
area's leading constant is six times the total deficit's, with one
extra inverse power of the gap count.

This does not say that either finite optimizer is unique or that
the two finite optimizers coincide. The [two-choice example](two_choices.md)
still has two global best insertions under these same smoothness and
positive-curvature hypotheses.

## Every face has a curvature sandwich

The [run classification](shifted_parabolas.md#the-band-is-still-all-the-bounded-faces)
names every bounded face by a consecutive interior run i,…,j. Let

```
α = p_i−p_{i−1},       β = p_{j+1}−p_j,
H = p_j−p_i.
```

For a singleton run i=j, H=0. Let x,z be the secants on its two
gaps. Its triangular face has area

```
F = αβ(z−x)² / [2(α+β)].
```

For a longer run, H>0. Let y be the secant from p_i to p_j, with
x,z the two outer-gap secants. Set A=y−x>0 and B=z−y>0. The
quadrilateral's area is

```
F = α²β A² / [2(α+H+β)(α+H)]
  + αβ AB / (α+H+β)
  + αβ² B² / [2(α+H+β)(H+β)].
```

Here every coefficient is positive. One direct derivation subtracts
an affine intercept and translates slope labels, putting the first
two selected intercepts at (0,0) and (α,0). The four face vertices
in the straightened (U,Y) plane then have coordinates

```
(0, H A/(α+H)),
(0, [(H+β)A+βB]/(α+H+β)),
(−αt, t),       t=A+βB/(H+β),
(−αA, A).
```

Their shoelace area is the displayed positive quadratic form. The
common horizontal slide `X=U+Y²/2` preserves this area exactly.

Let c_I,C_I be the minimum and maximum of h″ on the run's outer
interval I=[p_{i−1},p_{j+1}]. Subtracting `c_I p²/2` leaves a convex
intercept law, while subtracting `C_I p²/2` leaves a concave one.
The selected secant differences therefore obey

```
c_I(α+H)/2 ≤ A ≤ C_I(α+H)/2,
c_I(H+β)/2 ≤ B ≤ C_I(H+β)/2.
```

Substitution into the positive quadratic form gives

```
c_I² F₀ ≤ F ≤ C_I² F₀,
F₀ = αβ(α+2H+β)/8.
```

The singleton has the same bounds with H=0, using
`c_I(α+β)/2≤z−x≤C_I(α+β)/2`. Thus the sandwich covers **every**
bounded pocket, not only neighboring triangles.

## An upper bound for arbitrary placements

Let ω(t) be the modulus of continuity of w on [a,b]. Consider a
singleton triangle with neighboring gaps α,β and interval I. By
the sandwich and `αβ≤(α+β)²/4`,

```
F^(1/3) ≤ (max_I w)(α+β)/32^(1/3).
```

Fix any η>0. Mark the gaps longer than η and discard the singleton
triangles touching them. There are at most L/η marked gaps and
at most 2L/η discarded triangles. At least
`m−1−2L/η` triangles remain.

Every remaining triangle's two-gap interval has length at most 2η.
For either gap J inside that interval,

```
(max_I w)|J| ≤ ∫[J]w + ω(2η)|J|.
```

Every gap is counted in at most two of the remaining triangles.
Since the smallest area S_m cannot exceed any such triangle,

```
(m−1−2L/η) S_m^(1/3)
    ≤ [2W+2Lω(2η)]/32^(1/3),

S_m ≤ [W+Lω(2η)]³ / [4(m−1−2L/η)³]
```

once the denominator is positive. This holds for every placement,
including ones with large gaps; no vanishing-mesh assumption was
silently imposed on an unknown optimizer. First let m grow, then
let η decrease to zero. Uniform continuity proves
`limsup m³S_m*≤W³/4`.

For completeness, a finite maximum exists. The value S_m extends
continuously by zero to partitions with a collapsed gap: some
adjacent triangle tends to zero by the global curvature upper
bound. Interior values are positive. Compactness of the closed
ordered simplex then places a maximizer in its interior. The
asymptotic upper bound itself did not require this existence fact.

## Equal curvature mass bounds all the pockets below

For the equal-w-mass placement, every gap g satisfies

```
W/(m C^(2/3)) ≤ g ≤ W/(m c^(2/3)).
```

The mesh is therefore O(1/m). If a run has k=j−i+1 interior
labels, its middle span H contains k−1 gaps. If g_min is the
smallest gap in its outer interval, then

```
F₀ ≥ k g_min³/4.
```

Choose a fixed integer K≥(C/c)². For every run with k>K, the
global lower curvature bound and global gap lower bound give

```
F ≥ c² k [W/(m C^(2/3))]³/4
  = k(c/C)² W³/(4m³)
  ≥ W³/(4m³).
```

Only runs of at most K labels remain. Their outer intervals have
length at most (K+1) times the mesh, hence tend uniformly to zero.
On such an interval the positive continuous curvature has
`c_I/C_I→1` uniformly. Every gap there has length at least
`W/(m C_I^(2/3))`. Thus each of these short-run pockets obeys

```
F ≥ k(c_I/C_I)² W³/(4m³)
  ≥ (1−o(1)) W³/(4m³).
```

Together the long and short cases cover the entire face list.
The smallest area of this particular placement is at least
`(1−o(1))W³/(4m³)`, proving the matching lower limit and theorem.

## The finite goals still differ

For cubic intercepts h(p)=p³/3 on [1,3], choose these five rational
slope labels:

```
1, 33/20, 54/25, 521/200, 3.
```

Their six pockets have smallest area
`1482792649/3000000000≈0.494264216333` and total area
`1223303885873/240000000000≈5.097099524471`.

The [unique total-area optimum](shifted_placement.svg) instead has
total approximately 5.097121872422 and one singleton pocket of area
at most 0.491225750752. The command freshly repeats the rational
shooting proof for this four-gap optimum, then bounds that singleton
with the exact positive cubic triangle polynomial. The rational
competitor's **smallest** pocket exceeds that upper bound, while its
total is below the optimum's certified lower bound.

Thus this exact finite arrangement trades a little total for a
larger minimum. It is a comparison, not a claimed finite maximin
optimizer. The shared asymptotic density does not identify the
finite compromise.

## Exact controls

For cubic intercepts on [1,3], the limit is

```
W³/4 = (27/125)(243^(1/3)−1)³ ≈ 31.082084469912.
```

Selected 96-bit rational controls near the equal-density nodes give:

| Gaps m | m³ × smallest area, approximately |
| ---: | ---: |
| 2 | 32.864922911262 |
| 4 | 31.263718886550 |
| 8 | 31.116507868051 |
| 16 | 31.089724794319 |
| 32 | 31.083891003276 |
| 128 | 31.082192914111 |

The theorem concerns the exact equal-density sequence. These are
finite rational illustrations; their rounded decimals do not define
outward bounds or a literal all-m sequence. They are not claimed
to maximize the smallest area at their finite counts.

```sh
python3 experiments/shifted_maximin.py
```

Only the standard library is needed. It checks 29 complete clipped
arrangements and their 342 exact face polynomials, including quadratic,
cubic, quartic, and discrete-convex intercept data. Smooth examples
exercise the local curvature sandwich. Eight rational density
placements check **all 10,798 faces**, not only the singleton ones.
Four invalid run-index controls also pass. The continuous argument
above proves the all-family limit; these finite checks independently
audit its face formula and chosen examples.

The [finite four-curve follow-up](cubic_maximin.md) now solves the cubic
case on [1,3]: its unique largest-minimum placement makes all three
pockets equal. A general finite smallest-pocket optimizer and a
shifted-family compromise curve remain open here. The asymptotic result
above identifies their shared leading density as the count grows.
