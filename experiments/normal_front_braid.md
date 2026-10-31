# Two braid words, one knot

The two [conormal fronts](normal_front.html) can now be read as exact
**positive braid words on eleven strands**, each with **106 generators**.
An explicit **195-generator conjugator** proves that the braids are
conjugate. Their ordinary closures therefore represent **the same knot**.
They also have the same complete Alexander polynomial, of degree **96**,
normalized with constant and leading coefficient one. At −1 its value
is **189**. All 97 coefficients agree.

The knot equivalence comes from the conjugacy witness, beyond matching
polynomials. The explicit calculation certifies ordinary isotopy of the
closures. A classification corollary below also gives existence of a
Legendrian isotopy. No plane-curve route is constructed. The
[crossing-word lower bound](triple_distance.md) still applies to routes
without either kind of touch.

The [record](normal_front_braid.json) contains both words, section charts,
the conjugator, its full free-group images, and polynomial coefficients
in increasing degree order. A
[standalone braid drawing](normal_front_braid.svg) shows the words as
strands. It is a diagram of their order, not a picture at geometric scale.

## Which knot, and which braid?

Use the left-normal coordinates

```
θ = normal angle,
h = q·(cos θ,sin θ),
p = dh/dθ = q·(−sin θ,cos θ).
```

The lifted curve `(θ,p,h)` lies in `S¹ × R²`. These are the conormal
coordinates of [Ng, §2.1](https://sites.math.duke.edu/~ng/math/papers/planecurves.pdf#page=4).
Since θ increases strictly, the lift is a closed eleven-strand braid.
We use its ordinary braid closure in S³, with the product coordinates
`(p,h)` fixed along the circle; the solid-torus knot carries additional
information that this closure can forget.

At a front crossing, resolve the strand with larger slope p in front.
The strand arriving from lower h has the larger slope, so every crossing
is the same positive Artin generator. Index generator i from the lower
pair of adjacent heights, starting at one. Reversing the drawing's
crossing convention would mirror both closures; the normalized reciprocal
Alexander polynomials here would be unchanged.

## Start at a rational normal

Cut the circle at `N=(3/5,4/5)`, with angle `θ₀=atan(4/3)`.
A scalar rational contraction certifies each of its eleven parameter
visits: solve `q′·N=0` and prove that the left normal points along N.
The eleven-turn theorem proves that these eleven visits exhaust the
section. Their interval heights are pairwise ordered.

The continuous normal angle is

```
Θ(t) = π+11t+arg B(t),       Re B > 0.
```

At this section it equals `θ₀+2πk`, for k=1,…,11. Give a strand label
`k modulo 11`. The initial height orders, from bottom to top, are:

```
11 / 6:  8  7  6  9 10  5  4  1  3  0  2
11 / 8:  8  9  6  7  5 10  4  0  1  2  3
```

These labels follow successive normal turns. They are not crossing labels.

## Order every crossing rationally

The default program first repeats both [complete front censuses](normal_front_census.md).
Each supplies all 106 crossing boxes. The word calculation replays their
contractions, coorientation, point separation, and all front-point
separations.

For each visit box, enclose Θ and subtract an integer multiple of 2π to
place it strictly in `(θ₀,θ₀+2π)`. The integer's residue modulo eleven
identifies its strand. A floating-point estimate suggests the integer;
rational inequalities must prove the whole interval lies inside that
chart. The two visits' angle enclosures intersect because they give the
same normal at the certified root.

Angle bounds use forty alternating arctangent terms on [−1/2,1/2],
with the next term enclosing the remainder. Reciprocal and quarter-turn
identities reduce other arguments to that range. Machin's identity
`π=16 atan(1/5)−4 atan(1/239)` supplies π, and outward rounding to
dyadics with denominator 2⁸⁰ keeps the rational arithmetic manageable.
No numerical angle sort is trusted.

Disjoint angular intervals fix event order. Overlapping intervals form
a group. For each crossing height interval, extend it by **450 times
the whole group's angular width** on either side. This uses
`|dh/dθ|=|p|≤|q|≤450`. These extended height bands must be pairwise
disjoint, and no two crossings in the group may use the same strand.
The swaps therefore commute and can be ordered by height.

Each endpoint gives **98 ordered groups**: 96 single crossings and two
groups of five commuting crossings. Following their strand labels must
always find an adjacent pair. Swap it and record its positive generator.
After all 106 swaps, the final labels must be the initial labels minus
one modulo eleven. This checks the closure's full cyclic sheet shift;
in particular, its permutation has one cycle and the closure is a knot.

## A direct conjugacy witness

Let A and B be the two certified words, in endpoint order. The record
gives a positive word C of length **195**, with

```
A C = C B,       hence       C⁻¹ A C = B.
```

Verify this relation in the faithful Artin action on the free group with
generators x₁,…,x₁₁. Generator σᵢ acts by

```
xᵢ     ↦ xᵢ xᵢ₊₁ xᵢ⁻¹,
xᵢ₊₁   ↦ xᵢ,
all other generators fixed.
```

This is the standard faithful representation, also covered by
[Shpilrain, *Representing braids by automorphisms*, introduction and Theorem A](https://arxiv.org/pdf/math/0203167).
Equality of the eleven reduced free words therefore proves equality of
the braids. Conjugate braids have isotopic closures; see
[Birman–Brendle, *Braids: A Survey*, §2](https://www.math.columbia.edu/~jb/Handbook-21.pdf#page=12).

Two independent implementations check the relation. One updates just
the two affected generator images and reduces with a stack. The other
literally substitutes letters, in reverse composition order, and deletes
adjacent inverse pairs directly. They agree on every letter of all
eleven images of AC and CB. Their reduced lengths are

```
67, 69, 65, 69, 65, 89, 73, 93, 83, 71, 61.
```

All **805 letters** are compared and stored; no digest stands in for
word equality. Appending σ₁ to the proposed conjugator must fail the
relation. Controls also check elementary braid relations, distant
commutation, a single generator, nested cancellation, and invalid inputs.

A temporary **libbraiding** search found C. The literal witness is all
the verifier retains: the published check uses only Python's standard
library and does not trust or rerun that search.

### A classification corollary

**The two lifts are also Legendrian isotopic**, by
[Etnyre–Vértesi, *Legendrian satellites*, Theorem 4.4 and §4.1.1](https://etnyre.math.gatech.edu/preprints/papers/braidsatellites.pdf#page=19).
Here is the application. Scale `(p,h)` uniformly to put the lifts inside
their standard solid torus; `dh−p dθ` scales by the same positive factor.
Conjugacy identifies the underlying closed-braid pattern. Each front has
106 positive crossings and no cusps, so its relative Thurston–Bennequin
number is 106, equal to the positive word length. The theorem gives
uniqueness at that maximal value.

This is an inference from a classification theorem. The programs
construct no Legendrian isotopy. Projecting one back to a regular
plane-curve route would require a further argument keeping its tracing
velocity nonzero; no such route is supplied here.

## The entire polynomial, not sample agreement

For generator i, use the unreduced Burau block

```
[ 1−t   t ]
[  1    0 ]
```

on coordinates i,i+1, with identity elsewhere. Its all-ones vector is
fixed. For the product M, quotient that vector out by taking
`R_ij = M_ij−M_(n−1),j` for i,j<n−1. Then the standard closure formula is

```
Δ(t) = det(I−R(t)) / (1+t+⋯+t^(n−1)),       n=11,
```

up to the usual sign and monomial normalization. See
[Morton, *The Multivariable Alexander Polynomial for a Closed Braid*, introduction and §2](https://www.liverpool.ac.uk/~su14/papers/multiburau.pdf).

The numerator has degree at most **106**. To see this without guessing a
degree from samples, give every generator its own variable. Changing one
variable changes its matrix by a rank-one matrix. With all other factors
fixed, the determinant is affine in that variable. Thus the determinant
is multiaffine in the 106 separate variables; identifying them gives the
degree bound.

Evaluate at the **107 integers 0,…,106**, using integer matrices and
fraction-free Bareiss determinants. Newton forward interpolation then
recovers the entire numerator exactly. All monomial coefficients must be
integers; division by `1+t+⋯+t¹⁰` must have zero remainder. This leaves
97 coefficients, with constant and leading coefficient one, reciprocal
symmetry, `Δ(1)=1`, and `Δ(−1)=189`. Both arrays agree exactly.
Independent evaluations at −2, −1, and 107 also agree with the polynomial.

## Reproduce

Only the Python standard library is needed:

```sh
python3 experiments/normal_front_braid.py
python3 experiments/normal_front_braid.py --write
python3 experiments/normal_front_braid.py --saved
python3 experiments/normal_front_conjugacy.py
node experiments/normal_front_braid_figure.js
```

The default repeats the complete front covers, then certifies words and
polynomials and the conjugacy witness. `--write` saves the record only
after that full calculation.
`--saved` replays root boxes and the entire word/polynomial calculation,
**conditional on the archived census's completeness**; it omits the
whole-orbit covers. It cannot write a new certificate record.
The small conjugacy program checks the algebraic relation for the
recorded words, assuming their separate geometric certification.

Controls cover rational angle reductions and Machin's identity, Burau
braid relations and distant commutation, an independent Leibniz determinant
on 24 integer matrices, singular and pivot-changing matrices, the unknot,
trefoil, split link, and positive stabilization. Invalid generator indices
are rejected. The original intersection source remains unchanged.
