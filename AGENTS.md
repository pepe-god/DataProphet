# DataProphet

## Run commands

```
uv run data          # main GUI app (src.main)
uv run old101        # old101 GUI app (src.old101)
uv run python -m src # alternative: runs src/__main__.py
uv run ruff check .  # lint
uv run ruff format . # format
uv sync              # install/build after pyproject.toml changes
```

## Project structure

- `src/` is the only package, built with hatchling (`[tool.hatch.build.targets.wheel]`)
- Two separate GUI apps in one package: `src/main.py` (DataProphet) and `src/old101.py` (101)
- MySQL databases: `101m`, `140gsm`, `adresv2`, `109m` — config via `src/config.ini` (not committed)
- Python 3.14, managed by uv

## Gotchas

- `src/config.ini` is gitignored. Copy `src/config.ini.example` to `src/config.ini` and fill credentials before running.
- All imports are relative (`from .utils import ...`). Never run files directly with `python src/main.py` — always use `uv run data` or `uv run python -m src`.
- `pyproject.toml` has `[project.scripts]` entries (`data`, `old101`). After editing pyproject.toml, run `uv sync` to rebuild.
