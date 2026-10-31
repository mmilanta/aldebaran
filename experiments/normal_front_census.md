# One hundred and six shared tangent lines

Both rhythms **11 / 6** and **11 / 8** have exactly **106 cooriented
bitangent lines**. Each has exactly two contact points with the selected
travel direction. Their [conormal fronts](normal_front.html)
therefore each have exactly **106 ordinary double points**, with no cusp,
triple point, or higher meeting.

These are tangent-line counts, separate from the **forty crossings** of
each original drawing. Oppositely oriented parallel tangents are outside
this count. This result classifies the two endpoint fronts, not every
front on the blend, and it supplies no knot-equivalence conclusion.

The [rational record](normal_front_census.json) contains the root boxes
and cover statistics. The verifier discovers all products afresh and does
not read that record or use its counts to prune the search.

## A rational front without square roots

The [coordinate derivation](normal_front.md) uses a unit normal and the
signed tangent-line distance. For the exhaustive cover, normalize the
left normal with its L1 length instead:

```
v = q′(t),
L = |v_x|+|v_y|,
N₁ = (−v_y,v_x)/L,
H = q·N₁.
```

`L>0` everywhere. Equality of `(N₁,H)` means exactly the same cooriented
line; changing from Euclidean to L1 normalization loses no information.
The redundant two normal coordinates avoid an angular seam in the cover.

In each rational circle quarter,
`exp(it) = i^k (1+is)²/(1+s²)`, partition s in [0,1] into 512 cells.
Thus **2048 closed arcs cover the entire orbit**. At a cell center,
evaluate position and raw velocity exactly. A chart interval [l,h] has
t-radius at most h−l, since `dt/ds≤2`. Consequently

```
|q(t)−q(t_mid)| ≤ 2305(h−l),
|v(t)−v(t_mid)| ≤ 21345(h−l).
```

Component interval arithmetic encloses `L`, both components of `N₁`,
and H on the whole arc. Every denominator is proved positive.

Put each three-coordinate box in every integer grid bucket it meets.
Bucket widths are 1/4, 1/4, and 32; floors and membership use exact
rational and integer arithmetic. Equal front points belong to a common
bucket. Remaining interval comparisons can only remove disjoint boxes.

## Removing the diagonal

The earlier positive-curvature proof makes the normal angle strictly
increasing. Its rate also satisfies

```
0 < dθ/dt ≤ |q″|/|q′| ≤ 21345/775.
```

If two arc cells are d cells apart by the shorter cyclic index route,
their entire intervening arc has length at most `2(d+1)/512`.
When

```
2·21345·(d+1) < 6·775·512,
```

the normal advances by less than 6 < 2π on that arc. Two distinct
parameter visits there cannot have the same normal. This excludes the
diagonal, adjacent cells, and the orbit's last/first seam. The same test
first checks that one cell alone cannot contain a bitangent pair.

## Every surviving product is covered

On a product of two separated circle cells, solve

```
F(t,u) = (det(q′(t),q′(u)), det(q(t)−q(u),q′(t))) = 0.
```

The [selected-example proof](normal_front.md#two-rational-boxes) derives
its Jacobian. The census uses the same rational interval Fourier jets.
Let m be the product center and R the exact inverse of the center
Jacobian. Every zero is a fixed point of `x ↦ x−R F(x)`. The interval
image gives one of three outcomes:

1. One coordinate misses the original rectangle: no zero exists there.
2. The image is strictly interior and its maximum row-sum derivative
   norm is below one: exactly one zero exists there.
3. Otherwise bisect the longer parameter interval and cover **both**
   children. Hitting the depth limit rejects the attempted proof.

The 11 / 6 cover starts with **8510 product candidates**; 11 / 8 starts
with **8350**. Each complete cover finishes with **106 unique-root
leaves**. All leaves have disjoint interiors, and each certified root is
strictly interior to its leaf, so none can be counted twice. A root on a
partition boundary would prevent successful completion rather than be
accepted twice.

## Two points per line, and no higher meeting

Each root is refined to a small rational square contained strictly
inside its original unique-root leaf. Numerical Newton iterations only
suggest its center. A second contraction proves it afresh, with norm
less than **10⁻⁶**. Interval products then prove:

- The two velocities have positive dot product, hence matching directions.
- The two point boxes are separated in at least one coordinate.

Distinct points on a shared oriented line have different front slopes.
Thus their two graph branches cross transversely.

The two visit boxes also give a small enclosing `(N₁,H)` box for their
shared front point. All **5565 pairs** of such boxes are separated in at
least one coordinate, independently for each endpoint. Therefore all
106 front points are distinct. A line touching three points would yield
three bitangent pairs at the same front point, which this separation
excludes. Higher meetings are excluded for the same reason. Strictly
increasing normal angle already excludes front cusps.

## Reproduce

Use Python's standard library, from the repository root:

```sh
python3 experiments/normal_front_census.py
python3 experiments/normal_front_census.py --inner 6
python3 experiments/normal_front_census.py --write
```

The default proves both endpoints in a few minutes. `--partition` can
change the number of cells per quarter; insufficient bounds or unresolved
products cause failure. `--write` saves the record only after both entire
proofs succeed. Archived roots never seed the cover.

Controls check the Fourier derivative constants, independent rational
evaluations and Jacobian entries, a known certified bitangent's actual
inclusion in the bucket candidate list, exclusion of a shifted root,
local angle exclusions, and floor at negative bucket coordinates.
The original frozen intersection solver is unchanged. This is an exact
computer-assisted argument with rational intervals, not a proof-assistant
verification.
