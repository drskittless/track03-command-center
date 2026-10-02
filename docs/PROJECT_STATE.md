# Project State — Track 03 V0

Updated 2026-10-03. Source folder: `C:\Users\KIIT\Documents\KBC_vibeathon`.

## A. Repo state

### Local folder and Git

- Git is initialized in this folder and connected to `https://github.com/drskittless/track03-command-center.git`. Local `main` tracks `origin/main` at `9151e99` after a successful fast-forward from the A5 test cleanup commits. No feature branch or commit has been made for B1.
- The local status after B1 shows the skeleton and generated artifacts untracked, along with the planning files and PDF. No `.env` is present. The PDF remains unopened. The user reports contract/type generation was idempotent.
- Present files: `README.md`, `Kaun Banega Codepati 2026.pdf` (binary; not read), `Kaun_Banega_Codepati_2026_Problem_Statements.md`, `Track 03 V0_ Setup Runbook (3 devices) (1).md`, `Track 03 V0_ Setup Runbook (3 devices).md`, `TRACK_03_TEAM_WORKFLOW_AND_V0_PLAN.md`, `workflow.md`, and `docs/PROJECT_STATE.md`.
- The requested canonical path `docs/track03-v0-runbook.md` is absent. The `(1)` runbook copy contains the desktop-app TOOLING CHANGE; the other runbook copy does not.

### Part B skeleton comparison

- **DONE — owner-reported, artifact presence checked:** B1 monorepo skeleton exists: FastAPI health endpoint/tests, Python project config, contracts/fixtures placeholder, impact stub/tests, React/Vite/TypeScript app, contract generator and setup scripts, Git hooks, CI, PR template, CODEOWNERS, `.env.example`, and `.codex/config.toml`.
- **DONE — owner-reported:** `sh scripts/setup.sh kshitij`, `uv run ruff check .`, `uv run pytest` (3 passed, 1 warning), `./scripts/gen-contract.sh`, `pnpm -C apps/web lint`, and `pnpm -C apps/web test` (1 passed) all completed successfully. Contract generation was reported idempotent. These command outputs were supplied by the owner, not rerun in this Windows shell.
- The B1 files remain uncommitted. The local untracked planning files and PDF are separate from the B1 scaffold and should be reviewed before staging; do not blindly stage the PDF.
- B3 still needs `AGENTS.md`, the three role files, and the DEV Context index update. T-001 through T-012 have not been confirmed started.

## B. Project status

The following setup history is owner-reported; I did not independently inspect the GitHub repository or Notion workspace.

- **DONE — owner-reported:** A1 tools on this device; A2 GitHub repo created; A3 Notion DEV area created in the NEW workspace with Dev Tasks, Decisions & RFCs, Run Log, and Context index; internal Notion connection `Track03 App` created with Read/Update/Insert capabilities and token stored privately, not shared with a page.
- **DONE — owner-reported:** A4 DEMO data is complete: Events row, 11 Operations rows and dependency relations, and the Event Tasks and Impact Log databases. The DEMO page is <https://app.notion.com/p/3edc6a05cf938024855bd38887b8d9c0>; Events database is <https://app.notion.com/p/68c152f619ce452db8d76a49a0e1bdca>. The Notion MCP property-key quirk remains relevant: write property `ID` using `userDefined:ID`.
- **DONE — owner-reported:** `Track03 App` is connected only to the DEMO page, and all four DEMO database IDs have been collected.
- **PENDING — owner-reported status not confirmed:** Privately hand the token and four IDs to Prajjwal. The owner reported that the IDs were collected but did not say the handoff occurred.
- **DONE — verified from user-provided terminal output and screenshot:** A5 is complete on this device. Local `main` tracks `origin/main`; the temporary `T-000/hello-kshitij` branch was pushed, observed on GitHub, and cleaned up.
- **DONE — owner-reported:** A5 is complete on all three devices. Parth and Prajjwal completed the clone/test-branch checks; Parth's test branch was removed, and the accidental `HELLO.md` on main was removed in a follow-up commit. GitHub collaborator screenshot shows `parthmehrotra-py` and `praj267`; repo owner is `drskittless`.
- **DONE — owner-reported:** B1 repo skeleton, hooks, CI configuration, and contract/type generation are in place and passed the reported checks. The local skeleton artifacts are present; GitHub does not yet contain them because no commit was made.
- **IN PROGRESS — local files, not yet executable-verified:** A compact venue-change slice now defines shared models and seed records, deterministic downstream impact, FastAPI board/preview/apply/reset endpoints, a live Notion REST adapter, role-filtered React views, and PowerShell setup/contract scripts. Python syntax and PowerShell parsing passed. Full tests, generated contract refresh, browser run, and live Notion read/write remain unverified because this desktop shell lacks the Windows Python dependencies and cannot access WSL.
- **BLOCKED — app workspace permission:** Creating `T-001/venue-impact-demo` failed with `fatal: cannot lock ref 'refs/heads/T-001/venue-impact-demo': unable to create directory for .git/refs/heads/T-001/venue-impact-demo`. No branch or commit was created; user terminal can create the branch after tests.
- **PENDING — owner-reported status not confirmed:** B2a: Parth seeds the 12 Dev Tasks from C2 and reports ready. B2b: Prajjwal privately hands the Notion token and four database IDs to Kshitij and Parth. No secret should enter this repo or group chat. B2a and B3 are process setup, not blockers for the event demo slice.
- **PENDING:** B3: add `AGENTS.md`, role files, and the DEV Context index; then do its specified final commit/push only after reviewing exactly what will be included.
- **PENDING:** B4 per-device setup/Notion MCP, B5 branch protection, B6 role prompts; then freeze contract v0 before starting task implementation.

