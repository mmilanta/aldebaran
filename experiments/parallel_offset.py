"""Count inverse touches on the endpoint legs of the positive-front route.

Default: repeat both complete rational front covers and fresh plane counts.
--saved: assume completeness of normal_front_census.json, but still repeat
the smooth plane proofs. Standard library only. The analytic argument in
positive_front.md supplies the offset-family count; event locations are
not inputs and are not computed by this program.
"""

import argparse
import json
from pathlib import Path
from time import monotonic

from blend_cusps import require
from normal_front_census import FrontCensus, controls as front_controls
from verify_smooth_atlas import read_atlas, verify_case

HERE = Path(__file__).resolve().parent


def births(plane_count, front_count):
    require(
        type(plane_count) is int and type(front_count) is int
        and 0 <= plane_count <= front_count,
        "Use nonnegative integer crossing counts in increasing order.",
    )
    require((front_count - plane_count) % 2 == 0, "A birth adds two crossings.")
    return (front_count - plane_count) // 2


def controls():
    require(births(0, 0) == births(3, 3) == 0, "Equal-count control failed.")
    require(births(0, 2) == births(5, 7) == 1, "One-birth control failed.")
    for counts in ((1, 0), (-1, 1), (0, 1), (0, 2.0), (True, 3)):
        try:
            births(*counts)
        except ValueError:
            pass
        else:
            raise ValueError("An invalid crossing-count control was accepted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", action="store_true", help="assume the archived front cover's completeness; still repeat plane proofs")
    args = parser.parse_args()
    started = monotonic()
    controls()
    if args.saved:
        fronts = json.loads((HERE / "normal_front_census.json").read_text())["endpoints"]
        require([e["inner"] for e in fronts] == [6, 8], "Unexpected archived endpoints.")
        require(all(e["bitangents"] == len(e["roots"]) for e in fronts), "Archived front counts disagree with their root lists.")
        print("Assuming the archived complete front covers; fresh plane proofs follow.", flush=True)
    else:
        front_controls()
        fronts = [FrontCensus(inner).run() for inner in (6, 8)]
    atlas = read_atlas(HERE / "smooth_atlas.json")
    total = 0
    for front in fronts:
        case = next(c for c in atlas["verified"] if (c["outer"], c["inner"]) == (11, front["inner"]))
        _, inner, plane_count, seconds = verify_case(case)
        count = births(plane_count, front["bitangents"])
        total += count
        print(
            f"11/{inner}: {plane_count} original crossings (fresh {seconds:.2f}s proof), "
            f"{front['bitangents']} large-offset crossing pairs; exactly {count} inverse pair-births on the outward leg.",
            flush=True,
        )
    print(
        f"The full route can be made generic with exactly {total} inverse touches and no direct touches: "
        "births on the first offset leg, deaths on the reversed second leg, none in the middle.",
        flush=True,
    )
    print("This counts tangency pair-events using the analytic offset theorem; their locations and plane triple passages are not counted.", flush=True)
    print(f"Completed in {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
