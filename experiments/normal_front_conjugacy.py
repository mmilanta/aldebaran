"""Verify an explicit conjugacy of the two eleven-strand conormal braids.

Run: python3 experiments/normal_front_conjugacy.py
This audits the recorded braid words; normal_front_braid.py repeats fresh
geometric proofs before calling the same verifier. Standard library only.
The witness was found with a temporary libbraiding search. No search code
or external library is needed to verify it. See normal_front_braid.md.
"""

import json
from pathlib import Path

from blend_cusps import require

# A positive witness C with A C = C B, hence C^(-1) A C = B.
CONJUGATOR = (
    1,
    2,
    1,
    3,
    2,
    1,
    4,
    3,
    2,
    1,
    5,
    4,
    3,
    2,
    1,
    6,
    5,
    4,
    3,
    2,
    1,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    10,
    9,
    8,
    7,
    6,
    5,
    4,
    2,
    1,
    3,
    4,
    3,
    2,
    5,
    4,
    3,
    2,
    1,
    6,
    5,
    4,
    3,
    2,
    1,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    10,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    1,
    2,
    1,
    3,
    2,
    1,
    4,
    3,
    2,
    1,
    5,
    4,
    3,
    2,
    1,
    6,
    5,
    4,
    3,
    2,
    1,
    7,
    6,
    5,
    4,
    3,
    2,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    10,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    1,
    2,
    1,
    3,
    2,
    4,
    3,
    2,
    1,
    5,
    4,
    3,
    2,
    6,
    5,
    7,
    6,
    5,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    10,
    9,
    8,
    7,
    6,
    8,
    10,
    8,
)


def inverse(word):
    return [-letter for letter in reversed(word)]


def reduce_word(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return stack


def artin_action(word, strands=11):
    """Compose by updating just the two affected free-generator images."""
    require(type(strands) is int and strands > 0, "Use a positive free-group rank.")
    require(
        all(type(k) is int and 1 <= k < strands for k in word),
        "Use positive Artin generators.",
    )
    images = [[i + 1] for i in range(strands)]
    for generator in word:
        a, b = images[generator - 1], images[generator]
        images[generator - 1] = reduce_word(a + b + inverse(a))
        images[generator] = a
    return images


def substitution_action(word, strands=11):
    """Independent literal substitution, reversing the composition loop.

    Its reducer deletes adjacent inverse pairs directly rather than
    sharing the stack implementation above. Only short words occur here.
    """
    require(type(strands) is int and strands > 0, "Use a positive free-group rank.")
    require(
        all(type(k) is int and 1 <= k < strands for k in word),
        "Use positive Artin generators.",
    )
    images = [[i + 1] for i in range(strands)]
    for generator in reversed(word):
        replacements = {
            generator: [generator, generator + 1, -generator],
            generator + 1: [generator],
        }
        changed = []
        for image in images:
            expanded = []
            for letter in image:
                replacement = replacements.get(abs(letter), [abs(letter)])
                expanded.extend(
                    replacement if letter > 0 else [-x for x in replacement[::-1]]
                )
            while True:
                pair = next(
                    (
                        i
                        for i in range(len(expanded) - 1)
                        if expanded[i] == -expanded[i + 1]
                    ),
                    None,
                )
                if pair is None:
                    break
                del expanded[pair : pair + 2]
            changed.append(expanded)
        images = changed
    return images


def verify(first, second, witness=CONJUGATOR):
    witness = list(witness)
    left, right = list(first) + witness, witness + list(second)
    images = artin_action(left)
    require(
        images == artin_action(right),
        "The proposed witness does not satisfy A C = C B.",
    )
    require(
        images == substitution_action(left) == substitution_action(right),
        "The two Artin action implementations disagree.",
    )
    return images


def controls():
    for word in ([], [1], [1, 2, 1], [1, 3, 2, 1, 3]):
        require(
            artin_action(word, 4) == substitution_action(word, 4),
            "The action implementations disagree on a control.",
        )
    require(
        artin_action([1, 2, 1], 3) == artin_action([2, 1, 2], 3),
        "The Artin braid relation failed.",
    )
    require(
        artin_action([1, 3], 4) == artin_action([3, 1], 4),
        "Distant Artin actions do not commute.",
    )
    require(
        artin_action([1], 3) == [[1, 2, -1], [1], [3]],
        "The single-generator action changed.",
    )
    require(
        reduce_word([1, 2, -2, -1]) == [] and reduce_word([1, 2, -1]) == [1, 2, -1],
        "Free reduction failed on nested or noncancelling letters.",
    )
    for bad in ([0], [-1], [11], [1.5]):
        for action in (artin_action, substitution_action):
            try:
                action(bad)
            except ValueError:
                pass
            else:
                raise ValueError("An invalid positive generator was accepted.")


def main():
    controls()
    record = json.loads(
        (Path(__file__).resolve().parent / "normal_front_braid.json").read_text()
    )
    first, second = [endpoint["word"] for endpoint in record["endpoints"]]
    images = verify(first, second)
    try:
        verify(first, second, list(CONJUGATOR) + [1])
    except ValueError:
        pass
    else:
        raise ValueError("The altered-conjugator control was accepted.")
    print(
        f"Given the recorded geometric braid words: A C = C B, |C|={len(CONJUGATOR)}."
    )
    print(
        f"Two independent faithful Artin actions agree on all eleven full images: {[len(w) for w in images]}."
    )
    print(
        "The braids are conjugate and their ordinary closures are isotopic. Explicit Legendrian and plane-curve isotopies are not constructed."
    )


if __name__ == "__main__":
    main()
