# An atlas of smooth crossings

The sketchbook has 322 rhythm pairs. Needle, at 8 / 21, has its known cusp;
the other 321 are regular. **All 321 regular pairs now have complete smooth
crossing and region counts**, with a reproducible rational proof for each.

Across these separate drawings there are **14,335 transverse double points
and 14,656 bounded regions**. The only simple curves in the regular atlas
are rhythms **3 / 4 and 3 / 5**, with no crossings. The largest count is
**130 crossings and 131 bounded regions at 15 / 25**. Region winding labels
range from **−7 through +5** across the atlas. These claims concern the
original integer rhythm ranges and fixed arm lengths.

![A grid of certified smooth crossing counts. Rows are the outer rhythm from 2 to 15; columns are the inner rhythm from 3 to 25. Each cell records the number of transverse double points. Needle's cusp is marked separately.](smooth_atlas.png)

Each verified entry has exactly one more bounded region than crossings.
The [JSON record](smooth_atlas.json) gives its crossing count, bounded-region
count, complete histogram of winding labels, tangent index, and successful
quarter-circle partition size. The singular pair and any unresolved regular
pairs have separate statuses. A region of count zero in the histogram is
a bounded gap; the unbounded exterior is an additional zero-count region.

## Recompute a proof

Only Python's standard library is needed:

```sh
python3 experiments/verify_smooth_atlas.py --pair 4 7
python3 experiments/verify_smooth_atlas.py --jobs 2
```

The first command checks one curve; the second checks every archived case
using two independent processes. Omitting `--jobs` uses a single process.
The full rerun in this session took about ten minutes with four processes;
time depends on the machine. The slowest curves need finer partitions.
It fails if any proof, archived count, sampled graph comparison,
or independent tangent certificate fails. An unresolved pair receives no
count from this command.

Stored counts guide **none of the intersection search**. The verifier uses
only the rhythm pair and its proposed partition, reruns the full rational
cover, and compares its answer with the archive afterwards. It also checks
the recorded counts against an independent exact sampled-polygon census
and its tangent index against the exact velocity-polygon certificate.

## The proof is the earlier proof, repeated

The [smooth census guide](smooth_census.md) gives the complete argument:

1. Rational points parametrize each quarter of the time circle.
2. Rational rectangles enclose entire position arcs, using an analytic bound
   on their second derivative.
3. A velocity-disk bound excludes any intersection within local injective
   windows. Spatial buckets enumerate all remaining overlapping arc boxes;
   outward floating bounds are explicitly checked against rational bounds.
4. Exact contraction tests exclude empty boxes and prove the existence,
   uniqueness, and transversality of each accepted double point.
5. Disjoint refined image boxes exclude triple points. Disjoint parameter
   intervals determine the cyclic order of all crossing occurrences.
6. The resulting planar graph gives all faces and their winding labels,
   starting from a geometrically identified outside face.

Thus a completed case excludes hidden crossings, tangencies, triple points,
and smaller unseen regions. A finer repeated polygon survey is useful
evidence but is not the proof used here.

The broad survey tried quarter-circle partitions from 1,024 through 65,536,
with a computation budget for each curve. Targeted retries proposed finer
partitions where needed. Numerical speed estimates suggested partition
sizes, just as numerical Newton steps suggest root boxes; every accepted
result still had to pass all the rational checks. The atlas stores the
successful partitions, so verification skips that search.

One small change made the existing method more accommodating: refined root
boxes can now try radii as small as `2^−40`, in addition to the previous
`2^−30` through `2^−24`. A root for 13 / 25 lies close to an isolating-box
boundary. A smaller proposed box fits there. Strict containment and the
same rational contraction test still decide whether to accept it. No
numerical approximation has authority to certify a crossing.

The source hash recorded in the JSON identifies the intersection program
used for the archive. It is provenance, not a substitute for rerunning the
proof. This is a computer-assisted argument with exact predicates, rather
than an independently formalized proof in a theorem prover.

## The image and the areas

The grid's color measures the number of crossings; it does not describe
positive or negative winding. Region **counts and labels** are certified.
The boundaries and individual region areas in the other illustrations
remain polygonal approximations. The continuous total signed area still
has its separate exact Fourier formula.

To recreate the grid, the optional plotting program needs NumPy and
Matplotlib:

```sh
python3 experiments/plot_smooth_atlas.py
```

The drawing tools remain separate from the dependency-free website. The
[two-lobe study](two_lobes.html) is a small place to start exploring what
the counts mean, while [the three zero-turn curves](zero_turns.md) show
how different region arrangements can share a tangent index.
