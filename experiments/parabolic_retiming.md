# Each clock correction squeezes the triangle twice

The [three limiting parabolas](parabolic_triangle.md) meet at the
corrected clock μ=c₁. At a finite distance M, however, the actual
plane triple has further time corrections. A small pocket remains
if we stop the clock after its first correction.

For a generic smooth front triple, that pocket has area of order
**1/M³**, compared with **1/M** at the original front meeting.
The symmetric polynomial example cancels another clock coefficient:
its remaining area is of order **1/M⁵**. Four fresh rational
certificates below enclose that smaller area, including at M=10²⁰.
These are local selected-branch results. They do not assert that
the pocket is a face of a larger drawing or give a numerical threshold
for the whole movie.

## One more term in the clock

Use the [earlier radial coordinates and convention](radial_limit.md).
Translate the front event to `(α,s)=(0,0)` and write, at that event,

```
hᵢ=h₀,       hᵢ,α=pᵢ,       hᵢ,s=bᵢ,
hᵢ,αα=kᵢ,   hᵢ,αs=dᵢ,      hᵢ,ss=eᵢ.
```

The angular slopes pᵢ are distinct, and the event matrix is nonsingular:

```
J = [ p₀−p₁    b₀−b₁ ]
    [ p₀−p₂    b₀−b₂ ].
```

The first drift `(a₁,c₁)` already solves

```
J (a₁,c₁)ᵀ = −½(p₀²−p₁², p₀²−p₂²)ᵀ.
```

For a smooth family, the fixed-polar-angle graph has the expansion

```
Dᵢ,M(α,s) = hᵢ + hᵢ,α²/(2M)
                    + hᵢ,α²(hᵢ+hᵢ,αα)/(2M²) + O(M⁻³).
```

Every right-hand function in this formula is evaluated at `(α,s)`.
Substitute the event expansions

```
α_M = a₁/M+a₂/M²+O(M⁻³),
s_M = c₁/M+c₂/M²+O(M⁻³).
```

Put `nᵢ=a₁+pᵢ`, the first normal-angle coefficient of branch i. The
second-order residual has the compact expression

```
rᵢ = kᵢ nᵢ²/2 + dᵢ nᵢ c₁ + eᵢ c₁²/2 + h₀ pᵢ²/2.
```

Thus the same event matrix gives the next clock and angle coefficients:

```
J (a₂,c₂)ᵀ = −(r₀−r₁, r₀−r₂)ᵀ.
```

The common second height coefficient is
`z₂=pᵢa₂+bᵢc₂+rᵢ`. The normal angles have second coefficients

```
mᵢ = a₂+kᵢnᵢ+dᵢc₁+h₀pᵢ,
θᵢ,M = nᵢ/M+mᵢ/M²+O(M⁻³).
```

There is a useful check on the common-height term: if all second
derivatives vanish, `(a₂,c₂)=h₀(a₁,c₁)`. Changing the common height
has replaced the effective offset M by M−h₀, as it should.

### A Cartesian check of the expansion

The program also substitutes the rational jets directly into
`qᵢ=(hᵢ−M)N+hᵢ,θN′`. It does not use the radial expansion for this
check. With ε=1/M, `θᵢ=nᵢε+mᵢε²` and
`s=c₁ε+c₂ε²`, the common coefficients are

```
qₓ = −1/ε+h₀ + (z₁+a₁²/2)ε
                    + (z₂+a₁a₂−h₀a₁²/2)ε² + O(ε³),
qᵧ = −a₁ + (h₀a₁−a₂)ε + O(ε²).
```

The exact sine, cosine, and support-polynomial jets must give these
same values on all three branches. Terms omitted from θ at order
ε³ do not affect the displayed coefficients: their contributions
cancel in qₓ and enter qᵧ only at ε².

## Why an extra clock term buys two area powers

Let `V=|(p₀−p₁)(p₀−p₂)(p₁−p₂)|` and

```
K = (det J)²/(2V) = V/(8c₁²) > 0.
```

In the stretched plane, the limiting triangle has exact area
`K(μ−c₁)²`. The finite stretched family extends smoothly through
ε=0. Its pairwise crossings remain transverse, and its ordinary
triple occurs at a smooth clock

```
μ*(ε) = c₁+c₂ε+c₃ε²+⋯.
```

Near that event, the three pairwise crossings vary smoothly with μ
and ε. Integrate the three boundary arcs with a consistent orientation.
The signed area and its first μ derivative vanish at μ=μ*(ε).
Taylor's formula therefore factors its positive local area as

```
stretched area = (μ−μ*(ε))² L(μ,ε),
L(c₁,0)=K>0,
```

where L is smooth. Positivity follows from K>0 and continuity in a
small neighborhood. This is the usual
[quadratic triple-area argument](triple_area.md), applied to a family
that is regular even at ε=0. The physical area is exactly ε times
the stretched area.

