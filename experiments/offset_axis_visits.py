"""The two mirror-fixed visits stay alone on both whole outward offset legs.

The starting visit is separated by a supporting line. A complete Sturm
calculation excludes every possible meeting with the halfway visit, for
all M >= 0. Consequently no ordinary three-visit meeting lies on the
mirror axis of either unperturbed family. Higher axis meetings remain
possible. Standard library only; no numerical hints or archived roots.
"""

from fractions import Fraction as Q
from time import monotonic

from blend_cusps import (Interval as I, add, isolate_roots, product,
                        remainder, require, scale, trim, value)
from rhythm_tangencies import evaluate


def subtract(p, q):
    return add(p, scale(q, -1))


def chebyshev(kind, degree):
    require(kind in ("T", "U") and type(degree) is int and degree >= 0,
            "Choose a nonnegative Chebyshev degree and kind T or U.")
    p, q = (Q(1),), (Q(0), Q(1 if kind == "T" else 2))
    if degree == 0:
        return p
    for _ in range(1, degree):
        p, q = q, subtract(product((0, 2), q), p)
    return q


def exact_divide(p, q):
    p = list(trim(p))
    result = [Q(0)] * (len(p) - len(q) + 1)
    while len(p) >= len(q) and p != [0]:
        factor, shift = p[-1] / q[-1], len(p) - len(q)
        result[shift] = factor
        for i, coefficient in enumerate(q):
            p[i + shift] -= factor * coefficient
        p = list(trim(p))
    require(trim(p) == (0,), "The proposed polynomial factor did not divide exactly.")
    return trim(result)


def polynomials(inner):
    require(type(inner) is int and inner in (6, 8), "Choose inner rhythm 6 or 8.")
    x = add(add((0, 245), scale(chebyshev("T", 11), 140)), scale(chebyshev("T", inner), 65))
    Y = subtract(add((245,), scale(chebyshev("U", 10), 140)), scale(chebyshev("U", inner - 1), 65))
    V = add(add((245,), scale(chebyshev("U", 10), 1540)), scale(chebyshev("U", inner - 1), 65 * inner))
    w = subtract(add((0, 245), scale(chebyshev("T", 11), 1540)), scale(chebyshev("T", inner), 65 * inner))
    A = subtract(product(x, V), product(Y, w))
    R = add(product(x, x), product((1, 0, -1), product(Y, Y)))
    D = subtract(product(R, V), scale(product(x, A), 2))
    P = subtract(subtract(D, scale(A, 640)), scale(V, 102400))
    return x, Y, V, w, A, P


def prove(inner):
    x, Y, V, w, A, P = polynomials(inner)
    # A pole v_x=0 could reach the axis only with y=0. On the upper
    # half-circle this would require a common zero of Y and V.
    p, q = Y, V
    while q != (0,):
        p, q = q, remainder(p, q)
    require(len(p) == 1 and p[0] != 0, "An axis pole may give an unhandled visit.")
    reduced = exact_divide(P, (1, 2, 1))  # remove the identical c=-1 visit
    roots = isolate_roots(reduced, bits=70)
    reasons = []
    for low, high in roots:
        c = I(low, high)
        length = -value(Y, c) / value(V, c)
        center_plus_320 = value(A, c) / value(V, c) + 320
        require(length.high < 0 or center_plus_320.low > 0,
                "A halfway-axis root may describe an outward meeting.")
        reasons.append("inward" if length.high < 0 else "wrong side")
    require(len(roots) == 9 and reasons.count("inward") == 5,
            "The complete halfway-axis root inventory changed.")
    # Independent Fourier evaluations audit the polynomial coordinates
    # and circle equation at rational unit-circle chart controls.
    controls = 0
    for quarter in (0, 1):
        for s in (Q(1, 7), Q(1, 3), Q(3, 5), Q(4, 5)):
            denominator = 1 + s * s
            cosine, sine = (1 - s * s) / denominator, 2 * s / denominator
            if quarter == 1:
                cosine, sine = -sine, cosine
            point = evaluate(quarter, s, Q(inner - 6, 2))
            velocity = evaluate(quarter, s, Q(inner - 6, 2), 1)
            expected = (value(x, cosine), sine * value(Y, cosine),
                        -sine * value(V, cosine), value(w, cosine))
            require(all(a.low == a.high == b for a, b in zip((*point, *velocity), expected)),
                    "The Chebyshev polynomials disagree with independent Fourier jets.")
            L = point[1] / velocity[0]
            X = point[0] + L * velocity[1]
            B = L * L * sum(v * v for v in velocity)
            residual = B - (X + 320) * (X + 320)
            polynomial = value(P, cosine) / value(V, cosine)
            require(residual.low == residual.high == polynomial,
                    "The eliminated circle equation disagrees with the original geometry.")
            controls += 5
    print(f"11/{inner}: degree {len(reduced) - 1}, all nine interior roots excluded "
          "(five inward, four wrong-side); Y and V coprime; "
          f"{controls} exact Fourier / polynomial controls.", flush=True)


if __name__ == "__main__":
    started = monotonic()
    require(1540 - 245 - 520 == 775 > 0 and 245 + 1540 - 520 > 0,
            "The uniform speed or starting-velocity sign failed.")
    for inner in (6, 8):
        prove(inner)
    print("The starting and halfway visits stay alone for every outward M >= 0. "
          "No ordinary axis triple occurs; higher axis meetings remain possible.")
    print(f"Elapsed {monotonic() - started:.2f}s.")
