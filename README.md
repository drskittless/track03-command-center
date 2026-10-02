# Track03 Event Command Center

A focused KBC-NOTION-03 prototype: operators can preview and confirm venue, event-date, and volunteer/equipment deployment changes. A deterministic dependency engine explains downstream impact, creates role-owned follow-up tasks, and records changes in Notion. The prototype also captures a short post-event closeout.

## Run on Windows PowerShell

From the repository root, install dependencies once per device:

```powershell
# Only if uv is not installed; reopen PowerShell after installation.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
.\scripts\setup.ps1 kshitij
```

Start the API in one PowerShell window:

```powershell
uv run uvicorn apps.api.app.main:app --reload --port 8000
```

Start the web app in a second window:

```powershell
pnpm -C apps/web dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Select a team view and try the venue, schedule, and deployment scenarios. Review the dependency paths and follow-up tasks before confirming. Fixture mode includes **Reset scenario** to restore the seed.

## Data modes

- Fixture mode is the default and requires no credentials. It is for rehearsing the workflow.
- To use the connected demo workspace, copy `.env.example` to `.env`, add the private Notion token and four database IDs, and set `USE_FIXTURES=false`. Keep `.env` private and untracked.
- Venue changes update the event venue and directly located operations. Schedule changes update the event date. Deployment changes move the selected volunteer or equipment record. Each confirmed change creates follow-up tasks and an Impact Log entry with relations.
- Event closeout marks the event done and stores its summary and lessons in the Impact Log.
- The app reads operational records from Notion and writes confirmed changes there. The dependency preview is computed by the app from the Notion relationships.

## Architecture

- `contracts/`: shared Pydantic request/response models and seeded demo data.
- `impact/`: deterministic downstream dependency evaluator for the three change scenarios.
- `apps/api/`: FastAPI board, preview, apply, and fixture-reset endpoints; fixture and Notion stores.
- `apps/web/`: role-filtered Operations, Volunteers, and Leadership dashboard, change review, and event closeout.
- `scripts/`: setup and contract generation for PowerShell and the existing shell-based CI.

## Checks

```powershell
uv run ruff check .
uv run pytest
.\scripts\gen-contract.ps1
pnpm -C apps/web lint
pnpm -C apps/web test
pnpm -C apps/web build
```
