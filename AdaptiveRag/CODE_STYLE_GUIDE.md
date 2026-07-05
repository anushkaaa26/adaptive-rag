# Code Style Guide

## Python
- Follow PEP 8; run `flake8 src/` before committing.
- Use type hints on all public function signatures.
- Add a docstring to every module, class, and function describing its purpose.
- Prefer `pathlib`/f-strings over older string formatting.
- Keep functions focused: one responsibility per function, especially inside
  `src/rag/nodes.py` where each function is a single LangGraph node.

## Imports
- Group imports: standard library, third-party, then local (`src.*`), separated
  by a blank line.
- Avoid wildcard imports.

## Naming
- Modules and functions: `snake_case`.
- Classes and Pydantic models: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE` (e.g. `MAX_RETRIES`).

## Error Handling
- Catch specific exceptions where possible; use `except Exception as exc` only
  at API/route boundaries, and always log with `logger.exception(...)`.
- Raise `HTTPException` with an appropriate status code from route handlers,
  never let raw exceptions bubble up to the client.

## Tests
- New logic in `src/tools/`, `src/models/`, or other pure-function modules
  should have a corresponding test in `tests/`.
- Tests that require live external services (OpenAI, Qdrant, MongoDB) should
  be mocked or skipped by default; only pure-function/unit tests run in CI.

## Commit Messages
- Use conventional prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
  `chore:`.
