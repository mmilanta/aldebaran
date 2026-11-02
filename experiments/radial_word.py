"""Read sufficiently distant parallel offsets from their positive front words.

Default: fresh complete front covers and strand-order proofs, fresh original
plane proofs, then two independent integer strangeness calculations and a
signed audit of every move. --saved assumes the archived front completeness
and its word extraction, while still reproving the original plane curves.
--write requires the default fresh proofs. Standard library only.
See radial_word.md for the geometric limiting argument and its scope.
"""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
from time import monotonic

from blend_cusps import require
from normal_front_braid import certify_word
from normal_front_census import FrontCensus, controls as front_controls
from positive_front import move_word, positive_word, replay
from strangeness import audit_word, compute_case, from_faces, from_word
from verify_smooth_atlas import read_atlas

HERE = Path(__file__).resolve().parent


def radial_word(braid, strands):
    """Follow each wire, then the closure, starting at the lowest height.

    A strand arriving from lower height has exponent +1; the other -1.
    Crossing labels are generator positions, not height ranks. Only knots
    are accepted: a multicomponent closure needs a different formulation.
    The note derives the sign and proves that the initial edge has index 1/2.
    """
    positive_word(braid, strands)
    order = list(range(strands))
    visits = [[] for _ in range(strands)]
    for crossing, generator in enumerate(braid):
        at = generator - 1
        lower, upper = order[at : at + 2]
        visits[lower].append((crossing, 1))
        visits[upper].append((crossing, -1))
        order[at], order[at + 1] = upper, lower
    # order[rank] is the initial wire finishing at that rank. The closure
    # continues a wire at the initial wire with its FINAL rank, so invert it.
    next_wire = [0] * strands
    for rank, wire in enumerate(order):
        next_wire[wire] = rank
    word, closure, seen = [], [], set()
    wire = 0
    while wire not in seen:
        seen.add(wire)
        closure.append(wire)
        word.extend(visits[wire])
        wire = next_wire[wire]
    require(wire == 0 and len(seen) == strands, "The closure must have exactly one component.")
    require(len(word) == 2 * len(braid), "A wire visit was lost at the closure.")
    return word, closure


def invariant(braid, strands, all_starts=False):
    word, closure = radial_word(braid, strands)
    # The incoming edge before word[0] is the last edge in the cyclic word.
    # Its RIGHT side is the unbounded face: rank zero is outermost.
    faces = from_faces(word, 2 * len(word) - 1)
    result = (audit_word(word, 1, faces) if all_starts else from_word(word, 1))
    require(result.value == faces.value and result.indices == faces.indices
            and result.edge_indices2 == faces.edge_indices2,
            "The signed walk and independent face winding disagree.")
    require(faces.tangent_index == strands, "The radial graph has the wrong tangent index.")
    require(min(faces.face_counts) >= 1 and max(faces.face_counts) == strands
            and faces.face_counts[strands] == 1,
            "The radial graph must have positive winding and one innermost face.")
    return {
        "strands": strands,
        "crossings": len(braid),
        "initial_index2": 1,
        "exterior_halfedge": 2 * len(word) - 1,
        "closure_order": closure,
        "word": [list(visit) for visit in word],
        "strangeness": result.value,
        "tangent_index": faces.tangent_index,
        "winding_regions": {str(k): v for k, v in faces.face_counts.items()},
    }


def audit_movie(source, movie):
    """Audit each complete planar rotation system, not just the endpoints."""
    first, second = [entry["word"] for entry in source["endpoints"]]
    require(movie["strands"] == source["strands"] == 11
            and movie["start"] == first and movie["finish"] == second,
            "The movie does not match the geometric front words.")
    counts = replay(first, second, movie["moves"])
    braid = list(first)
    previous = invariant(braid, 11)["strangeness"]
    changes, triples = Counter(), []
    for index, move in enumerate(movie["moves"]):
        braid = move_word(braid, move)
        current = invariant(braid, 11)["strangeness"]
        delta = current - previous
        kind = move[0]
        require(delta in (-1, 1) if kind == "triangle" else delta == 0,
                "A local front rule has the wrong radial strangeness change.")
        changes[kind, delta] += 1
        if kind == "triangle":
            triples.append({"move": index + 1, "delta": delta,
                            "before": previous, "after": current})
        previous = current
    require(braid == second, "The signed audit misses the final word.")
    require(counts == movie["counts"], "The movie's stored counts differ.")
    require(sum(item["delta"] for item in triples)
            == invariant(second, 11)["strangeness"] - invariant(first, 11)["strangeness"],
            "The signed triple changes do not telescope.")
    return {
        "counts": counts,
        "positive_triples": changes["triangle", 1],
        "negative_triples": changes["triangle", -1],
        "signed_change": sum(item["delta"] for item in triples),
        "triangle_changes": triples,
    }


