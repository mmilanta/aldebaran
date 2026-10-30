# Four triangles are not enough

The straight blend from **11 / 6** to **11 / 8** has
[four triple passages and eight touches](rhythm_route.md). Four is the
smallest possible triple count on a generic regular route between those
drawings: strangeness falls from 15 to 11, and each ordinary triple
changes it by one.

Could another route use those four triples and avoid every touch?
**No. Any generic regular route without self-tangencies needs at least
twelve ordinary triple passages, if such a route exists.**

This exact finite-search lower bound applies to arbitrary generic regular
routes between these endpoints, beyond Fourier blends or arm detours.
It constructs no route with twelve triples, and does not prove that a
route without touches exists at all. Cusps and higher multiple meetings
are outside the statement.

## The necessary word move

Label each crossing and record its two visits around the parameter circle,
with exponent `e = −sign det(current tangent, other tangent)`. The two
visits have opposite exponents. Each endpoint has forty crossings and
eighty signed entries. Fresh rational smooth proofs reproduce their
exact words from the [strangeness atlas](strangeness_atlas.json).

Along a route with only ordinary triple passages, all forty pairwise
crossings persist. At a triple, its three crossings form a vanishing
triangle on either side of the event. On each branch, two nearby crossing
visits exchange order. They are adjacent in the word: a sufficiently
small event neighborhood contains no other crossing. The six visits
are distinct positions.

Every actual triple therefore gives this operation:

1. Choose three disjoint pairs of adjacent positions, including pairs
   across the cyclic seam.
2. Their label pairs must be **ab, ac, bc** for three distinct labels.
3. Swap the two signed entries in each chosen pair.

Signs travel with visits. Every pair of tangents remains transverse
through an ordinary triple, so its determinant keeps its sign. A
schematic unsigned example is:

```
… a b … a c … b c …    ↔    … b a … c a … c b …
```

The individual pairs can have either order; the search includes all of them.

## A deliberately larger graph

Take all cyclic signed words with two opposite visits per label. Join
words whenever the three-pair swap is possible. Identify cyclic shifts
and arbitrary renaming of crossing labels.

We do not require a planar realization, an empty bounded triangle, or
the local orientation of a geometric passage. We also forget the exterior
face. These omissions add paths; they cannot remove an actual route's
word path. The program deliberately admits the outer three-pair swap
of three separate curls, for instance.

Between events the cyclic signed word is unchanged. Thus a geometric
route with T triples and no tangencies induces a walk of at most T edges
in this larger graph. A move preserving the canonical word can give a
repeated vertex. A distance lower bound in the larger graph remains a
lower bound for geometric routes. Conversely, an abstract word path
would not by itself construct a geometric route.

## Two balls that do not meet

Explore all words within five moves of each endpoint. The numbers of
**new** words at each exact distance are:

| Distance | From 11 / 6 | From 11 / 8 |
| ---: | ---: | ---: |
| 0 | 1 | 1 |
| 1 | 16 | 11 |
| 2 | 121 | 72 |
| 3 | 615 | 352 |
| 4 | 2,419 | 1,374 |
| 5 | 7,809 | 4,524 |
| Total within five | **10,981** | **6,334** |

The two sets have **no common word**. A path of ten or fewer moves could
be split at a vertex at most five moves from each end. That vertex would
belong to both sets. Therefore no such path exists, giving T ≥ 11.

For a geometric route, strangeness supplies parity. If T₊ and T₋ count
positive and negative passages, then

```
T₊ − T₋ = −4,
T = T₊ + T₋ = 4 + 2T₊.
```

T is even, so **T ≥ 12**. The jump rule is
[Arnold's axiom in Shumakovitch, Theorem 1.3.A(ii)](https://math.dartmouth.edu/~chernov/strangeness.pdf#page=5).
Parity is applied only to an actual geometric route; no strangeness
filter prunes abstract search states.

Every route attaining the unrestricted minimum of four triples therefore
needs some tangencies. Since the endpoint J-invariants agree, direct-touch
changes cancel separately from inverse-touch changes. A nonempty tangency
list has at least two members. This does not show that the straight
blend's eight touches are minimal.

## Reproduce and audit

Use Node and Python, with only their standard libraries:

```sh
node experiments/triple_distance.js
```

The default repeats three rational smooth proofs: both endpoints and a
positive control at blend weight **9/100**. Their full signed words must
match the archives. The known segment from zero to 9/100 contains exactly
four triples and no touch; both searches find its word connection within
four moves.

The first enumeration uses crossing labels and an adjacency graph. It
tries every cyclic starting point and renames labels in first-visit order.

The second uses no crossing labels. Each visit records its sign and the
forward cyclic distance to its partner. It enumerates triples of disjoint
adjacent edges whose six endpoints are paired entirely among themselves,
with no edge joining a visit to its own partner. This is exactly a
triangle of three paired crossings. It permutes positions and partners,
then uses a minimum-rotation algorithm to canonicalize the distance sequence.

The searches share the short breadth-first loop, but their move generation
and canonical encodings differ. Afterward, the partner-distance states
are translated back to words. **Every reached word agrees**, beyond
matching layer counts. Full strings determine membership; hashes in the
[summary](triple_distance.json) only identify the endpoints.

Controls cover cyclic seams, relabeling, move reversal, too few labels,
the deliberately admitted outer triangle, malformed words, and all 510
nonempty binary sequences of length at most eight for minimum rotation.
Archived layer counts never guide pruning.

`--saved` skips fresh smooth proofs. `--write` saves the summary only
after both full enumerations agree and their balls are disjoint. Regenerate
the positive-control archive with:

```sh
python3 experiments/triple_distance_endpoints.py --write
```

The earlier frozen intersection solver is unchanged. This is an exact
computer-assisted combinatorial argument relying on the smooth endpoint
proofs and the ordinary-event classification above. It is not a
proof-assistant verification or an exhaustive search of geometric homotopies.
