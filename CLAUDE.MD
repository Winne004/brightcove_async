# Python Package Management with uv

Use uv exclusively for Python package management in this project.

## Package Management Commands

- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

Use these commands:

- Add a runtime dependency: `uv add <package>`
- Add a dev dependency: `uv add --group dev <package>`
- Remove a dependency: `uv remove <package>`
- Sync environment from the lockfile: `uv sync`
- Lock dependencies: `uv lock`

## Running Python Code

- Run a Python script with `uv run python <script-name>.py` (or `uv run python -m <module>`)
- Run Python tools with `uv run <tool>` (e.g. `uv run pytest`, `uv run ruff`, `uv run ty`, `uv run pre-commit`)
- Launch a Python REPL with `uv run python`