def controls():
    """Exhaust small closures and audit geometric signs and bad inputs."""
    from fractions import Fraction as Q

    # At the midpoint of a quintic swap, rotate the polar direction to zero.
    # q_alpha = (h', -(R-h)); the lower incoming wire has h' = +15/8.
    radius, slope = Q(199, 2), Q(15, 8)
    v, w = (slope, -radius), (-slope, -radius)
    require(v[0] * w[1] - v[1] * w[0] == -2 * radius * slope < 0,
            "The arriving-lower exponent must be +1.")
    # The staircase braid closes into nested curls: its word is
    # 0+ 1+ ... (n-2)+ (n-2)- ... 1- 0-. Crossing means are 1,...,n-1.
    for strands in range(2, 9):
        record = invariant(list(range(1, strands)), strands, True)
        expected_word = ([(j, 1) for j in range(strands - 1)]
                         + [(j, -1) for j in reversed(range(strands - 1))])
        require(record["word"] == [list(v) for v in expected_word]
                and record["strangeness"] == strands * (strands - 1) // 2,
                "The nested-curl control changed.")
    # On two strands an odd string gives alternating signs on each wire.
    # Every crossing has mean winding one; the first-visit weights sum to one.
    for length in range(1, 12, 2):
        require(invariant([1] * length, 2, True)["strangeness"] == 1,
                "The two-strand alternating control changed.")
    tested = 0
    for strands in range(2, 5):
        for length in range(1, 8):
            for braid in product(range(1, strands), repeat=length):
                # Compute the closure's component count by following rank
                # swaps directly. This control is separate from wire lists.
                ends = []
                for start in range(strands):
                    end = start
                    for g in braid:
                        if end == g - 1:
                            end = g
                        elif end == g:
                            end = g - 1
                    ends.append(end)
                seen, end = set(), 0
                while end not in seen:
                    seen.add(end)
                    end = ends[end]
                if len(seen) == strands:
                    record = invariant(braid, strands, True)
                    require(record["closure_order"] == _cycle(ends),
                            "The closure followed the permutation in the wrong direction.")
                    tested += 1
                else:
                    reject(lambda: radial_word(braid, strands))
    for braid, strands in (([], 2), ([1], 3), ([0], 2), ([-1], 2),
                           ([2], 2), ([True], 2), ([1.0], 2), ([1], True)):
        reject(lambda: radial_word(braid, strands))
    # Incorrect closure direction can still make a valid cyclic word in very
    # small examples. This non-involutory permutation is a dedicated control.
    require(radial_word([1, 2], 3)[1] == [0, 2, 1], "The inverse-permutation control failed.")
    return tested


def _cycle(permutation):
    result, at = [], 0
    while at not in result:
        result.append(at)
        at = permutation[at]
    return result


def reject(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError("An invalid radial closure was accepted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    require(not (args.saved and args.write), "Writing requires fresh complete front proofs.")
    started = monotonic()
    tested = controls()
    print(f"{tested} small one-component closures pass both formulations, every base edge, and both symmetries; multicomponent and malformed controls fail.", flush=True)
    source = json.loads((HERE / "normal_front_braid.json").read_text())
    if args.saved:
        endpoints = source["endpoints"]
        print("Assuming the archived front completeness and geometric word extraction.", flush=True)
    else:
        front_controls()
        endpoints = [certify_word(FrontCensus(inner).run()) for inner in (6, 8)]
        require([entry["word"] for entry in endpoints]
                == [entry["word"] for entry in source["endpoints"]],
                "Fresh geometric braid words differ from the archived words.")
    require(source["strands"] == 11 and [e["inner"] for e in endpoints] == [6, 8],
            "Both eleven-strand endpoints are required.")
    atlas = read_atlas(HERE / "smooth_atlas.json")
    records = []
    for endpoint in endpoints:
        inner = endpoint["inner"]
        record = invariant(endpoint["word"], 11, True)
        case = next(c for c in atlas["verified"] if (c["outer"], c["inner"]) == (11, inner))
        original, seconds = compute_case(case)
        record.update({"inner": inner, "braid_word": endpoint["word"],
                       "original_strangeness": original["strangeness"],
                       "outward_signed_triples": record["strangeness"] - original["strangeness"]})
        record["outward_triple_lower_bound"] = abs(record["outward_signed_triples"])
        print(f"11/{inner}: St {original['strangeness']} -> {record['strangeness']}; at least {record['outward_triple_lower_bound']} outward triple passages. Original plane proof {seconds:.2f}s.", flush=True)
        records.append(record)
    movie = audit_movie(source, json.loads((HERE / "positive_front.json").read_text()))
    require([r["strangeness"] for r in records] == [-87, -101], "The large-offset values changed.")
    require((movie["positive_triples"], movie["negative_triples"], movie["signed_change"])
            == (354, 368, -14), "The signed movie count changed.")
    # The middle count is a geometric conclusion only after the uniform
    # large-offset theorem in the note. No explicit threshold is computed.
    lower_bound = sum(r["outward_triple_lower_bound"] for r in records) + len(movie["triangle_changes"])
    signed_total = records[0]["outward_signed_triples"] + movie["signed_change"] - records[1]["outward_signed_triples"]
    require(lower_bound == 936 and signed_total == -4, "The route bookkeeping failed.")
    result = {"version": 1,
              "scope": "Sufficiently large common offset; no numerical threshold. Endpoint covers and words freshly reverified when written. Middle count uses the uniform radial-family argument in radial_word.md.",
              "endpoints": records, "movie": movie,
              "route_triple_lower_bound": lower_bound, "route_signed_triples": signed_total}
    if args.write:
        (HERE / "radial_word.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Movie: {movie['positive_triples']} positive and {movie['negative_triples']} negative radial triples; net {movie['signed_change']}.", flush=True)
    print("For a sufficiently distant version of the constructed route: exactly 722 middle triples, at least 936 total, net -4. No finite offset threshold or complete offset-leg triple count is asserted.", flush=True)
    print(f"Elapsed {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
