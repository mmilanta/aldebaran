# Four radius points, three spatial visits

The [analytic shoulder argument](fold_shoulder.md) constructs meetings
arbitrarily close to the universal radial threshold when the fold count
grows. It leaves its numerical cutoff, ordinary-passage status, and
fourth-visit question open. The following **three finite examples** now
have separate exact local certificates:

| Folds d | Selected phase φ/π, rounded | Selected meeting | Rotated copies |
| --- | --- | --- | --- |
| 30 | 0.9149574927371… | Negative ordinary triple, exactly three visits | 30 |
| 60 | 0.9002485310056… | Negative ordinary triple, exactly three visits | 60 |
| 120 | 0.8963074237035… | Negative ordinary triple, exactly three visits | 120 |

Each row certifies one rotational batch. **This is not an event census**
at any of those fold counts. It neither proves that the selected meeting
comes first nor rules out unrelated events at the same phase. It gives
no cutoff or remainder bound for the large-fold theorem and does not
certify continuation from these points to its analytic branch.

The [reading page](fold_shoulder_events.html) and
[standalone sheet](fold_shoulder_events.svg) illustrate the difference
between sharing a radius and sharing a spatial position.

## Isolate the three visits

The curve is

```
z(t,φ) = 245 exp(it) + 140 exp(i(d+1)t) + 65 exp(i(φ−(d−1)t)).
```

Use rational quarter-circle charts for the three times and phase,
`exp(it)=i^q(1+is)²/(1+s²)`. The four real equations are the real and
imaginary parts of `z(t₀,φ)−z(t₁,φ)` and `z(t₀,φ)−z(t₂,φ)`.
Numerical leads only suggest chart centers. A rational inverse of the
midpoint Jacobian gives a contraction on a closed four-dimensional
cube of chart radius 10⁻¹². Its derivative norm is below 0.000006 for
all three examples, and its image lies strictly inside the cube.
The fixed point therefore exists and is unique in that cube.

The [existing local triple calculation](fold_triples.md) supplies this
contraction test. It now also accepts larger positive fold counts and
an optional evaluator. The new evaluator uses binary complex powers
with outward rational rounding at 45 decimal places. Every multiplication
still encloses its exact interval image; rounding never substitutes a
floating-point decision. Binary powers avoid the excessive interval
width of successively multiplying a rotating interval hundreds of times.

At the enclosed root, all three pairwise tangent determinants are
nonzero. The unfolding quantity

```
D₀₁ = det(V₀,V₁),  D₁₂ = det(V₁,V₂),  D₂₀ = det(V₂,V₀),
bᵢ = det(Vᵢ,Wᵢ),
H = b₀ D₁₂ + b₁ D₂₀ + b₂ D₀₁
```

is strictly negative. Here `Vᵢ=z_t(tᵢ,φ)`, `Wᵢ=z_φ(tᵢ,φ)`, and
visits are in increasing time order. This is the negative local passage
convention of the earlier triple studies. The quadratic area coefficient
`H²/(2|D₀₁D₁₂D₂₀|)` is also enclosed in the record. No area estimate
at a specified nonzero phase offset follows without a remainder bound.

## Recover the fourth ellipse point without searching the orbit

Put `u=dt` and factor `z=exp(it) B`, where

```
B(u,φ) = 245 + 140 exp(iu) + 65 exp(i(φ−u)).
```

Its real part is at least 40. Set `c=cos φ`, `s=sin φ`, and let ρ be
the common spatial radius. In the chart `v=tan(u/2)`, the real and
imaginary numerators of B are

```
X(v) = (385+65c) + 130s v + (105−65c)v²,
Y(v) = 65s + (280−130c)v − 65s v².
```

Clearing the positive denominator `(1+v²)²` from `|B|²=ρ²` gives

```
P(v) = (15250−13650c−ρ²)v⁴ − 9100s v³
     + (167700−109200c−2ρ²)v² + 136500s v
     + (152450+50050c−ρ²).
```

This is a direct expansion of `X²+Y²−ρ²(1+v²)²`, using `c²+s²=1`.
The independent audit repeats that identity formally in all three
symbols c,s,ρ².