## C. Tooling decision log

The runbook copy with the TOOLING CHANGE box says the team uses Codex in the ChatGPT desktop app instead of the Codex CLI. CLI install/version/login steps are skipped; open a Codex thread in the app with the project folder; configure/authenticate Notion under app Settings → MCP servers (Streamable HTTP at `https://mcp.notion.com/mcp`); use that screen to check server status; restart the app if needed; accept the project trust prompt. Terminal tools such as Git, GitHub CLI, Node, pnpm, and uv remain part of the runbook. The other runbook copy has no tooling-change box and retains the old CLI procedure.

## D. CLI leftovers

`rg` hits in the two local runbook files are listed below. These are proposed replacements only; neither runbook was edited. Line numbers refer to the current local copies.

| File and line(s) | CLI text | Proposed replacement |
|---|---|---|
| `Track 03 V0_ Setup Runbook (3 devices) (1).md:13` | `npm install -g @openai/codex`; `codex --version` | Use the desktop app; skip CLI install/version pinning and post each app version in team chat. |
| `(1).md:15,397,714,775,862` | Run `codex` and paste a prompt / start Codex from terminal | Open a new Codex thread in the desktop app with this project folder open, then paste the prompt. |
| `(1).md:16` | `codex mcp add` / `codex mcp login notion`; `~/.codex/config.toml` | App Settings → MCP servers → add/authenticate `notion` using Streamable HTTP and `https://mcp.notion.com/mcp`; restart the app if needed. |
| `(1).md:17,667` | `codex mcp list` | Check that `notion` is enabled and signed in on the app's MCP servers screen. |
| `(1).md:115-116,122-123,158` | CLI install and `codex --version` checks | Skip Codex CLI steps; use the desktop app. Keep checks for non-Codex terminal tools. |
| `(1).md:144` | `Run codex` for Codex login | Skip; sign-in is through the desktop app. |
| `(1).md:427` | Create `.codex/config.toml` with MCP server config | Configure the Notion server in app Settings → MCP servers; keep any non-MCP project settings only if still needed. |
| `(1).md:659-667` | Start/exit CLI, `codex mcp login notion`, help/list | Use app trust prompt if shown, then authenticate and verify `notion` in app Settings → MCP servers. |
| `(1).md:775,862` | Run `codex` and paste task prompt | Open a Codex thread in the app with the project folder, then paste the prompt. |
| `(1).md:961-962` | CLI not-found recovery; start `codex` to fix MCP | Replace with desktop-app sign-in and MCP-server screen troubleshooting. |
| `Track 03 V0_ Setup Runbook (3 devices).md:93-94,100-101,136` | CLI install and `codex --version` checks | Skip Codex CLI steps; use the desktop app. |
| `Track 03 V0_ Setup Runbook (3 devices).md:122,375,692,753,840` | Run `codex` and paste prompt / start Codex from terminal | Open a Codex thread in the app with the project folder, then paste the prompt. |
| `Track 03 V0_ Setup Runbook (3 devices).md:405` | Create `.codex/config.toml` MCP server config | Configure the Notion server in app Settings → MCP servers; retain non-MCP settings only if still needed. |
| `Track 03 V0_ Setup Runbook (3 devices).md:637-645` | Start/exit CLI, `codex mcp login notion`, help/list | Use app trust prompt if shown, then authenticate and verify `notion` in app Settings → MCP servers. |
| `Track 03 V0_ Setup Runbook (3 devices).md:939-940` | CLI not-found recovery; start `codex` to fix MCP | Replace with desktop-app sign-in and MCP-server screen troubleshooting. |

The matches above cover CLI invocations and MCP setup instructions. A literal `codex login` and `rmcp` were not found. The desktop-app runbook itself mentions `~/.codex/config.toml` at line 16 as shared configuration; configure MCP through the app as that same line directs.

## E. Risks or conflicts

- Git is now linked locally to the owner-reported public remote, and A5's single-device test passed. The other devices' clones/branch tests, GitHub branch protection, and CI are not verified.
- The canonical runbook path named in the request is missing, and two differently sized runbook copies coexist. Only one has the required desktop-app override. Following the older copy would reintroduce CLI instructions.
- The B1 skeleton prompt asks for `CODEOWNERS` at `.github/CODEOWNERS`, while the requested existence check named root `CODEOWNERS`; neither currently exists. Keep the intended `.github/CODEOWNERS` location explicit when implementing.
- Git and the A5 branch test now work in this folder. The Part B guardrails are still absent; GitHub branch protection and CI status have not been verified.
- Runbook A1 says Windows users should move to Ubuntu/WSL and use that terminal, while the desktop-app override changes only Codex interaction. The chosen local workspace is a Windows Documents path; the runbook does not verify whether the app and team setup will use this path directly or a WSL clone.

## F. Next five steps, in order

1. Install native Windows `uv`, run `scripts/setup.ps1 kshitij`, and refresh generated schemas/types with `scripts/gen-contract.ps1`.
2. Run Python and web checks, start API/web from PowerShell, and rehearse the fixture venue-change path.
3. Prajjwal privately supplies the Notion token and four database IDs; verify live Notion read, preview, apply, and readback.
4. Create `T-001/venue-impact-demo` from the user terminal, stage the product files only (exclude the PDF and unrelated planning files), push, open a PR, and check CI.
5. Use remaining time for teammate review/polish and the complete live demo; defer B2a/B3/B4–B6 unless time remains.
