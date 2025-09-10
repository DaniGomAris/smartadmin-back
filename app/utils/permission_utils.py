class RolePermissions:
    @staticmethod
    def can_delete_user(current_role: str, target_role: str) -> bool:
        if current_role == "master" and target_role in ["admin", "master"]:
            return True
        if current_role == "admin" and target_role == "user":
            return True
        return False

    @staticmethod
    def can_update_user(current_role: str, target_role: str) -> bool:
        if current_role == "master" and target_role in ["admin", "master"]:
            return True
        if current_role == "admin" and target_role in ["user", "admin"]:
            return True
        return False

    @staticmethod
    def can_create_user(current_role: str, target_role: str) -> bool:
        if current_role == "master" and target_role == "admin":
            return True
        if current_role == "admin" and target_role == "user":
            return True
        return False

    @staticmethod
    def can_assign_role(current_role: str, target_role: str) -> bool:
        if current_role == "master" and target_role in ["admin", "master"]:
            return True
        if current_role == "admin" and target_role in ["user", "admin"]:
            return True
        return False
