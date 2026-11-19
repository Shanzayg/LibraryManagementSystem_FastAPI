from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LoanCreate(BaseModel):
    # The user comes from the login token later (topic 17), so only book_id here.
    book_id: int = Field(gt=0, examples=[1])


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: datetime | None = None