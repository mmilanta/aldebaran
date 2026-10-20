# Aldebaran

This is the repository Codex edits and pushes to. The trusted agent workflow and standing prompt are in the separate private [`mmilanta/aldebaran-controller`](https://github.com/mmilanta/aldebaran-controller) repository.

Codex runs in a GitHub-hosted container started by a manual dispatch **in the controller repo**. It can commit and push directly to this repo's `main` and other branches using a GitHub token scoped to **only this repo**. The controller is not writable with that credential, so Codex cannot push changes to its workflow configuration. There is no `publish` job or review gate: pushed changes become available here immediately.

See the [controller README](https://github.com/mmilanta/aldebaran-controller#readme) for initial secrets setup, one-time ChatGPT Plus sign-in, and run instructions. No Codex credentials from your work laptop are used.
