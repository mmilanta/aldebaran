# Two ways to touch

The [interactive study](touch.html) follows four selected contacts on the
same 11 / 6 → 11 / 8 route as [the triple passages](rhythm_passages.md):

```
z(t,a) = 245 exp(it) + 140 exp(11it)
       + 65 [(1−a) exp(−6it) + a exp(−8it)].
```

The frequency-eleven arm dominates every other velocity, so **|z′| ≥ 775**
for every time and weight in [0,1]. None of the contacts stops the point.
Two different visits meet with parallel velocities.

## Four touches and their reflections

Times, weights, and positions below are rounded display approximations.
The contraction tests use rational centers and rational inequalities.

| Weight | Two above-axis visits | Position | Travel | Lens exists locally |
| --- | --- | --- | --- | --- |
| 0.103860136179… | 0.571920159, 1.118754227 | (289.266887, 157.056844) | Same direction | Before |
| 0.322975096577… | 0.982785795, 5.866065711 | (150.746783, 61.832770) | Opposite directions | After |
| 0.393710135492… | 1.464286973, 2.898412227 | (−117.729046, 184.953303) | Opposite directions | Before |
| 0.863940915397… | 2.468980377, 3.008114568 | (−223.925746, 227.420758) | Same direction | After |

Reflection sends `(t,u)` to `(2π−u,2π−t)` and `(x,y)` to `(x,−y)`.
Each reflected event is certified separately. Uniqueness and the exact
reflection identity identify the reflected weights; their simultaneity
does not depend on rounding the printed decimals.

For **each of these eight selected events**, the certificate proves:

* Exactly one solution of equal position and parallel velocity lies in
  its stated rational three-dimensional box.
* The visits are distinct, both velocities are nonzero, and their
  direction agreement or opposition is certified.
* Relative graph curvature and weight separation are nonzero. The
  selected branches therefore have an ordinary quadratic contact, with
  two local crossings on the stated side and none on the other.
* The shrinking lens has the area coefficient enclosed below.
* A whole-orbit cover excludes all other visits from a disk around the
  contact, throughout the browser's complete weight range. Each admitted
  branch slot has a strictly monotone physical coordinate. The contact
  is therefore an isolated two-branch meeting, with no third visit.

These small event boxes alone are a **local list**. A separate argument
below classifies four complete short weight windows. The browser's slider
neighborhoods are wider still; neither calculation classifies the full
route. The isolated local lens is a face of the full drawing sufficiently
close to the contact; this local statement does not classify every pocket
elsewhere in the drawing.

## A rational contact calculation

[rhythm_tangencies.py](rhythm_tangencies.py) uses the same circle charts
as the earlier certificates:

```
exp(it) = i^q (1+is)²/(1+s²),     0 ≤ s ≤ 1,   q = 0,1,2,3.
```

Interval complex multiplication encloses the Fourier sum and its first
three t-derivatives. It also encloses the exact weight derivatives,
`∂z/∂a = 65(exp(−8it)−exp(−6it))`. The new evaluator is independent of
the frozen intersection evaluator. **960 exact component comparisons**
check agreement on positions and velocities, all circle quarters, and
affine t-jets through third order.

For two chart parameters s and u, solve

```
F = (z_x(s,a)−z_x(u,a), z_y(s,a)−z_y(u,a), det(V_s,V_u)) = 0,
V = ∂z/∂t.
```

The first two Jacobian columns use `dt/ds = 2/(1+s²)`. For the last
equation they are `det(A_s,V_u) dt/ds` and
`det(V_s,A_u) dt/du`, where A is t-acceleration. The weight column is
the position difference's weight derivative, followed by
`det(∂V_s/∂a,V_u)+det(V_s,∂V_u/∂a)`.

Every selected center has a cube of radius **10⁻¹¹** in `(s,u,a)`.
Let R be the exact rational inverse of the center Jacobian and J the
interval Jacobian on the cube. The program checks both

```
||Id−RJ||∞ < 0.01,
−R F(center) + (Id−RJ)[−r,r]³ ⊂ (−r,r)³.
```

Thus `x ↦ x−RF(x)` is a contraction mapping the closed cube strictly
inside itself. It has exactly one fixed point, and invertibility of R
makes this a unique zero of F in the cube. The largest of the eight
actual norm bounds is below **2.3 × 10⁻⁷**. A shifted weight, coincident
visits, reversed visit order, and negative radius are rejected as negative
controls.

