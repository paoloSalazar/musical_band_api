import logging
from fastapi import APIRouter, HTTPException
import services.permission as service
from schemas.permission import PermissionResponse, RolePermissionCreate
from exceptions import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/permissions")


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
