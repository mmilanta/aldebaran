# Why the first branch is so short

The [four-curve frontier drawing](cubic_frontier.svg) needs an enlarged
graph for its first stage: one triangle grows before the two triangles
tie. A constant-curvature family has no such stage; its total optimizer
already has equal triangles. The cubic family approaches that case in
a surprisingly flat way.

As the curvature variation tends to zero, the first stage's **relative
minimum gain is cubic** in the perturbation, while its **relative total
cost is sixth order**. Their ratio has the simple limit

```
relative total cost / (relative minimum gain)² → 1/12.
```

This is an asymptotic theorem for every sufficiently small positive
perturbation. It supplies **no explicit perturbation threshold**, no
uniform numerical remainder bound, and no complete arbitrary-endpoint
frontier classification. The [complete [1,3] proof](cubic_frontier.md)
has its own exact continuous certificates and remains separate.

## Normalize the endpoint span

For original positive endpoints a<b, put

```
L=b−a,  q=1+3a/L,  ε=1/q=L/(L+3a).
```

Use normalized interior labels x,y in (0,1); the original labels are
`a, a+Lx, a+Ly, b`. In this note, scale every area by `18/(L⁵q²)`.
The complete face formulas become

```
Aε = x(y−x)y [1+ε(x+y−1)]²,
Bε = (y−x)(1−y)(1−x) [1+ε(x+y)]²,
Fε(x) = x(1−x)(1+εx)²,
Cε = Fε(x)−Aε,
Tε = Fε(x)+Bε.
```

The common scale cancels from relative changes. For the endpoints
[1,3], ε=2/5. Its displayed percentages come from the exact finite
certificate, rather than substituting 2/5 into an unbounded asymptotic
remainder.

At ε=0,

```
T₀ = [1−x³−(y−x)³−(1−y)³]/3.
```

Strict convexity of the gap cube gives the unique total optimizer
`(x,y)=(1/3,2/3)`. The two triangles have scaled area 2/27,
the quadrilateral 4/27, and the total 8/27.

## Two smooth root families

Write `(x₀(ε),y₀(ε))` for the total optimizer. Write
`(xₛ(ε),yₛ(ε))` for the nearby solution of `Aε=Bε`, `∂yTε=0`.
Both start at (1/3,2/3). Their defining systems are

```
total:  (∂xTε, ∂yTε) = (0,0),
switch: (Aε−Bε, ∂yTε) = (0,0).
```

At ε=0, their Jacobians with respect to (x,y) are

```
total:  [ −4/3   2/3 ]     switch: [ 1/3   1/3 ]
        [  2/3  −4/3 ],            [ 2/3  −4/3 ].
```

Their determinants are 4/3 and −2/3. Thus the implicit function
theorem gives unique nearby root families. Repeated differentiation
of the polynomial identities makes them smooth to every order.
The standard theorem and derivative formula are described in the
University of Toronto's
[multivariable calculus notes](https://www.math.toronto.edu/courses/mat237y1/20199/notes/Chapter3/S3.1.html).
Here all needed Jacobians and Taylor coefficients are computed exactly.

The [standard-library program](cubic_frontier_limit.py) solves the
coefficient equations recursively with rational arithmetic. Through
cubic order they give

```
x₀ = 1/3 + 2ε/9 −  2ε²/81 − 14ε³/243 + O(ε⁴),
y₀ = 2/3 + 2ε/9 − 16ε²/81 + 28ε³/243 + O(ε⁴),

xₛ = 1/3 + 2ε/9 −  2ε²/81 − 10ε³/81  + O(ε⁴),
yₛ = 2/3 + 2ε/9 − 16ε²/81 + 20ε³/243 + O(ε⁴).
```

Both coordinates agree through second order. Their displacement is

```
(xₛ−x₀, yₛ−y₀) = (−16,−8) ε³/243 + O(ε⁴).
```

At the total optimizer, `Aε−Bε = 8ε³/243 + O(ε⁴)>0`, so B
really is the smaller triangle for small positive ε.

## The gain is cubic

Let `s₀=Bε(x₀,y₀)` and `sₛ=Aε(xₛ,yₛ)=Bε(xₛ,yₛ)`. Exact
substitution gives

```
sₛ−s₀ = 16ε³/729 + O(ε⁴).
```

Since s₀→2/27, the relative gain is

```
g = (sₛ−s₀)/s₀ = 8ε³/27 + O(ε⁴).
```

## Stationarity squares the cost

Let `H₀` be the total system's base-point Jacobian, which is also
the Hessian of T₀. The total optimizer has zero gradient. With
`v=(−16,−8)/243`, Taylor expansion around it therefore gives

```
Tε(x₀,y₀)−Tε(xₛ,yₛ)
  = −(vᵀH₀v/2) ε⁶ + O(ε⁷)
  = 128ε⁶/59049 + O(ε⁷).
```

The limiting total is 8/27, so the relative cost is

```
c = 16ε⁶/2187 + O(ε⁷),
c/g² → 1/12.
```

The program reconstructs both root jets through order six, checks
**28 zero equation-residual coefficients**, and confirms that the
total loss has zero coefficients through order five. Its independent
Hessian quadratic form gives the same sixth-order coefficient.

## Why this describes an actual first frontier branch

The implicit equations alone would only describe stationary candidates.
There is a global argument for every sufficiently small ε>0.

On the compact closed ordered triangle `0≤x≤y≤1`, Tε converges
uniformly to T₀. The latter has its unique maximum at (1/3,2/3).
Choose a small convex rectangle U around that point, within the open
ordered triangle. For small enough ε, every placement whose total
is at least the switch total lies in U: otherwise a sequence of such
placements outside U would limit to a second maximizer of T₀.

H₀ is negative definite. By continuity, shrink U and the perturbation
interval so that Tε is strictly concave throughout U. The quadrilateral
also stays strictly larger than either nearby triangle, because its
base-point area is twice theirs.

Locally `∂yTε=0` defines `y=rε(x)` with `r₀′(1/3)=1/2`.
Along it, the derivative of `Aε−Bε` tends to 1/2, so it is positive.
The expansions above give xₛ<x₀ and positive triangle difference at
x₀. Thus for every x between them, `Aε≥Bε` and `Cε>Bε`.
Also `Bε,x<0`, so the minimum rises strictly as x decreases.

For `Mε(x)=Tε(x,rε(x))`, strict concavity gives
`Mε″=Tε,xx−Tε,xy²/Tε,yy<0`. Since Mε′(x₀)=0,
`Tε,x>0` before x₀. Consequently `λ=−Tε,x/Bε,x≥0` and

```
∇Tε + λ∇Bε = 0.
```

For the requirement `s=Bε(x,rε(x))`, the function
`Tε+sλ log(Bε/s)` is strictly concave on U and stationary at the
candidate. Its value bounds every feasible competitor's total from
above, by the same
[supporting argument](cubic_frontier.md#a-support-proves-global-optimality)
as in the finite proof. Competitors outside U already have smaller
total. This proves the unique global total optimum for every minimum
between s₀ and sₛ. The switch is its first triangle tie; no
quadrilateral tie precedes it.

The compactness argument establishes existence of a positive
perturbation range. It does not provide a numerical endpoint for it.
The rest of the general-endpoint frontier remains an open question.

## Reproduce

```sh
python3 experiments/cubic_frontier_limit.py
```

There are no dependencies or saved numerical roots. Rational Taylor
arithmetic reconstructs all coefficients; the nonsingular systems,
smooth implicit function theorem, and global argument above justify
the asymptotic statements and their optimization meaning.
