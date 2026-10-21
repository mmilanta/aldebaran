# Why only Needle stops

The modular polynomial calculation in [stationary_points.py](stationary_points.py)
classifies the 322 rhythm pairs exactly. Here is a second route, using only
reductions at 7 and 13, followed by two triangle equalities. It explains why
nearly all the pairs can be ruled out together.

These arguments use the current slider ranges, `2 ≤ m ≤ 15` and `3 ≤ n ≤ 25`.
They do not claim a classification for arbitrary rhythms or different arm lengths.

## From motion to a polynomial

Relative to the drawing's center, the point is

```
z(t) = 245 exp(it) + 140 exp(imt) + 65 exp(−int).
```

Set `w = exp(it)`. Dividing the derivative by `5i` and multiplying by `wⁿ`
shows that a point at rest is exactly a unit-circle root of

```
F(w) = 28m w^(m+n) + 49 w^(n+1) − 13n.
```

Put `N = m+n` and `K = n+1`. The reciprocal of a degree-N polynomial is
`F*(w) = wᴺ F(1/w)`.

## A small algebraic tool

If an integer polynomial has a root `α` on the unit circle, the primitive
integer minimal polynomial `H` of `α` is reciprocal up to sign. Indeed,
`1/α = conjugate(α)` is also a root, so `H` and `H*` have a common root;
irreducibility and primitiveness give `H* = ±H`. In particular, the leading
and constant coefficients of `H` agree up to sign. Gauss's lemma lets us write
`F = HG` with integer `G`.

This has three useful consequences for reduction modulo a prime `p`:

1. **A nonzero constant rules out a reciprocal factor.** If `F mod p` is a
   nonzero constant, both factors reduce to nonzero constants. But `H` has
   equal leading and constant coefficients up to sign. Its constant coefficient
   would be nonzero modulo `p`, so its leading coefficient would be nonzero
   too, preserving its positive degree. Contradiction.

2. **Unit leading coefficients preserve the factor's degree.** If the leading
   coefficient of `F` is nonzero modulo `p`, the same is true for `H` and `G`.
   For reciprocal `H`, its constant coefficient is then nonzero too. Its
   reduction is a positive-degree reciprocal factor of the reduced polynomial.
   In particular, if `F` and `F*` reduce to coprime polynomials, no such `H`
   exists.

3. **A single prime at both ends can rule out a monomial reduction.** Suppose
   the leading and constant coefficients of `F` are each divisible by `p`
   exactly once, and `F mod p` is a nonzero monomial. If `H` had leading and
   constant coefficients not divisible by `p`, its reduction would have both
   ends nonzero and could not divide a monomial. Thus both are divisible by
   `p`, exactly once. The leading and constant coefficients of `G` are then
   both nonzero modulo `p`. Since `G mod p` divides a monomial and has a
   nonzero constant coefficient, it must be constant; since its degree is
   preserved, `G` itself is constant. Consequently `F` would be reciprocal
   up to sign. If it is not, there is no unit-circle root.

The minimal polynomial need not have all its roots on the unit circle.
Reciprocity alone is what these arguments use.

## First sieve: 7

If `7` does not divide `n`, then `F mod 7` is the nonzero constant `−13n`.
Consequence 1 eliminates **280 pairs** immediately.

The remaining inner rhythms are `n = 7k`, with `k = 1, 2, 3`. Divide `F` by 7:

```
f(w) = 4m wᴺ + 7 wᴷ − 13k.
```

If `7` divides `m`, the reduction is again a nonzero constant, eliminating
**6 more pairs** (`m = 7, 14`). Otherwise its leading and constant coefficients
are nonzero modulo 7. Write `a = 4m` and `c = 13k`. The reduction is
`a wᴺ − c`, with reciprocal `a − c wᴺ`. A linear combination gives

```
c(a wᴺ − c) + a(a − c wᴺ) = a² − c².
```

Unless `a² = c² mod 7`, these polynomials are coprime, so consequence 2 excludes
the pair. The necessary condition is `m = ±2k mod 7`. It eliminates **24 pairs**
and leaves just these twelve:

| Inner rhythm | Possible outer rhythms |
| --- | --- |
| 7 | 2, 5, 9, 12 |
| 14 | 3, 4, 10, 11 |
| 21 | 6, 8, 13, 15 |

## Second sieve: 13

Return to `F`. For `m ≠ 13`, its leading coefficient is nonzero modulo 13.
The reduction is

```
wᴷ (28m w^(m−1) + 49).
```

A reciprocal factor with nonzero constant coefficient must divide the
binomial `B(w) = 28m w^(m−1) + 49`, and also its reciprocal. Combining those
binomials gives the constant `(28m)² − 49²`. Thus a necessary condition is
`m² = 25 mod 13`, or `m = 5, 8` in the current ranges. This eliminates **9 pairs**.

The exceptional outer rhythm `m = 13` appears only with `n = 21` in our table.
Here

```
F(w) = 364 w³⁴ + 49 w²² − 273.
```

Both end coefficients contain exactly one factor of 13; the middle coefficient
is not divisible by 13. The reduction is the monomial `49 w²²`. Since `364`
and `273` differ, `F` is not reciprocal up to sign. Consequence 3 eliminates
**this pair**.

Only `(5, 7)` and `(8, 21)` remain.

## Two triangles, two different outcomes

For **(5, 7)**, divide by 7:

```
20 w¹² + 7 w⁸ = 13.
```

On the unit circle, `|13 − 7w⁸| ≤ 20`. Equality is necessary, and it forces
`w⁸ = −1`; the equation then forces `w¹² = 1`. But these imply both
`w²⁴ = −1` and `w²⁴ = 1`. Impossible. This eliminates the **321st pair**.

For **Needle, (8, 21)**, dividing by 7 gives

```
32 w²⁹ + 7 w²² = 39.
```

Now `32 + 7 = 39`. Equality in the triangle inequality forces both
`w²⁹ = 1` and `w²² = 1`. Since `gcd(29, 22) = 1`, this gives **w = 1**.
It really is a root. Thus Needle has exactly one stationary point per cycle,
at `t = 0` modulo `2π`.

At that time, the second and third derivatives are

```
z″(0) = −37870
z‴(0) = 530040 i.
```

They are linearly independent over the reals, so the point is an ordinary cusp.
Locally, measured from the tip,

```
x(t) − x(0) = −18935 t² + O(t⁴)
y(t) − y(0) =   88340 t³ + O(t⁵).
```

The drawing approaches along the horizontal tangent, comes to rest, and leaves
on the other side of that tangent. The close-up on the home page samples the
actual curve, rather than this local approximation.

The accounting and arithmetic are reproduced in
[cusp_sieve.py](cusp_sieve.py). The older polynomial-gcd program remains an
independent check of the result.
