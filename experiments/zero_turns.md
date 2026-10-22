# When the direction's turns cancel

Rhythms **4 / 7** enclose eight regions. Every region has winding count
0, +1, or +2, while the tangent makes **zero net turns** over the whole
orbit. Positive and negative changes in the direction of travel cancel
even though no region has a negative winding count.

![Three orbital curves have tangent index zero: rhythms 2/3, 4/7, and 6/11. The first has one positive and one negative region; the second has four zero-count gaps, one plus-one region, and three plus-two regions; the third has twenty bounded regions including one tiny minus-one region.](zero_turns.png)

The [two-lobe study](two_lobes.html) is an especially friendly example of
a zero tangent index. Its clockwise loop and counterclockwise lobe have
opposite region counts. Following that example alone might suggest that
a zero tangent index requires a negative-winding region. The curve at
4 / 7 gives a different arrangement.

## All three zero-index pairs

The [exact tangent atlas](tangent_turning.py) contains just three zeros
among the 321 regular slider pairs. Their complete smooth region censuses
are now certified:

| Rhythms | Crossings | Bounded regions | Count −1 | Count 0 | Count +1 | Count +2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 / 3 | 1 | 2 | 1 | 0 | 1 | 0 |
| 4 / 7 | 7 | 8 | 0 | 4 | 1 | 3 |
| 6 / 11 | 19 | 20 | 1 | 8 | 6 | 5 |

The unbounded exterior is a further region of count zero in every case.
The center lies in a region of count +1, as it does for all the original
rhythm pairs. The single negative region in 6 / 11 has area about 41.54
square drawing units in the illustrated polygon; it is hard to see at
this scale. The exact census does not depend on its visibility.

Run [zero_turns.py](zero_turns.py) with Python's standard library:

```sh
python3 experiments/zero_turns.py
```

The program first checks the whole tangent atlas to find all three zero
indices. It then applies the existing rational
[intersection certificate](smooth_census.md) to each curve, checking every
possible crossing, separating its two parameter occurrences, excluding
triple points, and constructing the smooth planar graph with winding
labels. The partition sizes per quarter-circle are 1,024, 2,048, and 8,192.
The resulting histograms agree with independent exact sampled-polygon
censuses. The 2 / 3 case also has its [hand proof](two_lobes.md).

In particular, this is a statement about **all** regions of the smooth
4 / 7 curve, including any too small to see in the image. It is not an
inference from an absence of blue pixels. These three examples are also
included in the [complete smooth atlas](smooth_atlas.md), which now covers
all 321 regular rhythm pairs.

## Where the zero goes in the region formula

At a transverse double point, the four adjacent region counts have the
form `k−1, k, k, k+1`, counting corners with multiplicity. Assign the
crossing their mean, `k`. The tangent index equals the sum of region counts
minus the sum of crossing counts. This is Theorem 5.1 in
[Damián Wesenberg, *A new formula for rotation number*](https://arxiv.org/abs/2010.01422).

For **4 / 7**, the bounded region counts sum to

```
4 × 0 + 1 × 1 + 3 × 2 = 7.
```

Every crossing has mean 1: it must touch counts `0, 1, 1, 2`, since the
complete region census has neither negative counts nor a count above 2.
Seven crossings therefore also contribute 7. Their subtraction leaves
`7 − 7 = 0`. No negatively labeled region is needed.

For **2 / 3**, the region sum and crossing sum are both zero. For
**6 / 11**, they are both 15. The exact sampled graph calculation checks
these identities independently of the velocity-angle certificate. Once
the smooth region census and the independent smooth tangent certificate
are available, the formula gives these same crossing sums for the smooth
curves too.

## Recreating the picture

For the optional figure, install NumPy, Matplotlib, and Shapely in a local
environment and run:

```sh
python3 experiments/zero_turns.py --figure
```

The figure program builds a 48,000-segment polygon for each curve, splits
it into faces with Shapely, and labels an interior point of each face by
an independent accumulated-angle sum. It preserves interior rings when
painting the faces and checks all three histograms against the table.
The resulting PNG is a static illustration; the standard-library rational
checks establish the smooth topology. Nothing is added to the website's
runtime or controls.
