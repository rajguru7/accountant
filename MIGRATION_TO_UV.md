# Migration to Modern Python Tooling (uv + ruff)

This document explains the migration from legacy Python tooling to modern development tools.

## What Changed

### Package Management: pip → uv

**Before:**
- `setup.py` - Legacy setuptools configuration
- `requirements.txt` - Manual dependency management
- `pip install -e .` - Install packages

**After:**
- `pyproject.toml` - Modern Python packaging standard (PEP 517/621)
- `uv.lock` - Lockfile for reproducible builds
- `uv sync` - Fast dependency resolution and installation (10-100x faster)
- `.venv/` - Virtual environment managed by uv

### Code Quality: black + flake8 → ruff

**Before:**
- `black` - Code formatter
- `flake8` - Linter
- Multiple tool configurations

**After:**
- `ruff` - All-in-one linter and formatter (10-100x faster)
- Single configuration in `pyproject.toml`
- Includes isort, pyupgrade, and more

### Pre-commit Hooks

**New:**
- `.pre-commit-config.yaml` - Automated code quality checks
- Runs on every commit to maintain code standards

## Benefits

1. **Speed**: `uv` is 10-100x faster than pip for installing packages
2. **Reliability**: Lockfile ensures reproducible environments across machines
3. **Modern Standards**: Uses PEP 517/621 for packaging
4. **Simplified Tooling**: Single tool (ruff) instead of multiple formatters/linters
5. **Automated Quality**: Pre-commit hooks ensure consistent code quality

## Commands Cheat Sheet

### Old Commands → New Commands

| Old | New |
|-----|-----|
| `pip install -e .` | `uv sync --extra dev` |
| `pip install package` | `uv add package` |
| `pip install --dev package` | `uv add --dev package` |
| `pytest` | `uv run pytest` |
| `black .` | `uv run ruff format .` |
| `flake8 .` | `uv run ruff check .` |
| `python script.py` | `uv run python script.py` |
| `fava ledger/main.bean` | `uv run fava ledger/main.bean` |

### New Development Workflow

1. **Initial setup:**
   ```bash
   # Install uv (one-time)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Clone and setup project
   git clone <repo>
   cd accountant
   uv sync --extra dev
   ```

2. **Running code:**
   ```bash
   # Run any Python command
   uv run python ingestion/runner.py
   uv run fava ledger/main.bean
   ```

3. **Testing:**
   ```bash
   # Run tests
   uv run pytest tests/ -v

   # With coverage
   uv run pytest --cov
   ```

4. **Code quality:**
   ```bash
   # Format code
   uv run ruff format .

   # Check and fix linting issues
   uv run ruff check --fix .

   # Type checking
   uv run mypy .
   ```

5. **Pre-commit hooks:**
   ```bash
   # Install hooks (one-time per clone)
   uv run pre-commit install

   # Run manually
   uv run pre-commit run --all-files
   ```

6. **Adding dependencies:**
   ```bash
   # Add runtime dependency
   uv add pandas

   # Add dev dependency
   uv add --dev pytest-mock
   ```

## What to Delete

You can now **remove** these legacy files (but keep for reference during migration):
- ❌ `setup.py` - Replaced by `pyproject.toml`
- ❌ `requirements.txt` - Replaced by `pyproject.toml` dependencies
- ⚠️ Keep `.gitignore` but updated for `.venv/` and `uv.lock`

## Python Version

Minimum Python version updated to **3.11** (was 3.8) for:
- Better performance
- Modern type hints
- Latest Python features

## Troubleshooting

### "Command not found: uv"
```bash
# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Module not found" errors in tests
```bash
# Resync dependencies
uv sync --extra dev

# Verify installation
uv run python -c "import ingestion; import plugins"
```

### Pre-commit hooks not running
```bash
# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install

# Test manually
uv run pre-commit run --all-files
```

## Documentation

- [uv documentation](https://docs.astral.sh/uv/)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [pre-commit documentation](https://pre-commit.com/)
- [Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
