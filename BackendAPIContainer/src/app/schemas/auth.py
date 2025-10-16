from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., description="Desired username")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email to reset")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Expiry time in seconds")
