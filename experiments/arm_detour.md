# Give the first arm more room

There is another way to connect the [three zero-turn drawings](zero_turns.md)
without stopping. It uses only finite sums of circular motions: lengthen
the first arm, blend the drawings, then shorten the arm again. Two such
three-leg routes connect the original **2 / 3, 4 / 7, and 6 / 11** curves.
Every intermediate curve has tangent index **0** and center winding **+1**.

This calculation is a companion to the [interactive two-route study](blend.html).
The study’s second route uses angles and distances. These further detours
are mathematical notes, with their own reproducible certificate.

Write

```
z_(m,n,R)(t) = R e^(it) + 140 e^(imt) + 65 e^(−int).
```

The original first length is `R = 245`. The two routes are:

| Route | First leg | Middle leg | Last leg |
| --- | --- | --- | --- |
| 2 / 3 → 4 / 7 | At 2 / 3, increase R from 245 to 300 | Hold R = 300; linearly blend 2 / 3 into 4 / 7 | At 4 / 7, decrease R from 300 to 245 |
| 4 / 7 → 6 / 11 | At 4 / 7, increase R from 245 to 700 | Hold R = 700; linearly blend 4 / 7 into 6 / 11 | At 6 / 11, decrease R from 700 to 245 |

In each middle leg, match points at the same orbit time and interpolate
their positions. The frequencies themselves remain integers; this is
not a continuously changing frequency, which could break closure. The
three legs join at exactly identical parametrized curves. Crossings are
allowed, while zero velocities are excluded throughout.

The round lengths 300 and 700 are convenient choices. No claim of a
minimal required arm length is made.

## Certify the complete legs

For any two endpoint curves `z_A,z_B`, the straight position blend has
velocity

```
v_a(t) = (1−a) z_A′(t) + a z_B′(t).
```

At each fixed time, every blended velocity lies on one segment. Evaluate
its endpoints exactly at rational unit-circle points. On an interval of
width `h` in the rational quarter parameter, the angle spans at most `2h`.
If

```
M = max(R_A + 140m_A² + 65n_A², R_B + 140m_B² + 65n_B²),
```

both endpoint velocities vary by at most `E = 2Mh`. So does every matched
point on their segments, uniformly over all blend weights. Compute the
starting segment’s exact squared distance from zero and a dyadic lower
bound `d₀` for its square root, using the same rational projection as
the [angle-and-distance certificate](regular_blend.md). Accept only when

```
d₀ − E > 1.
```

Otherwise bisect the interval. All four quarters must complete; a depth
limit raises an error. The six completed covers give:

| Leg | Accepted intervals | Deepest split |
| --- | ---: | ---: |
| 2 / 3, R: 245 → 300 | 65 | 6 |
| At R = 300, 2 / 3 → 4 / 7 | 436 | 10 |
| 4 / 7, R: 300 → 245 | 146 | 9 |
| 4 / 7, R: 245 → 700 | 181 | 9 |
| At R = 700, 4 / 7 → 6 / 11 | 394 | 10 |
| 6 / 11, R: 700 → 245 | 321 | 12 |

All six continuous two-parameter legs therefore have speed **greater
than one drawing unit per radian**. The original endpoints independently
have tangent index zero, which cannot change on a regular route. Also,
after factoring out `e^(it)`, every intermediate position has residual
real part at least `min(R_A,R_B)−140−65 ≥ 40`. The curve never reaches
the center, whose winding count stays +1 throughout both routes.

Run the standard-library program:

```sh
python3 experiments/arm_detour.py
```

It certifies **1,543 intervals** in total. As a negative control, the
same procedure is applied to the original 2 / 3 → 4 / 7 straight blend
at length 245. That route has the [two known cusp events](blend_cusps.md),
and the verifier rejects it at the depth limit. A failed cover on its
own does not prove singularity; the separate cusp classification does.
