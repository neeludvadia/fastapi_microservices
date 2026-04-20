from sqlmodel import SQLModel, Field
from typing import Optional

# Replaces this SQL from db.sql:
# CREATE TABLE "user" (
#   id SERIAL PRIMARY KEY,
#   username VARCHAR(255) NOT NULL,
#   email VARCHAR(255) NOT NULL,
#   password VARCHAR(255) NOT NULL
# );
#
# SQLModel reads this class and creates the table automatically
# (like `prisma db push` in the Node.js version)

class User(SQLModel, table=True):
    __tablename__ = "user"  # matches the original SQL table name

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str  # stored as a bcrypt hash
