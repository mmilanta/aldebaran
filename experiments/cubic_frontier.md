# First one pocket. Then two.

Four complete curves `Xₚ(Y)=Y²/2−pY+p³/3`, with outer labels 1 and 3,
have a **unique best arrangement for every feasible smallest-pocket
requirement**. Their complete efficient total/minimum frontier has two
branches. First the smaller triangle B grows alone. Then triangles A
and B tie and grow together. The quadrilateral C joins them only at the
largest-minimum endpoint.

The first label x decreases along the frontier; the second label y
initially decreases a little, then increases. The change happens at

```
x = 1.82562173837493…,
y = 2.459833321660885…,
smallest area = 1.186344511893067… .
```

![The complete total/minimum frontier and an enlarged first branch.
Two complete arrangements at a shared scale compare the switch with
a later point where both triangles have grown.](cubic_frontier.svg)

The [standalone drawing](cubic_frontier.svg) keeps its proof link when
saved. The first branch's area loss is so small that it has a separate,
explicitly enlarged graph; the two arrangement panels share unit scale.

This closes the four-curve compromise left open by the
[maximin result](cubic_maximin.md). It is specific to cubic intercepts,
four curves, and [1,3]. The [general-endpoint maximin](cubic_four_general.md)
and [five-curve maximin](cubic_five.md) remain separate results.

## What is being optimized?

Write the labels as `1<x<y<3`, and use the complete face list from the
[consecutive-run calculation](shifted_maximin.md):

```
A = (x−1)(y−x)(y−1)(1+x+y)²/18,
B = (y−x)(3−y)(3−x)(x+y+3)²/18,
F(r) = (r−1)(3−r)(r+4)²/9,
C = F(x)−A = F(y)−B,
T = A+C+B = F(x)+B = F(y)+A.
```

For a requirement s, maximize T subject to `A,C,B ≥ s`. This formulation
includes the actual complete pockets, rather than selected subregions.
Let s₀ be the smallest area at the unique
[total-area optimum](shifted_placement.md), and S* the unique
[maximin value](cubic_maximin.md). They are approximately

```
s₀ ≈ 1.17553521349958,  S* ≈ 1.52100777946364.
```

Requirements below s₀ select that same total optimum; requirements
above S* are infeasible. The nontrivial frontier is s₀≤s≤S*.

## A smaller room restores concavity

