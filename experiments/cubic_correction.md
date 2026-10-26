# The first correction to the cubic

The [common cubic model](cubic_pockets.md) is a leading approximation.
Its parameter cusp does not exactly match the finite-scale orbital
contact boundary. The next Taylor terms explain the first discrepancy.

This addendum encloses those coefficients with rational interval
arithmetic. It also certifies four small finite-phase contact boxes,
then bounds their difference from a two-term prediction. It does not
classify all perturbed events or give a uniform numerical neighborhood
for the asymptotic expansions.

Run with the Python standard library:

```sh
python3 experiments/cubic_correction.py
```

## The five terms of weighted degree five

Keep the original physical height y, weight change `δ = a−a₀`, and
phase φ. As before, let A mean the earlier A′. The branch separation is

```
g = 2 A δ y + 2 C y³ + B φ
  + D y⁵ + E δ y³ + F δ² y + G δ φ + J y² φ
  + terms of weighted degree at least seven.
```

The weights of y, δ, φ are 1, 2, 3. Reflection requires the combined
power of y and φ to be odd, so the weighted degree is odd as well.
The displayed five monomials are all the possibilities at degree five.
Analyticity and the previously proved vanishing lower terms justify
the expansion; the list is not inferred from sampled values.

The new rational enclosures imply, with these deliberately looser
decimal bounds,

| Coefficient | Strict lower bound | Strict upper bound |
| --- | ---: | ---: |
| D | −0.000000003686902453 | −0.000000003686902452 |
| E | −0.0000433462083 | −0.0000433462082 |
| F | −6.275628730 | −6.275628728 |
| G | 78.737300156 | 78.737300157 |
| J | 0.00149416340585 | 0.00149416340586 |

The program prints tighter outward-rounded endpoints. Every proof
decision uses fractions, including the construction of these bounds.

## Invert height as a formal series

The base visits have orbit offsets `u = ±u₀` from π. Their cosine and
sine are already enclosed at the algebraic contact. Thus every base
Fourier factor is an integer power of `c ± i s`; no numerical sine or
cosine decides a coefficient bound.

For rational Y, M, N, substitute

```
y = Y h,     δ = M h²,     φ = N h³,
u(h) = u_base + t₁h + t₂h² + ... + t₅h⁵.
```

An exponential series `exp(i p(h)) = Σ e_n h^n`, with p(0) = 0,
has the exact coefficient recurrence

```
e₀ = 1,
n e_n = i Σ from k=1 to n of k p_k e_(n−k).
```

Compose the five orbital Fourier terms with the time series.
At each order n, the unknown t_n enters the height coefficient only
through the nonzero base vertical velocity. Divide the remaining
height residual by that velocity to obtain t_n. This is formal series
reversion of the analytic height chart, so the calculated coefficients
are Taylor coefficients of the actual branches.

Subtract the two horizontal jets. The fifth coefficient is

```
D Y⁵ + E M Y³ + F M² Y + G M N + J Y² N.
```

Five choices isolate D, E, F, G, J. The E and F extraction uses
M = ±1/100 to reduce interval dependency when subtracting the larger
F contribution. Three additional substitutions check reconstruction.
Every inverted height coefficient must contain its target; the
separation's even coefficients and its linear coefficient must contain
zero. Its cubic coefficient is checked against the independent earlier
enclosures of A, C, B.

After each interval operation, rational endpoints are rounded outward
to a grid of spacing 2⁻¹⁰⁰. This limits integer growth without losing
the enclosure. Positive cube roots use integer binary search and
outward dyadic endpoints, rather than floating-point root functions.
The initial contact box remains the main source of uncertainty.

## Contact weight and height, one term further

For this calculation use the **physical** phase scaling `φ = h³`,
`y = h v`, `δ = h² k`. These v and h are not the normalized height
and arbitrary scale of the interactive page. Write

```
R(v,k) = D v⁵ + E k v³ + F k² v + G k + J v².
```

The two rescaled tangency equations are

```
2 A k v + 2 C v³ + B + h² R(v,k) + O(h⁴) = 0,
2 A k   + 6 C v²     + h² R_v(v,k) + O(h⁴) = 0.
```

