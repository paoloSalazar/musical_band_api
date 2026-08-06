# Future Fixes and Improvements

## SQLAlchemy Query Optimization and Security

### Observation: Loading Full Objects in Relationships
When using eager loading with `selectinload` for relationships (e.g., `EventMusician.musician` and `User.role`), the entire related objects are loaded by default, including all attributes from the associated tables. This can expose unnecessary data and pose security risks if sensitive fields (e.g., passwords, internal IDs) are included.

### Recommended Fix
Use `load_only` to restrict loaded attributes to only what's needed:
```python
from sqlalchemy.orm import selectinload, load_only

query.options(
    selectinload(EventMusician.musician).load_only(User.id, User.name, User.email).selectinload(User.role).load_only(UserRole.name),
    selectinload(EventMusician.event).load_only(Event.id, Event.name, Event.date)
)
```
- Benefits: Reduces memory usage, improves performance, and enhances security by limiting data exposure.
- Apply to all data access functions where full objects aren't required.

### Additional Considerations
- Regularly audit queries for over-loading.
- Consider using `defer` for lazy-loading sensitive fields if needed.
- Test query performance with `EXPLAIN` or SQLAlchemy's query logging.