T is [not concave on the whole ordered triangle](cubic_maximin.md#why-the-complete-compromise-is-still-a-separate-problem).
We only need competitors whose smallest area is at least s₀>1.
Every arrangement with `A,C,B≥1` lies strictly inside the rectangle

```
R = [11/8, 2] × [23/10, 14/5].
```

Here is an explicit localization argument. F increases up to
`ρ=(1+√11)/2` and decreases thereafter. Since `F(x)=A+C≥2`,
`F(11/8)=24037/12288<2` excludes x≤11/8. Similarly,
`F(y)=B+C≥2` and `F(14/5)<2` exclude y≥14/5. Also

```
A ≤ (y−1)³(1+2y)²/72,
B ≤ (3−x)³(x+6)²/72.
```

The first bound increases with y and is less than 1 at y=23/10.
The second decreases with x and equals 8/9 at x=2. Thus y>23/10
and x<2. These inequalities use `(x−1)(y−x)≤(y−1)²/4` and its
right-hand counterpart.

On **all of R**, T is strictly concave. Differentiate the exact total
polynomial and form `−Tₓₓ` and `TₓₓTᵧᵧ−Tₓᵧ²`. After mapping R to
[0,1]², their tensor Bernstein expansions have, respectively,

```
12 strictly positive coefficients, bidegree (2,3);
49 strictly positive coefficients, bidegree (6,6).
```

Their minimum coefficients are `170209/72000` and
`640338611/1024000000`. Bernstein basis functions are nonnegative
and sum to one, so these finite identities prove strict Hessian signs
on the **entire rectangle**. The [program](cubic_frontier.py) rebuilds
every coefficient from the face formulas; the [record](cubic_frontier.json)
lists them all. This is a continuous proof, not a grid test.

## A support proves global optimality

The identities for T give `Tₓ=Aₓ` and `Tᵧ=Bᵧ`. Also `Aᵧ>0` and
`Bₓ<0` everywhere in the ordered triangle. Both log A and log B are
concave there: their formulas are sums of logarithms of positive
affine functions.

Suppose a candidate with active area s has nonnegative numbers
λA,λB satisfying

```
∇T + λA ∇A + λB ∇B = 0,
λA(A−s) = λB(B−s) = 0,
A,C,B ≥ s.
```

Then, on R, the function

```
H = T + sλA log(A/s) + sλB log(B/s)
```

is strictly concave and stationary at that candidate. It has its
unique global maximum there. Every feasible competitor has H≥T,
whereas H=T at the candidate, so the candidate uniquely maximizes
T for that requirement. Every relevant competitor is in R by the
localization argument. No concavity of T outside R is needed.

## The first branch: only B is constrained

For endpoints a<b, define the unique best insertion

```
r(a,b) = [a+b+√(17a²+2ab+17b²)]/8.
```

It follows either from the earlier insertion calculation or from
these directly checked derivative factorizations:

```
Tₓ = −(y−1)(x+y+1)[4x²−x(y+1)−y²−1]/18,
Tᵧ = (3−x)(x+y+3)[x²+xy−4y²+3y+9]/18.
```

Let (x₀,y₀) be the total optimizer, approximately
`(1.82986223579931, 2.46157890321972)`. The first branch is

```
y = r(x,3),      σ ≤ x ≤ x₀,
s = B(x,y).
```

Here σ is the switch defined below. Both coordinates increase with
x, and the branch lies in `[1.82,1.84]×[2.45,2.47]`. A further
positive Bernstein certificate proves `C>B` on that whole rectangle.
Since x<ρ<y, the function `F(x)−F(r(x,3))` increases strictly with x.
It vanishes at σ, so `A>B` above the switch.

On this branch `Bᵧ=Tᵧ=0`. The function `M(x)=T(x,r(x,3))` has

```
M″ = Tₓₓ−Tₓᵧ²/Tᵧᵧ < 0.
```

Its derivative vanishes at x₀, so `Aₓ=Tₓ>0` for x<x₀. Thus
`λA=0`, `λB=−Aₓ/Bₓ>0` give the support. At the total endpoint
both multipliers are zero. Because `ds/dx=Bₓ<0`, every requirement
from s₀ to the switch value appears exactly once.

## The switch is one algebraic point

The switch is where `F(x)=F(y)` meets `y=r(x,3)`. Exact elimination
gives

```
52σ⁶+461σ⁵+148σ⁴−7528σ³−12250σ²+24585σ+28832 = 0,
1.825 < σ < 1.826,

η = (469+163σ−83σ²−21σ³)/(25σ²+98σ−115).
```

A Sturm calculation proves exactly one simple root in that bracket.
Substitution into both defining equations has zero polynomial
remainder modulo the sextic. Rational bounds put η in (2.459,2.460),
so it is the positive insertion root. The denominator is strictly
positive. The switch's quadrilateral is strictly larger than A=B,
and `Aₓ>0` there. Since `F(x)−F(r(x,3))` is strictly increasing on
the first branch, there is no second switch on it.

## The second branch: the triangles tie

Let (α,β) be the proved maximin labels. The second branch is

```
F(x)=F(y),      α ≤ x ≤ σ,      y>ρ,
s=A(x,y)=B(x,y).
```

F is strictly decreasing above ρ, so y is unique; it increases as
x decreases. The branch connects (σ,η) to (α,β) and stays in
`[1.63,1.83]×[2.45,2.62]`. On that whole rectangle the polynomial

```
J = AₓBᵧ−AᵧBₓ
```

has **64 positive tensor Bernstein coefficients** of bidegree (7,7).
Consequently

```
ds/dx = J/F′(y) < 0.
```

The first-insertion optimum r(1,y) increases with y, and `Aₓ>0`
at the switch. Hence `Aₓ>0` throughout this branch. Likewise,
`Bᵧ<0` after the switch because y increases while r(x,3) decreases.
Together with `Aᵧ>0`, `Bₓ<0`, and J>0, this proves positivity of

```
λA = Bᵧ(Bₓ−Aₓ)/J,
λB = Aₓ(Aᵧ−Bᵧ)/J.
```

These solve the two support equations exactly. At the switch λA=0,
and λB agrees with the first branch's support.

Finally C>s until the maximin endpoint. At the switch this is a
strict rational inequality. A zero of `C−A` along `A=B` would make
all three faces equal. The
[affine equal-area relation](cubic_maximin.md#why-does-the-second-label-have-that-rational-formula)
and its cubic prove that there is exactly one such ordered placement:
(α,β). Continuity therefore keeps C>s on the entire open branch.

The requirement rises continuously from the switch to S*, so the
two branches exhaust [s₀,S*]. The total decreases strictly: on the
second branch `dT/dx=Aₓ+BᵧF′(x)/F′(y)>0`, and x moves downward.
Each point is therefore efficient, and the unique supports exclude
every competing placement. This is the complete frontier.

## Reproduce

```sh
python3 experiments/cubic_frontier.py
python3 experiments/cubic_frontier.py --write
python3 experiments/cubic_frontier.py --x 7/4
python3 experiments/cubic_frontier_figure.py
```

Only the Python standard library is needed. All accepted signs and
root enclosures use exact rational arithmetic. The program checks
64 reconstructions of the Bernstein identities, eight complete
clipped arrangements and their 24 faces, five endpoint precisions,
and seven invalid controls. These finite checks audit the implementation;
the continuous sign identities and the supporting argument prove the
classification.

At x=7/4, the second label is about 2.520561337966. Both triangular
areas are about 1.356168525976, and total area is about 4.800178942642.
The rational JSON keeps bounds, rather than trusting these decimals.
