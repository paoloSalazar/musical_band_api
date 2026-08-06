================================================================================
                 MUSICAL BAND API - ADMIN ENDPOINTS DOCUMENTATION
================================================================================

Base URL: http://localhost:8000/api

Authorization:
    - All admin endpoints require JWT Bearer token in Authorization header
    - Admin role is required for all operations
    - User roles also require specific permissions (see each endpoint)

================================================================================
                           1. USER ROLES (ADMIN ONLY)
================================================================================

Prefix: /api/user-roles

Authorization: Admin role + specific permissions
    - read:user_roles    - For GET operations
    - write:user_roles   - For POST/PATCH operations
    - delete:user_roles  - For DELETE operations

--------------------------------------------------------------------------------
1.1 GET /api/user-roles/
--------------------------------------------------------------------------------
Description: Retrieve all user roles from the database.
Access:      Admin role + read:user_roles permission

Response (200 OK):
    [
        {
            "id": integer,
            "name": "string",
            "description": "string|null"
        },
        ...
    ]

Error Responses:
    500 - Internal server error

--------------------------------------------------------------------------------
1.2 GET /api/user-roles/{name}
--------------------------------------------------------------------------------
Description: Retrieve a user role by its name.
Access:      Admin role + read:user_roles permission

Path Parameters:
    name (string, required) - The unique name of the role

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    404 - User role not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.3 POST /api/user-roles/
--------------------------------------------------------------------------------
Description: Create a new user role.
Access:      Admin role + write:user_roles permission

Request Body (JSON):
    {
        "name": "string",           // Role name (must be unique)
        "description": "string|null" // Optional role description
    }

Response (201 Created):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    409 - Role already exists
    500 - Internal server error

--------------------------------------------------------------------------------
1.4 PATCH /api/user-roles/
--------------------------------------------------------------------------------
Description: Update a user role's description.
Access:      Admin role + read:user_roles + write:user_roles permissions

Request Body (JSON):
    {
        "name": "string",           // Role name (for identification)
        "description": "string|null" // New description
    }

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    404 - Role not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.5 PUT /api/user-roles/
--------------------------------------------------------------------------------
Description: Replace an existing user role's data completely.
Access:      Admin role + read:user_roles + write:user_roles permissions

Request Body (JSON):
    {
        "id": integer,              // Role ID (required for identification)
        "name": "string",           // New role name
        "description": "string|null" // New description
    }

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    404 - Role not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.6 DELETE /api/user-roles/{name}
--------------------------------------------------------------------------------
Description: Delete a user role by name.
Access:      Admin role + delete:user_roles permission

Path Parameters:
    name (string, required) - The name of the role to delete

Response (200 OK):
    true

Error Responses:
    404 - Role not found
    500 - Internal server error


================================================================================
                          2. PERMISSIONS (ADMIN ONLY)
================================================================================

Prefix: /api/permissions

Authorization: Admin role required (no additional permissions needed)

--------------------------------------------------------------------------------
2.1 GET /api/permissions/
--------------------------------------------------------------------------------
Description: Retrieve all permissions from the database.
Access:      Admin role

Response (200 OK):
    [
        {
            "id": integer,
            "name": "string",
            "description": "string|null"
        },
        ...
    ]

Error Responses:
    500 - Internal server error

--------------------------------------------------------------------------------
2.2 GET /api/permissions/{permission_id}
--------------------------------------------------------------------------------
Description: Retrieve a permission by its ID.
Access:      Admin role

Path Parameters:
    permission_id (integer, required) - The unique identifier of the permission

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    404 - Permission not found
    500 - Internal server error

--------------------------------------------------------------------------------
2.3 POST /api/permissions/
--------------------------------------------------------------------------------
Description: Create a new permission.
Access:      Admin role

Request Body (JSON):
    {
        "name": "string",           // Permission name (must be unique)
                                    // Convention: "action:resource"
        "description": "string|null" // Optional permission description
    }

Example:
    {
        "name": "read:events",
        "description": "Permission to read event information"
    }

Response (201 Created):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    409 - Permission already exists
    500 - Internal server error

