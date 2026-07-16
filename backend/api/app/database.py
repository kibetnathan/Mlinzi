import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

# Load DBURL
load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/default"
)

# Create db engine
engine = create_engine(DATABASE_URL, echo=True)


def get_db():
    with Session(engine) as session:
        yield session
