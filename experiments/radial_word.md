# The long way around

Moving the drawings far outward makes their weave readable from the
certified positive braid words. The resulting strangeness values are
**−87 for 11 / 6** and **−101 for 11 / 8**. They differ sharply from
the original values **15** and **11**.

Consequently, a generic outward leg continued sufficiently far has at
least **102** ordinary triple passages for the first drawing and
**112** for the second. The [33 inverse touches on each leg](parallel_offset.md)
do not change strangeness and cannot account for these differences.
These are triple **lower bounds**, not complete counts of those legs.

There is a further consequence for the [6,367-move construction](positive_front.md).
For a sufficiently large common offset, its middle has exactly **722
ordinary plane triple passages**: **354 positive and 368 negative**.
Thus a sufficiently distant version of that particular complete route
has at least **936 triple passages**, in addition to its **66 inverse
touches**. This is a long route between two drawings whose strangeness
differs by only four.

The offset can be chosen finite, but **no numerical threshold for these
triple conclusions is supplied**. The earlier offset **10⁹** proves
regularity and absence of touches in the middle. We do not assert that
it also meets the stronger event-stability threshold established here
by compactness. Increase the common offset if necessary. All inverse
contacts are below 157, so this does not change their count.

## A drawing that becomes a graph

Use the left-normal chart of the [conormal front](normal_front.md):

```
N(θ) = (cos θ, sin θ),       p = h_θ,
q_M = (h−M) N + p N′.
```

At either endpoint θ runs over eleven turns, with one closed trace.
For M sufficiently large, both `M−h` and `M−h−h_θθ` are positive.
Set α to the continuous polar angle of **−q_M**, and let r be its radius.
Then

```
r² = (M−h)²+p²,
α = θ − atan(p/(M−h)),
α_θ = (M−h)(M−h−h_θθ)/r² > 0.
```

So the plane drawing has eleven radial visits in every polar direction.
Its radial deficit `D_M(α)=M−r` tends to h as M tends to infinity.
The elementary identities

```
D_M = h − p²/(r+M−h),
(D_M)_α = p r/(M−h)
```

prove uniform C¹ convergence on the finite angular cover, after the
increasing coordinate change θ↔α. In particular, the [106 transverse
front crossings](normal_front_census.md), their cyclic visit orders,
and their determinant signs persist for all sufficiently large M.
The compact complement of small crossing neighborhoods has a nonzero
height gap, so there are no additional crossings. Distinct front
crossing points similarly exclude plane triples at those endpoint
offsets. The graphs' seam poses no extra condition: all formulas are
periodic on the eleven-turn cover.

## Derive the signs before reading the word

Write the plane curve in radial coordinates as

```
q(α) = −(M−D(α)) N(α),
q_α = D′ N − r N′,       r>0.
```

At a double point both radii agree. If the two arriving strands are
a and b, their determinant is

```
det(q_a′, q_b′) = r (D_b′−D_a′).
```

