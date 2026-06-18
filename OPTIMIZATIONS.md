# DataProphet Optimization Audit

## Remaining Issues

**6 findings. 0 critical. 0 high. 3 medium. 3 low.**

### F28: `_add_children_of` Reintroduces N+1 for CSV Grouping

- **Severity:** Medium
- **Impact:** More DB round-trips per tree generation
- **Evidence:** `services.py:330-336` — For each sibling/relative, `get_relatives(WHERE_PARENTS, ...)` fetches children individually.
- **Recommended fix:** Batch-fetch all children in one query, group by parent TC, then interleave into results.
- **Status:** ❌ Open (regression from grouping refactor)

### F29: `get_full_person` Opens 3 Connections Per Person

- **Severity:** Medium
- **Impact:** 18 connection checkouts for 6 ancestor calls
- **Evidence:** `services.py:138-159` — Each `get_full_person` call opens 3 separate pool connections.
- **Recommended fix:** Pre-fetch all ancestor TCs, then batch-fetch address/GSM data in bulk.
- **Status:** ❌ Open (low priority)

### F30: `validate_tc` vs `is_valid_tc` Inconsistency

- **Severity:** Medium
- **Impact:** Different validation behavior across codebases
- **Evidence:** `old101.py:36-37` vs `utils.py:7-9`. old101 accepts all-zeros TC; modern path rejects it.
- **Recommended fix:** Replace `validate_tc` in old101.py with `from src.utils import is_valid_tc`.
- **Status:** ❌ Open

### F31: `search_database` Uses `SELECT *` in old101

- **Severity:** Low
- **Impact:** Over-fetching columns not needed for CSV output
- **Recommended fix:** Replace `SELECT *` with explicit column list matching `CSV_HEADER_SEARCH`.
- **Status:** ❌ Open (legacy code)

### F32: `_write_children_and_grandchildren` N+1 in old101

- **Severity:** Low
- **Impact:** Extra queries in legacy family tree generation
- **Status:** ❌ Open (legacy code, lower priority)

### F33: `_write_siblings_and_nieces` 3-Level N+1 in old101

- **Severity:** Low
- **Impact:** Extra queries in legacy sibling branch
- **Status:** ❌ Open (legacy code, lower priority)

## Quick Wins

| # | Fix | Time | Impact |
|---|-----|------|--------|
| 1 | **F30:** Replace `validate_tc` with `is_valid_tc` in old101 | 10 min | Medium — consistency |
| 2 | **F31:** Replace `SELECT *` with explicit columns in old101 search | 30 min | Low — less data transfer |

## Validation Plan

- All 47 tests must pass after any change.
- Time `generate_tree` for a family with 5+ siblings, 3+ extended relatives.
- Verify CSV grouping is preserved — cousins/nieces appear under their parent.
- `uv run ruff check src/ tests/` must pass.

## Architecture Notes

- **`old101.py` is standalone legacy** — no imports from other `src.` modules.
- **`services.py` is the modern path** — modular, batch-optimized, cached.
