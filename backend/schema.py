import datetime
import pydantic

class UserBase(pydantic.BaseModel):
    email : str

class UserCreate(UserBase):
    hashed_password : str

    class Config:
        orm_mode = True

class User(UserBase):
    id : int

    class Config:
        orm_mode = True
        from_attributes = True

class LeadBase(pydantic.BaseModel):
    first_name : str
    last_name : str
    email : str
    company : str
    note : str

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id : int
    owner_id : int
    date_created : datetime.datetime
    date_last_updated : datetime.datetime

    class Config:
        orm_mode = True
        from_attributes = True