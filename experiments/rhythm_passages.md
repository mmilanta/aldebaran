# The same counts, a different weave

The [new study](weave.html) begins with rhythms **11 / 6** and **11 / 8**.
Their smooth crossing atlases agree on:

| Quantity | Both drawings |
| --- | ---: |
| Transverse crossings | 40 |
| Bounded regions | 41 |
| Tangent index | 11 |
| Regions of winding +1 | 10 |
| Regions of winding +2 | 19 |
| Regions of winding +3 | 10 |
| Regions of winding +4 | 2 |

Their [strangeness](strangeness.md) values differ: **15** and **11**.
Among the original 321 regular pairs, this is the only group with the
same crossing count, tangent index, and winding histogram but different St.
The integers do not specify the arrangement of the crossings.

A simple route between them already keeps moving:

```
z(t,a) = 245 exp(it) + 140 exp(11it)
       + 65 [(1−a) exp(−6it) + a exp(−8it)],
0 ≤ a ≤ 1,       0 ≤ t ≤ 2π.
```

The frequency-eleven term in the velocity has magnitude 1540. The sum
of all the others has magnitude at most `245+65(6+2a) ≤ 765`. Thus
**|z′| ≥ 775** everywhere on the full route. The tangent index remains
eleven. Also, `Re(exp(−it)z) ≥ 40`, so the center retains winding one.

## Four passages, in two complete windows

Each row describes one above-axis triple and its reflected partner.
Times, weights, and positions in this table are rounded approximations.

| Weight | Three above-axis visits | Meeting position | Window proved completely |
| --- | --- | --- | --- |
| 0.047120044569… | 0.802571286, 1.290851955, 1.730807324 | (63.821819, 316.024128) | [0.0471, 0.0472] |
| 0.075511676380… | 0.141583727, 0.557257415, 1.092285444 | (286.185256, 124.989044) | [0.0755, 0.0756] |

Reflection sends the position to `(x,−y)` and visits to `2π−t`, in
reversed order. It leaves the weight unchanged. The exact coefficients
make this a symmetry of the entire family, not just the drawing.

Throughout **each complete window**, the certificate proves:

* Every pair of distinct visits with equal position lies in one of forty
  disjoint, regular crossing charts. Each chart contains one such pair
  at every weight, with a nonzero tangent determinant.
* Only two disjoint groups of three charts can acquire a third visit.
  Each has exactly one ordinary triple event, and the two events are
  reflections of each other at the same weight.
* There is no tangency, fourth visit, or other curve event in the window.
  Away from the two simultaneous triples, there are forty distinct
  transverse crossing points.
* Fresh smooth endpoint proofs and both strangeness formulations give
  **15 → 13** in the first window and **13 → 11** in the second.
  The three crossings in each selected group contribute a change of
  **−1**; every other crossing contribution stays fixed.

The cover accounts for the entire orbit and every weight in the stated
windows, beyond locating numerical roots or comparing snapshots.

These four local jumps total −4, matching the endpoint difference.
This is **not a complete event census of the full route**. Additional
events outside the windows could have cancelling signed jumps. Numerical
exploration also finds two-branch tangencies elsewhere, which do not
change St. No exhaustive claim about them is made here.

## A rational calculation with a real parameter

The standard-library program is [rhythm_passages.py](rhythm_passages.py).
It imports the earlier frozen [intersection solver](certify_intersections.py)
without editing it, and reuses the finite Fourier evaluator from
[the earlier triple passage](triple_passage.py).

On quarter q, put

```
exp(it) = i^q (1+is)²/(1+s²),       0 ≤ s ≤ 1.
```

Position, its derivative with respect to s, and its raw t-velocity are
rational whenever s and a are rational. The four terms have frequencies
1, 11, −6, and −8. The evaluator passes **800 exact component comparisons**
against the frozen original evaluator at the two endpoints and against
affine mixtures at six interior or window-end weights.

For a weight interval with midpoint a₀ and radius r, uniform bounds are

```
|∂z/∂a| ≤ 130,
|∂z′/∂a| ≤ 910,
|z″| ≤ M = 245 + 140·121 + 65(1−a_low)·36 + 65 a_high·64,
|z′| ≤ V = 245 + 140·11 + 65(1−a_low)·6 + 65 a_high·8,
|∂²z/∂s²| ≤ L = 4M+2V.
```

The last inequality uses `dt/ds ≤ 2` and `|d²t/ds²| ≤ 2`.
An arc of s-length h stays inside its endpoint rectangle enlarged by
`L_middle h²/8 + 130r`: interpolation error at the middle weight, plus
the displacement covering every other weight.

Each quarter is divided into **1024 arcs**, making **4096** in all.
Closed spatial buckets enumerate every overlapping pair of these enlarged
rectangles. Binary comparisons are used only after exact rational checks
that the rounded rectangles enclose the rational ones.

Single-arc injectivity and nearby-pair exclusions use the original
monotonicity argument uniformly in a. If the initial middle-weight
velocity v₀ satisfies

