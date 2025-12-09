"""
Migration script to add share_code to existing users
Run this ONCE after deploying the new code
"""

from database import Session
from models.user import User
from utils.share_code import generate_share_code, is_share_code_unique


def migrate_add_share_codes():
    """Add share_code to all users who don't have one"""
    db = Session()
    
    try:
        # Find all users without share_code
        users = db.query(User).filter(
            (User.share_code == None) | (User.share_code == '')
        ).all()
        
        print(f"Found {len(users)} users without share_code")
        
        for user in users:
            # Generate unique share code
            user_share_code = generate_share_code()
            while not is_share_code_unique(user_share_code, db):
                user_share_code = generate_share_code()
            
            user.share_code = user_share_code
            print(f"✅ Added share_code for {user.identifier}: {user_share_code}")
        
        db.commit()
        print(f"\n✅ Migration completed! Updated {len(users)} users")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting migration...")
    migrate_add_share_codes()
