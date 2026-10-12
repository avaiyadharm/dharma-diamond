from enum import Enum
from typing import List
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    INVENTORY_MANAGER = "inventory_manager"
    SALES_STAFF = "sales_staff"
    ACCOUNTANT = "accountant"
    READ_ONLY = "read_only"

# Role permission hierarchy mappings
ROLE_HIERARCHY = {
    UserRole.ADMIN: [UserRole.ADMIN, UserRole.INVENTORY_MANAGER, UserRole.SALES_STAFF, UserRole.ACCOUNTANT, UserRole.READ_ONLY],
    UserRole.INVENTORY_MANAGER: [UserRole.INVENTORY_MANAGER, UserRole.READ_ONLY],
    UserRole.ACCOUNTANT: [UserRole.ACCOUNTANT, UserRole.READ_ONLY],
    UserRole.SALES_STAFF: [UserRole.SALES_STAFF, UserRole.READ_ONLY],
    UserRole.READ_ONLY: [UserRole.READ_ONLY],
}

def require_roles(allowed_roles: List[UserRole]):
    def role_checker(current_user):
        if current_user.role == UserRole.ADMIN.value:
            return current_user
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have sufficient permissions to perform this action"
            )
        return current_user
    return role_checker