The script does not edit [certify_intersections.py](certify_intersections.py).
Numerical Newton locations suggest the boxes; they never decide whether
a box passes.

### Making sure there is no third branch

For each touch, a disk of radius **26, 12, 15, or 15** drawing units
admits only the two selected visit slots. Its center is the exact rational
position at the first proposed chart center, not the rounded table entry.
The weight interval is the exact source hint **±0.003**, including every
browser setting. Each selected s-slot has radius **1/50**.

The other parts of all four circle quarters are covered with rational
endpoint rectangles and second-derivative interpolation allowances, using
the frozen solver's `bounds` method. Enlarging each rectangle by **0.39**
in each coordinate covers every weight, because `|z_a| ≤ 130`. Its
minimum squared distance from the disk center exceeds the squared radius.
The program checks every omitted arc: **4016 or 4017** rectangles suffice
per event. Both selected slots also have uniform monotonicity certificates,
obtained by interval t-velocities on **32 subintervals each**. The least
certified absolute coordinate velocity exceeds **618** across all eight
proofs. The contact box lies strictly within its disk.

This rules out a third visit at the event, and prevents an unrelated arc
from cutting a lens that lies in the disk. It does not count all meetings
of the two admitted branches through the full displayed weight range.

## Four complete continuous windows

[rhythm_touch_windows.py](rhythm_touch_windows.py) adds a whole-orbit,
continuous-weight census around each contact. These are exact decimal
rational endpoints, centered on the source hints with radius **1/100000**:

| Touch pair | Complete weight window | Crossings at its ends |
| --- | --- | --- |
| First | [0.10385013617856, 0.10387013617856] | 40 → 36 |
| Second | [0.32296509657704, 0.32298509657704] | 36 → 40 |
| Third | [0.39370013549163, 0.39372013549163] | 40 → 36 |
| Fourth | [0.86393091539713, 0.86395091539713] | 36 → 40 |

**Each whole window has exactly two reflected ordinary tangencies and no
other event.** Every persistent crossing lies in one of **36 regular
product charts**, each with exactly one transverse crossing at every
weight. Two additional product charts admit the selected contact pairs.
All individual visit slots are disjoint. Hence no third or fourth visit
can join any crossing anywhere in the window. A cover of **4096 rational
arcs** excludes all other crossings at every weight, using the earlier
uniform `Family` cover. The contact charts are accepted by containment
in that cover, rather than mistaken for regular charts.

Inside a contact chart each s-slot has radius **1/1000**. Split it into
sixteen subintervals. Interval velocities, accelerations, and weight
motions prove that the selected physical coordinate stays monotone, and
that the separation g has **g_XX and g_a of fixed nonzero signs** on the
entire product chart and weight interval. Each branch is a graph over
a common physical-coordinate interval about X₀: half-width 1 for the
first touch, and 1/2 for the others. Endpoint bounds bracket this interval
at every weight.

To locate the critical point, enclose both graph inverses at X₀ using
the mean value theorem and the uniform coordinate-speed bounds. This
gives an interval for g_X(X₀,a). Its magnitude is smaller than the
minimum |g_XX| times the common half-width. Thus g_X has opposite signs
at the two common endpoints, and strict curvature gives one critical
point m(a) at every weight. It depends smoothly on a. Its value has

```
d/da g(m(a),a) = g_a(m(a),a),
```

because g_X vanishes there. This derivative has a fixed nonzero sign,
so the critical value can pass through zero only once in the entire
window. The small contraction box already proves one such zero. This
classifies the tangencies even though the crossing equations themselves
are singular at the contact. Two false-chart controls reject a repeated
branch and a displaced contact slot.

Fresh smooth censuses at the eight exact window endpoints confirm the
crossing counts in the table and St = 11. These are distinct from the
slightly more distant snapshots used for the J⁺/J⁻ table below. The
continuous argument rules out intervening events **inside these four
windows**. It leaves the gaps between windows to a separate census.

## The lens's three-halves law

Use a physical coordinate X along which both velocities are nonzero,
and write the branches as graphs of the other physical coordinate Y.
No spatial stretching is needed: X is y for the first and third
contacts, and x for the other two. Subtract the later graph from the
earlier one. At the contact, translated to `X = 0`, its separation is

```
g(X,δ) = αδ + (β/2)X² + O(|X|³+|Xδ|+δ²),
δ = a−a_contact.
```

