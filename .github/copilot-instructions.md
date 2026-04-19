# Copilot Workspace Instructions

## Mandatory Development Checklist

**Before any changes:**
- [ ] Lint: `uv run ruff check .`
- [ ] Build: `uv sync`
- [ ] Test: `uv run pytest`

## Project Overview

**Soc Ops** is a Social Bingo game built with Python (FastAPI + Jinja2 + HTMX). Players find people who match questions to mark squares and get 5 in a row.

## Architecture

```
app/
├── templates/       # Jinja2 HTML templates & components
├── static/          # CSS & JS assets
├── models.py        # Pydantic models (GameState, BingoSquare)
├── game_logic.py    # Board generation & bingo detection
├── game_service.py  # Session management (GameSession)
├── data.py          # Question bank
└── main.py          # FastAPI routes & HTMX endpoints
tests/               # API & game logic unit tests
```

## Key Commands

```bash
uv run uvicorn app.main:app --reload --port 8000  # Dev server
uv run pytest                                     # Tests
uv run ruff check .                               # Lint
```

## Styling & Design

- Custom CSS utilities (Tailwind-like) in `app/static/css/app.css`
- Frontend: Distinctive typography, cohesive themes, animations — avoid generic AI aesthetics
- State: Server-side via `GameSession`, persisted with signed cookies, HTMX for updates

## Resources

- **Instructions**: `css-utilities.instructions.md`, `frontend-design.instructions.md`, `general.instructions.md`
- **Prompts**: `setup.prompt.md`, `cloud-explore.prompt.md`
- **Docs**: `README.md`, `workshop/`, `docs/`