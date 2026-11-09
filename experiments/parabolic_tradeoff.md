# Every compromise follows alternating gaps

The [smallest-pocket calculation](parabolic_balance.md) found different
optima for total area and for the smallest area. Between those two
ends, which arrangements improve one objective as little as possible
when improving the other?

For every even slope count, the complete efficient curve uses alternating
gaps. It is an exact cubic in the two area coordinates. Odd counts have
no tradeoff: equal gaps uniquely maximize both objectives.

![Six equally spaced slopes and a rational alternating arrangement, each with ten named pockets. The alternating arrangement increases the smallest area from 16/125 to 5/36 while reducing the total from 64/25 to 275/108. A cubic graph follows every efficient compromise through the irrational smallest-area optimum.](parabolic_tradeoff.svg)

These are the complete exact parabolas `Xᵢ=(Y−pᵢ)²/2`, with distinct
slopes and fixed outer slopes of span L. The result concerns their
bounded pockets at limit parameter zero. It makes no assertion about
faces of a finite orbital drawing.

## The whole curve

Let n=2k+2 be even, and put m=n−1=2k+1. Use gaps

```
a, b, a, b, …, a, b, a,
(k+1)a + kb = L,
t = b/a.
```

All efficient arrangements, and only those arrangements, have this
form, with

```
1 ≤ t ≤ 2,                          n=4,
1 ≤ t ≤ [1+√(k²+k+1)]/k,           n≥6.
```

Here efficient means that no other arrangement has at least as much
total area and at least as large a smallest area, with one inequality
strict. Once the outer slopes and the two objective values are fixed,
the arrangement on this curve is unique.

The formulas become cubic if we use the normalized half-difference
u=(b−a)/(2L). The mean gap c=(a+b)/2 satisfies L=mc−Lu, so

```
a = L[1−(m−1)u]/m,
b = L[1+(m+1)u]/m.

B(u) = L³(1−1/m²)/24 − L³(m²−1)u²(3+2u)/(24m²),
S(u) = L³[(1+u)³−m²u²(1+u)]/(4m³).
```

B is the total bounded area; S is the smallest individual area.
The parameter starts at zero. It ends at

```
u_end = 1/8,                                       n=4,
u_end = [m√(m²+3)−m²+3]/[3(m²−1)],                 n≥6.
```

For n≥6 the latter is the positive root of
`3−2(m²−3)u−3(m²−1)u²=0`. The four-slope end occurs earlier:
its quadrilateral catches up with the two triangular pockets at t=2.

## Why these are the two area coordinates

