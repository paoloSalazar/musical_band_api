import logging
from fastapi import APIRouter, HTTPException
import services.permission as service
from schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate, RolePermissionCreate
from exceptions import DatabaseError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/permissions")


# ============================================
# Permission CRUD Endpoints
# ============================================


@router.get("/")
def get_all() -> list[PermissionResponse]:
    """Get all permissions"""
    try:
        permissions = service.get_all()
        logger.info(f"API request: Retrieved {len(permissions)} permissions")
        return permissions
    except DatabaseError as e:
        logger.error(f"Database error in get_all: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{permission_id}")
def get_one(permission_id: int) -> PermissionResponse:
    """Get a permission by ID"""
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


@router.post("/")
def create(permission: PermissionCreate) -> PermissionResponse:
    """Create a new permission"""
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


@router.patch("/{permission_id}")
def update(permission_id: int, permission_update: PermissionUpdate) -> PermissionResponse:
    """Update a permission"""
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


@router.delete("/{permission_id}")
def delete(permission_id: int) -> bool:
    """Delete a permission"""
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
# Role-Permission Assignment Endpoints
# ============================================


@router.get("/{role_id}/permissions")
def get_role_permissions(role_id: int) -> list[PermissionResponse]:
    """Get all permissions for a role"""
    try:
        permissions = service.get_role_permissions(role_id)
        logger.info(f"API request: Retrieved {len(permissions)} permissions for role {role_id}")
        return permissions
    except DatabaseError as e:
        logger.error(f"Database error in get_role_permissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/role/{permission_id}/roles")
def get_permission_roles(permission_id: int):
    """Get all roles for a permission"""
    try:
        roles = service.get_permission_roles(permission_id)
        logger.info(f"API request: Retrieved {len(roles)} roles for permission {permission_id}")
        return roles
    except DatabaseError as e:
        logger.error(f"Database error in get_permission_roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roles/assign")
def assign_permission_to_role(permission_id: int, role_id: int) -> dict:
    """Assign a permission to a role"""
    try:
        result = service.assign_permission_to_role(permission_id, role_id)
        logger.info(f"API request: Assigned permission {permission_id} to role {role_id}")
        return {"success": result, "message": f"Permission {permission_id} assigned to role {role_id}"}
    except DatabaseError as e:
        logger.error(f"Database error in assign_permission_to_role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roles/remove")
def remove_permission_from_role(permission_id: int, role_id: int) -> dict:
    """Remove a permission from a role"""
    try:
        result = service.remove_permission_from_role(permission_id, role_id)
        logger.info(f"API request: Removed permission {permission_id} from role {role_id}")
        return {"success": result, "message": f"Permission {permission_id} removed from role {role_id}"}
    except DatabaseError as e:
        logger.error(f"Database error in remove_permission_from_role: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