The three visits give three distinct finite roots `v₀,v₁,v₂`, enclosed
by rational interval powers of their time circles. In every example
the leading coefficient is nonzero, so the missing chart point u=π
is not on this radius. The **only remaining root** is

```
v₃ = 9100 sin φ/(15250−13650 cos φ−ρ²) − v₀−v₁−v₂.
```

Its interval is disjoint from the first three. It supplies the fourth
ellipse point B₃ at the same radius; it need not supply a fourth visit
to the specified spatial point z.

## Test the direction

If a fourth time visit existed, its unit time direction would have to
be `w=z/B₃`. Its ellipse parameter u₃ would then obey

```
w^d = exp(iu₃).
```

All quantities on both sides have rational interval enclosures at the
certified triple root. A component of their difference stays strictly
away from zero:

| d | Excluded component | Difference, rounded |
| --- | --- | --- |
| 30 | Imaginary | −1.978706… |
| 60 | Real | −0.745907… |
| 120 | Imaginary | −1.314596… |

Thus the fourth ellipse point has the wrong direction in every case.
There is no spatial fourth visit. A fixed nonzero B and a specified z
determine `exp(it)` uniquely, so different rotational lifts of any one
ellipse point cannot add further visits either. Together with the
quartic this accounts for the entire orbit at the selected meeting.

The rotational identity `z(t+2π/d)=exp(2πi/d)z(t)` gives d distinct
copies, since the common point is nonzero. It preserves the local
tangent and unfolding signs.

## Repeat

```sh
python3 experiments/fold_shoulder_events.py --write
python3 experiments/fold_shoulder_events_check.py
python3 experiments/fold_shoulder_events_figure.py
```

The first program freshly proves all three local events and saves the
[exact record](fold_shoulder_events.json). The second independently
expands the quartic, compares Fourier jets and automatic derivatives,
checks degenerate controls, repeats all three proofs, and compares
every archived field. All use only the standard library. Rounded
picture geometry supplies no proof predicate.

## A fourth candidate comes very close

A separate [saved local certificate](fold_shoulder_close.json) uses
**10,115 folds**. It too proves a selected negative ordinary triple
with exactly three visits. The nearest rotational copy of its fourth
equal-radius ellipse candidate lies only

```
0.0000035508 < distance < 0.0000035509
```

drawing units from the triple point. The original first arm is 245
units long. This small distance is a rationally bounded near miss,
rather than a numerical fourth visit. This is another selected batch,
without a census or a certified continuation to the analytic branch.

The direction residual gives the unit complex ratio
`M=(z/B₄)^d exp(−iu₄)`. Its small argument, divided by −2π, is the
signed offset in one fold sector. The absolute offset g is strictly
between zero and one tenth, so the closest rotational copy is unique.
Its spatial distance is `2ρ sin(πg/d)`. Rational square-root and
arctangent enclosures, followed by `x−x³/6 ≤ sin x ≤ x` for 0<x<1,
give the bounds above.

This measures a **particular equal-radius point on the fourth branch**.
It is not a lower bound on the distance from the entire fourth branch.
The no-fourth-visit conclusion uses the exact direction mismatch,
independently of this distance interpretation.

```sh
python3 experiments/fold_shoulder_events.py --replay experiments/fold_shoulder_close.json
```

The replay treats stored centers as suggestions, repeats the rational
contraction and fourth exclusion, recomputes the angular and chord
bounds, and compares every archived field. No floating-point discovery
or external package is needed. The main independent checker includes
this replay too.

A later selected-branch numerical scan through 100,000 folds supplied
an even closer lead at **79,866 folds**. Its
[separate exact local certificate](fold_shoulder_near_79866.json) now
proves another negative ordinary triple and the point-distance bounds

```
0.00000008555 < distance < 0.00000008556.
```

It has the same point-to-point interpretation, without a whole-branch
clearance, event census, or claim of a globally closest near miss. The
numerical scan supplies no proof about its other sampled fold counts.
Repeat this selected certificate with

```sh
python3 experiments/fold_shoulder_events.py --replay experiments/fold_shoulder_near_79866.json
```

The independent checker includes both near-fourth records. Independent
110-digit event solves and direct nearest-copy calculations agree with
both sets of saved root and distance bounds.
