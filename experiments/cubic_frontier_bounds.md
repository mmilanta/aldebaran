# A limit with a ruler

Yesterday's [cubic-gain/sixth-order-cost limit](cubic_frontier_limit.md)
describes a very cheap first improvement: enlarge the smallest pocket
until the two triangles tie. It now has a **stated finite range and
uniform error bounds**. The same certificate also proves the complete
two-stage total/minimum frontier throughout that range.

For four curves `Xₚ(Y)=Y²/2−pY+p³/3`, fix positive outer labels a<b.
Put

```
ε = (b−a)/(b+2a).
```

Everything below holds for **0<ε≤1/10**, equivalently
**1<b/a≤4/3**. It does not classify every positive endpoint pair.
The separate [finite [1,3] certificate](cubic_frontier.md) still
covers its larger span.
An independent [ordering theorem](cubic_total_order.md) does cover every
positive span at the total optimum: C>A+B and A>B. That one-point
ordering does not by itself extend the full frontier classification.

Let g be the relative increase in the smallest area from the
largest-total placement to the first triangle tie. Let c be the
relative loss of total area over that same step. Each uses its own
area at the largest-total placement as its denominator. Then

```
g = (8/27) ε³ [1 − 3ε/2 + r_g ε²],     −1/5 < r_g < 1/5,
c = (16/2187) ε⁶ [1 − 3ε + r_c ε²],       1 < r_c < 3,

c/g² = 1/12 − θ ε²,                    1/25 < θ < 1/20.
```

The remainders depend on ε. These are simultaneous inequalities
for **every** ε in the interval, rather than estimates from selected
roots. In particular, the ratio is slightly *below* 1/12, and its
error is quadratic even though the individual leading laws have
linear relative errors.

![Continuous error bands for the two area laws and their ratio, with
the three complete pockets at a first triangle tie.](cubic_frontier_bounds.svg)

