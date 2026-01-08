import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Render provides DATABASE_URL in environment variables
# Default to a local postgres url for testing if env var not set
# Ensure to replace 'user', 'password', 'localhost', 'dbname' with actual values for local testing
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# If using Heroku/Render, the url might start with postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
