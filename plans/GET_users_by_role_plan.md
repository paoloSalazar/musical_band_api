# GET /api/users?role=... Plan (Non-TDD)

Context
- Time reference: 2026-05-15T11:09:14-04:00
- Working directory: /Users/paolosalazar/Projects/python/fastapi/musical_band_api

Purpose
- Implement multi-valued role filtering for GET /api/users while preserving existing behavior when the role parameter is omitted. No TDD approach.

Assumptions
- Current endpoint supports pagination via skip, limit, and optional order_by.
- No role filtering exists today.

API design
- Accept repeated query parameter role (e.g., /api/users/?role=musician&role=auxiliar_musician).
- If role is absent, maintain current behavior.
- If role(s) provided, filter users whose role.name is in the provided set and return paginated results.

Data flow
- Web layer: read roles: List[str] | None from query in get_all endpoint.
- Service layer: extend get_all_paginated(skip, limit, order_by, roles=None) or introduce filtered_get_all_by_roles(roles, skip, limit, order_by).
- Data layer: filter with IN (:roles) on role name; apply skip/limit and order_by in query.

Validation & error handling
- 401 for missing/invalid auth remains unchanged.
- 400 for invalid/unparseable role values (unknown roles).
- 500 for database errors; maintain existing error messaging.

Tests (non-TDD approach)
- API tests validating role filtering behavior:
  - GET /api/users/?role=musician returns only musician users.
  - GET /api/users/?role=musician&role=auxiliar_musician returns users with either role.
  - GET /api/users/?role=invalid_role returns 400 (invalid input).
  - Pagination with role filtering preserves skip/limit behavior.
- Note: Tests should be written to exercise integration points (web/service/data) and reflect real-world usage; not driven by a Test-Driven Development workflow.

Documentation & contract
- Update endpoints.rest with multi-valued role query usage.
- Document behavior and edge cases in project docs.

Backward compatibility & risks
- No change when role param is omitted.
- Monitor performance; rely on DB-side filtering.

Deliverables
- Updated API contract doc (endpoints.rest) and new tests for role filtering.
- Plan file updated for traceability and future reference.

Implementation Status: COMPLETED
- Web layer: Added roles parameter to get_all endpoint.
- Service layer: Added roles parameter and validation for existing roles.
- Data layer: Added roles parameter and SQL filtering using UserRole.name.in_(roles).
- Tests: Added unit tests for single role, multiple roles, invalid role (400), and pagination with roles.
- Docs: Updated endpoints.rest with examples.
- All tests pass, including existing ones.
