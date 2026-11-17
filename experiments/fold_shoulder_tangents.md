# The finer weave has a flatter meeting

The [analytic shoulder branch](fold_shoulder.md) gives at least three
visits for every sufficiently large fold count. Its four-equation
Jacobian is nonzero, but that alone does not prove that the three
spatial tangents are pairwise transverse. A first-order expansion does.

**All three selected pairs are transverse for sufficiently large d.**
In increasing time order their unfolding quantity H is negative. If no
fourth branch joins the point, this is an ordinary negative triple.
There is still **no numerical cutoff or uniform fourth-visit exclusion**.
However, a fourth branch cannot join at both of two consecutive
sufficiently large fold counts. Hence **infinitely many ordinary negative
triples approach the shoulder**, and at least one selected batch is
ordinary in each such pair of fold counts. The radial threshold is the
**unattained infimum even for ordinary negative triple phases**.
In fact the selected batch is ordinary at a **density-one set of
integer fold counts**: the proportion tends to 100% as more folds are
counted. This is an asymptotic statement with no effective starting
count or density error bound.
The [finite certificates](fold_shoulder_events.md) settle those local
questions separately at d=30,60,120, without identifying a continuation
to this branch.

The outer tangent pair is unusually flat: its small angle decays as
**d⁻³**, while the other two angles decay as d⁻². The selected triangle's
quadratic area coefficient K grows linearly:

```
K_d/d → 871.385387546664… .
```

Here K_d is the coefficient as the phase offset tends to zero at each
fixed d. This does not supply a uniform finite-offset area estimate as
d grows, nor say that the selected triangle is a face of the full curve.

## Keep one more order

Use the shoulder notation

```
f = |B|²,  β = arg B,  a=f_θθθ/6>0,  b=f_θφ<0,
κ=β_θ>0,  s=2π/κ,  C=−as²/b,
h=1/d,    θ_i=θ*+h y_i(h),    φ=φ*+h²λ(h).
```

The three limiting y values are −s,0,s. Label visits by that **ellipse
order**, with subscripts −,0,+. These labels run opposite to their
increasing time order when h is small and positive.

Two additional coefficients suffice:

```
a₄ = f_θθθθ/24 = D(cos²θ*−sin²θ*)/4 ≈ −2333.912034770,
κ₂ = β_θθ = −245 Im B/|B|² ≈ 0.3331504239594,
T = 3aκ₂−2κa₄ ≈ 20100.38094101 > 0.
```

Here D=36400. The radial degeneracy equations give the a₄ identity.
For κ₂, use `β_θθ=Im(B_θθ/B−(B_θ/B)²)`, `B_θθ=245−B`, and
`Re(B_θ/B)=0` at the shoulder. The square term is real there.
The rational calculation proves a₄<0 and κ₂>0, so both summands in
T are positive.

Put `c₂=f_θθφ/2`. For either i=0,+, the desingularized equations expand as

```
F_i = a(y_i³−y_-³)+bλ(y_i−y_-)
    + h[a₄(y_i⁴−y_-⁴)+c₂λ(y_i²−y_-²)] + O(h²),

Q_i = κ(y_i−y_-)−2πj
    + h[(κ₂/2)(y_i²−y_-²)+(y_i−y_-)] + O(h²),
```

where j=1,2 for the middle and final labels. Constant-in-θ radial and
angular terms cancel between visits. These expansions follow from the
analytic equations, so the remainders hold along their implicit branch.

Write `y_i=y_i(0)+hη_i+O(h²)` and `λ=C+hL+O(h²)`. Solving the four
first-order equations gives L=−2C/κ and

```
η_- =  s/κ − κ₂s²/(6κ) − a₄s²/(3a) − c₂C/(3a),
η_0 =        κ₂s²/(3κ) − a₄s²/(3a) − c₂C/(3a),
η_+ = −s/κ − κ₂s²/(6κ) − a₄s²/(3a) − c₂C/(3a).
```

The program clears the common denominator 6abκ and verifies all four
polynomial residuals formally. The mixed coefficient c₂ will cancel
from the outer tangent's leading term.

## The third determinant needs that extra order

At a common spatial point z, a velocity divided by z is

```
V_i/z = d f_θ(θ_i,φ)/(2f) + i[1+d β_θ(θ_i,φ)].
```

