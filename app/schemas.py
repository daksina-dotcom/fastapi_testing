from pydantic import BaseModel, EmailStr, Field,model_validator
from datetime import datetime
from typing import Optional, Literal, List


class VacationBase(BaseModel):
    start_date: datetime
    end_date: datetime
    contact_location: Optional[str] = None

    @model_validator(mode='after')
    def validate_date(self):
        if self.end_date<self.start_date:
            raise ValueError("End date cannot be before the Start date")

        if self.start_date<datetime.now():
            raise ValueError("Start date cannot be in the past")
        return self

class VacationCreate(VacationBase):
    pass


class VacationOut(VacationBase):
    id: int

    class Config:
        from_attributes = True


class VeteranBase(BaseModel):
    pension_status: bool = True
    honorable_discharge: bool = True


class VeteranCreate(VeteranBase):
    pass


class VeteranOut(BaseModel):
    retirement_date: datetime = datetime.now
    pension_status: bool = True
    honorable_discharge: bool = True


class SoldierBase(BaseModel):
    soldier_name: str = Field(..., min_length=2, max_length=100)
    email_id: EmailStr
    rank: Literal["Lieutenant", "Major", "Colonel"] = "Lieutenant"
    status: Literal["Active", "Inactive", "Retired", "Discharged"] = "Active"


class SoldierUpdate(BaseModel):
    soldier_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email_id: Optional[EmailStr] = None
    rank: Optional[Literal["Lieutenant", "Major", "Colonel"]] = None
    status: Optional[Literal["Active", "Inactive", "Retired", "Discharged"]] = None


class SoldierCreate(SoldierBase):
    secret_password: str = Field(..., min_length=8)


class SoldierOut(SoldierBase):
    soldier_id: int
    joined_at: datetime
    vacation_record: Optional[VacationOut] = None

    class Config:
        from_attributes = True


class BulkPromote(BaseModel):
    soldier_ids: List[int]
    new_rank: Literal["Lieutenant", "Major", "Colonel"]


class BulkDelete(BaseModel):
    soldier_ids: List[int]


class SoldierCreateResponse(BaseModel):
    result: str
    data: SoldierOut


class SoldierLogin(BaseModel):
    email_id: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
