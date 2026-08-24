# Logging Improvements Plan

## Analysis: Adding User Context to Logging Records

To add `user_name` and `role` fields to logging records while maintaining the current format, you need context-aware logging using FastAPI middleware and custom formatters.

### Current State (verified in codebase)
- `main.py:4-11` configures logging via `logging.basicConfig()` with format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`, writing to `logs/logs.txt` + console.
- `auth/auth.py:141` `get_current_user` decodes the JWT (`decode_access_token`) and looks up `UserRole` from the DB by `role_id` (`auth/auth.py:187-191`), returning `id`, `email` (`sub`), `role` (DB name), `permissions`, `role_id`.
- Token payload carries `sub` (email), `user_id`, `role_id` (`services/auth.py:53`).
- Every `data/*.py` and `services/*.py` module uses `logger = logging.getLogger(__name__)`.
- Logging setup runs **before** other imports in `main.py:3`, so the config must stay import-safe.
- Tests use `pytest` + `pytest-mock` (`mocker`) + `pytest-asyncio` (see `tests/unit/web/test_user.py`). No `TestClient`/`httpx` usage in tests — functions are tested by calling them directly with mocked deps. `pytest.ini` sets `TESTING=1` (SQLite in-memory).

## Required Changes (Phased, TDD)

### Phase 1 — Context Management Setup
- **Create** `utils/logging_context.py`:
  - `user_name_context: ContextVar[str] = ContextVar("user_name", default="anonymous")`
  - `user_role_context: ContextVar[str] = ContextVar("user_role", default="None")`
  - Helpers: `set_user_context(user_name, user_role)`, `clear_user_context()`, `reset_user_context()` (alias used by middleware/auth), `get_user_name()`, `get_user_role()`
- **TDD**: `tests/unit/utils/test_logging_context.py` — defaults, set+get, clear/reset to defaults.
- **No dependencies** on other phases; foundational.

### Phase 2 — Custom Logging Formatter
- **Create** `utils/custom_formatter.py`:
  - `ContextAwareFormatter(logging.Formatter)` overriding `format()` to read context vars and inject `record.user_name` / `record.user_role` (fallback to `'anonymous'` / `'None'`)
  - Expose `LOG_FORMAT` class constant: `'%(asctime)s - %(name)s - %(levelname)s - %(user_name)s - %(user_role)s - %(message)s'` (centralized so `main.py` and its tests share one source of truth)
- **TDD**: `tests/unit/utils/test_custom_formatter.py` — formatter output includes user/role, uses defaults when no context, `LOG_FORMAT` constant matches target string.
- Depends on Phase 1.

### Phase 3 — Logging Configuration Update
- **Create** `utils/logging_config.py` with `configure_logging()`:
  - Manual `FileHandler('logs/logs.txt')` + `StreamHandler` (replaces `logging.basicConfig`)
  - Uses `ContextAwareFormatter(LOG_FORMAT)` for both handlers, level `INFO`
  - Re-applies SQLAlchemy/watchfiles suppression (`logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)` etc.)
- **Modify** `main.py`: replace `logging.basicConfig(...)` block (`main.py:4-19`) with a call to `configure_logging()` (keep before other imports to preserve the import-ordering constraint).
- **TDD**: `tests/unit/utils/test_logging_config.py` — formatter uses `LOG_FORMAT` with `%(user_name)s`/`%(user_role)s`, SQLAlchemy logger suppressed, root level `INFO`.
- Depends on Phase 2.

### Phase 4 — Authentication Integration
- **Modify** `auth/auth.py` `get_current_user` (`auth/auth.py:141`):
  - After building the return dict (after `auth/auth.py:198`), call `set_user_context(email, role_name)`
  - At the token-invalid guard (`auth/auth.py:176-181`), call `reset_user_context()` before raising `HTTPException`
  - For the no-`role_id` branch (`auth/auth.py:184-191`), pass `'None'` as the role
- **TDD**: `tests/unit/auth/test_log_context.py` — valid token sets context to (email, role_name); invalid token raises 401 + resets context to defaults; no-role-id token sets role to `'None'`.
- Depends on Phase 1. `get_current_user` already imports `get_db` + `UserRole`, so no new DB path is needed.

### Phase 5 — Request Middleware (context reset)
- **Modify** `main.py`: add `@app.middleware("http")` that calls `reset_user_context()` at **request start** and `clear_user_context()` after `await call_next(request)` (request end) — preventing `contextvar` leakage between requests on the same async task.
- **Decision**: the middleware does **NOT** decode JWT or set user context. That work is already done authoritatively in `get_current_user` (Phase 4). Decoding again here would duplicate the JWT decode + DB role lookup. Endpoints that bypass `get_current_user` are unauthenticated by definition, so `anonymous`/`None` is the correct value for them.
- **TDD**: covered by the `reset_user_context`/`clear_user_context` unit tests in Phase 1 (no `TestClient` in this repo; see Convention note below).
- Depends on Phase 1 (helpers exist) + Phase 3 (app configured).

## Execution Order

```
1 → 2 → 3 → 4 → 5
```

After each phase run:
```bash
pytest tests/unit/utils/ tests/unit/auth/ -q   # targeted
ruff check utils/ auth/ main.py               # lint
```
Final verification: `pytest -q` (full suite) + confirm a new log line reads e.g.:
```
2026-... - services.user - INFO - admin@example.com - admin - Retrieved user with email admin@example.com
```

## Key Considerations

- **Performance**: `contextvar` access is fast; middleware reset is negligible. No extra JWT decode or DB lookup in the request path.
- **Thread/Async Safety**: `contextvars` isolate contexts per asyncio task in FastAPI — no manual threading concerns.
- **Fallback Values**: Unauthenticated requests automatically show `anonymous`/`None` via context defaults.
- **No dependency cycles**: `utils/logging_context.py` imports only stdlib; `utils/custom_formatter.py` imports only `logging_context`. `auth/auth.py` imports `logging_context` (no cycle: `logging_context` does not import `auth`).
- **Testing convention**: No `TestClient`/`httpx` usage exists in the repo. Follow the established pattern of calling functions directly with mocked deps (`pytest-mock` `mocker`, `@pytest.mark.asyncio` for async). The middleware reset logic is therefore unit-tested via the extracted `reset_user_context`/`clear_user_context` helpers rather than an end-to-end HTTP test.

## Key Design Refinements (vs. original draft)

- `basicConfig` is **not** left inline; it is wrapped in `utils/logging_config.py:configure_logging()` so it is unit-tested.
- The format string is centralized as `ContextAwareFormatter.LOG_FORMAT` (single source of truth; testable).
- `reset_user_context()` helper is added (vs. the original "clear") — reusable by both the failure path (Phase 4) and the middleware (Phase 5).
- The middleware's role is reduced to **reset only** — it does not decode JWT, avoiding duplicate JWT+DB work already performed in `get_current_user`.

## Files To Create / Modify

| Action | File | Phase |
|---|---|---|
| Create | `utils/logging_context.py` | 1 |
| Create | `utils/custom_formatter.py` | 2 |
| Create | `utils/logging_config.py` | 3 |
| Modify | `main.py` (call `configure_logging` + middleware) | 3, 5 |
| Modify | `auth/auth.py` (`get_current_user`) | 4 |
| Create | `tests/unit/utils/test_logging_context.py` | 1, 5 |
| Create | `tests/unit/utils/test_custom_formatter.py` | 2 |
| Create | `tests/unit/utils/test_logging_config.py` | 3 |
| Create | `tests/unit/auth/test_log_context.py` | 4 |
