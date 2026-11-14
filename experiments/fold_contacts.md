# The folds stay. The crossings change.

The [drawing and reading page](fold_contacts.html) follows the
[six phase variations](fold_variations.md). Keep the original lengths and
write

```
z(t,φ) = 245 exp(it) + 140 exp(i(d+1)t) + 65 exp(−i(d−1)t+iφ),
0 ≤ φ ≤ π,       d = 7 or 14.
```

The rotational symmetry stays d-fold, speed stays at least `75d−40`,
and the tangent turns d+1 times. Yet the crossing pairs change:

| Folds | First contact phase φ/π | Second contact phase φ/π | Crossing pairs along the turn |
| --- | --- | --- | --- |
| 7 | 0.341592201887… | 0.951535764936… | 7 → 21 → 35 |
| 14 | 0.914296764567… | 0.962912214409… | 70 → 98 → 126 |

**These are all the tangencies between distinct visits on this entire
closed phase interval.** Each row has two batches of d ordinary quadratic
touches. At the first sevenfold contact the branches travel in opposite
directions; at the other three they travel in the same direction. All
four batches create crossing pairs as φ increases. There is no tangency
at either phase endpoint.

A crossing *pair* is an unordered pair of distinct parameter visits at
the same point. At a transverse three-visit meeting, that point contributes
three pairs. The pair counts above stay valid through such meetings, but
**this calculation does not locate or classify triple passages**, count
distinct intersection points at every exceptional phase, or construct a
complete movie of all winding regions. At the contact phases themselves,
the d tangent pairs replace the disappearing/arriving 2d transverse pairs.
Thus their total distinct-visit pair counts are 14 and 28 for seven folds,
and 84 and 112 for fourteen folds.

The other half of a **full starting-angle turn** follows by the exact
identity `z(−t,2π−φ)=conj(z(t,φ))`. It reflects the first half and runs
its events in reverse phase order. Thus the full crossing-pair sequences
are **7 → 21 → 35 → 21 → 7** and **70 → 98 → 126 → 98 → 70**,
with four batches of contacts each. This symmetry transfers the tangency
classification; it still does not classify triple passages.

## Two visits make a triangle

Choose the shorter parameter separation and write the two visits as
`a+b` and `a−b`, where `0<b≤π/2`. Except for antipodal visits, this
represents each unordered pair once. Divide their position difference by
`10i exp(ia) sin b`. With `x=cos b`, it becomes

```
49 + P(x) exp(i d a) − Q(x) exp(i(φ−d a)) = 0,
P(x) = 28 U_d(x),       Q(x) = 13 U_(d−2)(x),
sin(k b) = sin b U_(k−1)(cos b).
```

Here U is the Chebyshev polynomial of the second kind, constructed by its
two-term recurrence. Set `u=exp(i d a)` and `v=exp(i(φ−d a))`. The equation
is the triangle `Qv=49+Pu`. Squaring its lengths gives

```
cos(d a) = (Q²−49²−P²)/(98P),
D = 4·49²P² − (Q²−49²−P²)².
```

For a noncollinear triangle, D>0. Multiplying u and v and taking real
parts eliminates the midpoint:

```
cos φ = C(y) = N(y)/H(y),           y = x²,
N = (Q²−P²)² − 49²(P²+Q²),
H = 2·49² P Q.
```

N and H are even in x. For odd d their common factor y is cancelled.
In this reduced form their degrees in y are 13 and 5 for d=7, and
28 and 13 for d=14. No trigonometric root search is needed.

The exact identity

```
H²−N² = D (Q²−P²)²
```

uses the uncancelled N and H. Consequently, a solution of
`N−cH=0` with `−1<c<1` has D>0. The sign of sin φ selects exactly
one of the two triangle orientations, since

```
sin φ = ± (Q²−P²) sqrt(D) / (2·49² P Q).
```

That fixes u and hence gives exactly d different midpoints a modulo
2π. Each interior root y therefore represents exactly d unordered
crossing pairs. There is no ambiguity from choosing the other orientation.

## Where can a pair become tangent?

Inside `0<φ<π`, the triangle is noncollinear. The Jacobian with respect
to `(a,φ)` is nonsingular: its determinant is a nonzero multiple of
the triangle's signed area. Thus `(a,φ)` are locally smooth functions
of b. Two branches are tangent precisely when this phase projection
has a critical point. Since sin φ and sin b cos b are nonzero, this is
equivalent to `C′(y)=0`.

The numerator `N′H−NH′` contains the factor `Q²−P²`. Its zeros give
cos φ=±1 and belong to the separate endpoint analysis. Remove that
factor, including the already cancelled y when d is odd. The remaining
critical polynomial R has degree **11 for d=7** and **26 for d=14**.

[fold_contacts.py](fold_contacts.py) constructs all coefficients anew
and uses complete rational Sturm isolation on `0<y<1`. It isolates
**five** roots of the first R and **six** of the second. Rational
interval bounds reject **three and four**, respectively, because C
lies strictly outside [−1,1]. The remaining two roots in each family
give the table above. Every R root is simple, and the remaining factors
and denominators are nonzero there. These are nondegenerate critical
points, not unresolved multiple roots.

