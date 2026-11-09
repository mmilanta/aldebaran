# A midpoint needs the right intercepts

The [best-insertion rule](parabolic_pockets.md#where-should-the-next-curve-go)
puts the next slope at the midpoint of a widest gap. That rule uses
the original parabolas' specific intercepts, not only their common
curvature. Sliding them sideways independently can change the answer.

Here is a small variation with an exact non-midpoint optimum, and
a total-area formula that explains what changed. It is a different
family from the [alternating-gap compromise theorem](parabolic_tradeoff.md).

## Keep the common curve; change the intercepts

Expand the original family as

```
Xₚ(Y) = Y²/2 − pY + p²/2.
```

Replace the final term by an intercept h(p):

```
Xₚ(Y) = Y²/2 − pY + h(p).
```

The curve with label p has slid horizontally by `h(p)−p²/2`.
The same horizontal slide `U=X−Y²/2` still straightens every branch
into `U=h(p)−pY`, preserving every horizontal width and area.

Choose ordered slope labels p₀<⋯<p_N. Write hᵢ=h(pᵢ), gaps
`gᵢ=pᵢ₊₁−pᵢ`, and adjacent secants

```
sᵢ = (hᵢ₊₁−hᵢ)/gᵢ.
```

Assume the sᵢ increase strictly. These are discrete strictly convex
intercepts; a differentiable function between the samples is unnecessary.
A strictly convex function h on the whole interval supplies them.
The outer span is L=p_N−p₀, and

```
s̄ = (h_N−h₀)/L = Σgᵢsᵢ/L.
```

## The band is still all the bounded faces

At a fixed height Y, the leftmost line is `minᵢ(hᵢ−pᵢY)`.
The leftmost of the two outer lines is
`min(h₀−p₀Y,h_N−p_NY)`. The band between them contains precisely
the bounded faces, apart from their boundaries.

To adapt the earlier run argument, the lines left of a point
(U,Y) satisfy `hᵢ−pᵢY<U`. Subtracting an affine function preserves
discrete strict convexity, so this sublevel set is consecutive.
An empty run, or one including an extreme slope, gives an unbounded
face: the latter extends toward arbitrarily large positive or
negative Y. A nonempty interior run is bounded by its two end
lines and the neighboring two lines.

Every interior run occurs. The chord joining its two neighboring
intercept points lies strictly above all its interior intercepts.
At the height equal to that chord's slope, the neighboring lines
meet above all the selected lines. A point just below their meeting
has exactly the desired run to its left. The half-plane intersection
is convex and connected, so this is one face. Singleton runs give
triangles, and longer runs give quadrilaterals. Thus n chosen slopes
still give `(n−1)(n−2)/2` bounded faces.

## Total area is a weighted secant variance

The lower envelope starts with the p₀ line and switches from line i
to i+1 at Y=sᵢ. Using `x₊=max(x,0)`, it is

```
F(Y) = h₀−p₀Y − Σgᵢ(Y−sᵢ)₊.
```

The outer envelope switches once, at s̄:

```
G(Y) = h₀−p₀Y − L(Y−s̄)₊.
```

Their difference G−F is the band's width. It vanishes outside
the first and last switching heights. Integrate up to any R above
all of them:

```
B = [Σgᵢ(R−sᵢ)² − L(R−s̄)²]/2
  = [Σgᵢsᵢ² − Ls̄²]/2
  = Σgᵢ(sᵢ−s̄)²/2.
```

The R² and R terms cancel by the two span identities. This formula
is half the unnormalized gap-weighted variance of the adjacent
secant slopes. It holds for the complete arrangement, with the
stated strict-convexity assumption.

For the original h(p)=p²/2, `sᵢ=(pᵢ+pᵢ₊₁)/2`. The identity

```
∫[pᵢ,pᵢ₊₁] p² dp = gᵢsᵢ²+gᵢ³/12
```

reduces the variance formula to `(L³−Σgᵢ³)/24`, as before.

## Insert one slope

Split one old gap of width g into a+b=g. Let s_left and s_right
be the two new secants, and suppose the augmented intercept
sequence stays strictly convex. Its old secant was their weighted
mean. The variance formula gives

```
ΔB = [a s_left² + b s_right² − (a s_left+b s_right)²/g]/2
   = ab(s_right−s_left)²/(2g).
```

Only this gap's contribution changes. For h(p)=p²/2, the secant
difference is always g/2, so this is abg/8 and the midpoint wins.
For a general intercept function that difference can depend on
the inserted position, even while the original gap stays fixed.

In a larger arrangement this is extra band area, not necessarily
the area of one newly named face. With only two old slopes, the
new band is exactly the single pocket made by the third branch.

## A cubic intercept moves the optimum

Take `h(p)=p³/3` on [1,3], keeping the outer slopes 1 and 3.
This h is strictly convex there. Insert a new slope r. The two
new secants have difference `2(r+4)/3`, so the one pocket has area

```
A(r) = (r−1)(3−r)(r+4)²/9,       1≤r≤3,
A′(r) = 2(r+4)(5+2r−2r²)/9.
```

The derivative is positive and then negative, changing sign once
inside the interval. Thus the unique global maximum is

```
r* = (1+√11)/2 ≈ 2.158312395178,
A(r*) = (66√11−71)/36 ≈ 4.108256560096.
```

The midpoint r=2 instead gives exactly 4. The shift increases the
best attainable pocket by about 2.71% relative to that midpoint
choice. No numerical optimizer is needed to identify it.

## Reproduce

```sh
python3 experiments/shifted_parabolas.py
```

The standard-library calculation compares complete exact line
clipping, independent piecewise band integration, and the secant
variance. It also identifies every run's polygon and integrates its
curved boundary after undoing the common slide. Affine intercept
changes and slope-label rescaling check the geometric invariances.
Original quadratic, cubic, quartic, and nonuniform discrete examples
exercise the formula beyond equally spaced slopes.

The cubic maximum is retained in an exact quadratic field. Another
101 rational controls and four freshly clipped rational pockets
approaching its irrational slope agree with the bound. The written
envelope identity and derivative prove the general formula and
specific optimum; a finite list of controls alone would not do so.

The alternating-gap theorem continues to concern the original
h(p)=p²/2. A general strictly convex intercept law has the same run
count and a new area formula, but no general smallest-pocket or
compromise optimum is claimed here. A picture of the shifted
three-parabola example is a thread for another visit.