If the clock stops at `s=c₁/M`, then μ=c₁ and
`μ−μ*(ε)=−c₂ε+O(ε²)`. Consequently

```
A_M(c₁/M) = K c₂²/M³ + O(M⁻⁴).
```

For c₂≠0 this is a positive inverse-cube leading law. If c₂=0,
the next clock error is O(ε²) in μ and the area is O(M⁻⁵).
Correcting a generic clock through c₂ has that same improvement.

More generally, truncate the event clock through its nth term,
`s̃_M=Σ[j=1,n] cⱼ/Mʲ`, with n≥1. The first omitted coefficient gives

```
A_M(s̃_M) = K cₙ₊₁²/M^(2n+1) + O(M^−(2n+2)).
```

If the omitted coefficient vanishes, the stated leading coefficient
is zero and the area is smaller still. Each additional matched clock
term gains two powers of distance. These Taylor statements hold
locally for sufficiently large M; no explicit uniform error constant
or finite-M threshold is inferred from them.

## An asymmetric second-order example

For a concrete smooth local family, take quadratic support graphs

```
hᵢ(θ,s) = h₀+pᵢθ+bᵢs+kᵢθ²/2+dᵢθs+eᵢs²/2,

h₀ = 3/5,
p = (−2,1,2),       b = (0,1,0),
k = (1,−2,3),       d = (−1,2,0),       e = (2,1,−1).
```

Their exact coefficients are

```
a₁=0,       c₁=3/2,
a₂=19/32,   c₂=519/160,   z₂=581/80,
K=2/3,      Kc₂²=89787/12800=7.014609375.
```

Independent numerical four-variable triple solves recover the second
clock coefficient. Separate two-variable pair solves and sampled
arc boundaries give the residual area at `s=3/(2M)`:

| M | M(Ms_M−3/2), numerical | M³ × residual physical area, numerical |
| ---: | ---: | ---: |
| 64 | 3.49700120 | 8.37459358 |
| 256 | 3.30391870 | 7.33288798 |
| 1024 | 3.25861106 | 7.09291365 |
| 8192 | 3.24560116 | 7.02435207 |
| Limit | 3.24375 | 7.014609375 |

Two other quadratic families have nonzero first angular shifts and
different clock signs. Their numerical events and residual pockets
approach the exact second-order formulas too. These quadratic graphs
are local examples, not a proposed global route between the orbital
drawings.

For the explicit asymmetric quadratic family, one more Cartesian jet
order gives `c₃=48503/3200`. Stopping at
`s=3/(2M)+519/(160M²)` now gives

```
M⁵ × area → (2/3)(48503/3200)²
           = 2352541009/15360000 ≈ 153.160221940104.
```

The numerical scaled areas are 159.39086258 at M=256,
154.68942970 at M=1024, and 153.35035707 at M=8192. The other two
quadratic families also show the two-power improvement after matching
c₂. Their exact third coefficients come from substituting unknown
third normal and clock coefficients in the Cartesian jets and solving
the resulting rational four-variable system. This uses the **explicit
quadratic support families**; a general smooth family needs its third
derivatives too. Its Hessians alone do not determine c₃.

## The symmetric model leaves a fifth-order pocket