Three rational cosines, one per phase interval, give independent exact
counts for `N−cH`:

| d | Witness cosines, in increasing phase order | Roots y in (0,1) |
| --- | --- | --- |
| 7 | 9/10, 0, −99/100 | 1, 3, 5 |
| 14 | 0, −99/100, −999/1000 | 5, 7, 9 |

No root can enter or leave these open intervals except at the already
isolated critical phases: the endpoint and denominator cases below are
excluded. Multiplying by d proves the complete crossing-pair staircase.

## The exceptions are part of the proof

* **P=0:** the sine recurrence gives `|Q|≤26<49`, so the triangle
  cannot close.
* **Q=0:** a meeting would require P²=49². The exact polynomial
  gcd of Q and P²−49² is constant for both d values.
* **b=π/2:** P=Q=0 for odd d; for even d their absolute lengths
  sum to 41. Neither can balance 49. There are no antipodal meetings.
* **b=0:** the visits coincide. The uniform positive velocity bound
  excludes tangency roots entering from this diagonal.
* **φ=0 or π:** either D=0 (a collinear triangle) or Q²−P²=0.
  The program proves these polynomials have simple roots and no common
  root. At D=0, their nonzero derivatives make the two-visit position
  Jacobian nonsingular. At Q²−P²=0 with D>0, the derivative of P−Q
  or P+Q and the nonzero triangle height do the same. Thus all endpoint
  meetings are transverse. Complete isolation and feasibility signs give
  7 and 35 pairs for the sevenfold endpoints, 70 and 126 for fourteen.

The endpoint multiplicity differs from the interior formula: a feasible
D root contributes d pairs, while a feasible Q²−P² root contributes
2d, because both triangle orientations now have the same phase. This
also independently checks that the endpoint counts join the staircase.

## Ordinary touches with only two branches

The one-variable argument is global. A separate local proof checks its
geometric interpretation. Use rational unit-circle charts

```
exp(it) = i^q (1+is)²/(1+s²),       0≤s≤1,
```

for each visit and for the phase. Solve equal position and zero velocity
determinant in those three chart coordinates. Yesterday's floating-point
seeds suggest cubes of radius 10⁻¹¹; **only rational inequalities accept
them**. An exact inverse of the center Jacobian defines `T(X)=X−RF(X)`.
All four cubes satisfy

```
||Id−R DF(X)||∞ < 0.01,
T(cube) lies strictly inside cube.
```

The actual norm bounds are below 1.3×10⁻⁶. Contraction proves one unique
root per cube. The interval identity
`y=(1+cos(t−s))/2` identifies each local solution with exactly one root
in the complete global critical list. Rotation supplies its d copies.
Their positions have radius greater than 100, so these copies are distinct.

For each selected contact, a **unit-radius disk** around an exact rational
position admits only the two selected visits, throughout a phase-chart
radius of 1/10000. Rational endpoint rectangles plus second-derivative
interpolation bounds exclude every other arc of the whole orbit. The
four covers use 1016, 1015, 1016, and 1017 excluded arcs. Each admitted
slot is strictly monotone in a physical coordinate. This excludes a
third visit at every contact; the local lens is a face sufficiently
close to its birth. It does not extend the disk's isolation claim to
the whole orbital route or to the wider illustration window.

In graph coordinates let g be the difference between the selected
branches, α its phase derivative at the contact, and β its second
spatial derivative. The certificate proves αβ<0, so the ordinary contact
creates two crossings as phase increases. The new lens area is

```
area = K (φ−φ_contact)^(3/2) + o((φ−φ_contact)^(3/2)),
K = (4/3) |α| sqrt(2 |α/β|).
```

The coefficients, in drawing-unit area per radian^(3/2), are approximately
**339.159441, 19506.785210, 9289.341318, and 19128.998192**, in the
table's order. They use phase in radians, not the displayed fraction φ/π.
Rational square-root bounds enclose all four coefficients in the record.
The coefficient is unchanged by switching physical graph axes, since
the common slope factors cancel. The illustrated separation graph
rotates into a tangent frame and enlarges its normal scale.

## Reproduce

```sh
python3 experiments/fold_contacts.py
python3 experiments/fold_contacts.py --write
python3 experiments/fold_contacts_check.py
python3 experiments/fold_contacts_figure.py
```

The first command repeats the complete proof without trusting saved
roots or counts. `--write` archives the freshly proved intervals in
[fold_contacts.json](fold_contacts.json). Seven negative controls reject
a displaced phase, coincident visits, invalid radius or phase quarter,
and unsupported fold controls. All mathematical programs use the Python
standard library. The illustration is numerical, and its approximated
touch position is labelled accordingly; the JSON is a proof receipt,
not an input to the certificate. The reading page needs no JavaScript.

The separate [exact evaluator audit](fold_contacts_check.py) uses complex
division and automatic differentiation, independently of the certificate's
conjugated powers and analytic Jacobian formulas. It checks 4,608 exact
Fourier-jet components and 612 Jacobian entries at 68 rational states.
Those finite comparisons audit the implementation; the complete Sturm
and contraction arguments supply the continuous theorem.
