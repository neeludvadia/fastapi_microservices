from sqlmodel import Session, select
from fastapi import HTTPException, status
from src.models.user_model import User
from src.dto.user_schema import RegisterRequest
from src.interfaces.user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> User | None:
        # Equivalent to:
        # db.query(`SELECT * FROM "user" WHERE email = $1`, [email])
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def create(self, data: RegisterRequest, hashed_password: str) -> User:
        # Equivalent to:
        # db.query(`INSERT INTO "user" (username, email, password) VALUES ($1, $2, $3) RETURNING *`,
        #          [username, email, hashedPassword])
        db_user = User(
            username=data.username,
            email=data.email,
            password=hashed_password,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)
