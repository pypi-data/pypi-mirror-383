import sqlalchemy
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime,
    ForeignKey, Float, inspect, text, select, desc, event
)
from pathlib import Path
import datetime
from typing import Optional, List

# --- Database Setup ---
APP_DIR = Path.home() / ".config" / "klai"
DB_PATH = APP_DIR / "history.db"
APP_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}")
metadata = MetaData()

# Enforce foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# --- Table Definitions ---
conversations = Table(
    "conversations", metadata,
    Column("id", Integer, primary_key=True),
    Column("start_time", DateTime, default=lambda: datetime.datetime.now(datetime.UTC)),
    Column("title", String, default="Untitled Conversation"),
    Column("system_prompt", String, default="You are a helpful assistant."),
    Column("model", String),
    Column("temperature", Float),
    Column("top_p", Float)
)

messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True),
    Column("conversation_id", Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
    Column("parent_id", Integer, ForeignKey("messages.id", ondelete="CASCADE")),
    Column("timestamp", DateTime, default=lambda: datetime.datetime.now(datetime.UTC)),
    Column("role", String, nullable=False),
    Column("content", String, nullable=False),
    Column("is_active", sqlalchemy.Boolean, default=True)
)

# --- Database Management ---
def init_db():
    metadata.create_all(engine)
    inspector = inspect(engine)
    conv_cols = {c['name'] for c in inspector.get_columns('conversations')}
    msg_cols = {c['name'] for c in inspector.get_columns('messages')}
    with engine.connect() as conn:
        if 'system_prompt' not in conv_cols: conn.execute(text("ALTER TABLE conversations ADD COLUMN system_prompt VARCHAR DEFAULT 'You are a helpful assistant.'"))
        if 'model' not in conv_cols: conn.execute(text("ALTER TABLE conversations ADD COLUMN model VARCHAR"))
        if 'temperature' not in conv_cols: conn.execute(text("ALTER TABLE conversations ADD COLUMN temperature FLOAT"))
        if 'top_p' not in conv_cols: conn.execute(text("ALTER TABLE conversations ADD COLUMN top_p FLOAT"))
        if 'parent_id' not in msg_cols: conn.execute(text("ALTER TABLE messages ADD COLUMN parent_id INTEGER REFERENCES messages(id) ON DELETE CASCADE"))
        if 'is_active' not in msg_cols: conn.execute(text("ALTER TABLE messages ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        conn.commit()

# --- Data Access Functions ---
def create_conversation(model: str, system_prompt: str, temperature: Optional[float] = None, top_p: Optional[float] = None) -> int:
    with engine.connect() as conn:
        result = conn.execute(conversations.insert().values(
            title=f"Chat @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            model=model, system_prompt=system_prompt, temperature=temperature, top_p=top_p
        ))
        conn.commit()
        return result.inserted_primary_key[0]

def add_message(conversation_id: int, role: str, content: str, parent_id: Optional[int] = None) -> int:
    with engine.connect() as conn:
        result = conn.execute(messages.insert().values(
            conversation_id=conversation_id, role=role, content=content, parent_id=parent_id
        ))
        conn.commit()
        return result.inserted_primary_key[0]

def get_active_branch(conversation_id: int) -> List[sqlalchemy.Row]:
    with engine.connect() as conn:
        return conn.execute(
            select(messages).where(messages.c.conversation_id == conversation_id, messages.c.is_active == True).order_by(messages.c.timestamp)
        ).fetchall()

def get_new_messages(conversation_id: int, last_message_id: int) -> List[sqlalchemy.Row]:
    with engine.connect() as conn:
        return conn.execute(
            select(messages)
            .where(messages.c.conversation_id == conversation_id)
            .where(messages.c.id > last_message_id)
            .order_by(messages.c.timestamp)
        ).fetchall()

def get_conversation(conversation_id: int) -> Optional[sqlalchemy.Row]:
    with engine.connect() as conn:
        return conn.execute(select(conversations).where(conversations.c.id == conversation_id)).first()

def update_conversation_settings(conversation_id: int, title: str, system_prompt: str, model: str, temperature: float, top_p: float):
    with engine.connect() as conn:
        conn.execute(conversations.update().where(conversations.c.id == conversation_id).values(
            title=title, system_prompt=system_prompt, model=model, temperature=temperature, top_p=top_p
        ))
        conn.commit()

def list_conversations(page: int = 1, per_page: int = 20, search: str = "") -> List[sqlalchemy.Row]:
    query = select(conversations).order_by(desc(conversations.c.start_time)).limit(per_page).offset((page - 1) * per_page)
    if search:
        matching_ids = select(messages.c.conversation_id).where(messages.c.content.ilike(f"%{search}%")).distinct()
        query = query.where(conversations.c.id.in_(matching_ids))
    with engine.connect() as conn:
        return conn.execute(query).fetchall()

def delete_conversation(conversation_id: int):
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(conversations.delete().where(conversations.c.id == conversation_id))
        conn.commit()

def deactivate_branch_from(message_id: int):
    with engine.connect() as conn:
        conn.execute(
            messages.update().where(messages.c.parent_id == message_id).values(is_active=False)
        )
        conn.commit()