# Three pockets, the same room

Four [shifted parabolas](shifted_parabolas.md) can make their three
pockets equally large. For cubic intercepts and fixed outer labels
1 and 3, this is the **unique** placement with the largest smallest
pocket. Its two interior labels are approximately

```
1.630619586106,  2.611245185918.
```

Every pocket has area about **1.521007779464**. The placement that
[maximizes total area](shifted_placement.md) instead has smallest
area about 1.175535213500. Enlarging that minimum by about 29.39%
costs about 5.77% of the total area.

![Four cubic-intercept parabolas make three pockets. Two arrangements
compare the unique largest-total placement with the unique largest-minimum
placement, using the same coordinates and unit scale. The latter's three
pockets have equal area.](cubic_maximin.svg)

This is a finite theorem about **four complete curves**
`Xₚ(Y)=Y²/2−pY+p³/3`, on the fixed slope interval [1,3]. It neither
classifies their full compromise curve nor solves other finite counts.
The shared [asymptotic density](shifted_maximin.md) is a different result.
The [general four-curve extension](cubic_four_general.md) separately proves
the unique maximin for every fixed positive endpoint pair.
The [five-curve companion](cubic_five.md) separately solves the next count
on these same endpoints by a rational stationary-support certificate.

## The exact answer fits one cubic

Let α be the unique root in [1,3] of

```
8α³ + 20α² − 87α + 54 = 0.
```

The optimum has labels `1, α, β, 3`, where

```
β = (13α−12)/(4α−3) = (4α²+13α−24)/3.
```

Its three equal areas are

```
S* = (α−1)(3−α)(α+4)²/18
   = 47α²/144 + 487α/288 − 101/48.
```

There is just one root on [1,3]. The cubic is convex there and
negative at both 1 and 3/2, so it is negative throughout [1,3/2].
Its derivative is positive beyond 3/2, and its signs at 163/100
and 164/100 are opposite. Thus `1.63<α<1.64`, and the displayed
formula gives `α<β<3`. Rational bisection encloses the root and
all reported areas; no rounded root decides a proof inequality.

## Why does the second label have that rational formula?

There is a geometric reason, valid for **any four discrete strictly
convex intercepts** when their three bounded areas are equal. It
explains the candidate; global optimality still needs the cubic
family's proof below.

![Two middle lines become coordinate axes. One outer line joins
(1,0) to (0,−3), and the other joins (−3,0) to (0,1). They meet at
(3/2,3/2). The two triangles and central quadrilateral each have
area 3/2.](cubic_equal_shape.svg)

Straighten the parabolas, and use the two middle lines as axes.
Explicitly, if `Lᵢ(Y)=hᵢ−pᵢY`, put `r=U−L₁(Y)` and
`s=U−L₂(Y)`. This affine map has positive area factor `p₂−p₁`,
so it preserves area ratios. Write the outer lines' axis intercepts
as `(R,0),(0,−S)` and `(−T,0),(0,V)`, with R,S,T,V positive.
Convexity puts their meeting in the positive quadrant and gives
`ST>RV`.

The triangles have areas RS/2 and TV/2 in these coordinates.
If they are equal, write `S=qV`, `T=qR`, with q>1. The two outer
lines meet at `(Rq/(q−1),Vq/(q−1))`, so their central
quadrilateral has area `RVq/(q−1)`. Equality with either triangle
forces `q−1=2`. Thus `S=3V`, `T=3R`, and rescaling the two axes
gives exactly the diagram. Every equal-area four-line arrangement
has this one affine shape.

For gaps `u=p₁−p₀`, `v=p₂−p₁`, `w=p₃−p₂`, the line directions
give

```
S/R = (u+v)/u,       T/V = (v+w)/w.
```

Their product is 9 at equal areas. Since
`(u+v)(v+w)=uw+v(u+v+w)`, this is precisely

```
8uw = vL,       L=u+v+w.
```

On [1,3], with labels 1,x,y,3, solving this relation gives
`y=(13x−12)/(4x−3)`. It always lies strictly between x and 3
when 1<x<3. Along that relation, equality of the two triangle
areas reduces to the cubic above: the difference `F(x)−F(y)`
from the next section factors as

```
−8(x−3)(x−1)(2x+3)(2x²+2x−3)
  × (8x³+20x²−87x+54) / [9(4x−3)⁴].
```

All factors outside the cubic are nonzero in 1<x<3. This explains
both the rational formula for β and the equation selecting α.

## Name the three areas

Use arbitrary labels `1<x<y<3`. The consecutive-run classification
gives a triangle A, a quadrilateral C, and a triangle B. Their exact
areas are

```
A(x,y) = (x−1)(y−x)(y−1)(1+x+y)²/18,
B(x,y) = (y−x)(3−y)(3−x)(x+y+3)²/18.
```

Put

```
F(r) = (r−1)(3−r)(r+4)²/9.
```

This is the single pocket enclosed by labels 1,r,3. The two such
triangles for r=x,y overlap in C and leave A,B as their respective
remainders. Equivalently, integrate their straightened line
boundaries. Either calculation gives the polynomial identities

```
C(x,y) = F(x)−A(x,y) = F(y)−B(x,y).
```

