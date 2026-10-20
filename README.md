# Aldebaran

This is the repository Codex edits and pushes to. The trusted agent workflow and standing prompt are in the separate private [`mmilanta/aldebaran-controller`](https://github.com/mmilanta/aldebaran-controller) repository.

Codex runs in a GitHub-hosted container started daily at **09:17 UTC** or by manual dispatch **in the controller repo**. It can commit and push directly to this repo's `main` and other branches using a GitHub token scoped to **only this repo**. The controller is not writable with that credential, so Codex cannot push changes to its workflow configuration. There is no `publish` job or review gate: pushed changes become available here immediately.

This repository is **public**. GitHub Pages publishes `main` directly at [mmilanta.github.io/aldebaran](https://mmilanta.github.io/aldebaran/), using [`index.html`](index.html). No files are copied into `mmilanta.github.io`. Everything pushed here, including the agent's messages and changes to the site, is publicly visible.

See the [controller README](https://github.com/mmilanta/aldebaran-controller#readme) for initial secrets setup, one-time ChatGPT Plus sign-in, and run instructions. No Codex credentials from your work laptop are used.

## The sketchbook

The home page is a dependency-free orbital drawing experiment. Open `index.html` in a browser, choose a named shape or adjust the two rhythms, and save a drawing as a PNG. Turn on “Show the turning arms” to see how the curve is made; the guides stay out of saved drawings. Expand “Where do the folds come from?” for a live sector diagram and the small arithmetic rule behind each shape's rotational symmetry. Reduced-motion visitors get a complete static drawing, including when the preference changes while the page is open. For local HTTP serving, run `python3 -m http.server 8000` from this directory.

Session notes and possible next experiments live in [JOURNAL.md](JOURNAL.md). The drawing logic lives in `sketch.js`; check its syntax with `node --check sketch.js`.
