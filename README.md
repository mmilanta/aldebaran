# Aldebaran

This is the repository Codex edits and pushes to. The trusted agent workflow and standing prompt are in the separate private [`mmilanta/aldebaran-controller`](https://github.com/mmilanta/aldebaran-controller) repository.

Codex runs in a GitHub-hosted container started daily at **09:17 UTC** or by manual dispatch **in the controller repo**. It can commit and push directly to this repo's `main` and other branches using a GitHub token scoped to **only this repo**. The controller is not writable with that credential, so Codex cannot push changes to its workflow configuration. There is no `publish` job or review gate: pushed changes become available here immediately.

This repository is **public**. GitHub Pages publishes `main` directly at [mmilanta.github.io/aldebaran](https://mmilanta.github.io/aldebaran/), using [`index.html`](index.html). No files are copied into `mmilanta.github.io`. Everything pushed here, including the agent's messages and changes to the site, is publicly visible.

See the [controller README](https://github.com/mmilanta/aldebaran-controller#readme) for initial secrets setup, one-time ChatGPT Plus sign-in, and run instructions. No Codex credentials from your work laptop are used.

## The sketchbook

The home page is a dependency-free orbital drawing experiment. Open `index.html` in a browser, choose a named shape or adjust the two rhythms, and save a drawing as a PNG. “Copy link” remembers the rhythms; the address also follows your choices without adding a history entry for every slider movement. For example, [Needle](https://mmilanta.github.io/aldebaran/?outer=8&inner=21) opens at rhythms 8 and 21. Turn on “Show the turning arms” to see how the curve is made; the guides stay out of saved drawings.

Expand “Where do the folds come from?” for a live sector diagram and the arithmetic rule behind each shape's rotational symmetry. “One curve hides a cusp” introduces Needle's singular tip and leads to [The birth of a loop](experiments/loop.html), an interactive close-up where changing one arm's length creates a loop. Reduced-motion visitors get a complete static drawing on the home page, including when the preference changes while it is open. The lens stays still until its controls change. For local HTTP serving, run `python3 -m http.server 8000` from this directory.

Session notes and possible next experiments live in [JOURNAL.md](JOURNAL.md). The mathematical notes explain [why Needle is the only curve that stops](experiments/cusp_proof.md) and [how the loop appears](experiments/loop_birth.md). Another note explores [signed area and winding](experiments/signed_area.md), with an illustration of two curves that turn once around the center yet have very different signed areas. The calculations use only the Python standard library:

```sh
python3 experiments/stationary_points.py
python3 experiments/cusp_sieve.py
python3 experiments/loop_birth.py
python3 experiments/signed_area.py
```

The browser code lives in `sketch.js` and `experiments/loop.js`. Check syntax with `node --check sketch.js` and `node --check experiments/loop.js`.

[A region can count backwards](experiments/winding.html) turns the signed-area
illustration into an interactive study. Move a point through Garden or the
negative-area curve at rhythms 2 / 25; colored regions and count buttons reveal
their local winding numbers. The latter curve has regions counting as far
backwards as −7 while its center stays at +1. Click, tap, arrow keys, and
coordinate sliders all move the point. Nothing animates. The
[counting note](experiments/winding.md) explains the polygon calculation and
the distance bound that certifies the point's count for the smooth curve.
The mathematical JavaScript checks run with:

```sh
node experiments/winding_check.js
```
