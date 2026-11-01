"""A positive local-move movie between the two certified conormal words.

Run this file to build and independently replay the movie. Add --write to
save positive_front.json and its browser data. Only the standard library
is used. Geometric endpoint certification remains normal_front_braid.py's
job; this calculation starts from its recorded words.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import time

from blend_cusps import derivative, product as polynomial_product, require, scale, value
from normal_front_conjugacy import CONJUGATOR, artin_action

HERE = Path(__file__).resolve().parent


def positive_word(word, strands):
    require(type(strands) is int and strands >= 2, "Use at least two strands.")
    require(isinstance(word, (list, tuple)), "A word must be a list or tuple.")
    require(
        all(type(g) is int and 1 <= g < strands for g in word),
        "Use positive generators strictly below the strand count.",
    )


def move_word(word, move, strands=11):
    """Small independent verifier: inspect and replace exactly one subword."""
    positive_word(word, strands)
    require(isinstance(move, (list, tuple)) and len(move) == 2, "Malformed move.")
    kind, at = move
    require(type(at) is int, "Move positions must be integers.")
    changed = list(word)
    if kind == "commute":
        require(0 <= at < len(word) - 1, "Commutation lies outside the word.")
        a, b = word[at : at + 2]
        require(abs(a - b) > 1, "Only independent crossings commute.")
        changed[at : at + 2] = [b, a]
    elif kind == "triangle":
        require(0 <= at < len(word) - 2, "Triangle lies outside the word.")
        a, b, c = word[at : at + 3]
        require(a == c and abs(a - b) == 1, "Not an Artin three-strand move.")
        changed[at : at + 3] = [b, a, b]
    elif kind == "cycle":
        require(at == 1 and len(word) > 0, "Move exactly the first crossing past the cut.")
        changed = changed[1:] + changed[:1]
    else:
        raise ValueError("Unknown local move.")
    return changed


def expose(word, generator, moves, start=0):
    """Jacquemard's leading-letter extraction, recording Artin relations.

    Move the leftmost requested letter left through independent letters.
    At j i, recursively expose j in the suffix and change j i j to i j i.
    Failed extraction leaves both arguments unchanged. The verifier above
    does not call this search or rely on its correctness.
    """
    before, count = word[:], len(moves)
    try:
        at = word.index(generator, start)
    except ValueError:
        return False
    while at > start:
        neighbor = word[at - 1]
        if abs(generator - neighbor) > 1:
            word[at - 1 : at + 1] = [generator, neighbor]
            moves.append(["commute", at - 1])
        else:
            require(abs(generator - neighbor) == 1, "Extraction lost its leftmost letter.")
            if not expose(word, neighbor, moves, at + 1):
                word[:], moves[count:] = before, []
                return False
            require(word[at - 1 : at + 2] == [neighbor, generator, neighbor], "Extraction triple changed.")
            word[at - 1 : at + 2] = [generator, neighbor, generator]
            moves.append(["triangle", at - 1])
        at -= 1
    return True


def build(first, second, witness=CONJUGATOR):
    positive_word(first, 11)
    positive_word(second, 11)
    positive_word(witness, 11)
    word, moves = list(first), []
    for generator in witness:
        require(expose(word, generator, moves), "The next conjugator letter cannot be exposed positively.")
        require(word[0] == generator, "The wrong letter reached the cut.")
        word[:] = word[1:] + word[:1]
        moves.append(["cycle", 1])
    for at, generator in enumerate(second):
        require(expose(word, generator, moves, at), "The final positive words did not straighten.")
    require(word == list(second), "The final word is not literally the target.")
    return moves


def components(word, strands=11):
    positions = list(range(strands))
    for generator in word:
        at = generator - 1
        positions[at], positions[at + 1] = positions[at + 1], positions[at]
    seen, cycles = set(), 0
    for start in range(strands):
        if start in seen:
            continue
        cycles += 1
        at = start
        while at not in seen:
            seen.add(at)
            at = positions[at]
    return cycles


def replay(first, second, moves, witness=CONJUGATOR):
    """Verify every local rule, closed component count, and both endpoints."""
    word, cycled = list(first), []
    require(len(first) == len(second), "Endpoint lengths differ.")
    for move in moves:
        if move[0] == "cycle":
            cycled.append(word[0])
        word = move_word(word, move)
        require(len(word) == len(first), "A move changed the crossing count.")
        require(components(word) == 1, "A move lost the one-component closure.")
    require(word == list(second), "The movie ends at the wrong word.")
    require(cycled == list(witness), "The cut crossings differ from the conjugacy witness.")
    return dict(sorted(Counter(move[0] for move in moves).items()))


def controls():
    """Compare extraction with whole finite relation graphs, not itself."""
    tested = 0
    for length in range(7):
        words = list(product(range(1, 4), repeat=length))
        parent = {w: w for w in words}

        def root(w):
            while parent[w] != w:
                parent[w] = parent[parent[w]]
                w = parent[w]
            return w

        for word in words:
            for at in range(length):
                for kind, width in (("commute", 2), ("triangle", 3)):
                    if at + width > length:
                        continue
                    part = word[at : at + width]
                    allowed = (abs(part[0] - part[1]) > 1 if width == 2 else
                               part[0] == part[2] and abs(part[0] - part[1]) == 1)
                    if allowed:
                        other = tuple(move_word(word, [kind, at], 4))
                        parent[root(word)] = root(other)
        starts = {}
        for word in words:
            starts.setdefault(root(word), set()).update(word[:1])
        for word in words:
            for generator in range(1, 4):
                changed, moves = list(word), []
                success = expose(changed, generator, moves)
                require(success == (generator in starts[root(word)]), "Extraction disagrees with the exhaustive relation graph.")
                restored = list(word)
                for move in moves:
                    restored = move_word(restored, move, 4)
                require(restored == changed, "Recorded extraction moves do not replay.")
                require(not success or changed[0] == generator, "Extraction exposed the wrong letter.")
                require(success or (changed == list(word) and moves == []), "Failed extraction was not transactional.")
                tested += 1

    for word, move in (
        ([1, 2], ["commute", 0]), ([1, 3, 1], ["triangle", 0]),
        ([1, 2, 3], ["triangle", 0]), ([1], ["cycle", 0]),
        ([], ["cycle", 1]), ([1, 3], ["commute", -1]),
        ([1, 3], ["commute", True]), ([1, 3], ["commute", 0, 1]),
        ([1, 3], ["erase", 0]), ([0, 3], ["commute", 0]),
        ([1, 11], ["commute", 0]), ([1, -3], ["commute", 0]),
    ):
        try:
            move_word(word, move)
        except ValueError:
            pass
        else:
            raise ValueError("An invalid move was accepted.")
    return tested


def offset_bounds():
    """Exact constants for the explicit C² construction in the note.

    The analytic monotonicity and coordinate-change arguments are in
    positive_front.md; these checks audit their polynomial identities
    and rational arithmetic, rather than sampling their conclusions.
    """
    f = (0, Q(15, 8), 0, Q(-10, 8), 0, Q(3, 8))
    g = (1, 0, -3, 0, 3, 0, -1)
    require(
        derivative(f) == scale(polynomial_product((1, 0, -1), (1, 0, -1)), Q(15, 8)),
        "The triple model's derivative factorization changed.",
    )
    require(
        derivative(g) == scale(polynomial_product((0, 1), polynomial_product((1, 0, -1), (1, 0, -1))), -6),
        "The bump derivative factorization changed.",
    )
    require(value(f, Q(1, 8)) < value(g, Q(1, 8)) / 4, "The local crossing is not above 1/8.")
    require(value(f, Q(1, 4)) > value(g, Q(1, 4)) / 4, "The local crossing is not below 1/4.")
    require(value(derivative(f), Q(1, 4)) == Q(3375, 2048) > 1, "The local slope gap changed.")
    step = (0, 0, 0, 10, -15, 6)
    require(derivative(step) == scale(polynomial_product((0, 1, -1), (0, 1, -1)), 30), "The step derivative changed.")
    require(value(derivative(step), Q(1, 2)) == Q(15, 8), "The step's maximum slope changed.")
    # The second-derivative maximum is 10/sqrt(3), strictly less than 6.
    require(Q(100, 3) < 36, "The step second-derivative bound failed.")
    local = 5 + 6 / Q(14, 25) ** 2
    require(local == Q(4730, 196) < 25, "The displayed local offset is too small.")
    radius = Q(2305 * 212521, 118999)
    require(radius + 450 < 4567, "The endpoint support second derivative exceeds its bound.")
    dephased = 4 * 4567 + 450
    require(dephased == 18718, "The dephased endpoint bound changed.")
    # Each aligned actual gap is <= 2pi; each canonical gap is 2pi/106.
    first = Q(15, 8) * 106
    second = 106 ** 2  # 3*106²/pi < 106² since pi > 3.
    endpoint = 450 + dephased * first ** 2 + 900 * second
    require(endpoint == Q(5996024775, 8) < 750_000_000, "The endpoint alignment bound failed.")
    # Local block straightening: |d²h/dx²| <= 2070, block >= two slots.
    core = 10 + 2070 * Q(106, 6) ** 2
    require(core == 646080 < 1_000_000, "The core movie bound failed.")
    return {
        "displayed_local_upper_bound": str(local),
        "endpoint_alignment_upper_bound": str(endpoint),
        "core_upper_bound": str(core),
        "full_offset": 1_000_000_000,
        "scope": "The explicit C2 construction in positive_front.md, followed by smoothing with individual errors below one half in h and h_second.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the independently replayed record and browser data")
    args = parser.parse_args()
    started = time.monotonic()
    tested = controls()
    bounds = offset_bounds()
    source = json.loads((HERE / "normal_front_braid.json").read_text())
    first, second = [endpoint["word"] for endpoint in source["endpoints"]]
    moves = build(first, second)
    counts = replay(first, second, moves)
    require(
        artin_action(first + list(CONJUGATOR)) == artin_action(list(CONJUGATOR) + second),
        "The independent Artin conjugacy check failed.",
    )
    # Reject a legal but incomplete movie, as well as an altered endpoint.
    for target, altered in ((second, moves[:-1]), (second[::-1], moves)):
        try:
            replay(first, target, altered)
        except ValueError:
            pass
        else:
            raise ValueError("An incomplete or mistargeted movie was accepted.")
    result = {
        "description": "Positive Artin relations and cut rotations, independently replayed from the recorded geometric braid words.",
        "strands": 11, "start": first, "finish": second,
        "counts": counts, "offset_bounds": bounds, "moves": moves,
    }
    if args.write:
        (HERE / "positive_front.json").write_text(json.dumps(result, indent=2) + "\n")
        (HERE / "positive_front_data.js").write_text(
            "'use strict';\n\n// Generated by python3 experiments/positive_front.py --write.\n"
            + "const PositiveFrontData = " + json.dumps(result, separators=(",", ":")) + ";\n"
            + "if (typeof module !== 'undefined' && module.exports) module.exports = PositiveFrontData;\n"
        )
    print(f"{tested} extraction controls agree with complete four-strand relation graphs through length six.")
    print(f"{len(moves)} positive local moves: {counts}.")
    print("Every rule and one-component closure checked; the final word agrees literally.")
    print(f"Exact offset bounds: local {bounds['displayed_local_upper_bound']} < 25; full construction < 750000001 < {bounds['full_offset']}.")
    print(f"Elapsed: {time.monotonic() - started:.2f}s. Geometric endpoint completeness is assumed from its separate proof.")


if __name__ == "__main__":
    main()
