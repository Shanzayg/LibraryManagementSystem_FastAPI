from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


def clean_isbn(value: str | None) -> str | None:
    """Remove hyphens/spaces and make sure the ISBN is 10 or 13 digits."""
    if value is None:  # PATCH: field not provided
        return value
    digits = value.replace("-", "").replace(" ", "")
    if not digits.isdigit() or len(digits) not in (10, 13):
        raise ValueError("ISBN must be 10 or 13 digits")
    return digits


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Clean Code"])
    author: str = Field(min_length=1, max_length=100, examples=["Robert C. Martin"])
    isbn: str = Field(description="10 or 13 digits, hyphens allowed", examples=["9780132350884"])
    published_year: int = Field(ge=1900, le=date.today().year, examples=[2008])
    total_copies: int = Field(ge=0, examples=[3])

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        return clean_isbn(v)


class BookUpdate(BaseModel):
    """Every field optional: used for PATCH (send only what you want to change)."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    isbn: str | None = Field(default=None, description="10 or 13 digits, hyphens allowed")
    published_year: int | None = Field(default=None, ge=1900, le=date.today().year)
    total_copies: int | None = Field(default=None, ge=0)

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        return clean_isbn(v)


class BookOut(BaseModel):
    """What the API returns for a book."""
    model_config = ConfigDict(from_attributes=True)  # lets it read DB objects later

    id: int
    title: str
    author: str
    isbn: str
    published_year: int
    total_copies: int
    available_copies: int