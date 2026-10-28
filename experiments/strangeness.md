# Where the crossing remembers

The [interactive study](strangeness.html) lets the starting point move
around three drawings. Their crossing weights and weighted sum change.
A correction from the starting edge changes with them, keeping the
resulting integer fixed.

| Rhythms | Crossings | Tangent index | Strangeness St |
| --- | ---: | ---: | ---: |
| 2 / 3 | 1 | 0 | 0 |
| 4 / 7 | 7 | 0 | −1 |
| 6 / 11 | 19 | 0 | −1 |

The computations implement Alexander Shumakovitch's
[formulas for strangeness](https://math.dartmouth.edu/~chernov/strangeness.pdf#page=6),
§§1.4–1.7, with the normalization of §1.3. The invariant theorem and
its behavior at curve events come from that paper. Here we apply it
to the sketchbook's certified smooth crossing graphs and check two
formulations of the integer.

## The convention at a crossing

Use mathematical coordinates, with positive y upward, and travel in
increasing time. For a crossing first visited at s and then at t,

```
weight w = −sign det(z′(s), z′(t)).
```

Average its four surrounding sector winding labels to get an integer I.
Count every sector, even when one face repeats. Let δ average the two
region labels beside the starting edge. Then

```
St = Σ crossings w I + δ² − ¼.
```

For these orbital curves, t = 0 is uniquely rightmost, at x = 450:
equality in the cosine sum requires the first arm's cosine to equal 1.
Its vertical velocity is `245 + 140m − 65n`. The east side is exterior,
so δ is +½ for upward travel and −½ for downward travel. The correction
vanishes. Needle, 8 / 21, is the sole zero of this velocity in the
supported ranges and remains outside this regular-curve calculation.

That convenient base choice must not become an assumption everywhere.
On an interior edge δ can be ±3/2, giving correction 2, or ±5/2,
giving correction 6. The browser displays the correction explicitly.

## An integer walk around the word

Record each crossing label at every visit, with exponent
`e = −sign det(current tangent, other tangent)`. Its two exponents are
opposite, and its first is its weight. Store the doubled starting-edge
index D = 2δ, an odd integer. Passing a visit gives

```
vertex index I = (D + e)/2,
next doubled edge index = D + 2e.
```

Both visits must agree on I, and the edge-index walk must close.
All operations, including the correction `(D²−1)/4`, use integers.

For 4 / 7 the first four visits are `1⁺ 2⁻ 2⁺ 1⁻`. Starting at D = 1,
the doubled edge indices before them are 1, 3, 1, 3. Both visits to
crossing 1 give I = 1; both visits to crossing 2 give I = 1. Their
starting weights are +1 and −1.

Move the start past `1⁺`. Crossing 1's first remaining visit has
exponent −1, so its contribution falls by 2. The new starting edge
has D = 3, and its correction rises from 0 to 2. St remains −1.

In general, moving the start across exponent e flips that crossing's
weight from e to −e. Its contribution changes by `−2eI`. Meanwhile,

```
correction change = [(D+2e)² − D²]/4 = eD + 1 = 2eI.
```

The changes cancel. This also explains why forgetting the correction
fails at interior starting edges.

## A second calculation through the faces

`strangeness.py` reconstructs the planar rotation system from cyclic
visits and certified determinant signs. At every crossing, the four
outgoing rays have a determined counterclockwise order. A face walk
turns clockwise from the reversed incoming ray, keeping its face left.

After checking Euler's face count and identifying the exterior at t = 0,
the calculation propagates winding through the dual graph: left winding
equals right winding plus one. Every arc must agree. A vertex's four
face labels must have the form `I−1, I, I, I+1`.

Those sector averages recover I without the word's prefix recurrence.
The two labels beside every edge likewise recover its doubled index.
Both formulations must agree on every vertex, every edge, and St.
The complete winding histogram and the identity

```
tangent index = Σ bounded-face winding − Σ crossing mean winding
```

must match the earlier smooth atlas. The two formulations share the
certified cyclic order and determinant signs. They are not independent
intersection searches or a formal proof assistant verification.

## The complete original atlas

The [JSON record](strangeness_atlas.json) covers all **321 regular
rhythm pairs**, keeping Needle separate. Each entry gives the exact
signed word, initial doubled edge index, St, tangent index, crossing
count, and partition used for a fresh smooth proof.

There are **28,670 crossing visits** across these separate drawings.
Each supplies a possible starting edge, and every one was checked.
The two crossing-free curves have the Jordan-circle value 0.

In this finite atlas, St ranges from **−20 at 11 / 24** to
**+32 at 3 / 25**, each once. Garden, 7 / 13, has St = 0; Star,
6 / 9, has St = 5; Crown, 9 / 23, has St = −16. This integer is not
a ranking of visual complexity: Garden's 24 crossings share St with
the one-crossing 2 / 3 drawing.

There is even a pair whose earlier census statistics all agree:
**11 / 6 and 11 / 8** each have 40 crossings, tangent index 11, and
41 bounded faces with winding histogram `{1:10, 2:19, 3:10, 4:2}`.
Their St values are **15 and 11**. The arrangement carries information
that these aggregate counts miss.

Every archived St is divisible by its rotational fold count. The
[sector argument](strangeness_symmetry.md) proves this using winding one
about the rotation center. Its exact quotient-word audit also explains
why a sheet correction is needed before comparing actual values.

At every base edge the word calculation is repeated with its appropriate
correction. Reflection negates exponents and winding indices. Reversing
traversal reverses the word, keeps each visit's exponent, and negates
winding indices. Both preserve St. The integer walk checks those
transformations, and transformed planar graphs are checked separately.

Normalization controls include a Jordan circle and figure eight K₀,
both with value 0, and circles with k separate positive curls,
representing Kₖ₊₁, with value k for k = 1 through 8. Their tangent
indices are checked too. Malformed words, inconsistent visits, even
doubled edge indices, and a missing interior correction have negative
controls.

## What the endpoint difference tells us

The first two zero-turn drawings have different St. A generic regular
homotopy between them therefore needs a triple-point event: ordinary
self-tangencies leave St fixed, while a positive triple passage adds 1.
From 2 / 3 to 4 / 7 the net signed triple change is −1.

This constrains **generic** routes. The actual
[arm detour](arm_detour.html) retains reflection and has special cubic
contacts. The earlier list of selected meetings is not a census of
all branches. These endpoint values do not identify which events
account for the difference on that specific route. The equal values
at 4 / 7 and 6 / 11 do not exclude triple events: signed changes can cancel.

A [continuous-window certificate](triple_passage.md) now isolates one
negative triple passage on that first detour. Throughout weights
0.4641–0.4642 every crossing belongs to three specified branches,
and exactly one triple event occurs. Its St jump is −1. A
[magnified still](triple_passage.svg) shows the little triangle switching
sides. This classifies that narrow interval, rather than the full route.

## Reproduce

[The same counts, a different weave](weave.html) follows a different
route: a regular straight blend from 11 / 6 to 11 / 8. Those endpoints
have identical crossing, tangent, and winding-region counts, but St
15 and 11. Two complete short windows each contain exactly one
reflected pair of negative triple passages. The
[certificate](rhythm_passages.md) accounts for every crossing on each
whole window, without claiming a full-route event census.

Only Python's standard library or Node is needed:

```sh
# Three fresh smooth proofs and both invariant calculations:
python3 experiments/strangeness.py

# Reprove one pair and compare its exact word and counts:
python3 experiments/strangeness.py --pair 4 7

# Reprove all 321 (about six minutes with two processes here):
python3 experiments/strangeness.py --all --jobs 2

# Audit archived words WITHOUT repeating their smooth proofs:
python3 experiments/strangeness.py --saved

# Regenerate browser data and the standalone SVG from three fresh proofs:
python3 experiments/strangeness_figure.py

# Browser arithmetic, geometric probes, and all archived words:
node experiments/strangeness_check.js
```

Add `--write` to `--all` to regenerate the separate strangeness archive.
Stored values do not guide the intersection search. Fresh proofs use
the earlier smooth atlas's proposed partition sizes, repeat its complete
rational exclusion and contraction argument, check its planar census,
then extract words and compute St. The frozen intersection source is
unchanged, with SHA-256 matching the earlier atlas metadata.

Rounded times and positions appear only for the three displayed curves.
They place the picture; integer arithmetic uses the exact word. The
standalone SVG likewise has approximate geometry and exact integer labels.
It remains available without JavaScript or if any browser script fails.

The Node checks independently evaluate both tangents at each displayed
crossing, and sample winding in all four sectors and on both sides of
every displayed starting edge. Every probe has clearance more than
390 times its interpolation-error allowance at 96,000 samples. The
largest gap between rounded crossing visits is below 9.7 × 10⁻¹¹ drawing
units. These are floating-point implementation checks with comfortable
distance margins; the smooth certification is the rational calculation.
