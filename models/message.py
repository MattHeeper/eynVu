from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class AnonymousMessage(Base):
    """
    Anonymous Message model - stores all anonymous messages
    """
    __tablename__ = "anonymous_messages"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Sender Info
    sender_id = Column(Integer, nullable=False)
    sender_telegram_id = Column(BigInteger, nullable=False)
    sender_identifier = Column(String(20), nullable=False, index=True)
    
    # Recipient Info
    recipient_id = Column(Integer, nullable=False)
    recipient_telegram_id = Column(BigInteger, nullable=False)
    recipient_identifier = Column(String(20), nullable=False, index=True)
    
    # Message Content
    message_type = Column(String(20), default='text')
    message_text = Column(Text, nullable=True)
    message_file_id = Column(String(255), nullable=True)
    
    # Message Status
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Telegram Message IDs
    sender_message_id = Column(BigInteger, nullable=True)
    recipient_message_id = Column(BigInteger, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AnonymousMessage(id={self.id}, from={self.sender_identifier}, to={self.recipient_identifier})>"
    
    def get_preview(self, max_length=50):
        """Get message preview"""
        if not self.message_text:
            return f"[{self.message_type}]"
        
        preview = self.message_text[:max_length]
        if len(self.message_text) > max_length:
            preview += "..."
        
        return preview
