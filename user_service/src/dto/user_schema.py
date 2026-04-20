from pydantic import BaseModel, Field, EmailStr

# Equivalent to destructuring `{ username, email, password }` from req.body
# in the POST /register route, with validation built in

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")

# Equivalent to destructuring `{ email, password }` from req.body
# in the POST /login route

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., description="Password")

# Shape of the JWT payload — equivalent to the `user` object passed to jwt.sign()
# In Node: jwt.sign({ id, email }, secret)

class TokenPayload(BaseModel):
    id: int
    email: str

# Response returned after a successful login or validate
class AuthResponse(BaseModel):
    message: str
    token: str

# Response returned after a successful register
class RegisterResponse(BaseModel):
    message: str
    user: dict
