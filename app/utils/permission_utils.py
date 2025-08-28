def can_delete_user(current_role: str, target_role: str) -> bool:
    """
    Valida si un rol puede eliminar a otro usuario
    """
    if current_role == "master" and target_role in ["admin", "user"]:
        return True
    if current_role == "admin" and target_role == "user":
        return True
    return False

def can_update_user(current_role: str, target_role: str) -> bool:
    """
    Valida si un rol puede actualizar a otro usuario
    """
    if current_role == "master":
        return True
    if current_role == "admin" and target_role == "user":
        return True
    return False

def can_assign_role(current_role: str, target_role: str) -> bool:
    """
    Valida si un rol puede asignar un rol específico al crear o actualizar
    """
    if current_role == "master" and target_role in ["admin", "user"]:
        return True
    if current_role == "admin" and target_role == "user":
        return True
    return False
