# A fold divides the strangeness

Every value in the [strangeness atlas](strangeness.md) is divisible by
its rotational fold count `d = gcd(m−1,n+1)`. There is an explanation
beyond the finite table. For these curves,

```
z(t+2π/d) = exp(2πi/d) z(t),
wind(z,0) = 1,
z(t) != 0.
```

The last two facts follow from the positive real part of
`exp(−it)z(t)`: it is at least 245−140−65 = 40. For a generic curve
with this equivariance and winding one about the rotation center,
**d divides St**. Here is an argument using the
[Gauss-word formula](strangeness.md), with a useful warning about
what happens to the quotient's actual value.

## One sector becomes a closed curve

Identify the plane with the complex numbers and set

```
F(s) = z(s/d)^d,       0 ≤ s ≤ 2π.
```

The power closes one sector. Since z avoids zero, this map is locally
orientation preserving and has no critical point on the curve. Every
crossing orbit of z has d points and gives one transverse crossing
of F. Conversely, a crossing of F lifts to a crossing orbit of z.
Thus F is generic when z is generic. Its winding about zero is also 1.

Winding labels agree downstairs and upstairs. For a point q off F,
factor `z(t)^d−q` over its d roots. The complete z-path raised to the
dth power traverses F d times, so

```
d · wind(F,q) = Σ over r^d=q wind(z,r).
```

Rotation makes all d terms on the right equal. Hence each lifted region
has the same winding as its quotient region, and crossing mean indices I
agree. At s = 0 the original orbital curves and their quotient have
an exterior starting edge: their uniquely rightmost points have maximum
radius. Both base corrections vanish.

## The sheet offset matters

Take a crossing of F with earlier and later visits a < b. Its first
exponent is e. In one sector of z those two visits can belong to different
lifts of the crossing. Let k be the unique integer in 0,…,d−1 such that
rotating the later visit forward k sectors brings it to the earlier
visit's lift.

Among the d crossings in that orbit, the earlier quotient branch is
visited first d−k times. The other branch is visited first k times.
Their weights therefore sum to `e(d−2k)`. Summing over quotient crossings,

```
St(z) = d St(F) − 2 Σ e I k.
```

It would be wrong to drop that sheet sum. For the original rhythms
**15 / 6**, d = 7, the quotient has St = 2, while the sheet sum is 14:

```
St(z) = 7·2 − 2·14 = −14.
```

This is the only nonzero sheet sum in this finite original atlas.
Divisibility needs a further argument.

## A winding-ray identity

For any generic curve C avoiding zero, start on an exterior edge.
At a crossing with visits a < b, let j be the winding about zero of
its closed subpath from a to b. Write w = wind(C,0). Then

```
Σ crossings e I j = (w³−w)/6.
```

To see this, choose a ray from zero avoiding the vertices and basepoint.
Let l(t) count signed crossings of that ray since the start. At visits
to the same curve point, `j = l(b)−l(a)`. Let δ(t) denote the edge's
mean winding index. At a vertex visit with exponent e,

```
Δ(δ²) = (δ+e)²−δ² = 2eI.
```

The two occurrences of each crossing now give

```
Σ e I j = −½ Σ vertex visits l Δ(δ²).
```

Discrete integration by parts exchanges the vertex jumps for ray jumps.
The base edge has δ² = ¼; l increases by w over a complete circuit.
Writing σ = ±1 for a signed ray crossing, the result is

```
Σ e I j = ½ [Σ ray crossings σδ² − w/4].
```

Read winding labels along the ray from zero to infinity. At a crossing
with sign σ, the label changes from k to k−σ and
`δ = k−σ/2`. The rational polynomial

```
P(k) = k³/3 − k/12
```

has `P(k)−P(k−σ) = σ(k−σ/2)²`. Its sum telescopes from label w to
label 0, giving `Σ σδ² = w³/3−w/12`. Substituting proves the identity.
This proof works with negative and repeated ray crossings as well.

Apply it to F, whose w is 1. Its weighted subloop sum is zero.
Along a subloop of F with winding j, its lift gains angle `2πj/d`;
matching the earlier lift therefore requires

```
k ≡ −j (mod d).
```

Consequently `Σ e I k` is divisible by d. The lift formula proves
that St(z) is divisible by d too. The winding-one assumption is doing
real work; it is what makes the subloop sum vanish.

## An exact audit of the archived words

```sh
python3 experiments/strangeness_symmetry.py
```

Only the standard library is needed. The program audits saved words,
not new smooth intersection proofs. It shifts each complete cyclic
word by one sector and checks that both visits induce the same
permutation of crossings, that exponents repeat, and that every orbit
has exactly d members. Reducing labels to their rotation orbits gives
the quotient word. Its planar face calculation and integer recurrence
must agree, as must all starting edges and both symmetries.

The permutation determines k without angles or rounded coordinates.
The exact lift identity and divisibility hold for all 321 archived
curves; the 15 / 6 example ensures that a falsely simplified lift rule
would fail. Separate rational checks verify the telescoping primitive
for positive and negative labels. The geometric argument above proves
the general winding-one statement; the finite audit checks its use
and conventions in this sketchbook.
