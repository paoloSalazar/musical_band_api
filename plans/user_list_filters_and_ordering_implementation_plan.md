# User List Filters and Ordering Improvements Implementation Plan

## Overview
This plan outlines the implementation of enhanced filtering and ordering capabilities for the GET users endpoint (`GET /api/users/`).

**Current limitations**:
- Only `roles` filtering is supported (multi-value).
- `order_by` only supports direct columns on the `User` model (e.g. `name`, `email`, `created_at`).
- No support for filtering or ordering by `name`, `lastname`, `email`, or `role`.

**Goals**:
- Add filter parameters: `name`, `lastname` (or `last_name`), `email`, `role`
- Improve `order_by` to support: `name`, `lastname`, `email`, `role`
- Maintain backward compatibility
- Follow existing patterns in the codebase (pagination, role validation, etc.)

## Current Behavior Review

### Web Layer (`web/user.py`)
- Endpoint: `GET /` (line 162)
- Parameters:
  - `skip: int = 0`
  - `limit: int = 20`
  - `order_by: str | None = None`
  - `roles: list[str] | None = Query(None)`
- Calls `service.get_all_paginated(...)`
- Returns `UserPaginationResponse`

### Service Layer (`services/user.py`)
- `get_all_paginated(skip, limit, order_by, roles)`
- Validates provided roles against existing roles in DB
- Delegates to `data.get_all_paginated`
- Transforms results into `UserResponseWithRole` (includes `role` name via relationship)

### Data Layer (`data/user.py`)
- `get_all_paginated(...)`:
  - Always joins `User.role` via `selectinload`
  - Filters on roles using: `User.role.has(UserRole.name.in_(roles))`
  - Ordering: `getattr(User, order_by, None)` — **only direct User attributes**
  - No text search / partial matching
  - Returns `(users, total)`

### Model (`models/user.py`)
- Fields: `name`, `lastname`, `email`, `role_id`
- Relationship: `role` → `UserRole`

### Schema (`schemas/user.py`)
- `UserResponseWithRole` includes `name`, `lastname`, `email`, `role`
- `UserPaginationResponse` wraps paginated results

### Tests
- Good coverage for current `roles` filtering and basic `order_by`
- Tests exist in:
  - `tests/unit/web/test_user.py`
  - `tests/unit/services/test_user.py`
  - `tests/unit/data/test_user.py`

### Known Gaps
- Cannot filter by partial name / lastname / email
- Cannot order by `role` (relationship field)
- No support for case-insensitive search
- No direction control for `order_by` (ASC/DESC)

## Requirements

### New Filter Parameters (on `GET /api/users/`)
- `name` (string, optional) — partial, case-insensitive match on `User.name`
- `lastname` (string, optional) — partial, case-insensitive match on `User.lastname`
- `email` (string, optional) — partial, case-insensitive match on `User.email`
- `role` (string, optional) — exact match on role name (single value). Keep `roles` for backward compatibility or replace?

**Recommendation**: Add `role` (singular) for exact match. Keep `roles` (plural) for multi-select if needed, or deprecate in favor of repeated `role` params.

### Enhanced Ordering
- Support `order_by=name`
- Support `order_by=lastname`
- Support `order_by=email`
- Support `order_by=role` (order by `role.name`)
- Consider future direction support (e.g. `order_by=name:desc` or separate `order_dir` param)

### Non-Functional
- Maintain pagination behavior
- Keep performance acceptable (use proper indexes if needed)
- Full test coverage (TDD where possible)
- Update `endpoints.rest` and API documentation

## Design Decisions

1. **Matching Strategy**:
   - Text fields (`name`, `lastname`, `email`): Use `ilike('%value%')` for partial case-insensitive search.
   - `role`: Exact match (`==`).

2. **Parameter Naming**:
   - Use `lastname` to match the database column (avoid `last_name` for consistency with existing code).

3. **Ordering on Relationship**:
   - Will require a join or `order_by(User.role.property.mapper.class_.name)` when `order_by=role`.

4. **Backward Compatibility**:
   - All new parameters are optional.
   - Existing `roles` parameter remains supported.

5. **Layer Responsibilities**:
   - **Web**: Parse and pass new query params
   - **Service**: Validate (e.g. role exists), business rules
   - **Data**: Build dynamic query with filters + ordering

## Implementation Plan

### Phase 1: Data Layer Enhancements
- Extend `data/user.py:get_all_paginated(...)` signature to accept new filter parameters:
  ```python
  def get_all_paginated(
      skip: int = 0,
      limit: int = 20,
      order_by: str | None = None,
      roles: list[str] | None = None,
      name: str | None = None,
      lastname: str | None = None,
      email: str | None = None,
      role: str | None = None   # singular for exact match
  )
  ```
- Implement dynamic filtering using `ilike` for text fields.
- Improve ordering logic to support `role` (join handling).
- Update total count query accordingly.
- Add unit tests in `tests/unit/data/test_user.py`

**Estimated Time**: 1 day

### Phase 2: Service Layer
- Update `services/user.py:get_all_paginated(...)` to accept and forward new parameters.
- Add validation for new `role` parameter (similar to existing `roles` validation).
- Update logging and docstrings.
- Add unit tests in `tests/unit/services/test_user.py`

**Estimated Time**: 0.5 day

### Phase 3: Web Layer & API Contract
- Update `web/user.py:get_all(...)`:
  - Add new query parameters using `Query(...)`
  - Pass them to service
- Update docstring and OpenAPI description
- Consider whether to keep `roles` + add `role`, or unify
- Update `endpoints.rest` with new example calls
- Add integration-style tests in `tests/unit/web/test_user.py`

**Estimated Time**: 0.5 day

### Phase 4: Testing & Validation
- Expand existing test classes for new filter combinations
- Test ordering by `role`
- Test partial matching (case insensitivity)
- Test invalid role values (should return 400)
- Performance test with larger datasets (optional)
- Ensure all existing tests continue to pass

**Estimated Time**: 1 day

### Phase 5: Documentation & Polish
- Update `README.md` if user listing is documented
- Update any internal docs
- Consider adding `search` as a future unified search param (post-MVP)
- Add direction support for `order_by` if desired (e.g. `order_by=name:desc`)

**Estimated Time**: 0.5 day

## Potential Risks & Mitigations

- **Performance**: Multiple `ilike` filters on large tables → consider full-text search or trigram indexes later.
- **Role ordering**: Requires correct join handling to avoid duplicates or Cartesian products.
- **Parameter name conflict**: `role` vs existing `roles` → document clearly.
- **Timezone / created_at ordering**: Already supported indirectly.

## Success Criteria

- Users can filter by partial name, lastname, email
- Users can filter and order by role name
- `order_by=role` works correctly
- All new functionality is covered by tests
- No breaking changes to existing clients
- Response time remains acceptable

## Timeline Estimate

- Phase 1 (Data): 1 day
- Phase 2 (Service): 0.5 day
- Phase 3 (Web): 0.5 day
- Phase 4 (Testing): 1 day
- Phase 5 (Docs): 0.5 day

**Total**: ~3.5 days

## Team Requirements
- Backend developer familiar with SQLAlchemy dynamic queries
- QA for filter edge cases

---

**Next Step Recommendation**:  
Review this plan. Once approved, we can start with Phase 1 (Data Layer) using TDD. 

Would you like any adjustments to the scope, parameter names, matching strategy (partial vs exact), or priority of phases before we begin implementation?
