# Two equally good places

The [cubic example](shifted_parabolas.svg) has one best insertion.
The [power-law theorem](shifted_placement.md#the-same-argument-covers-every-positive-power)
gives a unique best finite placement for a whole family of intercepts.
Strict convexity alone does **not** give that uniqueness.

The [drawing](two_choices.svg) shows a simple counterexample. Keep outer
slope labels −1 and +1 and use

```
Xₚ(Y) = Y²/2 − pY + h(p),
h(p) = p⁴/4 + p²/16.
```

Its intercept law has `h″(p)=3p²+1/8≥1/8` throughout the interval.
Nevertheless there are exactly **two** global best new slopes, −1/2
and +1/2. Either makes a pocket of area **27/256**. The midpoint's
area is **25/256**, so either best choice gains exactly **8%** over it.
Both best pockets are reflections in Y=0, with identical coordinates
and unit scales in the drawing.

## The complete insertion formula

More generally, take any ε>0 and set

```
hε(p) = p⁴/4 + εp²/2,       −1≤p≤1.
```

This remains strictly convex, with second derivative `3p²+ε>0`.
The two outer intercepts agree. For an inserted slope r between them,
write `H=hε(1)` and `d=H−hε(r)`. The left and right secants differ by

```
s_right−s_left = d/(1−r) + d/(1+r)
                   = 2d/(1−r²).
```

The [insertion identity](shifted_parabolas.md#insert-one-slope) gives the
complete pocket area, since there were only two old curves:

```
Aε(r) = [(r+1)(1−r)/4] × [2d/(1−r²)]²
      = d²/(1−r²)
      = (1−r²)(r²+1+2ε)²/16.
```

The last polynomial also extends to the endpoints, where the area is
zero. There is one bounded pocket for each distinct interior r; no
unseen arrangement region is being left out.

## One maximum splits into two

Put z=r²∈[0,1] and c=1+2ε. Then

```
A = (1−z)(z+c)²/16,
dA/dz = (z+c)(2−c−3z)/16.
```

The first factor is positive. Thus:

- If ε≥1/2, the unique maximum is z=0 and hence r=0.
- If 0<ε<1/2, the unique maximizing square is
  `z=(1−2ε)/3`, giving the two slopes
  `r=±√((1−2ε)/3)`.

These derivative signs cover the whole interval. At ε=1/8 they give
z=1/4 and the rational maximizers ±1/2 used in the drawing. Direct
substitution gives 27/256 and the midpoint's 25/256.

As ε increases toward 1/2, the two best places approach each other
with the square root of the remaining parameter distance. At the
threshold the midpoint is still the unique maximum, but its loss is
quartic rather than quadratic:

```
A_(1/2)(r) = 1/4 − 3r⁴/16 − r⁶/16.
```

For 0<ε<1/2, write δ=1−2ε. The exact advantage over the midpoint is

```
A_max−A(0) = δ²(9−4δ)/432 > 0.
```

The parameter examples in the [JSON record](two_choices.json) include
the two-maximizer choice ε=1/8, the merging threshold ε=1/2, and
the single-midpoint choice ε=3/4.

## The same counterexample has positive slope labels

The symmetric labels make the reflection easy to draw. Their negative
values are not responsible for the failure of general uniqueness.
Relabel q=p−2 and use

```
H(p) = (p−2)⁴/4 + (p−2)²/16,       1≤p≤3.
```

For `X=Y²/2−pY+H(p)`, the common linear shear `X̃=X+2Y`
gives `X̃=Y²/2−qY+h(q)`. It has determinant one and preserves every
area. Thus positive outer labels 1 and 3 have precisely two best
insertions, 3/2 and 5/2, with the same areas above. H″ remains uniformly
positive. This H is outside the power laws used in the uniqueness proof.

The general [dense-placement theorem](shifted_parabolas.md#a-dense-arrangement-favors-stronger-curvature)
still applies: its hypotheses hold for every fixed ε>0 on this compact
interval. That theorem concerns the leading optimal area deficit as
the count grows; it did not claim a unique finite optimum for all h.

## Reproduce

```sh
python3 experiments/two_choices.py
python3 experiments/two_choices.py --write
```

Only the Python standard library is needed. The command makes 4,848
exact comparisons across 48 positive rational ε values, checks every
interior comparison against the general secant-variance formula, and
independently clips and integrates nine complete curved arrangements.
Five invalid controls reject inappropriate inputs. The derivative
argument proves the global and parameter-wide claims; these finite
controls audit the formulas and selected geometry.

The exported picture retains exact rational values in its record.
Its pocket arcs are quadratic Beziers with rounded coordinates.
The sextic area graph is sampled from the exact polynomial, with
different horizontal and vertical scales. The reading page links this
as a [companion to the shifted chapter](parabolic_pockets.html#sideways),
keeping it separate from the first five quadratic-intercept drawings.
