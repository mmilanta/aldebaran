# The middle pocket still matters

For **five** cubic-intercept parabolas on the fixed slope interval
[1,3], the largest smallest pocket has a unique placement. Its three
interior labels are approximately

```
1.648370786436389,
2.160107434272252,
2.603183034847801.
```

The three triangular pockets have the same area,
**0.494437008327896680…**. All three remaining pockets are larger.
The total area is about **5.097115943716227**.

This resolves the five-curve case left by the earlier
[finite comparison](shifted_maximin.md#the-finite-goals-still-differ).
The [four-curve result](cubic_maximin.md) has an exact cubic answer
and a drawing. Here the proof uses a rational contraction box and a
simpler global concavity argument. Both concern complete finite
arrangements of `Xₚ(Y)=Y²/2−pY+p³/3`; neither is a classification
of every finite count or the whole compromise frontier.

## A very small compromise

The [largest-total placement](shifted_placement.md) uses interior
labels about 1.650240766475, 2.162146131438, and 2.603606875834.
Its total is about 5.097121872422, and its minimum about
0.491225750751.

Moving all three labels to the new maximin placement increases the
minimum about **0.653723%**, while total area falls about
**0.000116315%**. These are percentages of the respective minimum
and total at the largest-total arrangement. They have different
baselines. The total falls only about 0.000005928706 in absolute area.

Every pocket is accounted for:

| Interior run | Type | Area, approximately |
| --- | --- | ---: |
| 1 | Triangle | 0.494437008328 |
| 1,2 | Quadrilateral | 1.026207385171 |
| 1,2,3 | Quadrilateral | 1.585952441431 |
| 2 | Triangle | 0.494437008328 |
| 2,3 | Quadrilateral | 1.001645092131 |
| 3 | Triangle | 0.494437008328 |

The table's decimals are readouts. Rational interval bounds in the
[record](cubic_five.json) strictly separate the three longer-run
areas from the common triangle area.

## Three triangles give a global upper bound

Write the labels as `1<x<y<z<3`, and put

```
T(a,p,b) = (p−a)(b−p)(b−a)(a+p+b)²/18,
T₁=T(1,x,y),   T₂=T(x,y,z),   T₃=T(y,z,3).
```

Each is an actual face by the consecutive-run classification. The
smallest of all six faces cannot exceed the smallest of these three.
Every log Tᵢ is concave on the open ordered simplex: it is a sum of
logarithms of positive affine functions of x,y,z.

More precisely, log T₁ is strictly concave in (x,y): the factors
`x−1` and `y−1` already give a negative definite Hessian on those
two coordinates. Similarly log T₃ is strictly concave in (y,z).
Thus, for any positive weights λ₁,λ₂,λ₃,

```
G = λ₁ log T₁ + λ₂ log T₂ + λ₃ log T₃
```

is strictly concave in all three coordinates. A point with zero
gradient is its unique global maximum. If the three areas are also
equal there, the same weighted-log argument as in the four-curve
proof bounds every challenger's smallest triangle by that area.

We only need to prove that such a point exists with **positive**
weights and that the other three faces do not undercut its triangles.

## A rational five-dimensional certificate

Normalize `λ₃=1−λ₁−λ₂`. For a triangle define the log-area partials

```
L(a,p,b) = −1/(p−a) − 1/(b−a) + 2/(a+p+b),
M(a,p,b) =  1/(p−a) − 1/(b−p) + 2/(a+p+b),
R(a,p,b) =  1/(b−p) + 1/(b−a) + 2/(a+p+b).
```

They differentiate with respect to a,p,b respectively. The five
equations in `(x,y,z,λ₁,λ₂)` are

```
T₁−T₂ = 0,
T₂−T₃ = 0,
λ₁ M(1,x,y) + λ₂ L(x,y,z) = 0,
λ₁ R(1,x,y) + λ₂ M(x,y,z) + λ₃ L(y,z,3) = 0,
λ₂ R(x,y,z) + λ₃ M(y,z,3) = 0.
```

The last three equations are exactly the three coordinates of ∇G.
Although G uses logarithms, all five equations and their derivatives
are rational functions. Their denominators stay strictly positive
on the certified box.

The [standard-library program](cubic_five.py) proposes a dyadic
rational center by Newton steps, then independently certifies the
closed box with radius `2⁻⁹⁶` in each of the five coordinates.
The proposal alone makes no proof decision. Rational interval
automatic differentiation encloses the complete Jacobian DF on
that box. Let R₀ be the exact inverse of DF at its center c. For

```
H(q) = q−R₀F(q),
```

the program proves both

```
sup_box ||I−R₀DF||∞ < 7.48 × 10⁻²⁸,
H(box) lies strictly inside box.
```

The contraction theorem therefore supplies a unique root of F in
the box. The Jacobian inverse is nonsingular, so a fixed point of H
is exactly a zero of F. All node intervals are separated and
interior, and all three weight intervals are positive. The weights
are approximately

```
λ₁ = 0.496343048058099,
λ₂ = 0.000762037190085,
λ₃ = 0.502894914751817.
```

The middle triangle has a very small positive weight. It is still
an active constraint; dropping it is not the certified optimization
problem. The equations prove that all three triangles have exactly
the same area, even though the node bounds and displayed decimals
are finite.

## Check every remaining face

Evaluate the [positive four-line face formula](shifted_maximin.md#every-face-has-a-curvature-sandwich)
on the node box. For cubic intercepts its secant differences factor:
on a run i,…,j with i<j,

```
A = (pⱼ−pᵢ₋₁)(pᵢ₋₁+pᵢ+pⱼ)/3,
B = (pⱼ₊₁−pᵢ)(pᵢ+pⱼ+pⱼ₊₁)/3.
```

Their interval bounds and the positive face formula prove each
longer-run area strictly greater than the triangle area's upper
bound. The candidate's actual minimum is therefore that common
triangle area. The preceding global support bounds every other
placement by it and forces equality only at this candidate.
Collapsed gaps on the boundary give a zero triangular area.
This completes the global finite maximin proof for all six faces.

## Reproduce

```sh
python3 experiments/cubic_five.py
python3 experiments/cubic_five.py --write
```

No external packages are used. The command repeats the rational
contraction, checks **24 complete clipped arrangements and 144 exact
face formulas**, and certifies compatible boxes at **five precisions**,
including both supported precision limits, 48 and 192 bits. A nearby
nonroot is rejected by the strict self-map test. Five invalid precision
controls are also rejected.

The JSON stores all six face enclosures, positive weight intervals,
the exact dyadic root center and radius, outward-rounded self-map
offsets, and a rational contraction-norm upper bound. Outward rounding
uses extra bits at higher requested precisions, preserving the strict
self-map inequalities. The default common area enclosure has width
less than 9×10⁻²⁹. The total-area comparison freshly repeats the
earlier monotone shooting certificate.
