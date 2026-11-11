# The same three pockets on any positive span

The [four-curve cubic maximin](cubic_maximin.md) extends to **every
fixed positive endpoint pair** a<b. The intercept law remains
`h(p)=p³/3`. The maximizing placement is unique and makes all three
areas equal.

Put `L=b−a` and `q=1+3a/L>1`. There is exactly one positive root u of

```
32u³ + (32q+8)u² − (4q+13)u − q = 0.
```

It lies strictly between 1/4 and 2/5. The optimal labels and area are

```
a,  a+Lu,  a+L·9u/(8u+1),  b,

S* = L⁵u(1−u)(q+u)²/36.
```

All three pockets have area S*, and total area is 3S*. This is a
four-curve theorem. It does not extend the separate five-curve result
beyond [1,3] or classify a whole compromise frontier.

## Normalize the equal-area equation

Write the interior normalized labels as x,y in (0,1). The
[universal affine relation](cubic_maximin.md#why-does-the-second-label-have-that-rational-formula)
gives `y=9x/(8x+1)`. The single pocket with outer labels 0,1 has
normalized area

```
F_q(x) = x(1−x)(q+x)²/18.
```

Original areas have an additional factor L⁵. This follows directly
by substituting the original labels a+Lt in the cubic triangle
formula: three gap factors contribute L³ and the squared sum of
labels contributes L². The normalized triangle formula is

```
T_q(r,s,t) = (s−r)(t−s)(t−r)(r+s+t+q−1)²/18.
```

Along `y=9x/(8x+1)`, equality of the two triangles reduces to the
displayed cubic. At x=1/4 that cubic has value −9/4, and at x=2/5
it has value `(315q−234)/125>0`. Its second derivative is positive
for x≥0. It is negative at both 0 and 1/4, and its derivative at
1/4 is `12q−3>0`. Thus it has exactly one positive root, in the
stated bracket. Substitution gives `F_q(u)=2S*/L⁵` and three equal
face areas. The program checks these equalities as rational-function
identities, not at a sampled list of parameters.

## Concavity holds on every positive endpoint pair

Let a,x,y,b be arbitrary original labels, with positive gaps
`U=x−a`, `V=y−x`, `W=b−y`. Build the quadrilateral area C as the
outer triple's triangle area minus the first inner triangle.
It is a homogeneous polynomial of degree five in a,U,V,W.

For derivatives with respect to x and y at **fixed a,b**, use

```
∂x = ∂U−∂V,       ∂y = ∂V−∂W.
```

Construct `Hₓ=Cₓ²−CCₓₓ`, `Hᵧ=Cᵧ²−CCᵧᵧ`, `E=CₓCᵧ−CCₓᵧ`,
and `D=HₓHᵧ−E²`, as in the fixed-endpoint proof. In the gap
coordinates, **all nonzero coefficients are positive**: Hₓ has
80 terms of degree eight, and D has 431 terms of degree sixteen.
Since a,U,V,W are positive, Hₓ and D are strictly positive.
Therefore log C has negative definite Hessian throughout every
positive ordered four-label domain. The two triangular log-areas
are also concave, being sums of logs of positive affine factors.

The [standard-library verifier](cubic_four_general.py) derives these
polynomials before specializing any endpoints. The
[record](cubic_four_general.json) lists all **511 coefficients**.
This is a continuous global sign proof, not a collection of
endpoint examples.

## The support is positive for the whole family

At the equal-area root, the cubic gives

```
q = u(13−8u−32u²) / [(4u−1)(8u+1)].
```

For the first triangle, quadrilateral, and last triangle respectively,
choose these weights:

```
λ₁ = (64u²−32u+19)(160u²−32u+7),
λ₂ = −2(7168u⁴−6400u³+2208u²−496u+31),
λ₃ = (32u²−16u+5)(512u²−16u+17).
```

Each quadratic factor is positive for every real u: its leading
coefficient is positive and discriminant negative. The quartic
inside λ₂ has Bernstein coefficients on [1/4,2/5]

```
−27, −162/5, −936/25, −5184/125, −25137/625.
```

They are all strictly negative, so λ₂ is strictly positive too.
The program proves exactly that the λ-weighted sum of the three
log-area gradients is zero. In those gradients q is held fixed;
its rational expression in u is substituted only to check the
identity at the candidate.

Consequently the weighted log-area sum is strictly concave and
stationary at this placement. The same global supporting-tangent
argument as in the [fixed-endpoint proof](cubic_maximin.md#positive-weights-support-the-equal-area-placement)
proves both the sharp minimum bound and uniqueness. A collapsed
gap gives a zero triangular area and cannot compete.

## Reproduce

```sh
python3 experiments/cubic_four_general.py
python3 experiments/cubic_four_general.py --write
```

The command reconstructs all 511 positive coefficients and checks
the continuous equal-area and support identities using rational
functions of u. It also clips six rational arrangements on widely
different endpoint pairs, bounds all eighteen faces, rejects four
invalid controls, and compares the [1,3] result with the independent
earlier root certificate. One endpoint span is only 2⁻¹²⁰. These
finite controls audit implementation; the preceding identities and
signs prove the all-endpoint theorem.

The saved selected nodes and areas have rational lower and upper
bounds. The six rational arrangements use box midpoints only for
their independent clipping controls; those finite midpoint samples
are not themselves claimed to be the exact maximizing placements.
