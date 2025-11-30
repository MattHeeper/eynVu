from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Log(Base):
    """
    Log model - stores all events and actions
    For security and debugging purposes
    """
    __tablename__ = "logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Event Info
    event_type = Column(String(50), nullable=False, index=True)
    # Event types: "user_join", "message_sent", "user_blocked", "station_created", etc.
    
    # User Info
    user_id = Column(Integer, nullable=True)  # Foreign key to users.id
    telegram_id = Column(BigInteger, nullable=True)
    identifier = Column(String(20), nullable=True)
    
    # Action Details
    action = Column(String(100), nullable=True)  # What happened
    target = Column(String(100), nullable=True)  # Who/what was affected
    details = Column(Text, nullable=True)  # JSON string with additional data
    
    # Result
    success = Column(Integer, default=1)  # 1=success, 0=failed
    error_message = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)  # For web interface (future)
    user_agent = Column(String(255), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Log(id={self.id}, event={self.event_type}, user={self.identifier})>"
    
    @classmethod
    def create_log(cls, db, event_type: str, user_id: int = None, 
                   telegram_id: int = None, identifier: str = None,
                   action: str = None, target: str = None, 
                   details: str = None, success: bool = True, 
                   error_message: str = None):
        """
        Create a new log entry
        
        Example:
            Log.create_log(
                db=db,
                event_type="user_join",
                user_id=1,
                telegram_id=123456,
                identifier="Ua1@gb2h",
                action="Registered to bot",
                success=True
            )
        """
        log_entry = cls(
            event_type=event_type,
            user_id=user_id,
            telegram_id=telegram_id,
            identifier=identifier,
            action=action,
            target=target,
            details=details,
            success=1 if success else 0,
            error_message=error_message
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return log_entry
    
    @classmethod
    def get_user_logs(cls, db, telegram_id: int, limit: int = 50):
        """Get logs for specific user"""
        return db.query(cls).filter(
            cls.telegram_id == telegram_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_logs(cls, db, event_type: str = None, limit: int = 100):
        """Get recent logs, optionally filtered by event type"""
        query = db.query(cls)
        
        if event_type:
            query = query.filter(cls.event_type == event_type)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
