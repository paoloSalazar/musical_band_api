import logging
from fastapi import APIRouter, HTTPException, Depends
import services.permission as service
from schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate, RolePermissionCreate
from exceptions import DatabaseError, NotFoundError, ConflictError
from auth.auth import get_current_user
from auth.roles import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/permissions")


# ============================================
# Permission CRUD Endpoints (Admin Only)
# ============================================


@router.get("/", dependencies=[Depends(require_admin)])
def get_all() -> list[PermissionResponse]:
    """Get all permissions (Admin only)"""
    try:
        permissions = service.get_all()
        logger.info(f"API request: Retrieved {len(permissions)} permissions")
        return permissions
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{permission_id}", dependencies=[Depends(require_admin)])
def get_one(permission_id: int) -> PermissionResponse:
    """Get a permission by ID (Admin only)"""
    try:
        permission = service.get_one(permission_id)
        if not permission:
            raise NotFoundError(f"Permission with ID {permission_id} not found")
        logger.info(f"API request: Retrieved permission {permission_id}")
        return permission
    except NotFoundError as e:
        logger.warning(f"Permission {permission_id} not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_one: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", dependencies=[Depends(require_admin)])
def create(permission: PermissionCreate) -> PermissionResponse:
    """Create a new permission (Admin only)"""
    try:
        created_permission = service.create(permission)
        logger.info(f"API request: Created permission '{created_permission.name}'")
        return created_permission
    except ConflictError as e:
        logger.warning(f"Conflict in create: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in create: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{permission_id}", dependencies=[Depends(require_admin)])
def update(permission_id: int, permission_update: PermissionUpdate) -> PermissionResponse:
    """Update a permission (Admin only)"""
    try:
        updated_permission = service.update(permission_id, permission_update)
        if not updated_permission:
            raise NotFoundError(f"Permission with ID {permission_id} not found")
        logger.info(f"API request: Updated permission {permission_id}")
        return updated_permission
    except NotFoundError as e:
        logger.warning(f"Permission {permission_id} not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in update: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{permission_id}", dependencies=[Depends(require_admin)])
def delete(permission_id: int) -> bool:
    """Delete a permission (Admin only)"""
    try:
        result = service.delete(permission_id)
        if not result:
            raise NotFoundError(f"Permission with ID {permission_id} not found")
        logger.info(f"API request: Deleted permission {permission_id}")
        return result
    except NotFoundError as e:
        logger.warning(f"Permission {permission_id} not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in delete: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================
# Role-Permission Assignment Endpoints (Admin Only)
# ============================================


@router.get("/{role_id}/permissions", dependencies=[Depends(require_admin)])
def get_role_permissions(role_id: int) -> list[PermissionResponse]:
    """Get all permissions for a role (Admin only)"""
    try:
        permissions = service.get_role_permissions(role_id)
        logger.info(f"API request: Retrieved {len(permissions)} permissions for role {role_id}")
        return permissions
    except DatabaseError as e:
        logger.error(f"Database error in get_role_permissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/role/{permission_id}/roles", dependencies=[Depends(require_admin)])
def get_permission_roles(permission_id: int):
    """Get all roles for a permission (Admin only)"""
    try:
        roles = service.get_permission_roles(permission_id)
        logger.info(f"API request: Retrieved {len(roles)} roles for permission {permission_id}")
        return roles
    except DatabaseError as e:
        logger.error(f"Database error in get_permission_roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roles/assign", dependencies=[Depends(require_admin)])
def assign_permission_to_role(permission_id: int, role_id: int) -> dict:
    """Assign a permission to a role (Admin only)"""
    try:
        result = service.assign_permission_to_role(permission_id, role_id)
        logger.info(f"API request: Assigned permission {permission_id} to role {role_id}")
        return {"success": result, "message": f"Permission {permission_id} assigned to role {role_id}"}
    except DatabaseError as e:
        logger.error(f"Database error in assign_permission_to_role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roles/remove", dependencies=[Depends(require_admin)])
def remove_permission_from_role(permission_id: int, role_id: int) -> dict:
    """Remove a permission from a role (Admin only)"""
    try:
        result = service.remove_permission_from_role(permission_id, role_id)
        logger.info(f"API request: Removed permission {permission_id} from role {role_id}")
        return {"success": result, "message": f"Permission {permission_id} removed from role {role_id}"}
    except DatabaseError as e:
        logger.error(f"Database error in remove_permission_from_role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
