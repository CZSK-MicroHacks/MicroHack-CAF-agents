# AGENTS.md

Coding conventions and tooling guidance for AI agents working in this repository.

## Stack

- **Python** — primary language
- **Microsoft Fabric** — data engineering and orchestration
- **Microsoft Foundry** — agent infrastructure
- **Copilot Studio** — conversational AI / agent authoring

## Python

Use `uv` for all package management. No `requirements.txt` — dependencies live in `pyproject.toml`.

```sh
uv init          # new project
uv add <pkg>     # add dependency
uv run <script>  # run without activating venv
uv sync          # install from lockfile
```

`pyproject.toml` is the single source of truth for dependencies, tooling config (ruff, pytest, mypy), and metadata.

## Code style

- Docstrings on all public functions and classes; skip obvious inline comments.
- No premature abstractions — solve the problem at hand, refactor when a pattern repeats.
- Keep modules focused and small; flat structure beats deep nesting.
- Prefer stdlib and direct SDK calls over wrapper layers.

## File structure

```
project/
├── pyproject.toml
├── uv.lock
├── src/
│   └── <module>/
└── tests/
```

Add sub-packages only when genuinely needed. Co-locate related logic rather than splitting by layer (handlers/, services/, utils/ for tiny projects is overkill).

## Checks

```sh
uv run ruff check .        # lint
uv run ruff format .       # format
uv run pytest              # tests
```

Fix lint errors before committing. Do not suppress warnings without a comment explaining why.
