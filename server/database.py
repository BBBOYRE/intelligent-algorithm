import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import Config

os.makedirs(Config.DB_DIR, exist_ok=True)

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表（开发用，生产环境用 alembic）"""
    from server.models import user, document, knowledge_base_model, audit_log, team, api_key, webhook  # noqa: F401
    from server.models import kb_permission, chat, inbox, memo  # noqa: F401
    Base.metadata.create_all(bind=engine)

    _migrate_user_columns()


def _migrate_user_columns():
    """Add new columns to existing tables if missing (SQLite migration)."""
    import sqlalchemy
    insp = sqlalchemy.inspect(engine)
    if "users" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("users")]
        with engine.begin() as conn:
            if "avatar" not in cols:
                conn.execute(sqlalchemy.text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500) DEFAULT ''"))
            if "bio" not in cols:
                conn.execute(sqlalchemy.text("ALTER TABLE users ADD COLUMN bio VARCHAR(500) DEFAULT ''"))
