import random
import string
from sqlalchemy.orm import Session


def generate_identifier(prefix: str, member_number: int, db: Session) -> str:
    """
    Generate unique identifier
    
    Format: Ua1@gb2h
    - U: User
    - a: Anonymous
    - 1: Last digit of member number (e.g., 23 → 3, 100 → 0)
    - @: Always present
    - gb2h: Random characters (letters + numbers)
    
    Args:
        prefix: "Ua" for users, "Rs" for radio stations
        member_number: Member number (e.g., 23)
        db: Database session to check uniqueness
        
    Returns:
        Unique identifier string
    """
    
    # Get last digit of member number
    last_digit = member_number % 10
    
    # Generate random part (4 chars: letters + numbers)
    max_attempts = 100
    
    for _ in range(max_attempts):
        # Random 4 characters (lowercase letters + numbers)
        random_part = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=4)
        )
        
        # Construct identifier
        identifier = f"{prefix}{last_digit}@{random_part}"
        
        # Check if unique
        if is_identifier_unique(identifier, db):
            return identifier
    
    # If failed after max_attempts, add extra random chars
    random_part = ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=6)
    )
    return f"{prefix}{last_digit}@{random_part}"


def is_identifier_unique(identifier: str, db: Session) -> bool:
    """
    Check if identifier is unique in database
    
    Args:
        identifier: Identifier to check
        db: Database session
        
    Returns:
        True if unique, False if exists
    """
    from models.user import User
    
    # Check in users table
    existing_user = db.query(User).filter(User.identifier == identifier).first()
    if existing_user:
        return False
    
    # TODO: Add checks for other tables (stations, etc.) when implemented
    
    return True


def parse_identifier(identifier: str) -> dict:
    """
    Parse identifier and extract information
    
    Args:
        identifier: Identifier string (e.g., "Ua1@gb2h")
        
    Returns:
        Dictionary with parsed information
    """
    try:
        # Split by @
        prefix_part, random_part = identifier.split('@')
        
        # Extract components
        prefix = prefix_part[:-1]  # "Ua"
        digit = int(prefix_part[-1])  # 1
        
        return {
            "prefix": prefix,
            "digit": digit,
            "random": random_part,
            "type": "user" if prefix == "Ua" else "station" if prefix == "Rs" else "unknown"
        }
    except Exception:
        return {
            "prefix": None,
            "digit": None,
            "random": None,
            "type": "invalid"
        }


def format_identifier_display(identifier: str) -> str:
    """
    Format identifier for display with emoji
    
    Args:
        identifier: Identifier string
        
    Returns:
        Formatted string with emoji
    """
    parsed = parse_identifier(identifier)
    
    if parsed["type"] == "user":
        return f"👤 {identifier}"
    elif parsed["type"] == "station":
        return f"📻 {identifier}"
    else:
        return identifier
