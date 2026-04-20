import bcrypt
from fastapi import HTTPException, status
from src.interfaces.user_repository_interface import IUserRepository
from src.dto.user_schema import RegisterRequest, LoginRequest
from src.core.security import create_token


class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def register(self, data: RegisterRequest) -> dict:
        # Equivalent to:
        # const userExists = await db.query(`SELECT * FROM "user" WHERE email = $1`)
        # if (userExists.rows.length > 0) return res.status(400).json(...)
        existing = self.repository.find_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        # Equivalent to: const hashedPassword = await bcrypt.hash(password, 10)
        hashed_password = bcrypt.hashpw(
            data.password.encode("utf-8"), bcrypt.gensalt(10)
        ).decode("utf-8")

        new_user = self.repository.create(data, hashed_password)

        return {
            "message": "User created",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
            }
        }

    def login(self, data: LoginRequest) -> dict:
        # Equivalent to: const user = await db.query(`SELECT * FROM "user" WHERE email = $1`)
        user = self.repository.find_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Equivalent to: const validPassword = await bcrypt.compare(password, user.rows[0].password)
        valid = bcrypt.checkpw(
            data.password.encode("utf-8"), user.password.encode("utf-8")
        )
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )

        # Equivalent to: const token = generateToken({ id, email })
        token = create_token({"id": user.id, "email": user.email})

        return {"message": "Login successful", "token": token}