The graph derivatives are enclosed directly from the event box:

```
α = [Y_a − (Y_t/X_t) X_a]_earlier − [Y_a − (Y_t/X_t) X_a]_later,
β = [(Y_tt X_t − X_tt Y_t)/X_t³]_earlier
  − [(Y_tt X_t − X_tt Y_t)/X_t³]_later.
```

All eight boxes exclude zero for both α and β. A pocket opens on the
side `sign(δ) = −sign(αβ)`. Its two ends have leading locations
`X = ±sqrt(−2αδ/β)`.

Put `P = |α|` and `Q = |β|`. Integrating the leading parabolic gap
between those ends gives

```
K = (4/3) P sqrt(2P/Q),
A(δ) = K |δ|^(3/2) + O(|δ|²),
```

on the pocket side. The square-root enclosure uses integer arithmetic.
The formula gives physical area and is unchanged by switching between
valid orthogonal graph coordinates at an exact tangency. The browser
rotates its coordinate frame to the common tangent, preserving area.

| Selected touch | Certified area coefficient K |
| --- | --- |
| First | 50734.52 < K < 50734.53 |
| Second | 5119.45 < K < 5119.46 |
| Third | 23648.17 < K < 23648.18 |
| Fourth | 9249.50 < K < 9249.51 |

The same inequalities pass separately for all four reflected events.
Their reflected coefficient intervals overlap. The theorem bounds the
limiting coefficients; it supplies no numerical bound on the finite-offset
area remainder displayed in the browser.

Numerical graph inversion and quadrature check seven offsets from 0.003
down to 0.000003, on the pocket side of every touch. The normalized areas
approach one. Refining Simpson quadrature from 128 to 512 intervals checks
stability separately. These are numerical cross-checks, not interval
integration or proof of a full region count.

## Two integers for two kinds of touch

A direct touch has agreeing travel directions. An inverse touch has
opposing directions. Arnold's J⁺ changes at direct touches; J⁻ changes
at inverse touches. For a generic plane curve with n crossings, winding
labels w_R on its regions and average winding i_v at its vertices,
Viro's formula is

```
J⁻ = 1 − Σ_regions w_R² + Σ_vertices i_v²,
J⁺ = J⁻ + n.
```

The exterior's zero label contributes nothing. These conventions, and
the signs of the changes, are described in
[MIT's lecture on Arnold invariants](https://ocw.mit.edu/courses/18-900-geometry-and-topology-in-the-plane-spring-2023/mit18_900s23_lec17.pdf).
[Alexander Mai's introduction](https://arxiv.org/abs/2210.00871), §3.2.1,
also explains the winding-square formula for J⁺.

The optional `--snapshots` run repeats eight fresh smooth intersection
proofs, exact crossing words, planar face walks, and the strangeness
audit. The two weights for touch i are the **exact rational** decimal
hint in the source, minus and plus **1/10000**. They give:

| Near touch | Crossings before → after | J⁺ before → after | J⁻ before → after | St at both |
| --- | --- | --- | --- | --- |
| First reflected pair | 40 → 36 | −14 → −18 | −54 → −54 | 11 |
| Second reflected pair | 36 → 40 | −18 → −18 | −54 → −58 | 11 |
| Third reflected pair | 40 → 36 | −18 → −18 | −58 → −54 | 11 |
| Fourth reflected pair | 36 → 40 | −18 → −14 | −54 → −54 | 11 |

Each direct lens birth changes J⁺ by +2 and each death by −2. Each
inverse birth changes J⁻ by −2 and each death by +2. The reflected pairs
double these local changes. The table is consistent with those rules;
it records individual certified drawings, not a continuous event-window
classification. Strangeness ignores ordinary two-branch touches.

## Reproduce it

All commands use only their standard runtimes:

```sh
python3 experiments/rhythm_tangencies.py
python3 experiments/rhythm_tangencies.py --snapshots
python3 experiments/rhythm_touch_windows.py --controls
python3 experiments/touch_figure.py
node experiments/touch_check.js
node --check experiments/touch_math.js
node --check experiments/touch.js
```

The generator repeats the local certificates and fresh nearby smooth
censuses before writing [touch_data.js](touch_data.js) and
[the still SVG](touch.svg). The latter works without JavaScript.
The browser never runs a proof. Its rounded locations, finite sampling,
root finding, and quadrature serve the drawing; the exact claims live
in the separate rational calculation.
