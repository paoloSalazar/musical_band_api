================================================================================
                    MUSICAL BAND API - ENDPOINT DOCUMENTATION
================================================================================

Base URL: http://localhost:8000/api

Authentication:
    - Most endpoints require JWT Bearer token in Authorization header
    - Format: Authorization: Bearer <token>
    - Use POST /api/users/login to obtain a token

================================================================================
                              1. USERS ENDPOINTS
================================================================================

Prefix: /api/users

--------------------------------------------------------------------------------
1.1 User Login
--------------------------------------------------------------------------------
Endpoint:    POST /api/users/login
Description: Authenticate a user and return a JWT access token.
Access:      Public (no authentication required)

Request Body (JSON):
    {
        "email": "string",      // User's email address
        "password": "string"     // User's password
    }

Response (200 OK):
    {
        "access_token": "string",    // JWT token
        "token_type": "bearer"
    }

Error Responses:
    401 - Invalid email or password
    500 - Internal server error

--------------------------------------------------------------------------------
1.2 Get Current User
--------------------------------------------------------------------------------
Endpoint:    GET /api/users/me
Description: Get current user information including roles and permissions.
Access:      Requires authentication (Bearer token)

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "lastname": "string",
        "second_lastname": "string|null",
        "email": "string",
        "role": "string",           // Role name (e.g., "admin", "user")
        "role_id": integer,
        "permissions": ["string"]   // List of permission names
    }

Error Responses:
    401 - Authorization header missing / Invalid or expired token
    404 - User not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.3 Get All Users
--------------------------------------------------------------------------------
Endpoint:    GET /api/users/
Description: Retrieve all users from the database.
Access:      Requires authentication (Bearer token)

Response (200 OK):
    [
        {
            "id": integer,
            "name": "string",
            "lastname": "string",
            "second_lastname": "string|null",
            "email": "string",
            "role_id": integer
        },
        ...
    ]

Error Responses:
    500 - Internal server error

--------------------------------------------------------------------------------
1.4 Get User by Email
--------------------------------------------------------------------------------
Endpoint:    GET /api/users/{email}
Description: Retrieve a user by their email address.
Access:      Requires authentication (Bearer token)

Path Parameters:
    email (string, required) - The email address of the user

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "lastname": "string",
        "second_lastname": "string|null",
        "email": "string",
        "role_id": integer
    }

Error Responses:
    404 - User not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.5 Create New User
--------------------------------------------------------------------------------
Endpoint:    POST /api/users/
Description: Create a new user account.
Access:      Public (no authentication required)

Request Body (JSON):
    {
        "name": "string",           // User's first name
        "lastname": "string",        // User's last name
        "second_lastname": "string|null",  // Optional second last name
        "email": "string",           // User's email (must be unique)
        "password": "string",        // User's password
        "role_id": integer           // ID of the role to assign
    }

Response (201 Created):
    {
        "id": integer,
        "name": "string",
        "lastname": "string",
        "second_lastname": "string|null",
        "email": "string",
        "role_id": integer
    }

Error Responses:
    409 - User already exists (email conflict)
    500 - Internal server error

--------------------------------------------------------------------------------
1.6 Update User Profile
--------------------------------------------------------------------------------
Endpoint:    PATCH /api/users/
Description: Update an existing user's profile.
Access:      Requires authentication (Bearer token)

Request Body (JSON):
    {
        "name": "string|null",           // Optional: User's first name
        "lastname": "string|null",        // Optional: User's last name
        "second_lastname": "string|null", // Optional: Second last name
        "email": "string|null",           // Optional: User's email
        "role_id": "integer|null"        // Optional: Role ID
    }

Response (200 OK):
    {
        "id": integer,
        "name": "string",
        "lastname": "string",
        "second_lastname": "string|null",
        "email": "string",
        "role_id": integer
    }

Error Responses:
    404 - User not found
    500 - Internal server error

--------------------------------------------------------------------------------
1.7 Change User Password
--------------------------------------------------------------------------------
Endpoint:    PATCH /api/users/{email}/password
Description: Change a user's password. Requires verification of current password.
Access:      Requires authentication (Bearer token)

Path Parameters:
    email (string, required) - The email of the user

Request Body (JSON):
    {
        "current_password": "string",  // User's current password
        "new_password": "string"      // New password to set
    }

Response (200 OK):
    {
        "message": "Password updated successfully"
    }

Error Responses:
    401 - Current password is incorrect
    404 - User not found
    500 - Internal server error


================================================================================
                           2. USER ROLES ENDPOINTS
================================================================================

Prefix: /api/user-roles

Authorization:
    - All endpoints require Admin role AND specific permissions:
        - read:user_roles    - For reading operations
        - write:user_roles   - For creating/updating operations
        - delete:user_roles  - For delete operations

