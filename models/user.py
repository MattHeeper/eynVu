from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    User model - stores all user information
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Telegram Info
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)  # @username (can be null)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    
    # eynVu Info
    identifier = Column(String(20), unique=True, nullable=False, index=True)  # Ua1@gb2h
    nickname = Column(String(13), nullable=True)  # نام مستعار (max 13 chars)
    
    # Membership Info
    join_date = Column(DateTime(timezone=True), server_default=func.now())
    member_number = Column(Integer, nullable=False)  # نفر چندم عضو شده
    
    # Stats
    total_messages_sent = Column(Integer, default=0)
    total_messages_received = Column(Integer, default=0)
    leaderboard_score = Column(Integer, default=0)
    
    # Permissions & Roles
    is_vip = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    titles = Column(Text, nullable=True)  # JSON string of titles (e.g., ["Radio Host", "Librarian"])
    
    # Status
    is_blocked = Column(Boolean, default=False)  # بلاک شده
    is_kicked = Column(Boolean, default=False)  # کیک شده
    muted_until = Column(DateTime(timezone=True), nullable=True)  # مسدود تا
    
    # Activity
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, identifier={self.identifier}, telegram_id={self.telegram_id})>"
    
    def get_display_name(self):
        """Return display name: nickname or first_name"""
        return self.nickname if self.nickname else self.first_name
    
    def get_full_info(self):
        """Return full user information as dict"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "name": f"{self.first_name} {self.last_name or ''}".strip(),
            "identifier": self.identifier,
            "nickname": self.nickname,
            "member_number": self.member_number,
            "join_date": self.join_date.isoformat() if self.join_date else None,
            "is_vip": self.is_vip,
            "is_admin": self.is_admin,
            "titles": self.titles,
            "stats": {
                "messages_sent": self.total_messages_sent,
                "messages_received": self.total_messages_received,
                "leaderboard_score": self.leaderboard_score
            }
        }
    
    def is_muted(self):
        """Check if user is currently muted"""
        if not self.muted_until:
            return False
        from datetime import datetime
        return datetime.now() < self.muted_until
