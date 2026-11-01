# A knot, one move at a time

The [viewer](positive_front.html) follows a literal **6,367-move positive
front movie** from the certified 11 / 6 braid word to the 11 / 8 word:

| Local move | Count |
| --- | ---: |
| Independent crossings exchange order | 5,450 |
| Three-strand Artin move | 722 |
| First crossing moves past the cut | 195 |

Every word has eleven strands, 106 positive crossings, and a one-component
closure. The last word agrees with its target **letter for letter**.
This is a constructive positive-front isotopy, beyond the earlier
[conjugacy witness and classification corollary](normal_front_braid.md).
The sequence is not asserted to be shortest. For the explicit construction
below, a common distance offset of **1,000,000,000** is sufficient. This
very loose bound serves the existence proof; the local viewer uses 25.

Together with the offset argument below, it proves:

> There is a regular route between the two original oriented plane
> drawings, with positive curvature throughout and **no direct
> self-tangency**. Inverse self-tangencies are allowed.

The [offset follow-up](parallel_offset.md) now counts **66 inverse
touches** on a generic version of this route and certifies all its
offset-leg contact locations. Its plane triple passages remain unclassified.
In particular it does not construct a route without **either** kind of touch, or attain the
[twelve-triple lower bound](triple_distance.md) for such a route.

The [JSON record](positive_front.json) lists all moves; the
[standalone sheet](positive_front.svg) illustrates one three-strand move.
The viewer displays a local smooth model for each selected rule, rather
than numerically parametrizing the entire plane route.

## Turn the witness into local moves

Write A and B for the endpoint words. The earlier positive conjugator
C has 195 letters and satisfies AC = CB. Expose its first letter at
the beginning of A using positive Artin relations, then cycle that
letter to the end. Repeat with the next letter of C. In this particular
calculation **all 195 extractions succeed**.

