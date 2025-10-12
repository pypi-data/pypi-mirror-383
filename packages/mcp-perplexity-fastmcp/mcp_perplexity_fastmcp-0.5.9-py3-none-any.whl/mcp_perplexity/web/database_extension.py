from typing import Optional, List, Dict
from quart import Quart
from ..database import DatabaseManager, Chat, Message
from datetime import datetime


class Database:
    def __init__(self, app: Optional[Quart] = None):
        self._database_manager: Optional[DatabaseManager] = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart):
        self._database_manager = DatabaseManager()

        # Register extension with Quart
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['database'] = self

    @property
    def database_manager(self) -> DatabaseManager:
        if self._database_manager is None:
            raise RuntimeError(
                "Database extension not initialized. "
                "Did you forget to call init_app()?")
        return self._database_manager

    def get_all_chats(self, page: int = 1, per_page: int = 50) -> Dict:
        """Get all chats with pagination and convert them to dictionaries to avoid session issues.

        Args:
            page: The page number (1-based)
            per_page: Number of items per page (default 50)

        Returns:
            Dict containing chats and pagination info
        """
        with self.database_manager.get_session() as session:
            # Calculate offset
            offset = (page - 1) * per_page

            # Get total count
            total = session.query(Chat).count()

            # Get paginated chats
            chats = session.query(Chat).order_by(Chat.created_at.desc())\
                .offset(offset).limit(per_page).all()

            # Convert to dictionaries while session is still open
            return {
                'chats': [{
                    'id': chat.id,
                    'title': chat.title,
                    'created_at': chat.created_at
                } for chat in chats],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }

    def get_chat(self, chat_id: str) -> Optional[Dict]:
        """Get a chat and convert it to a dictionary to avoid session issues."""
        with self.database_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat:
                return None
            # Convert to dictionary while session is still open
            return {
                'id': chat.id,
                'title': chat.title,
                'created_at': chat.created_at
            }

    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Get chat messages and convert them to dictionaries to avoid session issues."""
        with self.database_manager.get_session() as session:
            messages = session.query(Message).filter(
                Message.chat_id == chat_id
            ).order_by(Message.timestamp.asc()).all()
            # Convert to dictionaries while session is still open
            return [{
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp
            } for msg in messages]

    def delete_chat(self, chat_id: str) -> None:
        """Delete a chat and all its messages."""
        with self.database_manager.get_session() as session:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                session.delete(chat)
                session.commit()


# Create the extension instance
db = Database()
