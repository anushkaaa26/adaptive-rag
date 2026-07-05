# Verification Checklist

Use this before considering a change complete.

## Functionality
- [ ] `pytest` passes locally
- [ ] `python -m py_compile` (or equivalent) succeeds on all changed files
- [ ] New/changed endpoints tested manually via `/docs` (Swagger UI)
- [ ] Streamlit pages load without errors against a running backend

## Code Quality
- [ ] `flake8 src/` has no new warnings
- [ ] New functions have docstrings and type hints
- [ ] No secrets or API keys committed (check against `.gitignore`)

## RAG Pipeline Specific
- [ ] New/changed graph nodes are registered in `graph_builder.py`
- [ ] Conditional edges have all branches covered (no dangling states)
- [ ] Retry/loop conditions have a bounded exit (no infinite loops)

## Docs
- [ ] README.md updated if setup steps changed
- [ ] `.env.example` updated if new environment variables were added
