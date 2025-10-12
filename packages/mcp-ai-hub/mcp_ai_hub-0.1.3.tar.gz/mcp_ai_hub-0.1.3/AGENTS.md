# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/mcp_ai_hub/` (`server.py`, `ai_client.py`, `config.py`, `__init__.py`)
- Tests: `tests/` with shared fixtures in `tests/conftest.py`
- Config template: `config_example.yaml` (copy to `~/.ai_hub.yaml`)
- Packaging & tools: `pyproject.toml` (ruff, mypy, pytest), console script `mcp-ai-hub`
- Docs: `README.md`, `CLAUDE.md`

## Build, Test, and Development Commands
- Setup: `uv sync` and `uv pip install -e ".[dev]"`
- Run server: `uv run mcp-ai-hub [--transport stdio|sse|http] [--config PATH] [--log-level DEBUG]`
- Tests: `uv run pytest`
- Coverage: `uv run pytest --cov=src/mcp_ai_hub --cov-report=term-missing`
- Lint/format: `uv run ruff format . && uv run ruff check .`
- Type check: `uv run mypy src/`

## Coding Style & Naming Conventions
- Python 3.10+, PEP 8, 4-space indent, line length 88 (ruff configured)
- Type-annotate all functions; keep imports sorted (ruff `I`); avoid unused args
- Files/modules use `snake_case`; classes `PascalCase`; constants `UPPER_SNAKE_CASE`

## Testing Guidelines
- Frameworks: pytest, pytest-asyncio, pytest-cov
- Discovery: files `test_*.py` or `*_test.py`; classes `Test*`; functions `test_*`
- Add tests for new behavior and failure paths; use mocks (no real API calls)
- Maintain or increase coverage; HTML report emitted to `htmlcov/`

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`); imperative, present tense
- Keep commits focused; exclude generated artifacts (`htmlcov/`, `.coverage`, `coverage.xml`)
- PRs include: clear summary and rationale, linked issues, reproduction steps or command output, and test plan/results

## Security & Configuration Tips
- Never commit secrets; put real keys only in `~/.ai_hub.yaml` and `chmod 600 ~/.ai_hub.yaml`
- Prefer LiteLM provider/model IDs (e.g., `openai/gpt-4`, `anthropic/claude-3-5-sonnet-20241022`)

## Agent-Specific Instructions
- Treat this file as authoritative across the repo scope
- Keep changes minimal and idiomatic; run `ruff`, `mypy`, and `pytest` before large refactors