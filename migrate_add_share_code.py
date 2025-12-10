"""
Database migration to add share_code column to users table
Run this script ONCE to update the database schema
"""

from sqlalchemy import text
from database import Session
from models.user import User
from utils.share_code import generate_share_code, is_share_code_unique


def add_share_code_column():
    """Add share_code column to users table"""
    db = Session()
    
    try:
        print("🔧 Starting migration: Adding share_code column...")
        
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='share_code';
        """)
        
        result = db.execute(check_query).fetchone()
        
        if result:
            print("✅ Column share_code already exists. Skipping migration.")
            return
        
        # Add share_code column
        print("📝 Adding share_code column to users table...")
        alter_query = text("""
            ALTER TABLE users 
            ADD COLUMN share_code VARCHAR(9) NULL;
        """)
        db.execute(alter_query)
        db.commit()
        print("✅ Column added successfully!")
        
        # Add index
        print("📝 Creating index on share_code...")
        index_query = text("""
            CREATE INDEX ix_users_share_code ON users (share_code);
        """)
        db.execute(index_query)
        db.commit()
        print("✅ Index created successfully!")
        
        # Generate share codes for existing users
        print("📝 Generating share codes for existing users...")
        users = db.query(User).filter(
            (User.share_code == None) | (User.share_code == '')
        ).all()
        
        print(f"Found {len(users)} users without share_code")
        
        for i, user in enumerate(users, 1):
            user_share_code = generate_share_code()
            while not is_share_code_unique(user_share_code, db):
                user_share_code = generate_share_code()
            
            user.share_code = user_share_code
            print(f"  [{i}/{len(users)}] {user.identifier} → {user_share_code}")
        
        db.commit()
        print(f"✅ Generated {len(users)} share codes!")
        
        # Add unique constraint
        print("📝 Adding unique constraint...")
        constraint_query = text("""
            ALTER TABLE users 
            ADD CONSTRAINT uq_users_share_code UNIQUE (share_code);
        """)
        db.execute(constraint_query)
        db.commit()
        print("✅ Unique constraint added!")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE MIGRATION: Add share_code column")
    print("=" * 50)
    add_share_code_column()
