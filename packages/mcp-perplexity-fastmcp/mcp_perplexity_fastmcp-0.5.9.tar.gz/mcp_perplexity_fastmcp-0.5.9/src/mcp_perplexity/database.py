import os
from datetime import datetime
from contextlib import contextmanager
import logging
from typing import Optional, List, TypeVar, Type, Callable
from pathlib import Path

from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.pool import QueuePool

from .utils import get_logs_dir

# Setup logging
logger = logging.getLogger(__name__)

# Only enable logging if DEBUG_LOGS is set to true
if os.getenv('DEBUG_LOGS', 'false').lower() == 'true':
    logger.setLevel(logging.INFO)

    # Ensure logs directory exists
    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

    # File handler for database operations
    db_handler = logging.FileHandler(str(logs_dir / "database.log"))
    db_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(db_handler)
else:
    logger.setLevel(logging.CRITICAL)  # Effectively disable logging

# Disable propagation to prevent stdout logging
logger.propagate = False

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String)

    # Relationship with messages
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True)
    chat_id = Column(String, ForeignKey('chats.id'))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with chat
    chat = relationship("Chat", back_populates="messages")


T = TypeVar('T')


class SessionManager:
    """A proper context manager for database sessions."""

    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        self.session = self.session_factory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session is None:
            return

        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
                logger.error(f"Database session error: {exc_val}")
        finally:
            self.session.close()
            self.session = None


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv('DB_PATH', 'chats.db')

        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(
            self.db_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            connect_args={'check_same_thread': False}  # Required for SQLite
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_session(self):
        """Get a database session context manager."""
        return SessionManager(self.SessionLocal)

    def get_all_chats(self) -> List[Chat]:
        with self.get_session() as session:
            try:
                chats = session.query(Chat).order_by(
                    Chat.created_at.desc()).all()
                return chats
            except Exception as e:
                logger.error(f"Error fetching chats: {e}")
                raise

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        with self.get_session() as session:
            try:
                return session.query(Chat).filter(Chat.id == chat_id).first()
            except Exception as e:
                logger.error(f"Error fetching chat {chat_id}: {e}")
                raise

    def get_chat_messages(self, chat_id: str) -> List[Message]:
        with self.get_session() as session:
            try:
                return session.query(Message).filter(
                    Message.chat_id == chat_id
                ).order_by(Message.timestamp.asc()).all()
            except Exception as e:
                logger.error(
                    f"Error fetching messages for chat {chat_id}: {e}")
                raise

    def delete_chat(self, chat_id: str) -> None:
        """Delete a chat and all its messages."""
        with self.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                session.delete(chat)
                session.commit()
