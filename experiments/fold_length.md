# More folds, a longer line

The [finer weave](fold_band.md) stays inside one annulus while its
folds grow. Its line length has a simple expansion, uniform in the
backward arm's starting angle:

```
L_d = dP + C + O(1/d),
P ≈ 927.726656031576,
C ≈ 732.533267160587.
```

P is the perimeter of the same ellipse seen in
[One ellipse. Many folds.](fold_turn.html). Each extra fold adds
asymptotically one ellipse perimeter of line. Both leading constants
are independent of the starting angle and of the first arm's offset
R=245. That offset enters the bounded remainder.

There is an explicit uniform estimate, not only a limiting notation:

```
0 ≤ L_d−dP−C ≤ π·450²/(75d−450),       d≥7.
```

For d≥12 the upper error is at most `5400π/d`. The seven-, fourteen-,
thirty-, and sixtyfold settings in the study all meet the first
condition. No contact or crossing classification is needed.

## Integrate just one ellipse circuit

Use R=245, A=205, B=75, ψ=φ/2, and θ=u−ψ. Put

```
W(u) = R + exp(iψ)(A cos θ + iB sin θ),
z_d(t) = exp(it) W(dt).
```

The derivative has magnitude `|iW(dt)+dW′(dt)|`. Substituting u=dt
and splitting into d identical periods gives the exact length formula

```
L_d = ∫₀²π |dW′(u)+iW(u)| du.
```

The ellipse speed is

```
s(θ) = |W′(u)| = sqrt(A² sin² θ+B² cos² θ) ≥ B=75.
```

Define two phase-independent constants

```
P = ∫₀²π s(θ) dθ,
C = AB ∫₀²π 1/s(θ) dθ.
```

The first is its ordinary perimeter. To identify the constant term,
expand the norm to first order in iW around dW′. The linear term is
`Re(conj(W′) iW)/s`. Its numerator is

```
AB + R[−A sin θ sin ψ+B cos θ cos ψ].
```

The R-dependent terms change sign when θ advances by π, while s
stays the same. They integrate to zero. What remains is exactly C.

## Control the remainder at every phase

For real two-dimensional vectors v,w, write a=|v| and p=v·w/a.
If a>|w|, rationalizing the norm gives

```
|v+w|−a−p
  = (|w|²−p²)/(|v+w|+a+p)
  ≤ |w|²/[2(a−|w|)].
```

The expression is nonnegative by the supporting-line inequality for
the Euclidean norm. For v=dW′ and w=iW, we have

```
a≥75d,       |w|=|W|≤R+A=450.
```

Thus d≥7 makes every denominator strictly positive. Integrating the
pointwise bound over an interval of length 2π gives
`π·450²/(75d−450)`. The integrated linear term is C, proving the
stated uniform estimate. When d≥12, `75d−450≥(75/2)d`, which gives
the simpler `5400π/d` error.

The same bounds also show that the length difference between any two
starting angles is at most this remainder. Their annuli can look very
different while the high-fold line lengths become close.

## Compute the constants with exact tails

Let `q=1−B²/A²=1456/1681`. Complete elliptic integrals give

```
P = 4A E(q),       C = 4B K(q),

K(q) = ∫₀^(π/2) (1−q sin² x)^(-1/2) dx,
E(q) = ∫₀^(π/2) (1−q sin² x)^(1/2) dx.
```

Here q is the *parameter*; some conventions instead use its square
root as the modulus. There is no library convention to resolve in
the calculator: it defines the integrals by these formulas.

Set `c_n=binom(2n,n)/4^n`. Binomial expansion and the elementary
integral of `sin^(2n) x` give

```
K(q) = (π/2) Σ_(n≥0) c_n² q^n,
E(q) = (π/2) [1−Σ_(n≥1) c_n² q^n/(2n−1)].
```

Since 0<c_n≤1, after term N either omitted positive sum is at most
`q^(N+1)/(1−q)`. The standard-library calculator uses 512 exact
rational terms and an enclosed π. Both resulting constants have
rational enclosures narrower than 10⁻²⁵ drawing units.

```sh
python3 experiments/fold_length.py
python3 experiments/fold_length.py --numeric
```

The optional numerical audit integrates the original three-frequency
velocity directly, at twelve fold/phase combinations. It checks the
analytic bounds using a different parameterization. These quadrature
values are numerical checks; the norm inequality and rational series
tails supply the proofs.

## Equal time and equal ink give different radial weights

The [band note](fold_band.md#a-radial-statistic-that-stays-exactly-the-same)
shows that uniform time samples the ellipse with weight `du/(2π)`
exactly, at every d. Equal arc length supplies another weight. For a
continuous function g of radius, its normalized ink average is

```
[∫₀²π g(|W(u)|) |dW′(u)+iW(u)| du] / L_d.
```

The reverse triangle inequality gives
`||dW′+iW|/d−s|≤450/d` uniformly. Dividing numerator and denominator
by d therefore proves the limit

```
lim_(d→∞) ink_average_d(g)
  = [∫₀²π g(|W(u)|) s(u) du] / P.
```

In the finer weave, equal amounts of ink sample the ellipse by its
own arc length. Equal amounts of clock time sample its parameter
instead. This is a statement about radial statistics, separate from
any crossing count or winding multiplicity.