The strand arriving from **lower D** crosses upward relative to the
other: `D_a′>D_b′`. Its determinant is negative and therefore its
crossing exponent `−sign det(current tangent, other tangent)` is **+1**.
The other strand has exponent **−1**. This agrees with the
[existing strangeness convention](strangeness.md#the-convention-at-a-crossing).

At the initial section, lowest height means **largest radius**. Start
on this outermost wire just before the first crossing visit. Increasing
α travels counterclockwise; its right side is unbounded and has winding
zero, while its left side has winding one. The starting doubled edge
index is therefore **+1**, with zero starting correction. This is a
geometric choice of exterior, rather than a choice made to fit an integer.

Now label each wire by its initial height rank, starting at zero.
Scan the positive braid word in angular order. At each generator:

1. Append its crossing label with exponent +1 to the arriving lower wire.
2. Append the same label with exponent −1 to the arriving upper wire.
3. Exchange the two wire labels in the height order.

After the scan, continue each wire at the initial wire whose rank is
its **final rank**. This uses the inverse of the final rank-to-wire
array. The geometric closure is one cycle, and starting at rank zero
therefore visits every wire exactly once. Concatenate their visit lists
in that cycle order. Commuting disjoint crossings at the same angle
cannot change a wire's visit list.

This supplies a signed planar crossing word. The integer edge-index
walk and a separate planar face walk recover every crossing mean,
every edge index, and St independently of one another. The face walk
must give a sphere embedding, tangent index eleven, positive bounded
winding labels, and exactly one winding-eleven innermost region.

| Drawing | Original St | Far-out St | Signed outward triples | Minimum outward triples |
| --- | ---: | ---: | ---: | ---: |
| 11 / 6 | 15 | −87 | −102 | 102 |
| 11 / 8 | 11 | −101 | −112 | 112 |

The [new record](radial_word.json) archives both full 212-visit words,
their closure orders and winding histograms, and the signs of all 722
three-strand moves. Fresh complete front covers and rational strand-order
proofs are repeated before that record can be written. Fresh original
plane proofs re-establish the values 15 and 11.

## The entire family converges, including the event parameter

To transfer the middle's **event count**, pointwise convergence of
individual drawings is insufficient. Use the finite smooth family
`h(θ,s)` specified by the positive-front construction, with route
parameter s. It lives on a fixed compact angular cover. Its coordinate
changes, local blocks, and height interpolations preserve the cyclic
strand joins. All needed spatial and parameter derivatives are bounded.

In addition to the formulas above, differentiation at **fixed α** gives
the useful cancellation

```
α_s at fixed θ = −[(M−h) p_s+p h_s]/r²,
(D_M)_s at fixed α = r h_s/(M−h).
```

Thus D_M converges to h **uniformly in C¹ in both α and s**. One can
also set ε=1/M and extend the formulas smoothly to ε=0: the angular
coordinate change is the identity there and D_0=h. The implicit
function theorem then applies to crossings and triple events at ε=0.

Here is the complete front-event inventory of the specified family:

- Endpoint dephasing separates crossings in disjoint height bands.
  It cannot introduce a third strand at either crossing.
- Increasing angular coordinate changes preserve all strand equalities.
- Height interpolation between aligned diagrams keeps the same pairwise
  strict order off their crossing nodes and the same nonzero slope
  differences at those nodes. Their nodes are distinct. No triple is
  introduced in either endpoint straightening or local-block alignment.
- A commutation moves crossings in disjoint height bands. At equal
  angles their heights remain different. A cut change is a rotation.
- Each of the **722** three-strand blocks has exactly one front triple.
  For `h₀=f(x), h₁=δg(x), h₂=−f(x)`, it is `(x,δ)=(0,0)`.
  The differences `(f−δg, −f−δg)` have Jacobian determinant
  **−15/4** in `(x,δ)`. All three slopes are distinct, and δ changes
  transversely with the route parameter. Unused strands lie outside
  the block's height band. There is no fourth branch.

Make stage joins stationary in the family parameter before smoothing.
All triple neighborhoods lie in the interior of the smooth polynomial
blocks, so keep them fixed. Elsewhere, the finitely many pairwise
crossing slope gaps and triple-exclusion gaps have positive compact
margins. Sufficiently small smoothing preserves them, fixes the original
endpoints, and preserves the earlier strict regularity bounds. Therefore
one may choose the smooth constructed front family with exactly those
722 ordinary triples and no higher meeting.

For each triple, choose a small disjoint neighborhood in `(angle,s)`.
Its two height-difference equations have a nonsingular Jacobian. The
smooth ε extension and the implicit function theorem give exactly one
nearby plane triple for all small positive ε, with the same sign.
On the compact complement, every triple's pair of height differences
stays separated from `(0,0)`, uniformly. Thus no further triple can
appear. The same compactness argument excludes fourfold meetings and
preserves all nonzero pairwise crossing slope differences. Choose one
ε bound for these finitely many tests and all eleven strands.

This proves **exactly 722 ordinary plane triples** in the middle for
all sufficiently large M. The middle has no touches by the earlier
support-distance argument. Each triple's time generally shifts: the
[local offset-25 calculation](positive_front.md#the-plane-triple-comes-at-a-different-moment)
already exhibits that shift explicitly. No equality of front and plane
event times is used here.

## What the signed movie says

The verifier reconstructs the radial word and its planar faces after
**every** one of the 6,367 legal moves. Independent swaps and cut changes
have zero St change. Every three-strand move changes it by +1 or −1:

| Middle event sign | Count |
| --- | ---: |
| Positive triple | 354 |
| Negative triple | 368 |
| Total | 722 |
| Signed change | −14 |

The signs agree with the convention in
[Shumakovitch, §§1.3–1.7](https://math.dartmouth.edu/~chernov/strangeness.pdf#page=5):
an ordinary positive triple adds one to St; self-tangencies do not
change it. Applying that theorem to the family just constructed gives
the same signed counts in the plane.

Including the offset legs gives

```
15  −102→  −87  −14→  −101  +112→  11.
```

The arrows on the first and last legs give **net** signed changes.
They require at least 102 negative triples outward and at least 112
positive triples on the return leg. Extra positive/negative pairs may
occur there. The complete sufficiently distant route therefore has
at least **466 positive and 470 negative triples**, or **936 total**,
with net signed change **−4**. A generic perturbation separates any
simultaneous offset events and retains the 33 inverse births and 33
inverse deaths proved separately.

A later [selected fourfold calculation](offset_fourfold.md) strengthens
these lower bounds to **106 and 116 on the outward legs**, and **944
over the full route**. Each certified mirror-axis fourfold resolves
into two positive and two negative triples. The positive events force
extra passages beyond the signed differences used above. The basic
word calculation in this note and its script still reports 936; the
stronger bound uses those additional local geometric certificates.

This conclusion counts the middle completely and bounds the legs.
It does not supply an exact total for the route, locate its remaining
triples, claim a minimal construction, or give a finite numerical
threshold for triple stabilization.

## Reproduce

Only Python's standard library is needed:

```sh
python3 experiments/radial_word.py
python3 experiments/radial_word.py --write
python3 experiments/radial_word.py --saved
```

The default repeats both exhaustive endpoint front covers, their rational
word extraction, both original smooth plane proofs, the integer and face
calculations, and the entire signed movie audit. `--saved` instead assumes
the archived front completeness **and geometric word extraction**; it
still repeats the original plane proofs. It cannot write a new record.

Controls exhaust all positive words through length seven on two, three,
and four strands. Every one-component closure must pass both formulations,
every starting edge, reflection, and reversal; every multicomponent
closure must fail. Separate rank-following tests catch inverse-permutation
mistakes. Nested-curl staircase words have St=n(n−1)/2; every odd
two-strand word has St=1. Malformed generators and strand counts fail.
An exact rational polar tangent calculation checks the exponent sign.
The frozen intersection solver and all older certificate files are unchanged.

The geometric limit and uniform event argument are analytic proofs in
this note. The scripts check their finite combinatorial input and output;
they do not compute their compactness margins or a numerical M threshold.
