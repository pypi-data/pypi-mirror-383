# Changelog

## simtrial-python 0.1.2

### Linting

- Added ruff linter configuration to `pyproject.toml` with popular rule sets
  including pycodestyle, Pyflakes, pyupgrade, flake8-bugbear, flake8-simplify,
  and isort (#10).
- Fixed `ruff check` linting issues such as PEP 585 (#10).

## simtrial-python 0.1.1

### Maintenance

- Added Python 3.14 support and set as default development environment (#7).
- Updated GitHub Actions workflows to use the latest `checkout` and `setup-python` versions (#7).

## simtrial-python 0.1.0

- Increment version number to 0.1.0 to follow semantic versioning
  best practices (#6).

## simtrial-python 0.0.1

### New features

- Added a piecewise exponential sampler that mirrors the R implementation using
  inverse-CDF sampling with reproducibility hooks and type hints (#1).

### Testing

- Added pytest tests with 100% code coverage for the sampler, including
  validation, broadcasting, and RNG behaviors (#1).
- Added deterministic R-generated fixtures (`tests/fixtures/`) to
  cross-check Python draws (#1).
