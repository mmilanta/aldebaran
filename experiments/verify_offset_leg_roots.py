"""Recheck every archived outward-circle root with exact arithmetic.

This is a faster LOCAL audit, assuming the archived whole-domain covers.
It repeats the independent axis proof and every circle contraction,
direction, sign, reflection, and distinct-circle separation. It does not
repeat the pair graph or the exhaustive three-arc covers and cannot write
a new complete certificate. For completeness use offset_leg_census.py.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from time import monotonic

from blend_cusps import require
from offset_axis_census import prove as prove_axis
from offset_axis_visits import prove as prove_fixed
from offset_leg_census import (classify, clear_caches, contract, identify,
                               root_domains)

HERE = Path(__file__).resolve().parent


def audit_endpoint(endpoint, axis):
    inner = endpoint["inner"]
    require(type(inner) is int and inner in (6, 8) and axis["inner"] == inner,
            "Choose matching endpoint and independent axis proofs.")
    require(len(endpoint["roots"]) == endpoint["positive_triples"] + endpoint["negative_triples"],
            "The archived signed totals do not account for every root.")
    records = []
    for archived in endpoint["roots"]:
        domains = root_domains(archived, "coarse_box")
        require(len(domains) == 3 and all(type(q) is int and 0 <= q < 4
                and Q(0) <= low < high <= Q(1) for q, low, high in domains),
                "Malformed archived triple chart product.")
        require(all(a[0] < b[0] or a[0] == b[0] and a[2] < b[1]
                    for a, b in zip(domains, domains[1:])),
                "The archived visit domains are not strictly ordered.")
        status, data = contract(domains, inner)
        require(status == "root", "An archived root lacks a fresh existence-and-uniqueness contraction.")
        record = classify(domains, data, inner)
        require(record is not None, "An archived outward circle is inward.")
        # First compare the local fields. Grouping is rederived below.
        require(all(archived.get(key) == value for key, value in record.items()),
                "An archived local root, sign, radius, or center disagrees with its fresh proof.")
        records.append(record)
    result = identify(records, axis)
    require(records == endpoint["roots"], "Archived root order or event identifications disagree.")
    require(all(endpoint.get(key) == value for key, value in result.items()),
            "Archived event grouping or conditional tail metadata disagree.")
    positive = sum(r["strangeness_jump"] > 0 for r in records)
    negative = sum(r["strangeness_jump"] < 0 for r in records)
    require((positive, negative) == (endpoint["positive_triples"], endpoint["negative_triples"]),
            "Archived signed totals disagree with the freshly verified roots.")
    print(f"11/{inner}: all {len(records)} archived outward-circle subsets reverified locally; "
          f"{positive} positive, {negative} negative; "
          f"{result['separated_circle_pairs']} fresh circle-pair separations.", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=HERE / "offset_leg_census.json")
    args = parser.parse_args()
    started = monotonic()
    record = json.loads(args.record.read_text())
    require([e["inner"] for e in record["endpoints"]] == [6, 8], "The record must contain both ordered endpoints.")
    print("Assuming the archived pair-graph and complete triple-product covers. "
          "Repeating exact LOCAL root and event-identification proofs only.", flush=True)
    for endpoint in record["endpoints"]:
        try:
            prove_fixed(endpoint["inner"])
            axis = prove_axis(endpoint["inner"])
            audit_endpoint(endpoint, axis)
        finally:
            clear_caches()
    print(f"All archived roots and identifications passed; global completeness remains an assumed cover receipt. "
          f"Use offset_leg_census.py to repeat it. Elapsed {monotonic() - started:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