The earlier nonsingular implicit system gives analytic even functions
`v(h) = v₀ + v₂h² + O(h⁴)` and
`k(h) = k₀ + k₂h² + O(h⁴)`, with

```
v₀³ = B/(4C),     k₀ = −3 C v₀²/A.
```

At the limiting contact the first equation has zero v derivative.
Consequently its next coefficient determines k₂ directly, then the
second determines v₂:

```
k₂ = −R(v₀,k₀)/(2 A v₀),
v₂ = −[2 A k₂ + R_v(v₀,k₀)]/(12 C v₀).
```

The rational interval calculation proves

```
0.14737606110 < k₂ < 0.14737606113,
−88.15903154 < v₂ < −88.15903152.
```

Thus, for signed phase approaching zero,

```
a_contact = a₀ + k₀ |φ|^(2/3) + k₂ |φ|^(4/3) + O(φ²),
y_contact = v₀ cbrt(φ) + v₂ φ + O(|φ|^(5/3)).
```

The first correction to weight is positive. The first correction to
positive-phase height is negative. Their signs describe sufficiently
small phases, without claiming an explicit uniform range.

## Four finite prediction errors, enclosed separately

Floating-point Newton supplies only initial candidate centers.
Four rational midpoint Newton steps refine each suggestion. The existing
three-variable interval contraction test then certifies a unique
quadratic tangency in each box of radius **10⁻²⁰**. The largest
contraction norm is below 1.4 × 10⁻¹⁵. The proof function and the
frozen atlas certificate are reused without modification.

Subtract the interval-valued two-term prediction from each certified
contact. This gives genuine finite error enclosures, including the
uncertainty in a₀ and all four asymptotic coefficients. The following
are looser bounds than those printed by the program:

| Positive phase | Weight error, after two terms | Height error, after two terms |
| ---: | ---: | ---: |
| 0.001 | (3.8054567 × 10⁻⁸, 3.8054570 × 10⁻⁸) | (0.00084701528, 0.00084701530) |
| 0.0001 | (3.739633 × 10⁻¹⁰, 3.739638 × 10⁻¹⁰) | (0.00001861474, 0.00001861475) |
| 0.00001 | (3.7253 × 10⁻¹², 3.7257 × 10⁻¹²) | (0.0000004027647, 0.0000004027649) |
| 0.000001 | (3.7014 × 10⁻¹⁴, 3.7314 × 10⁻¹⁴) | (0.00000000868530, 0.00000000868534) |

At these four specified phases the weight error lies between
`0.03 φ²` and `0.05 φ²`, and the height error between
`80 φ^(5/3)` and `90 φ^(5/3)`. Those finite comparisons do not
prove those constants work on a continuous phase interval.
Reflection supplies the corresponding negative-phase statement,
with unchanged weight and reversed height.

## The mirror pocket gets its own next coefficient

At φ = 0, integrate the gap from height zero to the positive root.
Its first height scale is `L sqrt(δ)`, with `L² = −A/C`.
Moving that root has no contribution at the next order because the
leading integrand vanishes at the endpoint. Therefore each pocket has

```
area = K₀ δ² + K₁ δ³ + O(δ⁴),
K₀ = −A²/(2C),
K₁ = D L⁶/6 + E L⁴/4 + F L²/2.
```

No square root is needed to bound K₁: substitute the rational interval
expression for L². The calculation proves

```
−1704971.255 < K₁ < −1704971.254.
```

The negative correction explains the earlier numerical area ratios
approaching one from below. A fresh check using numerical roots and
Simpson integrals at two resolutions gives:

| δ | Actual numerical area / (K₀ δ² + K₁ δ³) |
| ---: | ---: |
| 0.001 | 1.0000853243 |
| 0.0003 | 1.0000076721 |
| 0.0001 | 1.0000008523 |
| 0.00003 | 1.0000000767 |

The coefficient enclosure is exact. These area quadratures are
numerical checks, not certified finite area intervals.

The program also checks 271 primitive cases: outward rounding with
negative numbers, integer cube-root boundaries, exponential jets against
independent factorial products, and rejection of nonzero constant phase.
It checks both height inversions at every computed coefficient, reflection
zeros, the known cubic term, and degree-five reconstruction. No new
controls or drawing runtime dependencies are needed for this addendum.