The [band formula](parabolic_pockets.md#follow-the-nearest-slope)
is `B=(L³−Σgᵢ³)/24`. Substituting the alternating gaps gives B(u).
Every adjacent triangular pocket has area `ab(a+b)/8`, giving S(u).

No longer-run pocket is smaller while 1≤t≤2. A longer run with
different end gaps has the same ab factor and a larger middle sum.
A run with two short end gaps has area at least `a²(a+b)/4`,
which is `(2/t)S`. With two long end gaps its area is at least
`b²(a+b)/4=2tS`. At t=2 a longer run can tie; it cannot undercut S.
For n≥6 the final t is strictly less than two.

Along the specified interval,

```
B′(u) = −L³(m²−1)u(1+u)/(4m²),
S′(u) = L³[3−2(m²−3)u−3(m²−1)u²]/(4m³).
```

Thus B decreases strictly and S increases strictly from one end to
the other. A zero derivative at an endpoint does not spoil strict
monotonicity on the closed interval. This establishes a tradeoff
within the alternating family. It remains to exclude every other
choice of gaps.

## A supporting bound for arbitrary gaps

Fix an interior candidate a,b on the stated curve, with smallest
area T=ab(a+b)/8. Write

```
f(x,y) = [xy(x+y)]^(1/3),
U = (1/a+1/(a+b))/3,
V = (1/b+1/(a+b))/3.
```

AM–GM on the three positive ratios x/a, y/b, and (x+y)/(a+b)
gives the supporting line

```
f(x,y)/f(a,b) ≤ Ux + Vy.
```

Reverse U,V when the reference pair is b,a. Now take any positive
gap sequence x₀,…,x₂ₖ summing to L whose **every** bounded pocket
has area at least T. Its adjacent triangles do too. Consequently
each of these linear expressions, denoted ℓᵢ, is at least one.

We need positive weights that make these pair inequalities add up
to the gradient of the cube sum. Put

```
r = U/V = t(t+2)/(2t+1),
λ = 3[(k+1)a²−krb²]/[kr−k−1],
H = (3a²+λ)/U,

μ₂ⱼ   = (k−j)H/k,
μ₂ⱼ₊₁ = (j+1)H/k,       j=0,…,k−1.
```

These are finite and positive at every interior candidate. Indeed,
r(t) increases strictly for t>0, and `kr=k+1` is precisely the
equation `kt²−2t−(k+1)=0` defining the larger-even optimum. Its
denominator here is therefore negative. Also

```
3a²+λ = 3kr(a²−b²)/(kr−k−1) > 0
```

because t>1. Four slopes stop at t=2 before that denominator
vanishes, so the same argument applies to them.

Let yᵢ denote the candidate gaps. Summing the weighted pair lines
gives the coefficient `HU=3a²+λ` at each even gap. At each odd
gap the coefficient is `(k+1)HV/k=3b²+λ`. Thus

```
Σ μᵢ(ℓᵢ−1) = Σ (3yᵢ²+λ)(xᵢ−yᵢ) ≥ 0.
```

Each reference pair has ℓᵢ=1; the fixed-span condition cancels λ.
Finally, the elementary identity

```
x³−y³−3y²(x−y) = (x−y)²(x+2y)
```

proves

```
Σ xᵢ³ − Σ yᵢ³
  = Σ μᵢ(ℓᵢ−1) + Σ (xᵢ−yᵢ)²(xᵢ+2yᵢ)
  ≥ Σ (xᵢ−yᵢ)²(xᵢ+2yᵢ) ≥ 0.
```

Preserving the candidate's minimum therefore cannot increase its
total area. Equality forces every xᵢ=yᵢ, since all gaps are positive.
This is a global bound over arbitrary gap sequences, without an
assumption of symmetry or alternation for the challenger.

It also quantifies uniqueness. If a challenger keeps minimum at
least T and loses total area ΔB, then

```
24ΔB ≥ Σ (xᵢ−yᵢ)²(xᵢ+2yᵢ) ≥ 2a Σ (xᵢ−yᵢ)².
```

A nearly optimal total under that minimum constraint must have
gaps close to the alternating candidate.

## Why this lists every efficient arrangement

At u=0, equal gaps uniquely maximize B by the cube-sum inequality.
At u_end, the [smallest-pocket theorem](parabolic_balance.md) uniquely
maximizes S. These separate endpoint proofs avoid taking an infinite
support weight at the larger-even endpoint.

Every interior alternating candidate is efficient by the supporting
bound. Conversely, consider any other arrangement. If its smallest
area is at most the equal-gap minimum, equal gaps dominate it.
If its minimum lies strictly between the two endpoint minima,
strict monotonicity of S gives a unique interior candidate with
exactly that minimum. The supporting bound says that candidate
has at least as much total area, strictly more unless the gaps
already agree. A minimum equal to the final maximum forces the
endpoint arrangement; a greater minimum is impossible.

This exhausts all possibilities. Odd counts are simpler: their
unique equal-gap arrangement maximizes both measures, so it
dominates every other arrangement.

## Read the six-slope drawing

The two pictured arrangements have fixed outer slopes −2,+2 and
ten pockets each. Letters A–J name the same consecutive runs in
both. Equal gaps 4/5 give

```
total = 64/25 = 2.56,
smallest = 16/125 = 0.128.
```

The rational example has slopes `(−2,−4/3,−1/3,1/3,4/3,2)` and
gaps `(2/3,1,2/3,1,2/3)`. Here u=1/24 and

```
total = 275/108 ≈ 2.546296296296,
smallest = 5/36 ≈ 0.138888888889.
```

Its ten areas are four at 5/36, two at 5/27, one at 10/27, and
three at 5/12. Improving the smallest pockets shrinks some larger
ones; it does not enlarge every pocket.

The final point has `u_end=(5√7−11)/36`, total
`(1156+260√7)/729≈2.529348890092`, and smallest area
`(−40+28√7)/243≈0.140251179876`. Its gaps begin
`a=4(4−√7)/9`, `b=2(√7−1)/3`. These are exact algebraic
coordinates; the printed decimals and SVG coordinates are rounded.

The area graph is one cubic Bézier because both B(u) and S(u) are
cubic. For v=u/u_end, its exact controls are

```
P₀ = (B(0), S(0)),
P₁ = P₀ + (u_end/3)(B′(0), S′(0)),
P₂ = P₃ − (u_end/3)(B′(u_end), S′(u_end)),
P₃ = (B(u_end), S(u_end)).
```

The record stores rational-plus-radical values, including these
controls. Rounding occurs only when generating the SVG. The two
parabola panels have identical unit scales on both axes. Only the
area graph uses separate scales for its two different measures.

## Put a price on a larger minimum

Suppose an extra unit of smallest-pocket area is worth η units of
total area. Maximize `B+ηS`, with η≥0. This question has a unique
global answer as well, not merely a stationary alternating candidate.

Write `D=3−2(m²−3)u−3(m²−1)u²`. At an interior point, its marginal
price is

```
η(u) = −B′(u)/S′(u) = m(m²−1)u(1+u)/D,
η′(u) = m(m²−1)[3+6u+(m²+3)u²]/D² > 0.
```

Thus B, considered as a function of S, is strictly concave: the
price of the next increment of minimum strictly increases. Its
tangent line bounds the whole efficient curve from above, and the
complete-frontier theorem bounds every other arrangement below it.
Consequently the tangent point uniquely maximizes `B+ηS`.

One can also select it directly. The derivative of `B+ηS` has the
sign of

```
3η − [2η(m²−3)+m(m²−1)]u − (m²−1)(3η+m)u².
```

For η>0 this is strictly decreasing for u≥0 and has one positive
zero. At larger-even counts that zero lies before u_end, because
the derivative at u_end is B′<0. With four slopes, use that root
until η=3, and use the endpoint u=1/8 for every η≥3. For η=0,
equal gaps uniquely maximize the total. Odd counts always keep
their shared equal-gap optimum.

If η=p/q is rational, multiply that quadratic by q. Its integer
coefficients give the selected u by an exact square root. The
program retains that quadratic field and compares the endpoint
using D(u)≥0, so it need not mix unrelated radical fields or round
an algebraic order test.

For the six-slope rational example, u=1/24 gives
`B′=−2/3`, `S′=2/15`, hence η=5. It is the **unique global
maximizer of B+5S**, with value 175/54. The dashed green line in
the drawing holds that score constant; the whole curve lies below
it and touches it just at the green point.

## The first gain costs only quadratically

Normalize the total loss and minimum gain by their equal-gap values:

```
δ = (B(0)−B(u))/B(0) = 3u²+2u³,
ρ = (S(u)−S(0))/S(0) = 3u−(m²−3)u²−(m²−1)u³.
```

The relative total loss has the same expression for every even
count. For a fixed count and a very small positive u,
`ρ=3u+O(u²)` while `δ=3u²+O(u³)`. Eliminating u gives
`δ=ρ²/3+O(ρ³)`: the first relative gain in the minimum costs only
quadratically in relative total area.

This expansion fixes m. It is not a uniform statement as the number
of slopes grows: the coefficient of u² in ρ itself grows like m².
For example, the maximin end has `u_end≈3/(2m²)`, relative minimum
gain `9/(4m²)+O(m⁻⁴)`, and relative total loss
`27/(4m⁴)+O(m⁻⁶)`. The two different limits should not be interchanged.

## Reproduce

```sh
python3 experiments/parabolic_tradeoff.py
python3 experiments/parabolic_tradeoff.py --write
node experiments/parabolic_pockets_figure.js
python3 experiments/parabolic_tradeoff.py --slopes 6 --price 5
```

Only standard runtimes are needed. The default calculation checks
126 exact frontier arrangements through twenty slopes, 385 support
challengers, twelve fresh complete clipped line arrangements with
independent curved integrals, seven invalid inputs, and 185 exact
cubic matches across four through twelve slopes. The support controls
include algebraic candidates, permutations, and rational challengers
on either side of the target minimum. They verify cubed AM–GM bounds,
positive weights, every gap coefficient, and the exact square remainder.
No rounded radical or numerical optimizer determines an inequality.
Another 66 exact price-selection/invalid controls include 180 rational
score challengers, odd counts, the four-slope cutoff, and the exact
price-five rational example. The optional price command prints its
selected gaps and score as exact rational-plus-radical values.

The finite controls audit formulas; the weighted inequality and
endpoint/dominance argument above prove the complete all-count result.
Use `--max-slopes 40` for additional arrangement controls.
