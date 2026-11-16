# Three visits approach the shoulder

The [radial threshold](fold_radial.md) forbids three or more visits at
one spatial point through φ*/π≈0.8949408271717914, for every positive
integer fold count d. That bound is also sharp for **actual spatial
meetings**, when d is allowed to grow.

For every sufficiently large integer d, there is a phase with at least
three distinct visits to one point, satisfying

```
φ_d = φ* + C/d² + O(d⁻³),
20.284022161534 < C/π < 20.284022161536.
```

Thus φ* is the **unattained infimum** of phases with a three-or-more-visit
meeting over all positive fold counts on this half-turn.

This is an analytic existence result. It supplies no numerical lower
cutoff for d, no ordinary-passage sign, and no exclusion of a fourth
visit. It does not alter the separately certified sevenfold and
fourteenfold censuses.

![Fourteen, thirty, and sixty folds become finer petals at zero phase,
and overlapping rings at three selected phases near the shoulder.](fold_shoulder.svg)

[Beyond the sliders](fold_shoulder.svg) keeps the same lengths and one
scale. Its phase choices are numerical illustrations. Regenerate the
six-drawing sheet with `python3 experiments/fold_shoulder_figure.py`;
its chord/rounding error budgets stay below 0.005 sheet units.

## Radius and angle together

Use the same offset ellipse

```
B(θ,φ) = 245 + exp(iφ/2)(205 cos θ + 75i sin θ),
f(θ,φ) = |B(θ,φ)|²,       β(θ,φ) = arg B(θ,φ).
```

Its real part stays at least 40, so β has one smooth, real-analytic
choice, with values between −π/2 and π/2. There is no angle seam.
The orbital point is `z=exp(it) B`, with θ=dt−φ/2. Three ellipse
parameters give a common spatial point when their radii agree and

```
G(θ_i,φ)−G(θ_0,φ) = 2πi,       i=1,2,
G(θ,φ) = θ+dβ(θ,φ).
```

Here i is the integer label, not the imaginary unit. To see sufficiency,
choose the time lifts

```
t_i = (θ_i+φ/2−2πi)/d.
```

The brackets B are unchanged by subtracting 2πi from θ. These times
give equal arguments `t_i+β_i`, and the equal radii then give equal z.
For integer d the curve is 2π-periodic, so every lift can be reduced to
one orbit. Distinct θ modulo 2π ensure distinct time visits.

## Expand at the flat shoulder

Let θ* be the unique radial degeneracy at φ*. The
[two critical-point equations](fold_radial.md#find-every-possible-change)
fix its negative cosine and sine:

```
cos θ* = −[(205×245/D) cos(φ*/2)]^(1/3),
sin θ* = −[(75×245/D) sin(φ*/2)]^(1/3),       D=36400.
```

At this point f_θ=f_θθ=0. Define

```
a = f_θθθ/6 = D sin θ* cos θ* > 0,
b = f_θφ = 50225 sin(φ*/2) sin θ*
           −18375 cos(φ*/2) cos θ* < 0,
κ = β_θ = Im(B_θ/B) > 0.
```

The exact interval calculation gives approximately
`a=17591.23129448`, `b=−37427.66819237`, and `κ=0.5396095508987`.
These signs, not the decimal approximations, enter the proof.

Put h=1/d and look for

```
θ_i = θ*+h y_i,       φ = φ*+h² λ.
```

Divide the two radius differences by h³. Their analytic limits at h=0
are

```
F_i = a(y_i³−y_0³)+bλ(y_i−y_0),       i=1,2.
```

The divisions have removable singularities: the constant radial terms
cancel, and f_θ=f_θθ=0 removes every lower power of h. For the angular
conditions, write

```
Q_i = [β(θ*+hy_i,φ*+h²λ)−β(θ*+hy_0,φ*+h²λ)]/h
      +h(y_i−y_0)−2πi.
```

These too extend analytically to h=0, where
`Q_i=κ(y_i−y_0)−2πi`. The joint limiting solution is

```
s = 2π/κ,
(y_0,y_1,y_2) = (−s,0,s),       λ = −as²/b = C > 0.
```

## The limiting solution persists

Order the equations F₁,F₂,Q₁,Q₂ and variables y₀,y₁,y₂,λ. Their limiting
Jacobian is

```
⎡ −2as²   −as²      0      bs ⎤
⎢ −2as²      0    2as²    2bs ⎥
⎢    −κ      κ       0      0 ⎥
⎣    −κ      0       κ      0 ⎦
```

Its determinant is **−6ab s³κ²**, which is nonzero. The analytic implicit
function theorem therefore gives real-analytic functions y_i(h),λ(h)
solving all four exact equations for sufficiently small real h. For
positive h, the three θ remain distinct, λ(h)>0, and φ stays below π.
Taking h=1/d along sufficiently large positive integers gives the claimed
common spatial point. Finally λ(h)=C+O(h) proves the stated phase law.

The first correction follows without another full system solve. Write
`y_i(h)=y_i(0)+h z_i+O(h²)` and `λ(h)=C+hL+O(h²)`. In Q₂ the quadratic
angular term vanishes because `y_2²=y_0²`; its first-order equation is
`κ(z_2−z_0)+2s=0`. In F₂ the fourth-order radial terms vanish for the
same symmetry: they involve differences of fourth or second powers.
Its first-order equation is

```
2as²(z_2−z_0)+2bsL = 0.
```

Consequently `L=−2C/κ`, and the sharper law is

```
φ_d = φ* + C/d² − 2C/(κd³) + O(d⁻⁴)
    = φ* + C/(d+1/κ)² + O(d⁻⁴).
```

The cubic correction divided by π is approximately −75.18036746292648.
These are asymptotic remainders, with no asserted finite-d error bound.

This argument concerns the selected three visits. A fourth radius
preimage exists nearby in phase and is not tested for spatial alignment.
Likewise a nonzero four-equation Jacobian does not by itself assert all
three pairwise tangent determinants are nonzero. Those are separate
questions for a finite ordinary-triple certificate.

## Reproduce the constants

```sh
python3 experiments/fold_shoulder.py --write
```

The standard-library program repeats the complete radial-threshold
calculation, encloses both cube roots and κ rationally, proves a>0,
b<0, κ>0, and bounds C. A formal determinant calculation verifies the
Jacobian identity without floating-point evaluation. The
[record](fold_shoulder.json) explicitly keeps its unquantified cutoff
and unproved ordinary/fourth-visit statuses.

Exploratory Newton solves suggest this branch passes through the already
certified negative fourteenfold batch at 0.9733588514569π. Selected
higher-fold suggestions are 0.9149574927371π for d=30,
0.9002485310056π for d=60, and 0.8963074237035π for d=120.
These finite values are **numerical leads**, not consequences of an
asserted numerical cutoff or new finite-event certificates.
