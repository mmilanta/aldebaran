# A pocket has a room of its own

The [area notes](cubic_pockets.md) carefully distinguish a gap between
two selected branches from a face of the full orbital drawing. An
unrelated arc could, in principle, enter that gap and subdivide it.
For the first phase study there is now a spatial isolation certificate.

Throughout the full control rectangle, **only the two selected time
charts can enter** the following closed rectangle in drawing coordinates:

```
−212 ≤ x ≤ −190,
 −32 ≤ y ≤  +32.
```

Both selected charts stay strictly between x = −212 and x = −190.
They are unique graphs of x against height over the complete
height interval. Consequently **any closed pocket between those graphs,
with both endpoint heights in [−32,+32], is one face of the full curve**.

This does not count how many pockets occur at every control value.
It establishes that other parts of the orbit cannot subdivide one
that lies in this window.

## The family covered

As in the [phase study](phase_unfolding.md), write

```
z(t,a,φ) = 300 exp(it)
         + 140 [(1−a) exp(2it) + a exp(4it)]
         + 65 exp(iφ) [(1−a) exp(−3it) + a exp(−7it)].
```

The certificate retains the complete parameter intervals

```
0.1375 ≤ a ≤ 0.1456,
−0.001 ≤ φ ≤ +0.001,
```

in every arc bound. These contain the browser controls. Time is
`t = π+u`, with selected charts

```
−0.76 ≤ u ≤ −0.46,      +0.46 ≤ u ≤ +0.76.
```

The earlier rational chart proof gives `y′ < −100` throughout both
charts, and opposite endpoint heights strictly beyond ±32. Every
displayed height therefore has exactly one time in each chart.

## Exclude the rest of the complete orbit

It is enough to cover `−π ≤ u ≤ π`. Use the slightly larger rational
interval `[−16/5,16/5]`. The alternating series for arctan(1), or its
finite geometric expansion under the integral, proves

```
π < 4 Σ from k=0 to 20 of (−1)^k/(2k+1) < 16/5.
```

The second inequality is checked by fractions. There is no floating-point
choice of the orbit endpoint.

Remove the two selected charts. Three closed rational intervals remain.
Subdivide each adaptively. The existing rational trigonometric bounds
enclose x and y for every time and every pair of control parameters in
an arc. A leaf succeeds only if **at least one coordinate interval is
strictly disjoint** from its corresponding rectangle interval.
Successful leaves are independently re-evaluated, and adjacent endpoints
are checked to make sure the cover has no gaps.

The proof needs **80 arcs**. In every accepted arc, at least one
coordinate is separated from the closed rectangle by **more than 0.664
drawing units**. The program rounds that printed bound downward using
integer arithmetic.

A second cover of **32 arcs** proves that the full two selected charts
remain strictly between x = −212 and x = −190. The earlier **32-interval**
height proof is rerun. Thus within the spatial rectangle the *entire*
orbital curve consists of exactly those two height graphs, with a
crossing or touch wherever their values happen to agree.

## Why a gap is a face

Take two consecutive meeting heights a < b inside [−32,+32]. Between
them the two height graphs do not meet. Each is an injective arc, and
together they form a simple closed boundary. Its interior lies
horizontally between them and vertically between a and b, hence entirely
inside the certified rectangle.

No other part of the complete orbit enters that rectangle. The open gap
is connected, contains no curve points, and has its entire boundary on
the curve. It is therefore one bounded component of the curve's
complement: a face of the full drawing. This conclusion does not require
a census elsewhere or a claim that all contacts are generic.

The mirror contact, at approximately `(−201.195546286,0)`, lies strictly
inside the rectangle. So do all six earlier certified finite-phase
contacts. The program checks their boxes against the time charts,
parameter range, and spatial rectangle.

In particular, the two mirror pockets and the pocket born at each of
those six ordinary touches are genuine faces for sufficiently small
positive increments from their birth. Their endpoints and graph arcs
remain inside this window by continuity. The common cubic limit's
shrinking pockets have the same property. No explicit largest increment
is claimed here.

This strengthens the interpretation of the earlier local area laws in
this specified family. It does not make the model's discriminant exact
for the full family, certify all numerical area integrations, or assign
every region of every control setting.

## Reproduce

```sh
python3 experiments/pocket_room.py
```

Only the Python standard library is used. Every cover decision and
coefficient bound uses fractions; the certificate reuses the existing
phase evaluation, height-chart proof, and six tangency boxes without
editing the frozen atlas certificate.

There is a useful negative control. At zero phase the halfway visit
u = 0 is exactly `(−225,0)`, independently of a. The chosen rectangle
excludes it. A larger rectangle extending left to −230 contains this
third branch and must be rejected. A point exactly on a rectangle wall
must also fail the strict exclusion predicate. Both controls pass.
