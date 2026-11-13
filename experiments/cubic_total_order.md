# One pocket outweighs the other two

At the largest-total placement of four cubic-intercept parabolas,
the quadrilateral has **more area than both triangles combined**.
Of those two triangles, the first is strictly larger than the second:

```
C > A+B,       A > B > 0.
```

These strict inequalities hold for **every fixed positive endpoint
pair**, not only the spans covered by the
[finite frontier certificate](cubic_frontier_bounds.md).
Thus B is always the sole smallest pocket at the total optimizer,
and C takes more than half of the total bounded area.

This classifies the area ordering at one optimum. It does **not**
classify the whole frontier for arbitrary positive endpoints.
The [complete [1,3] frontier](cubic_frontier.md) and the uniform
frontier on `1<b/a≤4/3` remain separate results.

## Move to the two midpoints

The curves are `Xₚ(Y)=Y²/2−pY+p³/3`. Write their original labels as

```
a = c−l,       b = c+l,        0<l<c,
x = c+h−d,     y = c+h+d.
```

Here c is the midpoint of the two fixed outer labels; c+h is the
midpoint of the two movable labels. The
[finite total-area theorem](shifted_placement.md) gives a unique
global optimizer and strictly decreasing gaps. Its first and last
gaps differ by 2h, so **h>0** at that optimizer. Also d>0.

At the total optimum, the neighboring-label stationarity equations are

```
4x²−x(a+y)−a²−y² = 0,
4y²−y(x+b)−x²−b² = 0.
```

Their sum and difference reduce to

```
3ch+4d²−dl+2h²−l² = 0,
(9c+10h)d = (3c+h)l.
```

Put

```
k = 9c+10h,
D = 72c²+195ch+106h²,
N = h(243c³+702c²h+660ch²+200h³).
```

Both denominators below are positive. Substituting the second
equation into the first gives the simple rational parameterization

```
d = l(3c+h)/k,       l² = N/D.
```

## Two positive factorizations

The complete face formulas in original labels are

```
A = (x−a)(y−x)(y−a)(a+x+y)²/18,
B = (y−x)(b−y)(b−x)(x+y+b)²/18,
C = (x−a)(b−x)(b−a)(a+x+b)²/18 − A.
```

Substitute the rational midpoint relations. Exact simplification gives

```
A−B = 32h³(3c+h)³(3c+2h)²(9c+10h) / (9D²),

C−A−B = 64h²l(3c+h)³ P(c,h) / [9(9c+10h)D²],

P(c,h) = 324c⁴+1539c³h+2574c²h²+1839ch³+478h⁴.
```

Every factor and every coefficient is strictly positive. Hence
A>B and C>A+B on **every** positive span. No interval partition,
numerical minimum, or limiting argument is needed for these signs.

The [standard-library program](cubic_total_order.py) checks both
identities as polynomial identities. It multiplies every label by k
before constructing the face polynomials, clearing the denominator
`18k⁵`. It then clears D² in each proposed factorization and reduces
every even power of l using `l²=N/D`. A final common power of D
clears that reduction's denominators. Both residual polynomials are
identically zero. The cleared positive numerators each have twelve
positive terms.

At constant curvature the two triangles would tie and the quadrilateral
would equal their sum. The displayed factors explain how those equalities
break: the triangle difference contains h³, while the quadrilateral's
excess contains h²l. The strict cubic result approaches those equalities
as the positive endpoint span becomes small relative to its location.

## Another scalar root finds the total optimizer

The midpoint relation also gives an alternative to the original ratio
shooting construction. Set `τ=l/c∈(0,1)` and `v=h/c`. Then v is the
unique positive root of

```
200v⁴+660v³+(702−106τ²)v²+(243−195τ²)v−72τ² = 0.
```

All its nonconstant coefficients are positive. Its derivative is
strictly positive for v≥0, while its constant term is negative.
It therefore has exactly one positive root. A particularly useful
relative bracket is

```
τ²/4 < v < τ²/3.
```

To verify it, write q=τ². At v=q/4 the polynomial is

```
q(−360−156q+118q²+25q³)/32 < 0;
```

the positive terms are at most 143 and the constant term is −360.
At v=q/3 it is

```
q[9+13q+(38/3)q²+(200/81)q³] > 0.
```

The recovered h is below l/3, and
`d/l=(3+v)/(9+10v)<1/3`. Thus the four labels remain strictly
ordered. The midpoint equations make them stationary, agreeing with
the unique total optimizer already proved by shooting.

The calculator bisects to a tolerance proportional to τ², preserving
relative accuracy even when h is much smaller than the endpoint span.
It evaluates A−B and C−A−B with the positive factors above;
subtracting separate area enclosures would obscure their tiny signs.

## Reproduce

```sh
python3 experiments/cubic_total_order.py
```

The command verifies the two continuous identities, compares six
rational endpoint pairs with the independent earlier shooting
construction, clips all eighteen complete faces, and rejects five
invalid controls. One span is 2⁻¹²⁰. The finite clipped arrangements
use rational midpoint labels to audit the geometry; the universal
ordering theorem concerns the exact optimizer and follows from the
positive factorizations.