For any pair, put `A_i=f_θ/(2f)` and `κ_i=β_θ`. Then exactly

```
det(V_i,V_j) = f[(A_i−A_j)/h + (A_iκ_j−κ_iA_j)/h²].
```

Since `f_θ=h²(3ay_i(0)²+bC)+O(h³)`, the two inner-pair limits are

```
det(V_-,V_0) → M,   det(V_0,V_+) → −M,
M = 3aκs²/2 > 0.
```

The outer leading terms cancel because `(−s)²=s²`. At the next order,

```
d det(V_-,V_+) →
  κ[−3as(η_-+η_+)−4a₄s³−2c₂Cs]+2aκ₂s³
  = s³(3aκ₂−2κa₄) = s³T > 0.
```

This last identity is checked formally, rather than from decimal
determinants. All three selected pairs are therefore transverse for
sufficiently small positive h. In increasing time order (+,0,−), the
three cyclic determinant signs are +,−,+.

Also `|V_i|=|z*|κd+O(1)`, where `|z*|²=f*`. Thus the outer small
angle has sine

```
[s³T/(f*κ²)] d⁻³ + O(d⁻⁴),
```

whereas the other two angle magnitudes have sine
`[M/(f*κ²)]d⁻²+O(d⁻³)`. Their directions approach the same limiting
direction, so these are small angles, rather than angles close to π.

## The sign and the area coefficient

At a common nonzero point, converting each pair's real and imaginary
position differences into a squared-radius difference and an argument
difference has determinant 2. Reordering the two radius rows before
the two angle rows contributes a minus sign. The changes
`t_i=h(θ_i+φ/2−2πj)`, `θ_i=θ*+hy_i`, `φ=φ*+h²λ`, and the equation
scalings cancel all powers of h. Consequently the desingularized
four-equation Jacobian, in ellipse order, has determinant **4H**.

Its limiting determinant is the already established `−6ab s³κ²`, so

```
H_ellipse → H* = −3ab s³κ²/2 > 0.
```

Reversing the three visit labels to increasing time order reverses H.
Hence the selected configuration has the negative local passage sign
when no fourth branch joins it. This conclusion does not assume that a
nonzero four-equation determinant itself forces tangent transversality;
the three pair determinants were checked separately above.

Finally the selected triangle coefficient is

```
K_d = H²/(2|D₀₁D₁₂D₂₀|),
K_d/d → H*²/(2M²s³T) = b²κ²/(2sT).
```

Rational enclosures give
`871.385387546 < b²κ²/(2sT) < 871.385387548`.
The local quadratic law concerns these three branches. An unexcluded
fourth branch could subdivide the selected triangle in the complete
drawing; neither the area coefficient nor these asymptotics excludes it.

## A fourth branch cannot join at consecutive large folds

At the shoulder level, the complex radial quartic in `w=exp(iθ)` has
equal leading and constant coefficients, both D/4. Its threefold root
is `w*=exp(iθ*)`. The product of its four roots is one, so the remaining
point has

```
w₄*=w*⁻³,       θ₄* ≡ −3θ* (mod 2π).
```

For completeness, use the radial degeneracy equations to write the
monic quartic as

```
w⁴ − 4(c³+is³)w³ + (12c²−6)w² − 4(c³−is³)w + 1
    = (w−w*)³(w−w*⁻³),
```

where in this display only c=cos θ*, s=sin θ*. Its fourth root is
distinct: equality with w* would force θ* onto a coordinate axis,
contradicting c<0 and s<0. The real radial derivative there is nonzero;
the rational program independently certifies its sign.

Consequently the fourth radial point has an analytic continuation
`θ₄(h)` at the selected common radius. The radius and phase vary by
O(h²), so `θ₄(h)=θ₄*+O(h²)`. The quartic ceiling accounts for every
radial candidate at these nearby meetings. Put

```
α = β(θ₄*,φ*)−β(θ*,φ*),
α/(2π) ≈ 0.17464982113377.
```

The exact enclosure proves **0<α<π**; in fact the complex ratio
`B(θ₄*,φ*)/B(θ*,φ*)` lies in the first quadrant. There is one analytic
choice of β because Re B≥40.

At a positive integer d, the fourth radial point supplies a spatial
visit to the selected common point if and only if