--------------------------------------------------------------------------------
2.1 Get All User Roles
--------------------------------------------------------------------------------
Endpoint:    GET /api/user-roles/
Description: Retrieve all user roles from the database.
Access:      Requires Admin role AND read:user_roles permission

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
2.2 Get User Role by Name
--------------------------------------------------------------------------------
Endpoint:    GET /api/user-roles/{name}
Description: Retrieve a user role by its name.
Access:      Requires Admin role AND read:user_roles permission

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
2.3 Create New User Role
--------------------------------------------------------------------------------
Endpoint:    POST /api/user-roles/
Description: Create a new user role.
Access:      Requires Admin role AND write:user_roles permission

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
2.4 Update User Role Description (PATCH)
--------------------------------------------------------------------------------
Endpoint:    PATCH /api/user-roles/
Description: Update a user role's description.
Access:      Requires Admin role AND read:user_roles + write:user_roles permissions

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
2.5 Replace User Role Data (PUT)
--------------------------------------------------------------------------------
Endpoint:    PUT /api/user-roles/
Description: Replace an existing user role's data completely.
Access:      Requires Admin role AND read:user_roles + write:user_roles permissions

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
2.6 Delete User Role
--------------------------------------------------------------------------------
Endpoint:    DELETE /api/user-roles/{name}
Description: Delete a user role by name.
Access:      Requires Admin role AND delete:user_roles permission

Path Parameters:
    name (string, required) - The name of the role to delete

Response (200 OK):
    true

Error Responses:
    404 - Role not found
    500 - Internal server error


================================================================================
                          3. PERMISSIONS ENDPOINTS
================================================================================

Prefix: /api/permissions

Authorization:
    - All endpoints require Admin role (no additional permissions needed)

--------------------------------------------------------------------------------
3.1 Get All Permissions
--------------------------------------------------------------------------------
Endpoint:    GET /api/permissions/
Description: Retrieve all permissions from the database.
Access:      Requires Admin role

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
3.2 Get Permission by ID
--------------------------------------------------------------------------------
Endpoint:    GET /api/permissions/{permission_id}
Description: Retrieve a permission by its ID.
Access:      Requires Admin role

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
3.3 Create New Permission
--------------------------------------------------------------------------------
Endpoint:    POST /api/permissions/
Description: Create a new permission.
Access:      Requires Admin role

Request Body (JSON):
    {
        "name": "string",           // Permission name (must be unique)
                                    // Convention: "action:resource" (e.g., "read:users")
        "description": "string|null" // Optional permission description
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
3.4 Update Permission
--------------------------------------------------------------------------------
Endpoint:    PATCH /api/permissions/{permission_id}
Description: Update an existing permission.
Access:      Requires Admin role

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
3.5 Delete Permission
--------------------------------------------------------------------------------
Endpoint:    DELETE /api/permissions/{permission_id}
Description: Delete a permission from the database.
Access:      Requires Admin role

Path Parameters:
    permission_id (integer, required) - The ID of the permission to delete

Response (200 OK):
    true

Error Responses:
    404 - Permission not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.6 Get Permissions for a Role
--------------------------------------------------------------------------------
Endpoint:    GET /api/permissions/{role_name}/permissions
Description: Retrieve all permissions for a specific role.
Access:      Requires Admin role

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

Error Responses:
    404 - Role not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.7 Get Roles for a Permission
--------------------------------------------------------------------------------
Endpoint:    GET /api/permissions/role/{permission_name}/roles
Description: Retrieve all roles that have a specific permission.
Access:      Requires Admin role

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

Error Responses:
    404 - Permission not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.8 Assign Permission to Role
--------------------------------------------------------------------------------
Endpoint:    POST /api/permissions/roles/assign?permission_name={permission_name}&role_name={role_name}
Description: Assign a permission to a role.
Access:      Requires Admin role

Query Parameters:
    permission_name (string, required) - The name of the permission to assign
    role_name (string, required) - The name of the role to assign the permission to

Response (200 OK):
    {
        "success": true,
        "message": "Permission 'permission_name' assigned to role 'role_name'"
    }

Error Responses:
    404 - Permission or role not found
    500 - Internal server error

--------------------------------------------------------------------------------
3.9 Remove Permission from Role
--------------------------------------------------------------------------------
Endpoint:    POST /api/permissions/roles/remove?permission_name={permission_name}&role_name={role_name}
Description: Remove a permission from a role.
Access:      Requires Admin role

Query Parameters:
    permission_name (string, required) - The name of the permission to remove
    role_name (string, required) - The name of the role to remove the permission from

Response (200 OK):
    {
        "success": true,
        "message": "Permission 'permission_name' removed from role 'role_name'"
    }

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
    - manage  - Full control (read + write + delete)

Common Resources:
    - users      - User management
    - user_roles - Role management
    - permissions - Permission management
    - events     - Event management

Example Permissions:
    - read:users
    - write:users
    - delete:users
    - read:user_roles
    - write:user_roles
    - delete:user_roles
    - read:permissions
    - write:permissions
    - delete:permissions


================================================================================
                              5. HTTP STATUS CODES
================================================================================

200 OK                  - Request succeeded (GET, PATCH, PUT)
201 Created            - Resource successfully created (POST)
400 Bad Request        - Invalid request format or parameters
401 Unauthorized       - Authentication required or invalid credentials
403 Forbidden          - Insufficient permissions (wrong role)
404 Not Found          - Resource does not exist
409 Conflict           - Resource already exists (duplicate)
500 Internal Server Error - Server-side error


================================================================================
                                 END OF DOCUMENTATION
================================================================================