All three are strictly positive in the open triangle `1<x<y<3`.
They are the **complete** face list, and their sum is the complete
band area. Substituting α and β and reducing polynomial numerators
modulo the cubic proves `A=C=B=S*` exactly. Equality of three
readouts by itself would not prove a maximum; the next two steps do.

## A global concavity certificate

Both log A and log B are concave: each is a sum of logarithms of
positive affine functions. For C, a little exact polynomial
arithmetic proves **strict** log-concavity on the entire open
triangle. Here is the certificate, including its interpretation.

Subscripts denote partial derivatives. Define

```
Hₓ = Cₓ²−CCₓₓ,
Hᵧ = Cᵧ²−CCᵧᵧ,
E  = CₓCᵧ−CCₓᵧ,
D  = HₓHᵧ−E².
```

The xx entry of the Hessian of log C is `−Hₓ/C²`; its determinant
is `D/C⁴`. Thus `Hₓ>0` and `D>0` make that Hessian negative definite.

Set `u=(x−1)/2`, `w=(3−y)/2`, `v=(y−x)/2`. These three numbers
are strictly positive and sum to 1. Expand Hₓ and D after
`x=1+2u`, `y=3−2w`. For each term of degree k, multiply it by
`(u+v+w)^(d−k)`, with d=8 for Hₓ and d=16 for D. This leaves its
value unchanged and produces a homogeneous polynomial.

Every nonzero coefficient is **positive**: Hₓ has 28 positive
terms and D has 91. All omitted coefficients are zero. Since
u,v,w are positive, both polynomial values are strictly positive.
This proves the Hessian signs throughout the continuous domain.
It is a finite algebraic certificate of a global statement, not a
sampling argument.

The [program](cubic_maximin.py) constructs both polynomials from
the face formulas, differentiates and multiplies them with exact
rational arithmetic, and performs the affine substitution and
homogenization explicitly. The [JSON record](cubic_maximin.json)
lists every coefficient, so the certificate is also inspectable
without running symbolic software. No symbolic package is needed
to reproduce it.

## Positive weights support the equal-area placement

At `(α,β)`, let the three vectors `g₁,g₂,g₃` be the gradients
of `log A,log C,log B`, respectively. Put

```
ω₁ = −det(g₂,g₃),
ω₂ = −det(g₃,g₁),
ω₃ = −det(g₁,g₂).
```

For any three two-dimensional vectors,
`ω₁g₁+ω₂g₂+ω₃g₃=0`. Here rational interval evaluation at the
certified root proves all three weights strictly positive. Their
approximate values are 4.861212, 1.770607, and 4.895864.

Consequently the function

```
G(x,y) = ω₁ log A(x,y) + ω₂ log C(x,y) + ω₃ log B(x,y)
```

is strictly concave, and has zero gradient at `(α,β)`. The tangent
inequality for a concave differentiable function proves that this
point is its unique global maximizer on the convex domain.

This supporting-tangent step is the standard differentiable
concavity criterion; see Boyd and Vandenberghe,
[*Convex Optimization*, §3.1.3, pp. 69–70](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf#page=83).
The face formulas, global polynomial signs, and positive weights
needed to apply it here are established above.

If any placement had all three areas at least S*, its G value
would be at least `(ω₁+ω₂+ω₃)log S*`, the value at `(α,β)`.
Strict concavity therefore forces that placement to be `(α,β)`.
This proves the sharp smallest-pocket bound and uniqueness.
When slope labels collide at the boundary of the closed ordered
simplex, at least one triangle has zero area, so no boundary
placement competes with the positive interior value.

## Why the complete compromise is still a separate problem

The logarithm of each face area is concave here. That does not make
their **sum** concave. In fact the total area `total=A+C+B`
has this exact Hessian at `(x,y)=(11/10,29/10)`:

```
[ −7429/4500      3519/500  ]
[  3519/500     −68989/4500 ].
```

Its determinant is `−6131662/253125<0`, so it has a positive as
well as a negative curvature direction. The program derives and
checks these entries from the exact face polynomials. Thus a
globally concave-total shortcut cannot classify the shifted
total/minimum frontier. The smallest-area proof above uses the
individual log-areas and does not need such a shortcut.

## Reproduce

```sh
python3 experiments/cubic_maximin.py
python3 experiments/cubic_maximin.py --write
python3 experiments/cubic_maximin_figure.py
```

Only the standard library is used. In addition to the **continuous
polynomial certificate**, the program audits 32 freshly clipped
arrangements and their 96 faces, 1,711 rational challengers, 64
exact evaluations of the homogenization identities, four invalid
precision controls, and overlapping node and support enclosures
at four precisions. The challenger grid is an implementation check;
the concavity and positive-weight argument proves the global result.
Sixty additional affine controls check general discrete-convex
intercepts and twenty exact equal-area examples among them. The
geometric reduction's displayed univariate factorization is checked
as an exact polynomial identity.

The drawing uses rounded coordinates from the rational node boxes.
Both panels share coordinates and unit scale. The areas in its table
are rounded readouts; the JSON retains rational lower and upper
bounds. The comparison's total-area optimum is freshly certified
by the earlier monotone shooting calculation.
The same figure command also regenerates the affine shape diagram;
its three polygon areas are exactly 3/2 in its labeled coordinates.
