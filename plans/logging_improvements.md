# Logging Improvements Plan

## Analysis: Adding User Context to Logging Records

To add `user_name` and `role` fields to logging records while maintaining the current format, you'll need to implement context-aware logging using FastAPI middleware and custom formatters.

## Required Changes

### 1. **Context Management Setup**
- Add `contextvars` import and create context variables in a new module (e.g., `utils/logging_context.py`):
  ```python
  import contextvars
  user_name_context: contextvars.ContextVar[str] = contextvars.ContextVar('user_name', default='anonymous')
  user_role_context: contextvars.ContextVar[str] = contextvars.ContextVar('user_role', default='None')
  ```

### 2. **FastAPI Middleware**
- Create middleware in `main.py` or a separate module to extract user info from JWT tokens on each request:
  - Decode JWT from Authorization header (if present)
  - Extract user name from token payload (using `sub` field for email)
  - Extract role from database lookup or token
  - Set context variables: `user_name_context.set(email)` and `user_role_context.set(role_name)`
  - For unauthenticated requests, context defaults to 'anonymous'/'None'

### 3. **Custom Logging Formatter**
- Create a custom formatter class (e.g., in `utils/custom_formatter.py`) that extends `logging.Formatter`:
  - Override `format()` method to access context variables
  - Add `%(user_name)s` and `%(user_role)s` to the format string
  - Use `contextvars.copy_context().run()` or direct access to get current context values

### 4. **Update Logging Configuration**
- Modify `main.py` logging setup:
  - Import the custom formatter
  - Replace `logging.basicConfig()` with manual handler configuration
  - Use the custom formatter for both file and stream handlers
  - Update format string to: `'%(asctime)s - %(name)s - %(levelname)s - %(user_name)s - %(user_role)s - %(message)s'`

### 5. **Authentication Integration**
- Modify `auth/auth.py` `get_current_user()` to also set context variables when user is successfully authenticated
- Ensure context is set early in the request lifecycle

## Key Considerations

- **Performance**: Context variable access is fast but middleware adds small overhead per request
- **Thread Safety**: `contextvars` handles async contexts properly in FastAPI
- **Fallback Values**: Unauthenticated requests automatically show 'anonymous'/'None' via context defaults
- **JWT Decoding**: Middleware needs to duplicate some JWT logic to avoid dependency cycles
- **Database Access**: Role lookup requires database query in middleware (consider caching)

This approach ensures user context is available to all log statements within a request, whether from web handlers, services, or data layers.