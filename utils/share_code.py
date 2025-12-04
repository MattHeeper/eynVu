import random
import string


def generate_share_code() -> str:
    """
    Generate random share code (6-9 characters)
    
    Examples: abc123, xyz789, def456gh
    
    Returns:
        Random share code
    """
    length = random.randint(6, 9)
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def is_share_code_unique(share_code: str, db) -> bool:
    """Check if share code is unique"""
    from models.user import User
    existing = db.query(User).filter(User.share_code == share_code).first()
    return existing is None