--------------------------------------------------------------------------------
2.4 PATCH /api/permissions/{permission_id}
--------------------------------------------------------------------------------
Description: Update an existing permission.
Access:      Admin role

Path Parameters:
    permission_id (integer, required) - The ID of the permission to update

Request Body (JSON):
    {
        "name": "string|null",           // Optional: New permission name
        "description": "string|null"    // Optional: New description
    }

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "description": "string|null"
    }

Error Responses:
    404 - Permission not found
    500 - Internal server error

--------------------------------------------------------------------------------
2.5 DELETE /api/permissions/{permission_id}
--------------------------------------------------------------------------------
Description: Delete a permission from the database.
Access:      Admin role

Path Parameters:
    permission_id (integer, required) - The ID of the permission to delete

Response (200 OK):
    true

Error Responses:
    404 - Permission not found
    500 - Internal server error


================================================================================
                     3. ROLE-PERMISSION ASSIGNMENTS (ADMIN ONLY)
================================================================================

Prefix: /api/permissions

Authorization: Admin role required

--------------------------------------------------------------------------------
3.1 GET /api/permissions/{role_name}/permissions
--------------------------------------------------------------------------------
Description: Retrieve all permissions assigned to a specific role.
Access:      Admin role

Path Parameters:
    role_name (string, required) - The unique name of the role

Response (200 OK):
    [
        {
            "id": integer,
            "name": "string",
            "description": "string|null"
        },
        ...
    ]

Example Request:
    GET /api/permissions/admin/permissions

Error Responses:
    404 - Role not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.2 GET /api/permissions/role/{permission_name}/roles
--------------------------------------------------------------------------------
Description: Retrieve all roles that have a specific permission.
Access:      Admin role

Path Parameters:
    permission_name (string, required) - The unique name of the permission

Response (200 OK):
    [
        {
            "id": integer,
            "name": "string",
            "description": "string|null"
        },
        ...
    ]

Example Request:
    GET /api/permissions/role/write:users/roles

Error Responses:
    404 - Permission not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.3 POST /api/permissions/roles/assign
--------------------------------------------------------------------------------
Description: Assign a permission to a role.
Access:      Admin role

Query Parameters:
    permission_name (string, required) - The name of the permission to assign
    role_name (string, required) - The name of the role to assign the permission to

Response (200 OK):
    {
        "success": true,
        "message": "Permission 'permission_name' assigned to role 'role_name'"
    }

Example Request:
    POST /api/permissions/roles/assign?permission_name=read:events&role_name=admin

Error Responses:
    404 - Permission or role not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.4 POST /api/permissions/roles/remove
--------------------------------------------------------------------------------
Description: Remove a permission from a role.
Access:      Admin role

Query Parameters:
    permission_name (string, required) - The name of the permission to remove
    role_name (string, required) - The name of the role to remove the permission from

Response (200 OK):
    {
        "success": true,
        "message": "Permission 'permission_name' removed from role 'role_name'"
    }

Example Request:
    POST /api/permissions/roles/remove?permission_name=write:users&role_name=moderator

Error Responses:
    404 - Permission or role not found
    500 - Internal server error


================================================================================
                         4. PERMISSION NAMING CONVENTION
================================================================================

Permissions follow the "action:resource" naming convention:

Common Actions:
    - read    - View/retrieve data
    - write   - Create and update data
    - delete  - Remove data
    - manage  - Full control

Common Resources:
    - users       - User management
    - user_roles  - Role management
    - permissions - Permission management
    - events      - Event management

Example Permissions:
    - read:users
    - write:users
    - delete:users
    - read:user_roles
    - write:user_roles
    - delete:user_roles


================================================================================
                              5. HTTP STATUS CODES
================================================================================

200 OK                  - Request succeeded
201 Created            - Resource successfully created
401 Unauthorized       - Authentication required or invalid credentials
403 Forbidden          - Insufficient permissions (not admin)
404 Not Found          - Resource does not exist
409 Conflict           - Resource already exists
500 Internal Server Error - Server-side error


================================================================================
                                 END OF DOCUMENTATION
================================================================================
