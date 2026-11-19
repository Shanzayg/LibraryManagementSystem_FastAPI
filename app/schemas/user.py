from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["ali@example.com"])
    full_name: str = Field(min_length=1, max_length=100, examples=["Ali Khan"])
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    """What the API returns for a user. No password field on purpose!"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str = "member"