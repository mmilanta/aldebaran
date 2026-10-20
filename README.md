# Aldebaran agent runner

Manually dispatch a GitHub Action to run **Codex CLI using ChatGPT Plus** inside a network-enabled container with this repository checked out. No always-on machine, OpenAI API key, GitHub PAT, or stored ChatGPT secret is needed. **You must be online to complete device-code login on every run.** Codex works for at most 15 minutes after login. If login or Codex times out, the run fails and publishes no partial changes.

Successful changes are passed as an untrusted patch to a separate, fresh publisher job, which rejects edits to `.github/` and pushes a new `agent/run-<run-id>-<attempt>` branch. It never pushes to `main`.

## Setup and run

1. Enable **device code login** in your [ChatGPT security settings](https://chatgpt.com/#settings/Security) (device authentication is currently beta). Your ChatGPT Plus account must support Codex CLI. No key needs to be added to GitHub Secrets.
2. Commit and push this repository to `main` and enable Actions. In **Settings → Actions → General → Workflow permissions**, allow read/write `GITHUB_TOKEN` permissions if required by your repository policy. The agent job requests only `contents: read`; only the separate publisher job requests `contents: write`.
3. In **Settings → Rules → Rulesets**, protect `main` from direct pushes and require review before merging. If your plan allows it, add a push ruleset restricting `.github/workflows/**` updates to maintainers. The workflow's own patch check protects this publishing path, but only GitHub-side rules can enforce a restriction for *all* credentials and workflows.
4. Open **Actions → Run Codex agent → Run workflow**, select `main`, and enter a task. Immediately open the `Sign in with ChatGPT Plus` step's live logs; use the displayed URL and one-time code to sign in in your browser **within 5 minutes**. If no code appears, check that device code login is enabled for your account. The login is discarded after the run.
5. Review the pushed branch and open a PR manually. Codex uses the subscription's default model; this workflow does **not** guarantee `gpt-6.1-sol` is available through Codex CLI.

The agent gets internet access and can read its temporary ChatGPT OAuth credential inside the container. Malicious tasks or repository content could exfiltrate it. Don't run untrusted inputs; revoke the Codex authorization from your ChatGPT account if compromised. The agent has no repository write token; the publisher has that token only in a separate job after Codex exits. The agent can edit the local checkout but cannot publish changes to `.github/` through this workflow. The time limit applies to Codex execution (15 minutes), not installation, login, and publishing; the agent job has a 25-minute ceiling. The official `openai/codex-action` needs a separately billed API key, so this workflow installs the Codex CLI and uses its interactive device-code login instead.
