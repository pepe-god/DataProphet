# AGENTS.md

## Commands

```bash
uv run start             # Launch GUI app (Tkinter)
uv run oldstart          # Launch legacy monolithic GUI
uv run pytest tests/ -v  # Run all 47 tests
uv run ruff check src/   # Lint source code
uv run ruff check tests/ # Lint tests
uv sync                  # Install deps
```

## Search Tools

- **Use `rg` (ripgrep) for all file content searches.** Do not use `grep` or `Select-String`.
  - `rg "pattern" src/` — search in source
  - `rg "pattern" src/ --type py` — Python files only
  - `rg -l "pattern" src/` — list matching files
  - `rg -n "pattern" src/` — show line numbers
  - `rg "class \w+" src/` — regex patterns supported

## Pre-commit

Pre-commit hooks run before each commit (never skip with `--no-verify`).

```bash
.venv/Scripts/python.exe -m pre_commit install          # Set up git hooks
.venv/Scripts/python.exe -m pre_commit run --all-files  # Run hooks manually
```

Hooks: merge-conflict check, trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, debug-statements, ruff check (--fix), ruff-format, detect-secrets, mypy, pytest.

## Architecture

- **`src/`** — all source code. Package name is `src`, not `dataprophet`. Imports use relative form (`from .database import ...`).
- **`main.py`** → `gui.py` → `services.py` → `database.py` (modern path)
- **`old101.py`** — standalone legacy monolith (own DB connections, own GUI, own everything). Do not refactor it to use `services.py`; keep it self-contained.
- **`services.py`** — `SearchService` and `FamilyService` share a `BaseService` base class with `execute_query` and `save_to_csv`.
- **`database.py`** — `DatabaseProvider` manages MySQL connection pools (class-level `_pools` dict, classmethods).
- **`config.ini`** — gitignored, contains MySQL credentials. Located in `src/` directory. Required at runtime. Sections: `DATABASE`, `FULLDATA`, `GSMDATA`, `ADRESSDATA`. A template is provided as `src/config.ini.example`.
- **`index/`** — gitignored output directory for CSV files (created at runtime).

## Key Gotchas

- **Entry points reference `src.*`** in `pyproject.toml` (`src.main:main`, `src.old101:main`). The package directory is literally named `src/`. Do not rename to `dataprophet/` — a previous attempt (commit `283435e`) was reverted (`0f11d9e`) because uv's editable install `.pth` mechanism conflicted.
- **`config.ini` is gitignored and not in the repo.** Tests that hit `load_config()` without mocking will fail if `config.ini` is missing. The first two tests in `test_config.py` (`test_loads_existing_config`, `test_config_has_database_sections`) require a real `config.ini`.
- **Mock patch paths must use `src.` prefix**, e.g. `@patch("src.database.load_config")`. Tests import from `src.*` directly.
- **`old101.py` uses SQL string interpolation** (`f"{field}='{value}'"`). Do not "fix" it to parameterized queries without also changing `execute_query`'s signature — it currently appends LIMIT/OFFSET via string concat.
- **`_fetch_ancestors` now batch-fetches all ancestor data** (parents + grandparents) in 3 total connections instead of 18. `get_full_person` still opens 3 connections for a single person call, but ancestor traversal uses batch queries.
- **Git identity:** `god` / `god@example.com`. Use this for commits.

## Testing

- 47 tests in `tests/`, run with `uv run pytest tests/ -v`.
- Fixtures in `tests/conftest.py`: `sample_person_dict`, `tmp_index_dir`.
- `test_config.py` tests `load_config` against real `config.ini` (no mocking for 2 of 3 tests).
- `test_services.py` and `test_database.py` mock DB connections heavily — no real MySQL needed.
- `tests/test_models.py` tests `Person` dataclass and constants only.

## Scope Notes

- `services.py` is the refactored modular version. `old101.py` is legacy. Both are maintained.
- The GUI uses Tkinter (no web framework). Long operations run in `ThreadPoolExecutor(max_workers=4)`.
- Output files go to `./index/` (gitignored, `*.csv` also gitignored).
- All user-facing strings in `old101.py` are Turkish. In `services.py`/`gui.py`, log messages are Turkish but UI labels use a mix.
