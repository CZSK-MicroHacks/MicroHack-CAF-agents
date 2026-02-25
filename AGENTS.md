# AGENTS.md

Coding conventions and tooling guidance for AI agents working in this repository.

## Stack

- **Python** — primary language
- **Microsoft Fabric** — data engineering and orchestration -> data agent
- **Microsoft Foundry** — agent infrastructure and Foundry IQ for institutional knowledge
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

## Agent coding

- Start with planning and make sure you understand the task and data before coding.
- Where possible create tests so you can validate your progress and fix issues early.

## Terraform IaC

- Scope: Applies to all MicroHack Terraform-based IaC projects.
- Versions: Use the latest stable Terraform and pin Terraform/provider versions in `versions.tf`.
- Providers: Use `azurerm` by default; use `azapi` only for Azure features not yet in `azurerm`.
- Layout: Keep provider/backend setup in `main.tf`; use `variables.tf` and `outputs.tf`; split resources into focused files (`networking.tf`, `rbac.tf`, etc.), and split further when files get large.
- Variables & naming: Prefer strict types over `any`, add clear descriptions, provide safe defaults, use `snake_case`, and keep names descriptive/unique.
- Comments & tags: Comment only non-obvious or critical decisions; tags are optional unless required, and shared tags should come from `locals`.
- State & modules: Always use remote state with locking, isolate state per environment, never commit state files, and keep reusable logic in semver-versioned modules (local path or tagged git source).
- Security: Never hardcode secrets; use Key Vault/env vars; mark sensitive outputs with `sensitive = true`.