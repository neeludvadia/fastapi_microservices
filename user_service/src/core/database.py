import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Load environment variables from the .env file
load_dotenv()

postgres_url = os.getenv("DATABASE_URL")

# The engine is what actually connects to the database (similar to new PrismaClient())
engine = create_engine(postgres_url, echo=True)

def create_db_and_tables():
    # This reads all classes that inherit from SQLModel and creates the tables
    # It functions as a lightweight version of `prisma db push`
    SQLModel.metadata.create_all(engine)

def get_session():
    # We use this to get a database connection per request
    with Session(engine) as session:
        yield session