Leading-letter extraction follows Jacquemard's algorithm, as recalled in
[Deloup–Garber–Kaplan–Teicher, *Palindromic Braids*, §2](https://arxiv.org/abs/math/0410288).
Find the first requested letter i. Commute it left across letters at
distance greater than one. At a blocking adjacent letter j, recursively
expose j in the suffix to form j i j, then replace that triple by i j i.
A failure restores the word and its move list.

After cycling all letters of C, straighten the remaining positive word
to the literal B by exposing B's letters in order and freezing each
completed prefix. Every extraction succeeds here too.

The search is not trusted as a verifier. A separate small replayer checks
each rule directly:

```
… i j …   ↔   … j i …          |i−j| > 1,
… i j i … ↔   … j i j …        |i−j| = 1,
i W       →   W i              closed-braid cut move.
```

It checks the exact endpoints, every intermediate length and component
count, and that the 195 cycled letters spell exactly C. No hash replaces
word equality. The old faithful Artin-action equality is an additional
independent control, rather than a substitute for the local moves.

As controls on the search, enumerate **all** four-strand positive words
through length six and every applicable relation edge. Connected
components of these finite graphs determine their complete starting
sets, because all positive relations preserve length. For each word
and each of the three possible generators, extraction must succeed
exactly when that starting letter occurs in its component. All **3,279**
tests agree, and every successful extraction's own move list replays.
Invalid moves, incomplete movies, and altered endpoints must fail.

The geometric completeness of A and B remains the job of the separate
[rational braid certificate](normal_front_braid.md). The new calculation
begins with those recorded words; it does not re-extract them from samples.

## A three-strand meeting with three distinct slopes

Here is an explicit local front, using angle coordinate x in [−1,1]. Set

```
f(x) = (15x−10x³+3x⁵)/8,
g(x) = (1−x²)³,
h₀ = f(x),       h₁ = δ g(x),       h₂ = −f(x),
−1/4 ≤ δ ≤ 1/4.
```

At the left boundary the heights are −1,0,1; at the right they are
1,0,−1. The first two derivatives of all three heights vanish at both
boundaries. Thus they fit constant outer strands with C² joins.

The outer strands cross only at x=0, with slopes ±15/8.
For a middle–outer meeting, solve f/g = ±δ. On the open interval,

```
(f/g)′ = (f′g−fg′)/g² > 0.
```

Indeed f is odd and strictly increasing, g is even and positive, and
g′ has the opposite sign to x. Thus f′g is positive and fg′ is
nonpositive. Also f/g goes from −∞ to +∞. Each pair has exactly one
crossing, with unequal slopes, for every δ.

For a quantitative check, `f(1/4) > g(1/4)/4`, so all middle–outer
meetings lie in (−1/4,1/4). Their slope differences have magnitude at
least `f′(1/4) = 3375/2048 > 1`. At δ=0 the three graph heights meet
at x=0, with slopes

```
15/8, 0, −15/8.
```

The Legendrian lift `(x,h′,h)` therefore has **three distinct points**
even at that instant. For negative δ the crossing word is i,(i+1),i;
for positive δ it is (i+1),i,(i+1). Reversing δ gives either direction
of the Artin move. There is no front tangency or cusp in this family.

This triple is a **three-contact tangent line**, not an original
plane triple point. The viewer reconstructs the three points at x=0;
the middle distance changes with δ while the outer two slopes remain
±15/8. At δ=0 all three points lie on the same line and stay apart.

## The other local models

A single crossing uses the quintic step

```
S(t) = 0                              t ≤ 0,
       10t³−15t⁴+6t⁵                  0 ≤ t ≤ 1,
       1                              t ≥ 1.
```

For a pair starting at heights j and j+1, use
`j+S((x−c)/w+1/2)` and `j+1−S((x−c)/w+1/2)`.
Their only crossing is at x=c, with distinct slopes. Both endpoint
jets match constant strands through order two.

For a commutation, apply this formula on the two disjoint height bands,
with width w=14/25 and centers

```
c₀ = −21(1−2u)/50,      c₁ = +21(1−2u)/50,      0 ≤ u ≤ 1.
```

At halfway, the crossings share an angle but have distinct heights.
The two bands cannot meet: their generators differ by at least two.
Unused strands remain at their integer heights. The viewer subtracts
the common middle height to center its local chart.

A cut move is a change of reading point on an unchanged closed front.
The displayed single crossing stays fixed while the dashed cut passes
it. Returning the cut to a standard angular origin is a base-circle
rotation; in the plane it can be implemented by a rigid rotation.

These positive front moves lift to Legendrian isotopies; the same
observation appears in [Etnyre–Vértesi, *Legendrian satellites*, §4.1.1](https://etnyre.math.gatech.edu/preprints/papers/braidsatellites.pdf#page=19).
Here the formulas and literal move list provide the construction without
using the uniqueness theorem to infer it.

### Why the local model matches the full word

For a canonical word front, give each crossing its own small angular
interval and use S there; outside it keep the integer height levels.
Follow strand identities through the swaps, and join matching heights
at the seam. The word's permutation has one cycle, so these eleven
pieces give one closed trace over eleven normal turns.

The three-strand polynomial model has the same pairwise crossing order
as the corresponding three-crossing block at either end of its move.
Align their crossing angles by an increasing change of horizontal
coordinate. Then interpolate their heights linearly. At any angle
away from a prescribed crossing, each pairwise difference has the same
strict sign in both graphs, so interpolation cannot create a meeting.
At a crossing the two derivatives have the same nonzero sign of their
difference, so interpolation keeps it transverse. This joins the block
to its local model and back. The same argument applies to commutations.
The coordinate changes fix the block boundaries; the constant endpoint
jets of the canonical graph still join through order two.

Here is one specific increasing coordinate change, with useful derivative
bounds. Given ordered source nodes cₖ and target nodes aₖ, write
`dₖ = cₖ₊₁−cₖ`, `Dₖ = aₖ₊₁−aₖ`, and choose
`ε = ½ minₖ(Dₖ/dₖ) > 0`. On each node interval set

```
φ(x) = aₖ + ε(x−cₖ) + (Dₖ−εdₖ) S((x−cₖ)/dₖ).
```

It has derivative at least ε, first derivative ε at all nodes, and
second derivative zero at all nodes. Thus it joins to an increasing
C² map, with

```
φ′ ≤ (15/8) maxₖ(Dₖ/dₖ),
|φ″| ≤ 6 maxₖ(Dₖ/dₖ²).
```

The straight coordinate homotopy `(1−u)x+uφ(x)` stays increasing.
For a circle, extend the nodes periodically; φ then has degree one and
the same cyclic jets. This supplies all crossing-aligning maps used here.

## Join the actual endpoint fronts

The actual endpoint fronts already have positive normal projection and
the certified words A and B. Most crossing angles are separately
ordered. The two groups of five simultaneous crossings occupy disjoint
height bands and use disjoint strands, as proved in the
[word certificate](normal_front_braid.md#order-every-crossing-rationally).
They can therefore be separated in angle by arbitrarily small independent
local coordinate changes in those bands, in the certified word order.
Choose disjoint angular neighborhoods of the two groups. In each active
band use `ψ(θ)=θ+δη(θ)`, with a smooth bump η equal to one near its
crossing. Choose the distinct shifts small enough that the bands stay
separate, and that `|ψ′|≤2`, `ψ′>0`, and `|ψ″|≤1` on every strand.
Scaling the finitely many shifts ensures all these inequalities;
the coordinate homotopy has the same bounds.

After this separation, align the crossing angles with a canonical word
front by an increasing circle-coordinate change. Interpolate strand
heights as above. Pairwise order on each open interval, and nonzero
slope differences at its ends, prove that the lift stays embedded.
This works at the seam too: the actual and canonical words have the
same strand permutation, and their cyclic jets agree. Apply it at both
endpoints of the move list.

The simultaneous groups can also be seen directly from reflection.
At each horizontal normal, reflection fixes one of the eleven visits
(t=0 or t=π) and pairs the other ten. A reflected pair has equal x
coordinates and therefore equal tangent-line height. This gives five
crossings at that angle. Their distinct height bands permit arbitrarily
small independent shifts into the recorded order.

The finite construction is C² in the front coordinate. One can smooth
its joins in C², including in the family parameter, while keeping the
endpoint fronts fixed. Embeddedness of the compact Legendrian family
is open in C¹ for `(θ,h′,h)`; equivalently it is open in C² for these
graphs. Thus smoothing preserves the positive normal projection and
the absence of equal `(θ,h,h′)` at distinct visits. A smooth positive-front
isotopy between the actual endpoints has now been constructed.

## One common offset makes the plane route regular

For the smooth family write hₛ(Θ) on the eleven-turn angular cover.
All formulas respect the cyclic joins. Set

```
N(Θ) = (cos Θ, sin Θ),
qₛ,M = (hₛ−M) N + hₛ′ N′,
∂qₛ,M/∂Θ = (hₛ+hₛ″−M) N′.
```

The family and angular cover are compact, so any **one** constant
`M > max(0, maxₛ,Θ(hₛ+hₛ″))` works. The explicit estimates below allow
**M = 10⁹** for this construction. Its projected velocity is strictly negative
in the N′ direction everywhere. Thus it never vanishes, N is still its
left normal, and the curve has positive curvature.

If two projected points met with the same travel direction, their left
normals would agree. Dotting their equality with N and N′ would then
give equal h and h′ at that direction. This contradicts embeddedness
of the front's Legendrian lift. Subtracting M from all heights does
not change either equality test. Therefore the offset route has
**no direct self-tangency**.

At either original endpoint, positive curvature gives `h+h″ = −ρ < 0`.
Increasing the offset from 0 to M, or decreasing it back, keeps the
velocity coefficient negative. Their lifts remain embedded because a
common offset preserves all equal-normal differences. These two offset
legs join the original drawings to the offset front isotopy and back.
They are regular and avoid direct touches as well.

This is a constructive existence argument, with a specified coarse
offset. It does **not** claim that the viewer's small local offset 25
works on the full endpoint-straightening isotopy. Drawing the full plane
movie at a useful scale, or finding a much smaller offset, remains a
separate project.

### A numerical bound for the entire construction

At the actual endpoints, the earlier curvature and speed bounds give

```
|h| ≤ 450,       |h′| ≤ 450,
|h″| ≤ 450 + 2305·212521/118999 < 4567.
```

The small independent dephasing maps above therefore give
`|h′|≤900` and `|h″|≤4·4567+450=18718`. Heights still have magnitude
at most 450. This includes the coordinate homotopy performing the
dephasing, not only its final graph.

For aligning these fronts with the canonical word, use the displayed
map φ with **106 equally spaced source crossing nodes**. Their spacing
is `d=2π/106`. Every positive target gap is at most 2π. Thus

```
φ′ ≤ 795/4,
|φ″| < 106² = 11236,       using π > 3.
```

These bounds also cover the straight coordinate homotopy, since its
first derivative is between 1 and φ′ and its second derivative is a
multiple of φ″. The chain rule gives the exact common upper bound

```
h+h″ ≤ 450 + 18718(795/4)² + 900·11236
      = 5996024775/8
      < 750000000.
```

It remains to bound the canonical word and its local moves. All its
heights lie between 0 and 10. A single step occupies an angular slot
of length `d=2π/106`; its second derivative is at most `6/d²`.
For the polynomial triple model at either endpoint δ=±1/4, the two
nonzero crossing positions have magnitude r with **1/8 < r < 1/4**.
The two rational comparisons `f(1/8)<g(1/8)/4` and
`f(1/4)>g(1/4)/4` prove that bracket.

Align the polynomial block's nodes `−1,−r,0,r,1` with the canonical
nodes `−1,−2/3,0,2/3,1`. The formula for φ gives `φ′≤10` and
`|φ″|≤256`. A canonical triple block in x-coordinates has
`|h′|≤45/16` and `|h″|≤27/2`. Consequently its horizontally changed
graph has

```
|h″| ≤ (27/2)·10² + (45/16)·256 = 2070.
```

For a commutation, use nodes `−1,−21/50,0,21/50,1` at the endpoint
model, mapped to `−1,−1/2,0,1/2,1`. The deliberately loose bounds
`φ′≤15`, `|φ″|≤384` and the canonical bounds `|h′|≤15/8`, `|h″|≤6`
give the same upper bound 2070. The local models themselves have
smaller second-derivative bounds; interpolation preserves the common
bound. Each block spans at least two angular slots, so
`|dx/dθ|≤106/(2π)<106/6`. The whole canonical movie satisfies

```
h+h″ < 10 + 2070(106/6)² = 646080 < 1000000.
```

The change of cut is a circle rotation and preserves these bounds.
The height interpolations joining the actual and canonical fronts also
preserve an upper bound on h+h″ by linearity. Thus the unsmoothed
finite family has h+h″ below 750,000,000 throughout. Smooth it with
less than one unit of error in h+h″, fixing the smooth original
endpoints, with individual errors in h and h″ below 1/2. The bound stays
below 750,000,001, well below **10⁹**; also `|h|<451` after smoothing.

The program checks the polynomial factorizations, the two rational
crossing brackets, and all these rational constants afresh. This is an
analytic estimate checked by exact arithmetic, rather than an interval
cover of a sampled or numerically chosen full route.

### The displayed local offset really is enough

The local model alone has an elementary uniform bound. For the triple,
`|f|≤1`, `|f″|≤15/2`, `|δg|≤1/4`, and the coefficient bound
`|δg″|≤18` suffice. For a swap, `|S″|≤6`; the active width is 14/25,
and the centered local heights have magnitude at most 5. Thus

```
h+h″ ≤ 5 + 6/(14/25)² = 4730/196 < 25.
```

The wider single-crossing cut chart satisfies this bound too. So the
viewer can safely reconstruct its local points with offset 25. This
bound is independent of sample density and progress.

## Reproduce

Only Python's and Node's standard libraries are needed:

```sh
python3 experiments/positive_front.py
python3 experiments/positive_front.py --write
node experiments/positive_front_check.js
node experiments/positive_front_figure.js
```

The Python default searches and replays the entire movie, then runs its
exact controls. `--write` saves the checked record and browser data.
The Node check independently replays the saved rules, compares the
geometric source words, and checks the local models and reconstruction.
The generated SVG uses the same polynomial formulas as the viewer.
Numerical derivative and rendering checks complement the analytic
inequalities; they do not replace them. The frozen intersection solver
and earlier certificates are unchanged.