Return to the [polynomial three-arc family](radial_limit.md#a-clock-we-can-enclose):

```
h₀(θ)=f(θ),       h₁(θ,δ)=δg(θ),       h₂(θ)=−f(θ),
f=(15θ−10θ³+3θ⁵)/8,       g=(1−θ²)³.
```

Here the common height, angular second derivatives, mixed derivatives,
and route second derivatives all vanish at the front triple. Hence
all rᵢ vanish and c₂=0. The earlier all-offset certificate already
supplies the next coefficient; there is no need to solve it again:

```
c₁=225/128,       c₃=−151875/32768,
δ_M=c₁/M+c₃/M³+O(M⁻⁵).
```

Stop at the leading corrected clock `δ=c₁/M`. Since K=8/15, the
factorization gives

```
M⁵ A_M(c₁/M) → (8/15)c₃²
              = 1537734375/134217728
              ≈ 11.457013897598.
```

There is also a direct geometric check of this coefficient. At the
actual triple, the two outer tangents lean by angles ±x from vertical,
and the middle tangent is vertical. Changing δ moves that middle
line horizontally by the same amount to first order. The triangle
of tangent lines has width |Δδ| and base `2|Δδ|cot x`, so its area
coefficient is exactly cot x. Since Mx→15/8, `cot x/M→8/15`.
Combining that with the clock error c₃/M³ gives the same fifth-order
coefficient. This tangent calculation is local at the true event;
the finite arc integrals below enclose the actual curved pocket.

This is a different pocket area from yesterday's `δ=0` calculation.
At M=25 the new area is enclosed by

```
0.0000011493597359649302572 < area
                          < 0.0000011493597359649302573.
```

Compare that with about 0.06564280426 at δ=0. Advancing the clock
has left a much smaller triangle, rather than making the finite
drawing meet at exactly the leading-order time.

### Fresh rational finite-area certificates

There is no subtraction of nearby floating-point areas in these
enclosures. The exact parameter is the rational number c₁/M.

First isolate the outer/middle crossing in scaled normal angles
`(σ₀,σ₁)=(Mθ₀,Mθ₁)`. Rational Newton midpoints supply a candidate.
An interval Jacobian then proves that `T=x−RF(x)` has derivative
infinity norm below 1/100 and maps the proposed dyadic box strictly
inside itself. This certifies one unique crossing in that box.
The outer/outer crossing is enclosed independently by the older
one-variable alternating-Taylor proof. Reflection gives the third
crossing.

All three selected arcs are decreasing height graphs on disjoint
normal slots. Their graph slopes `dX/dY=−M tan θ` are strictly
ordered, so each pair can meet at most once in these slots. The
certified crossings are distinct and their connecting arcs bound
one local pocket. This excludes extra intersections among those
three short arcs; it says nothing about other branches of a drawing.

For a polynomial support graph h, the Green integrand is itself a
polynomial:

```
det(q,q′) = (h−M)(h+h″−M).
```

Let P_f and P_δg be its primitives, chosen to vanish at zero.
If x is the positive outer/outer angle and `(u,t)` the outer/middle
pair of angles, reflection gives the unsigned area

```
area = |P_f(x)−P_f(u)+P_δg(t)|.
```

Evaluate those primitives on the rational root boxes. All cancellation
happens before rounding or decimal formatting. The four finite
certificates give:

| M | Strict rational enclosure of M⁵ × area, rounded outward |
| ---: | --- |
| 25 | (11.224216171532, 11.224216171533) |
| 100 | (11.442175282767, 11.442175282768) |
| 10⁶ | (11.457013897449, 11.457013897450) |
| 10²⁰ | (11.457013897597, 11.457013897598) |

The last enclosure still proves strictly positive area despite its
physical size of about 1.1457×10⁻⁹⁹. It also resolves the tiny deficit
of the scaled area below its limit. These four exact finite examples
support the analytic limit independently; they do not prove a uniform
area remainder over the whole half-line. The numerical sampled area
at M=25 agrees with the exact integral and is not used to accept a root.

### The next coefficient, without a half-line remainder bound

The stretched Cartesian family is analytic in τ=1/M²: f is odd,
g is even, and the apparent negative powers cancel in the stretched
coordinates. The outer root's earlier coefficients are

```
x = (15/8)/M − (1125/128)/M³ + (860625/8192)/M⁵ + O(M⁻⁷).
```

Substitute that series directly into
`δ=f(x)−f′(x)tan(x/2)`. Exact Taylor composition gives

```
c₅ = 160228125/4194304,
μ*(τ) = c₁+c₃τ+c₅τ²+O(τ³).
```

The direct root-equation jet also cancels exactly through τ².
Writing a=15/8, the tangent-area check gives

```
L(μ*(τ),τ) = cot x/M = 1/a+aτ+O(τ²).
```

At τ=0, the entire parabolic movie has exactly quadratic area, so
`L(μ,0)=1/a` throughout a neighborhood and its μ derivative vanishes.
Since `μ*(τ)−c₁=O(τ)`, changing from μ*(τ) to c₁ affects L only
at order τ². The same two displayed coefficients therefore apply to
`L(c₁,τ)`. Substituting the squared clock error yields

```
A_M(c₁/M) = 1537734375/(134217728 M⁵)
             − 638159765625/(4294967296 M⁷) + O(M⁻⁹).
```

The seventh-order coefficient is `a c₃²+2c₃c₅/a`, about
−148.583148984471. For an independent finite check, the exact
M=10²⁰ enclosure resolves
`M²[1537734375/134217728−M⁵A_M]` near +148.583148984471.
This closes another Taylor coefficient. It does **not** provide a
uniform constant for the O(M⁻⁹) remainder or assert an inequality
over every M≥25.

## Reproduce

Only the Python standard library is needed:

```sh
python3 experiments/parabolic_retiming.py
python3 experiments/retimed_pocket.py
```

The first program checks rational second-order coefficients, direct
Cartesian Taylor jets, the independent determinant area formula,
common-height changes, relabelings, and the symmetric cancellation.
It separately solves finite numerical triples and pockets, using two
boundary resolutions. The second program certifies its four finite
areas afresh, reading no archived roots or numerical hints. Its
rational trigonometric bounds, root boxes, contraction matrices, and
Green integrals use exact arithmetic throughout.

No new whole-movie crossing census, numerical middle threshold, or
all-offset area tail is claimed. The limiting parabolas and the two
drawings remain the simpler way to see why the area is quadratic in
the clock error.
