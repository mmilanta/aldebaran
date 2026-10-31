# One direction, eleven places

[Turn the normal](normal_front.html), or save the [standalone drawing](normal_front.svg).

The 11 / 6 and 11 / 8 drawings each have forty crossings, but they offer a
different kind of meeting too: **two distant points can share an oriented
tangent line**. A graph of normal direction and signed line distance
brings those points together. Its slopes still distinguish them.

## Eleven visits in every direction

Write the whole blend, with weight a in [0,1], as

```
q(t,a) = 245 exp(it) + 140 exp(11it)
       + 65(1−a) exp(−6it) + 65a exp(−8it).
```

Its velocity factors as `q′ = i exp(11it) B`, where

```
B(t,a) = 1540 + 245 exp(−10it)
       − 390(1−a) exp(−17it) − 520a exp(−19it).
```

`Re B ≥ 1540−245−520 = 775 > 0`. Thus its principal argument is a
continuous, periodic real function, with values strictly between −π/2
and π/2. It contributes no complete turn. The travel direction makes
exactly eleven turns, and so does its left normal.

The earlier [uniform curvature bound](rhythm_route.md#the-tangent-never-turns-backwards)
gives

```
det(q′,q″) ≥ 2,974,975,
775 ≤ |q′| ≤ 2305,
dθ/dt = det(q′,q″)/|q′|² ≥ 118999/212521 > 0.
```

Consequently the continuous normal angle

```
θ(t,a) = π + 11t + arg B(t,a)
```

is strictly increasing from π to 23π during one orbit. Any normal
direction has **exactly eleven distinct parameter visits** modulo 2π.
The orbit closes, so the first and final parameter values count as one
visit, not two. These statements hold on the entire blend. The interactive
page displays its two endpoints.

## Direction, distance, slope

Let `N(θ) = (cos θ, sin θ)` be the left unit normal. Set

```
h(θ) = q · N,
p(θ) = q · N′ = −x sin θ + y cos θ.
```

The tangent line is `{r : r·N = h}`. Since `q′·N = 0`, differentiation
along any one visit gives `dh/dθ = p`. In particular,

```
q = h N + p N′.
```

Distance and slope recover both coordinates of the original point.
At one crossing of the graph, two visits have equal θ and h; they
describe the same oriented line. If their slopes differ, their points
are distinct, separated by exactly `|p₁−p₂|` drawing units. Equal slopes
as well would mean the points themselves meet with equal travel
directions: a direct self-tangency.

The `(θ,h)` diagram is the **conormal front**, in the coordinates of
[Lenhard Ng, *Plane curves and contact geometry*, §2.1](https://sites.math.duke.edu/~ng/math/papers/planecurves.pdf#page=4).
The extra coordinate p is recovered from its slope. This page illustrates
that coordinate construction; it computes no conormal knot invariant.

The positive curvature also gives a useful check on the second derivative.
With `ρ = |q′|/(dθ/dt) > 0`, differentiating the reconstruction yields

```
h + h″ = −ρ.
```

The minus sign comes from using the left normal: for a counterclockwise
circle centered at the origin, h is its negative radius.

## Cutting one closed trace into eleven strands

For the controls, write `θ = π + β` modulo 2π, with `0 ≤ β ≤ 2π`.
Visit j, numbered from zero, solves

```
11t + arg B(t,a) = β + 2πj,       j = 0,…,10.
```

Strict increase proves uniqueness. The code bisects this equation inside
`[(β+2πj−π/2)/11, (β+2πj+π/2)/11]`, clipped to the orbit.
All numerical inversions use 46 bisections; this iteration count is an
implementation choice, not an interval certificate.

At β = 2π, strand j joins strand j+1 at β = 0. The last strand joins the
first at the orbit's closure. Their distances, slopes, and original points
agree across this seam. The eleven pieces therefore belong to a single
closed trace. Their numbering records successive normal turns, rather
than sorting points by height; two heights can exchange order.

## Two selected shared lines

The example button follows visits 1 and 7 in the page's numbering:

| Drawing | Normal angle | Signed distance | Point separation |
| --- | ---: | ---: | ---: |
| 11 / 6 | 282.163594° | −67.812559 | 571.333090 |
| 11 / 8 | 275.856400° | −89.779762 | 546.885401 |

The table and drawing use rounded numerical coordinates. The browser
bisects a sign-changing distance difference within one degree: normal
turns 102°–103° and 95°–96°, respectively, measured from the initial
leftward normal. A separate rational proof below certifies the two
selected bitangents. This does **not** count all
shared tangents, exclude multiple meetings of the front, or certify a
braid word. A front crossing is a shared tangent line; it is not a crossing
of the original curve.

### Two rational boxes

Use the existing circle charts `exp(it) = i^q (1+is)²/(1+s²)`.
For two visits, let `v=q′(t)`, `w=q′(u)`, `A=q″(t)`, `B=q″(u)`, and
`δ=q(t)−q(u)`. A shared tangent satisfies

```
F(t,u) = (det(v,w), det(δ,v)) = (0,0).
```

Before multiplying columns by the chart factors `2/(1+s²)`, its Jacobian is

```
       [ det(A,w)    det(v,B) ]
DF  =  [ det(δ,A)    det(v,w) ].
```

The extra terms in the second row simplify because `det(v,v)=0` and
`−det(w,v)=det(v,w)`. The proof uses interval Fourier jets, with exact
rational arithmetic, from the earlier tangency calculations. At each
rounded hint, it builds a rational chart square with radius **10⁻¹¹**.
The preconditioned map `x ↦ x−R F(x)` maps that square strictly inside
itself and has row-sum contraction norm **less than 10⁻⁷**. Therefore each
square contains exactly one solution.

An interval dot product proves `v·w>0`, selecting matching travel
directions rather than opposite parallel tangents. An interval bound on
`|δ|` gives **571 < separation < 572** for 11 / 6 and
**546 < separation < 547** for 11 / 8. In particular the two visits are
at distinct points, so their front slopes differ and the two front
branches cross transversely. No assertion about a third front strand is
needed or supplied by these selected two-visit certificates.

## Reproduce

Only the Python and Node standard libraries are needed:

```sh
python3 experiments/normal_front.py
node experiments/normal_front_check.js
node experiments/normal_front_figure.js
node --check experiments/normal_front.js
```

The check evaluates all eleven visits at 721 directions on each endpoint.
An independent complex derivative implementation verifies the normals,
speed and curvature inequalities, point reconstruction, and reflection.
Finite differences check the front slope. Every strand's seam is checked
in position, distance, and slope. The two examples must have coincident
lines and point separation equal to their slope difference. Invalid
rhythms, angles, branch indices, sample counts, and brackets are rejected.

The Python proof first makes 128 exact component comparisons with the
frozen rational circle evaluator and eight rational central-difference
checks of the analytic Jacobian. Shifted hints, reversed visits,
coincident visits, and negative radii must fail certification. The two
successful contraction proofs then run afresh.

The JavaScript checks are numerical implementation checks. The elementary inequalities
above supply the global eleven-visit statement; no sample grid is used
to infer its completeness. The older rational intersection solver and
its certificates are unchanged.
