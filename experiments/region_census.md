# Counting the spaces between the lines

The [interactive winding study](winding.html) colors regions by their local
turn counts. How many distinct regions are there? A pixel grid cannot answer
that reliably: a tiny region can fall between every pixel center.

There is an exact answer for the **stored sampled polygon**, before making
any claim about the full trigonometric curve. The standard-library program
[region_census.py](region_census.py) finds every intersection, constructs the
planar graph, walks every face, and propagates winding labels from the
unbounded region. After sampling, all those operations use integer or rational
arithmetic. No geometry library or floating-point predicate decides a crossing.
An [additional smooth-curve certificate](smooth_census.md) now establishes
the same complete counts for the four drawings below by covering the entire
continuous parameter domain. The sampled algorithm remains useful for the
broader survey, which has no such complete smooth certificate yet.

For the default 24,000 vertices:

| Drawing | Crossings | Bounded regions | Sum of region counts | Sum of crossing counts | Difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Garden · 7 / 13 | 24 | 25 | 33 | 32 | +1 |
| A negative total · 2 / 25 | 100 | 101 | −242 | −217 | −25 |
| Star · 6 / 9 | 25 | 26 | 51 | 45 | +6 |
| Crown · 9 / 23 | 64 | 65 | 81 | 96 | −15 |

The unbounded region has count zero and adds nothing to these sums. Bounded
regions with count zero are included in the region census. Garden has six;
the negative-total drawing has ten. The interactive study's 0 buttons now
visit such bounded gaps, rather than the exterior of the entire drawing.

## A route back to the tangent

The last column recovers the [turn count of the tangent](tangent_turning.md).
This is an instance of the region-and-crossing formula for a generic regular
plane curve: add the winding labels of all faces, then subtract the labels of
all crossings. A crossing's label is the average of its four corner labels,
which have the form `k−1, k, k, k+1`. Count a face twice if it occupies two
corners. See [Damián Wesenberg, *A new formula for rotation number*, Theorem 5.1](https://arxiv.org/abs/2010.01422).

These sums count regions, without weighting by their areas. They explain
another surprise: Crown's regions all have nonnegative counts, but its
tangent makes fifteen net clockwise turns. Its crossing-label sum is larger
than its region-label sum. For signed **area**, instead multiply each region's
label by its area; those contributions sum to the polygon's shoelace formula.
The program checks this latter cancellation exactly as a rational identity.

## How exact geometry starts from sampled coordinates

Python's sine and cosine first generate the polygon vertices as binary
floating-point numbers. Every such stored coordinate is an exact rational
with a power-of-two denominator. Use one common denominator to scale all
the coordinates to integers. This preserves the stored polygon exactly.
It does not replace trigonometric samples with exact values of sine or cosine.

Every potentially intersecting pair of edges is found by a spatial bucket
search. Overlapping edge bounding boxes share a bucket, including at bucket
borders, so this search does not miss an intersection. Integer determinants
decide whether two segments cross. Their crossing coordinates and parameter
fractions are rational numbers, also computed exactly.

After finding the crossings, discard ordinary degree-two vertices from the
graph while retaining each intervening arc's area integral. Sort the four
rays at each crossing by exact determinant signs. Walking from an incoming
arc to the ray clockwise from its reverse keeps the same face on the left.
This traces every oriented face boundary. The unbounded boundary has negative
oriented area; each bounded face has positive area.

Starting with zero outside, every forward arc increases the label by one
from its right face to its left face. Propagate these relations through the
dual graph. The program checks consistency on every arc, the four labels at
every crossing, Euler's identity `faces = crossings + 2` including the outside,
and exact agreement between weighted face areas and the full shoelace sum.

It rejects sampled degeneracies that this generic census does not handle:
overlapping segments, nonadjacent vertex touches, coincident rays, and
multiple branches at one crossing. Needle is excluded because of its cusp.
The code handles a simple polygon separately, with one bounded face.

## A region the raster cannot see

![Crown, colored gold by winding count, with a marked point on the right. A magnified view reveals a tiny region with count +3, only about 0.015 square drawing units in area.](small_region.png)

Crown has eight +3 faces in the 24,000-vertex polygon. Each covers about
**0.01455 square drawing units**, a small fraction of one native canvas
pixel's area. At 960 × 960 pixel centers over the study's coordinate range,
the winding raster sees only counts 0, +1, and +2. All eight +3 regions are
missed. Increasing a grid's resolution is useful, but its color set alone
does not certify the curve's complete set of winding counts.

One representative point is `(291.27, 0)`. Its distance from the sampled
polygon is more than 0.058 drawing units. The uniform polygon-to-curve error
bound is less than 0.000394, so the homotopy argument from the
[counting note](winding.md) proves that this point has count +3 for the smooth
Crown too. Rotating that point by the eightfold symmetry gives eight checked
examples, even though the raster misses their regions.

The magnified illustration uses a 96,000-vertex polygon and optional NumPy,
Matplotlib, and Shapely in [plot_small_region.py](plot_small_region.py). Those
tools supply the offline illustration; the exact census itself uses only
Python's standard library, and the website has no runtime dependencies.

## The broader survey

Run `python3 experiments/region_census.py` for the four displayed drawings,
or add `--all` to survey all 321 regular pairs. Every default-resolution
polygon's region-minus-crossing sum agrees with the independently certified
smooth tangent index. The two simple sampled curves are 3 / 4 and 3 / 5;
15 / 25 has the most crossings, 130, and 131 bounded regions.

The 24,000- and 96,000-vertex censuses agree for all 321 regular pairs, down
to every region-label histogram and crossing-label sum. An independent
Shapely construction and angle-sum labeling also agree at the default
resolution. These are useful checks of the sampled calculation.

These are exhaustive counts for those particular stored polygons. Agreement
with a tangent index is a useful check, but it does not establish that every
smooth crossing or region has been captured. That index can remain unchanged
while pairs of crossings appear or disappear. A proof of the smooth region
census must exclude hidden intersections and tangencies throughout the
continuous parameter domain. [That exclusion is now complete for Garden,
2 / 25, Star, and Crown](smooth_census.md); the remaining 317 regular pairs
are outside that certificate. A separate [hand proof for 2 / 3](two_lobes.md)
establishes its single crossing, leaving 316 regular pairs without a complete
smooth census. Refinement comparisons alone do not supply the missing
exclusion argument for them.