```
E_d = θ₄(1/d)−θ_-(1/d)
      + d[β(θ₄(1/d),φ_d)−β(θ_-(1/d),φ_d)] ∈ 2πℤ.
```

Use one continuous real lift of each θ near its limit. From the
analytic expansions and `κs=2π`,

```
E_d = αd + (θ₄*−θ*+2π) + O(1/d),
E_(d+1)−E_d → α.
```

Thus for all sufficiently large consecutive integers the latter
difference lies strictly between 0 and 2π. It cannot be the difference
of two integer multiples of 2π. The fourth point therefore cannot join
at both d and d+1.

At least one of those two fold counts has exactly the three selected
visits, whose transversality and negative local passage sign have
already been proved. This yields infinitely many ordinary negative
triple phases tending to φ* from above. The universal closed-interval
radial obstruction excludes any triple at or below φ*, proving the
stated unattained infimum. This argument supplies no numerical cutoff
and does not rule out fourth visits at isolated fold counts.

## The exceptional fold counts have density zero

The limiting angle α is an irrational multiple of 2π. This can be proved
with a small exact algebraic calculation, without assuming that a
decimal approximation is irrational.

Set `u=cos²θ*` and `L=A²−Du`, with A=205, B=75, D=A²−B². The center
degeneracy equations and its fixed distance 245 give

```
P(u) = D²[B²u³+A²(1−u)³] − 245²A²B² = 0.
```

In the axes rotated by −φ*/2, the shoulder radius vector is
`(cos θ* L/A, sin θ* L/B)`. The fourth point has
`cos θ₄*=4cos³θ*−3cos θ*` and
`sin θ₄*=4sin³θ*−3sin θ*`. Their dot product, divided by the common
squared radius `L³/(A²B²)`, simplifies to

```
cos α = 1 − 8A²B²u(1−u)/L².
```

Therefore X=2cos α satisfies `S(u)X−N(u)=0`, where
`S=L²` and `N=2S−16A²B²u(1−u)`. Eliminating u gives the primitive
integer cubic

```
117219944697856 X³ − 10221212798424576 X²
    + 110833317006886032 X − 92658189484824233 = 0.
```

The program builds it from the 3×3 matrix of multiplication by
`S(u)X−N(u)` in the quotient by P. Its determinant vanishes at the
actual X: evaluation at the actual u gives a nonzero left null vector.
The independent checker also builds the full 5×5 Sylvester determinant.

The cubic keeps degree three and has **no root modulo 31**, as a check
of all 31 residues proves. It is irreducible over the rationals. Its
monic normalization has trace

```
698970843/8016008,
```

which is not an integer. Thus X is not an algebraic integer. If α were
a rational multiple of 2π, `ζ=exp(iα)` would be a root of unity and
`X=ζ+ζ⁻¹` would be an algebraic integer, a contradiction. One elementary
way to see the latter implication is the integer recurrence
`C₀=2`, `C₁=X`, `C_(n+1)=XC_n−C_(n−1)`: for n≥1 it is monic, and
`C_n(ζ+ζ⁻¹)=ζⁿ+ζ⁻ⁿ`. A root of unity makes `C_n(X)−2=0` for some n.

Now fix any positive integer N. For j=1,…,N,

```
E_(d+j)−E_d → jα ∉ 2πℤ.
```

Consequently, once d is sufficiently large depending on N, two fourth
visits cannot occur within N fold counts of each other. There is at
most one exceptional fold in each consecutive block of N+1 large fold
counts. Its upper density is at most 1/(N+1). As N was arbitrary, the
exceptional set has density zero, and the selected ordinary negative
triples have natural density one.

This uses no equidistribution theorem and does not assert that the
exceptional set is empty or infinite. There is still no numerical
cutoff, finite-d remainder, or rate at which the density approaches one.

## Repeat the exact coefficients

```sh
python3 experiments/fold_shoulder_tangents.py --write
```

The standard-library program repeats the radial-threshold and shoulder
constant proofs, proves the new signs, verifies the four formal
first-order equations and outer-determinant identity, and saves the
[coefficient record](fold_shoulder_tangents.json). It asserts no numerical
fold cutoff, finite-d remainder bound, or uniform fourth-visit exclusion.
The same command proves the exact irrationality certificate. The
independent Sylvester and modular audits run with
`python3 experiments/fold_shoulder_events_check.py`.