```
|v₀| > 2M(d+1)/1024 + 910r,
```

every intervening velocity faces v₀, so projection along it is strictly
increasing. Squared rational norms decide this inequality without square
roots. The single-arc test uses d = 0.

Every remaining arc pair is recursively covered by spatial exclusion,
parametric contraction exclusion, or strict containment in a certified
crossing chart. The printed cover counts are:

| Window | Monotonicity exclusions | Spatial exclusions | Contraction exclusions | Leaves inside root charts |
| --- | ---: | ---: | ---: | ---: |
| First | 4096 | 416 | 343 | 128 |
| Second | 4096 | 415 | 308 | 107 |

These are cover leaves and exclusions, not additional crossings.

## Forty crossing charts, for every weight

Let `F(s,u,a)=z(s,a)−z(u,a)` on two specified quarters. At a proposed
rectangle's midpoint and middle weight, invert its 2×2 time Jacobian
exactly, obtaining R. Study

```
T_a(s,u) = (s,u) − R F(s,u,a).
```

The exact midpoint value is affine in a. Across a time radius ρ, a
Jacobian column changes by at most `Lρ+1820r`, because the derivative
with respect to a of an s-velocity is at most `2·910`.
The code bounds `I−R D_time F` and the whole image rectangle rationally.
An image coordinate disjoint from its original interval excludes roots.
A strict self-map with row-sum norm less than one proves exactly one
root for **every fixed a in the window**, with nonsingular time Jacobian.

The forty accepted product rectangles are pairwise disjoint. Their
time radii are 0.00001 or 0.00002 in the rational-circle parameter.
The exhaustive arc cover proves that they contain every possible
pairwise crossing. This also rules out hidden tangencies.

## Only two triples can occur

Two crossing charts can share a visit only when their corresponding
time intervals overlap. The exact overlap graph consists of two
three-vertex components, each a triangle; all other crossings have
separate visit intervals. Each component is therefore the only possible
source of one triple, and a fourth visit would require a larger component.

For each selected group, solve the four equations

```
z(s₁,a) − z(s₂,a) = 0,
z(s₁,a) − z(s₃,a) = 0.
```

The unknowns are three rational-circle times and a. Their 4×4 Jacobian
has the three time velocities in its first three columns and differences
of weight derivatives in its last column. Rational interval bounds
enclose that Jacobian on a box. A fixed inverse R gives a
four-dimensional contraction test for `X−R F(X)`.

A larger box contains the **entire weight window and every potentially
coincident visit** in that group. Its time and weight radii are both
0.0002. The contraction norm is below 0.477 in the first window and
below 0.639 in the second, proving uniqueness on these whole boxes.
These tests use the global bound `L ≤ 89990`, so they remain valid
where the larger box extends beyond the window.

A second box, with all radii 10⁻⁹, proves existence strictly inside the
window and encloses the weights:

```
0.04712004356938 < a_first  < 0.04712004556938,
0.07551167538036 < a_second < 0.07551167738036.
```

Both reflected roots pass the tests separately. All three pairwise
velocity determinants have a strict sign in each event box. The full
4×4 Jacobian is nonsingular, proving that weight moves the three regular,
pairwise transverse branches through an ordinary triple event.
Existence is not decided by the Newton hints, their residuals, or the SVG.

Fresh endpoint proofs match each refined crossing to its uniform chart
by **strict containment of exact rational boxes**. The signed words and
planar face walks independently compute St. Summing the changes in the
three contributions of each selected group gives −1, while every
unselected contribution stays fixed. The exterior starting edge remains
at t = 0, with index +½ and correction zero throughout.

## Reproduce and inspect

```sh
python3 experiments/rhythm_passages.py
python3 experiments/rhythm_passages.py --window 1
python3 experiments/weave_figure.py
node experiments/weave_check.js
```

Only the standard library and Node are needed. The certificate takes
about four seconds here. The generator repeats fresh proofs for both
endpoints and both complete event windows, then writes
[weave_data.js](weave_data.js) and [the standalone SVG](weave.svg).
The numerical figure code has no role in the proof decisions.

The browser checks cover all **804** combinations of two meetings,
201 local slider positions, and two reflections. Separate original-curve
evaluators verify the affine positions, velocities, and crossing markers.
Geometric sector probes check all eighty endpoint crossings against
their integer word indices.

For nonzero slider positions, a 48,000-edge polygon checks a point inside
each displayed little triangle. These probes have winding **+2 before**
and **+1 after**. The least clearance exceeds **27 times** the global
interpolation allowance `21345(2π/48000)²/8`, so these sampled probes
also clear the smooth curve. These are numerical implementation checks,
separate from the rational continuous-window proof.

The slider deliberately shows a wider local neighborhood, ±0.003 in
weight, so the triangle is visible. The event census remains limited
to the two specified windows. “Meeting” uses rounded coordinates; its
nearly coincident markers approximate the exact algebraic event.
