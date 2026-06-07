"""
Input validation utilities for usernames and passwords
"""
import re
from typing import List, Tuple


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_username(username: str) -> Tuple[bool, List[str]]:
    """
    Validate username according to security best practices
    
    Rules:
    - 3-50 characters length
    - Alphanumeric characters, underscore, dot, hyphen only
    - Must start with letter or number
    - Cannot end with dot
    - No consecutive dots
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    """
    errors = []
    
    if not username:
        errors.append("Le nom d'utilisateur est requis")
        return False, errors
    
    username = username.strip()
    
    # Length check
    if len(username) < 3:
        errors.append("Le nom d'utilisateur doit contenir au moins 3 caractères")
    
    if len(username) > 50:
        errors.append("Le nom d'utilisateur ne peut pas dépasser 50 caractères")
    
    # Character validation
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$', username):
        if len(username) == 1:
            if not re.match(r'^[a-zA-Z0-9]$', username):
                errors.append("Le nom d'utilisateur ne peut contenir que des lettres et chiffres")
        else:
            errors.append("Le nom d'utilisateur ne peut contenir que des lettres, chiffres, points, tirets et underscores")
            errors.append("Il doit commencer et finir par une lettre ou un chiffre")
    
    # No consecutive dots
    if '..' in username:
        errors.append("Le nom d'utilisateur ne peut pas contenir de points consécutifs")
    
    # Reserved usernames
    reserved = ['admin', 'root', 'administrator', 'user', 'guest', 'system', 'null', 'undefined']
    if username.lower() in reserved:
        errors.append(f"Le nom d'utilisateur '{username}' est réservé")
    
    return len(errors) == 0, errors


def validate_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password according to security best practices
    
    Rules:
    - 8-128 characters length
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    - No common weak passwords
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    """
    errors = []
    
    if not password:
        errors.append("Le mot de passe est requis")
        return False, errors
    
    # Length check
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if len(password) > 128:
        errors.append("Le mot de passe ne peut pas dépasser 128 caractères")
    
    # Character requirements
    if not re.search(r'[a-z]', password):
        errors.append("Le mot de passe doit contenir au moins une lettre minuscule")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Le mot de passe doit contenir au moins une lettre majuscule")
    
    if not re.search(r'\d', password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    
    # Common weak passwords
    weak_passwords = [
        'password', '123456789', 'qwerty', 'abc123', 'password123',
        '12345678', 'admin123', 'letmein', 'welcome', 'monkey',
        '1234567890', 'password1', 'qwerty123', 'admin', '123456'
    ]
    
    if password.lower() in weak_passwords:
        errors.append("Ce mot de passe est trop commun. Choisissez un mot de passe plus sécurisé")
    
    # No username in password (if we had username context)
    # We can add this check when calling from user creation
    
    return len(errors) == 0, errors


def validate_password_with_username(password: str, username: str) -> Tuple[bool, List[str]]:
    """
    Validate password with username context to prevent username inclusion
    """
    is_valid, errors = validate_password(password)
    
    # Additional check: password should not contain username
    if username and len(username) >= 3:
        if username.lower() in password.lower():
            errors.append("Le mot de passe ne peut pas contenir le nom d'utilisateur")
            is_valid = False
    
    return is_valid, errors


def get_password_strength(password: str) -> Tuple[str, int, str]:
    """
    Calculate password strength
    
    Returns:
        Tuple[str, int, str]: (strength_text, strength_score, color)
    """
    if not password:
        return "Aucun", 0, "#f56565"
    
    score = 0
    
    # Length scoring
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character diversity
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        score += 1
    
    # Complexity bonuses
    if len(set(password)) > len(password) * 0.7:  # Character diversity
        score += 1
    
    if score <= 2:
        return "Très faible", score, "#f56565"
    elif score <= 4:
        return "Faible", score, "#ed8936"
    elif score <= 6:
        return "Moyen", score, "#48bb78"
    elif score <= 7:
        return "Fort", score, "#38b2ac"
    else:
        return "Très fort", score, "#667eea"


def sanitize_input(input_str: str) -> str:
    """Sanitize user input by removing dangerous characters"""
    if not input_str:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_str.strip()
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
    return sanitized


# Quick validation functions for common use
def is_valid_username(username: str) -> bool:
    """Quick username validation check"""
    valid, _ = validate_username(username)
    return valid


def is_valid_password(password: str) -> bool:
    """Quick password validation check"""  
    valid, _ = validate_password(password)
    return valid