The [standalone drawing](cubic_frontier_bounds.svg) keeps its proof link
when saved. Its central traces and curve coordinates are rounded
illustrations; the shaded inequalities hold continuously.
Its three complete pockets undergo the same horizontal straightening
as the [band drawing](parabolic_pockets.md#follow-the-nearest-slope),
followed by a common determinant-one affine change of coordinates.
Their areas are preserved; the panel does not show their original shape.

## Use normalized areas

Write the original interior labels as `a+(b−a)x, a+(b−a)y`.
Scale every area by `18ε²/(b−a)⁵`. The complete face areas are

```
A = x(y−x)y [1+ε(x+y−1)]²,
B = (y−x)(1−y)(1−x) [1+ε(x+y)]²,
F(t) = t(1−t)(1+εt)²,
C = F(x)−A = F(y)−B,
T = A+C+B = F(x)+B = F(y)+A.
```

A and B are triangles; C is the entire quadrilateral between them.
The common positive scale cancels from g and c. The polynomial
family also makes sense at ε=0, which is used only as a continuous
limit in the certificate.

## Turn formal coefficients into enclosures

The two defining systems are the same as in the limiting note:

```
total:   G₀ = (Tₓ,Tᵧ) = 0,
switch:  Gₛ = (A−B,Tᵧ) = 0.
```

The [program](cubic_frontier_bounds.py) reconstructs both root
polynomials P(ε) through degree 16. At each degree the new pair
of coefficients solves the constant base-point Jacobian system.
No floating-point root enters this calculation. All residual
coefficients through degree 16 vanish exactly, and the first six
orders agree with the earlier independent jet recurrence.

For each system, write an actual root as

```
(x,y) = P(ε) + ε¹⁷ u,       ||u||∞ ≤ 100.
```

Let Y be the inverse base-point Jacobian. For ε>0 define

```
Φε(u) = u − Y G(P(ε)+ε¹⁷u, ε)/ε¹⁷.
```

Exact residual divisibility extends this polynomial map to ε=0.
Its derivative with respect to u is `I−Y D_(x,y)G`. On each of
16 closed slabs of width 1/160, rational interval arithmetic gives

```
||D_u Φε||∞ < 1/3,       ||Φε(0)||∞ < 20.
```

Thus Φε maps the radius-100 square strictly into itself:
`20+100/3<100`. Iteration contracts distances by less than 1/3,
so its iterates converge to a unique fixed point in that square.
Because Y is invertible, that fixed point solves G=0. This proves
the two root enclosures for every ε in every slab, including their
shared endpoints. It is an elementary contraction argument of the
kind underlying interval Newton methods; see Krawczyk and Neumaier's
[original interval-operator paper](https://arnold-neumaier.at/scan/45.pdf).
The map and inequalities above are the argument actually checked here.

The two Jacobians stay invertible because their preconditioned
defects have norm less than one. Their unique roots therefore
vary smoothly. The total root is the already proved
[unique global total optimizer](shifted_placement.md).

## Keep the small factors before evaluating

Substitute the root models into the exact area polynomials. The
coefficients beyond degree 16 are interval coefficients; they
enclose the unknown errors for every ε. There is no truncation
of these substituted polynomials.

Let B₀,T₀ denote areas at the total root, and Bₛ,Tₛ those at
the switch root. Before bounding them, cancel exact factors:

```
Dg = (Bₛ−B₀)/ε³,
Dc = (T₀−Tₛ)/ε⁶,
g/ε³ = Dg/B₀,       c/ε⁶ = Dc/T₀.
```

Every discarded coefficient is checked to be exactly zero.
In particular, the cost has no terms below degree six, so the
program never subtracts separately rounded endpoint areas to
recover a tiny cost.

To prove the displayed remainders, form

```
Rg = [Dg − (8/27)(1−3ε/2)B₀]/ε²,
Rc = [Dc − (16/2187)(1−3ε)T₀]/ε²,
D  = T₀ Dg²,
Rθ = [(1/12)D − Dc B₀²]/ε².
```

Their exact low-order coefficients vanish too. Rational Horner
bounds on the same 16 slabs certify

```
−1/5 < Rg/[(8/27)B₀] < 1/5,
   1 < Rc/[(16/2187)T₀] < 3,
1/25 < Rθ/D < 1/20.
```

The denominators are strictly positive. This proves the finite
area laws and the ratio bound without dividing an interval that
contains a vanishing ε. The command also encloses ε=2⁻¹⁶⁰ using
the retained factors; its gain and cost remain positive.

## The first tie really is on the global frontier

This requires more than solving two equations. Here is an explicit
version of the limiting note's localization and support argument.

The root tubes prove `B₀>7/100`, and both roots belong to

```
U = [1/3,9/25] × [2/3,7/10].
```

They also prove `xₛ<x₀` for every ε>0, by bounding
`(x₀−xₛ)/ε³` away from zero. The total and switch share the
best-right-insertion curve `y=rε(x)`, on which `Tᵧ=Bᵧ=0`.
The [explicit insertion formula](cubic_frontier.md#the-first-branch-only-b-is-constrained)
shows `rε′>0` for positive original labels. Hence the entire
connecting arc stays in U.

On this arc x<1/2 and y≥2/3. The function F increases below 1/2
and decreases above 2/3 for all 0≤ε≤1/10. For the latter claim,
its derivative has the sign of

```
1−2y+εy(3−4y) ≤ −1/3 + (1/10)(2/9) < 0.
```

Thus `A−B=F(x)−F(rε(x))` increases strictly with x. At the
switch it is zero, so A≥B along the entire first arc. A separate
**75-coefficient** Bernstein identity proves C>B on all of U.
Consequently B is its smallest face, and decreases strictly
with x because Bₓ<0 and Bᵧ=0.

Every competitor whose three areas exceed 7/100 lies inside

```
R = [1/7,1/2] × [1/2,7/8].
```

Indeed, `F(x)=A+C>7/50` and `F(y)=B+C>7/50` exclude
x≤1/7 and y≥7/8, using F's monotonicity on those outer ranges
and its upper bound at ε=1/10. If y≤1/2, then
`A≤y³/4≤1/32`. If x≥1/2, then
`B≤(1−x)³(1+2ε)²/4≤9/200`. Both contradict the threshold.
The program checks all four rational endpoint inequalities.

On the whole three-dimensional box `R×[0,1/10]`, **36 and
245 positive tensor Bernstein coefficients** prove respectively
`−Tₓₓ>0` and `TₓₓTᵧᵧ−Tₓᵧ²>0`. Thus T is strictly
concave on R for every parameter in range. The minimum
coefficients are `3481/3920` and `671/784`.

Along `y=rε(x)`, the second derivative of total area is
`Tₓₓ−Tₓᵧ²/Tᵧᵧ<0`. It has zero first derivative at x₀,
so Tₓ=Aₓ>0 before that endpoint. Choose

```
λA=0,       λB=−Aₓ/Bₓ>0.
```

They satisfy `∇T+λB∇B=0`. The formulas for A and B are products
of positive affine factors, so log A and log B are concave on
the ordered-label domain. For a smallest-area requirement
`s=B`, the function `T+sλB log(B/s)` is strictly concave on
the convex set `R∩{x<y}` and stationary at this placement.
Every feasible competitor
has this function at least as large as its own total area;
the candidate has it equal to its total. This proves the
candidate's unique global optimality, because all feasible
competitors are in R. The endpoint at x₀ uses λB=0.

## Both triangles then grow together

The same uniform room also completes the rest of the frontier
for every span in this range. Let u be the normalized maximin
root from the [general-endpoint theorem](cubic_four_general.md):

```
32εu³+(32+8ε)u²−(4+13ε)u−1=0,
v = 9u/(8u+1).
```

For 0<ε≤1/10, `1/4<u<27/100`, and v<39/50.
The program proves these bounds by endpoint signs of the cubic;
its unique positive root was proved in the general theorem.

The second branch is `F(x)=F(y)`, from the switch down to
`(u,v)`. The strict derivative signs above select exactly one
y, increasing as x decreases. It lies entirely in

```
V = [1/4,9/25] × [2/3,39/50].
```

On **all of `V×[0,1/10]`**, another **320 positive Bernstein
coefficients** prove `J=AₓBᵧ−AᵧBₓ>0`. Therefore
`ds/dx=J/F′(y)<0` for s=A=B. At the switch Aₓ>0 and
Bᵧ=0. Thereafter Aₓ stays positive, since x decreases
while its best-left-insertion value increases with y. Likewise
Bᵧ becomes negative: y increases while its best-right-insertion
value decreases with x. Also Aᵧ>0 and Bₓ<0 everywhere here.

The two nonnegative supports are

```
λA = Bᵧ(Bₓ−Aₓ)/J,
λB = Aₓ(Aᵧ−Bᵧ)/J.
```

Both are positive after the switch. The strictly concave function
`T+sλA log(A/s)+sλB log(B/s)` proves unique global optimality
by the same comparison. The quadrilateral stays larger than s:
it starts larger, and a first equality would give all three equal.
The [unique equal-area placement](cubic_four_general.md) is (u,v).
It therefore joins the triangles only at that final endpoint.

These two arcs cover every smallest-area requirement between the
total optimizer and the maximin endpoint. Requirements below that
interval select the total optimizer; those above it are infeasible.
This is the **complete frontier for 1<b/a≤4/3**. The quantitative
g and c above concern only its short first arc.

## Reproduce

```sh
python3 experiments/cubic_frontier_bounds.py
python3 experiments/cubic_frontier_bounds.py --write
python3 experiments/cubic_frontier_bounds.py --epsilon 1/10
python3 experiments/cubic_frontier_bounds_figure.py
```

Only the Python standard library is needed. The
[rational record](cubic_frontier_bounds.json) includes all 676
Bernstein coefficients, the root polynomials, the 32 contraction
receipts, 16 simultaneous remainder enclosures, and four examples.
It is output, not an input to the proof. Invalid perturbations and
an invalid power cancellation are rejected. Saved small areas are
rounded **outward** at relative binary precision, preserving their
positive lower bounds without enormous rational printouts.
