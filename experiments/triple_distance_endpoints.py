"""Fresh smooth words for triple_distance.js, including a positive control.

Run: python3 experiments/triple_distance_endpoints.py [--write]
The default prints a JSON record after all rational endpoint proofs pass.
--write also archives the four-triple control at blend weight 9/100.
Only the standard library and existing proof programs are used.
"""

import argparse
import hashlib
import json
from fractions import Fraction as Q

from rhythm_passages import snapshot
from strangeness import HERE, compute_case
from verify_smooth_atlas import read_atlas


def fresh():
    atlas = read_atlas(HERE / "smooth_atlas.json")
    archive = json.loads((HERE / "strangeness_atlas.json").read_text())
    digest = hashlib.sha256((HERE / "certify_intersections.py").read_bytes()).hexdigest()
    assert digest == atlas["certificate_code_sha256"] == archive["certificate_code_sha256"]
    endpoints = []
    for inner in (6, 8):
        case, = [r for r in atlas["verified"] if (r["outer"], r["inner"]) == (11, inner)]
        saved, = [r for r in archive["verified"] if (r["outer"], r["inner"]) == (11, inner)]
        result, _ = compute_case(case)
        assert result == saved
        endpoints.append(result)
    result = snapshot(Q(9, 100))
    control = {key: result[key] for key in (
        "weight", "crossings", "strangeness", "tangent_index", "initial_index2", "word"
    )}
    assert control["crossings"] == 40 and control["strangeness"] == 11
    control["certificate_code_sha256"] = digest
    return {"endpoints": endpoints, "control": control}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = fresh()
    if args.write:
        (HERE / "triple_distance_control.json").write_text(
            json.dumps(result["control"], indent=2) + "\n"
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
