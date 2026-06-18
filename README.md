# DataProphet

A Python-based desktop application for advanced data searching and family record management.

## Prerequisites

- Python 3.14 or higher
- MySQL Server
- [uv](https://docs.astral.sh/uv/) (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DataProphet
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

Create a `config.ini` file in the root directory with your database connection details:

```ini
[DATABASE]
host = localhost
user = your_user
password = your_password
database = your_db

[GSMDATA]
host = localhost
user = your_user
password = your_password
database = gsm_db
```

## Usage

```bash
uv run main          # Modern GUI (DataProphet v2.0)
uv run old101        # Legacy GUI (101 Veri Yönetim Sistemi)
```

## Testing

```bash
uv run pytest tests/ -v    # Run all tests
uv run ruff check src/     # Lint source code
uv run ruff check tests/   # Lint tests
```

## Project Structure

```
src/
  main.py         # Modern app entry point
  gui.py          # Tkinter GUI (DataProphetApp)
  services.py     # SearchService, FamilyService
  database.py     # MySQL connection pool management
  models.py       # Person dataclass, CSV headers
  config.py       # Config loader
  utils.py        # Validation, cleaning utilities
  old101.py       # Legacy standalone app
tests/
  test_*.py       # 47 tests (pytest)
```

## Features

- Advanced search with 20+ field filters
- Family tree generation with ancestor/descendant tracing
- Multi-threaded operations for UI responsiveness
- CSV export with grouped family records
- Connection pooling for efficient DB access
