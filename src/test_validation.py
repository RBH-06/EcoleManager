"""
Test validation constraints for username and password
"""
import sys
sys.path.append('.')

from utils.validation import validate_username, validate_password, get_password_strength

def test_validation():
    print("=== USERNAME VALIDATION TESTS ===\n")
    
    test_usernames = [
        'a',                  # Too short
        'ab',                 # Too short  
        'valid_user',         # Valid
        'admin123',           # Valid
        'user.name',          # Valid
        'user..name',         # Invalid (consecutive dots)
        'user@name',          # Invalid (@ symbol)
        '.username',          # Invalid (starts with dot)
        'username.',          # Invalid (ends with dot)
        'very_long_username_that_exceeds_fifty_characters_limit_test',  # Too long
        'admin',              # Reserved
        '123user'             # Valid
    ]

    for username in test_usernames:
        valid, errors = validate_username(username)
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f'{status:<12} | Username: "{username}"')
        if not valid:
            for error in errors:
                print(f'             └─ {error}')
        print()

    print("\n=== PASSWORD VALIDATION TESTS ===\n")
    
    test_passwords = [
        '123',                 # Too short, no complexity
        'password',            # No uppercase, digits, symbols
        'Password',            # No digits, symbols  
        'Password1',           # No symbols
        'Password1!',          # Valid strong password
        'VeryStrong123!@#',    # Very strong password
        'admin123',            # Weak common password
        'MySecurePass2024!',   # Strong password
        'a' * 129,             # Too long
        'ALLUPPERCASE123!',    # No lowercase
        'alllowercase123!'     # No uppercase
    ]

    for password in test_passwords:
        valid, errors = validate_password(password)
        strength, score, color = get_password_strength(password)
        
        # Truncate long passwords for display
        display_pass = password if len(password) <= 20 else password[:17] + '...'
        
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f'{status:<12} | Password: "{display_pass}" | Strength: {strength} ({score}/8)')
        if not valid:
            for error in errors:
                print(f'             └─ {error}')
        print()

    print("\n=== SUMMARY OF CONSTRAINTS ===\n")
    
    print("📝 USERNAME REQUIREMENTS:")
    print("   • Length: 3-50 characters")
    print("   • Characters: Letters, numbers, dots, hyphens, underscores only")
    print("   • Must start and end with letter or number")
    print("   • No consecutive dots")
    print("   • Cannot be reserved words (admin, root, etc.)")
    
    print("\n🔒 PASSWORD REQUIREMENTS:")
    print("   • Length: 8-128 characters")
    print("   • At least one lowercase letter (a-z)")
    print("   • At least one uppercase letter (A-Z)")
    print("   • At least one digit (0-9)")
    print("   • At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    print("   • Cannot be common weak passwords")
    print("   • Cannot contain the username")

if __name__ == "__main__":
    test_validation()