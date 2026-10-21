# One turn, but negative area

The original sketchbook keeps its arm lengths at 245, 140, and 65. Those
lengths guarantee that every curve winds once around the center. Surprisingly,
two of the 322 rhythm pairs have **negative signed area**.

![Two orbital curves colored by local winding count. Garden has positive gold regions, including overlapping regions counted more than once. Rhythms 2/25 have a positive gold center surrounded by negative blue loops; several blue loops overlap at the left. The total signed areas are 142300 pi and negative 6400 pi.](signed_area.png)

Color here records local winding count, rather than time as it does in the
sketchbook. A region enclosed twice in the positive direction counts twice;
a region enclosed in the negative direction subtracts from the total.
The white point is the center. The dotted circle has radius 40.
Signs use mathematical coordinates, with the imaginary axis pointing upward;
the sketchbook's screen coordinates point downward.

## Why the center always counts as one

Measure the point from the center and factor out the first arm's turn:

```
z(t) = exp(it) [245 + 140 exp(i(m−1)t) + 65 exp(−i(n+1)t)].
```

The expression in brackets has real part at least `245 − 140 − 65 = 40`.
It stays strictly in the right half-plane. Its argument is therefore continuous,
periodic, and between `−π/2` and `π/2`, contributing no net turn. The factor
`exp(it)` contributes exactly one.

Also, by the triangle inequalities,

```
40 ≤ |z(t)| ≤ 450.
```

The curve never enters the central disk of radius 40. Every point strictly
inside that disk has winding count one too: subtracting a fixed point `q`
from the curve leaves the bracket's real part at least `40 − |q| > 0`.

## Signed area adds the turns

For a closed parametrized curve, define

```
A = (1/2) ∫ [x(t)y′(t) − y(t)x′(t)] dt
  = (1/2) Im ∫ conjugate(z(t)) z′(t) dt,
```

over a full cycle. For a simple curve this is its area with an orientation
sign. With crossings, it weights each region by its local winding count.
It is not the area obtained by painting every visible region once.

The three integer frequencies `1`, `m`, and `−n` are distinct in the current
slider ranges. All mixed Fourier terms integrate to zero over `0 ≤ t ≤ 2π`.
Only each arm's squared length times its frequency survives:

```
A = π(245² + 140²m − 65²n)
  = π(60025 + 19600m − 4225n).
```

For `m ≥ 3`, even `n = 25` gives a positive coefficient, at least 13200.
For `m = 2`, the coefficient becomes negative only at `n = 24, 25`:

| Outer / inner | Signed area |
| --- | --- |
| 2 / 24 | −2175π |
| 2 / 25 | −6400π |

There are no zero-area pairs in the current ranges. The center's winding count
remains positive in both negative-total drawings; sufficiently large or
multiply counted negative regions elsewhere outweigh it.

## Checking the drawing's actual polygon

The canvas draws 24,000 straight segments. For `N` uniformly spaced samples,
with `N > m+n`, discrete Fourier orthogonality gives an exact polygon identity:

```
A_N = (N/2) [245² sin(2π/N) + 140² sin(2πm/N) − 65² sin(2πn/N)].
```

This tends to the continuous area as `N` increases. The elementary bound
`|sin u − u| ≤ |u|³/6` gives

```
|A_N − A| ≤ (π/6)(245² + 140²m³ + 65²n³)(2π/N)².
```

[The standard-library calculation](signed_area.py) evaluates the full
24,000-vertex shoelace sum and winding count for all 322 pairs. In this run,
the greatest difference between the direct shoelace sum and the discrete
Fourier formula was below `7 × 10⁻¹⁰` square drawing units. The greatest
polygon-versus-continuous area difference was about 2.372 square units.
These are floating-point checks of the identities above, not their proofs.

The same calculation finds that **109 pairs reach radius 40 exactly**. To reach
that lower bound, both smaller arms must oppose the first. If
`d = gcd(m−1, n+1)`, this is possible exactly when both `(m−1)/d` and `(n+1)/d`
are odd; then `t = π/d` is one such time. If either reduced rhythm is even,
the two required odd half-turns are incompatible.

The illustration uses oriented crossings of the sampled polygon at a
1200-by-1200 grid of pixel centers. It approximates the region boundaries;
the formula gives the exact continuous signed area. Recreate it with
[plot_signed_area.py](plot_signed_area.py), which needs NumPy and Matplotlib.
That program cross-checks the local colors with an independent sum of argument
changes around test points, including a point in every displayed color.
Those optional plotting tools are not dependencies of the website or the
standard-library calculation.
