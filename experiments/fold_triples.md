# The count stays. The order changes.

The [complete contact census](fold_contacts.md) counts crossing pairs
through two phase turns. A second question survives: can three visits
meet, changing their order while leaving that count alone?

For the same family

```
z(t,φ) = 245 exp(it) + 140 exp(i(d+1)t) + 65 exp(−i(d−1)t+iφ),
0 ≤ φ ≤ π,
```

a separate calculation now certifies **four selected ordinary triple
batches**. These are local existence results, **not a complete triple
census** or an exclusion of other events elsewhere in the half-turns.

![Three equal-scale close-ups of a selected sevenfold triple. A blue,
gold, and green branch bound a small triangle before the meeting, meet
approximately at one point, then enclose a triangle on the other side.
Each square spans 0.1 drawing units.](fold_triples.svg)

The [standalone triptych](fold_triples.svg) shows actual numerical
orbital branches at phase offsets −0.0001, approximately zero, and
+0.0001 radians from the selected sevenfold event. Exact angle bounds
place all three controls inside its fourth-branch exclusion interval;
the viewing squares lie inside its unit-radius isolation disk.

| Folds | Phase φ/π, rounded | Three visits in radians, rounded | Passage sign |
| --- | --- | --- | --- |
| 7 | 0.961750812235… | 0.234085460252, 0.897613502688, 1.595850683561 | +1 |
| 14 | 0.924452362405… | 0.122974565688, 0.882667558779, 1.282700330976 | +1 |
| 14 | 0.973358851457… | 0.010627798311, 0.413385855615, 0.796746669138 | −1 |
| 14 | 0.977378583506… | 0.032921468158, 0.832508465524, 5.939275130196 | +1 |

Rotating each meeting by 2π/d supplies d distinct copies. The sevenfold
half-turn therefore has **at least seven** ordinary triple passages.
The fourteenfold half-turn has **at least forty-two**, twenty-eight
positive and fourteen negative. These are lower bounds. A numerical
scan suggests they might be exact, but a finite scan cannot exclude
additional events or cancelling pairs between its samples.

The sign convention is the one used for [strangeness](strangeness.md):
each positive ordinary passage increases St by one, each negative
passage decreases it by one. These selected batches contribute net
changes +7 and +14 on their respective half-turns. No claim here
identifies those contributions with the movies' complete signed change.

## A four-variable contraction

[fold_triples.py](fold_triples.py) uses the independently audited
rational Fourier evaluator from the contact calculation. There are
three distinct visit-chart parameters s₁,s₂,s₃ and one phase-chart
parameter p. Solve the four scalar equations

```
z(s₁,p)−z(s₂,p) = 0,
z(s₁,p)−z(s₃,p) = 0.
```

The rational circle chart is again
`exp(it)=i^q(1+is)²/(1+s²)`. The derivative of t with respect to its
chart parameter is `2/(1+s²)`, and the phase column contains the
differences of `∂z/∂φ=65i exp(−i(d−1)t+iφ)` with the corresponding
positive phase-chart factor.

Numerical solves suggest a cube of radius **10⁻¹¹** for each event.
The exact center Jacobian inverse R gives the point map `X−RF(X)`.
Rational interval bounds prove strict containment inside the cube
and an infinity-norm contraction bound below **1.3×10⁻⁶**. Thus each
cube has exactly one root and its Jacobian is nonsingular. All three
velocity determinants are nonzero, proving pairwise transverse branches
and an ordinary unfolding rather than a tangency or persistent triple.

The separate [automatic-differentiation audit](fold_triples_check.py)
compares **320 exact Jacobian entries at twenty rational states**,
including all four centers, with a separate complex-division construction.
It also checks twenty exact determinant identities: the physical-time
four-variable Jacobian has determinant −H; chart coordinates multiply
this by four strictly positive circle factors.
Three negative controls reject a displaced phase, repeated visits,
and a negative cube radius. These finite checks audit implementation;
the interval inequalities prove each continuous local statement.

## No fourth branch

Each event has a **unit-radius disk** centered at an exact rational
proposed position. A continuous phase-chart radius **1/10000** is
covered, including the root image. Each selected visit has an admitted
slot of radius at most 1/200, shortened near a quarter boundary.
All selected slots are disjoint and monotone in a physical coordinate.

Endpoint rectangles plus `|z_ss|≤4 max|z_tt|+2 max|z_t|` and a phase-motion
allowance of 13/1000 enclose every omitted arc. **1019, 1018, 1020,
and 1018** excluded arcs close the four whole-orbit covers. No fourth
visit enters any disk during its stated phase interval. The contact
positions have radius greater than 100, so rotation gives d different
meeting points at each selected phase. The three fourteenfold phases
are proved distinct by disjoint rational enclosures.

These covers exclude other branches; they do **not** assert that the
entire admitted-slot product contains only one triple throughout the
phase window. Root uniqueness is inside the much smaller contraction
cube. A complete event-window or whole-route classification would need
additional narrowing and exclusion arguments.

## The little triangle's quadratic area

At the selected root let Vᵢ be the raw t-velocity and Wᵢ the phase
motion. Set

```
D₁₂ = det(V₁,V₂),  D₂₃ = det(V₂,V₃),  D₃₁ = det(V₃,V₁),
bᵢ = det(Vᵢ,Wᵢ),
H = b₁D₂₃ + b₂D₃₁ + b₃D₁₂.
```

In cyclic visit order, sign H is the signed triple passage. The
[three-line area calculation](triple_area.md) gives

```
area = K (φ−φ*)² + O(|φ−φ*|³),
K = H² / (2 |D₁₂ D₂₃ D₃₁|).
```

The four certified coefficients are approximately **8095.340121,
14535.464990, 19193.892933, and 40763.298436**, in table order.
Phase is in radians, so K has drawing-unit area per radian². Fourth-branch
exclusion makes the small curved triangle a face sufficiently close to
its meeting. No numerical finite-offset threshold is asserted.

## Reproduce and continue

```sh
python3 experiments/fold_triples.py
python3 experiments/fold_triples.py --write
python3 experiments/fold_triples_check.py
python3 experiments/fold_triples_figure.py
```

The default repeats all four local proofs and every fourth-branch
exclusion, without reading the [archived record](fold_triples.json).
All commands use the standard library. The signs are rational interval
decisions, not deductions from the numerical scan's invariant jumps.

For a future complete census, cover the phase intervals with regular
crossing product charts and prove their individual visit slots disjoint,
as in the older [whole rhythm route](rhythm_route.md). The certified
contact phases and these four triple batches provide candidate event
windows. Unlike that older affine family, the phase parameter follows
a rational unit circle; its derivative bounds and nonlinear Jacobian
column need to be retained. The continuous global exclusion is still
work to do.
