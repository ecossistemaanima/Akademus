import re

def validate_password_policy(password: str):
    """
    Política de Senha do Akademus:
    - No mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial (!@#$%^&*()-_=+[]{}|;:,.<>?)
    """
    if len(password) < 8:
        return False, "A senha deve conter no mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos 1 letra maiúscula."
    if not re.search(r"[a-z]", password):
        return False, "A senha deve conter pelo menos 1 letra minúscula."
    if not re.search(r"[0-9]", password):
        return False, "A senha deve conter pelo menos 1 número."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        return False, "A senha deve conter pelo menos 1 caractere especial (!@#$%^&*...)."
    return True, ""
