from abc import ABC, abstractmethod
from src.models.user_model import User
from src.dto.user_schema import RegisterRequest

# Equivalent to TypeScript's `export interface IUserRepository`
# Forces the repository class to implement all these methods

class IUserRepository(ABC):

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def create(self, data: RegisterRequest, hashed_password: str) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass
