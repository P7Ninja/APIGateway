from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

# user service
class BaseUser(BaseModel):
    username: str = Field(examples=["John123"])
    email: str = Field(examples=["example@email.com"])
    gender: str = Field(examples=["male"])
    birthday: date = Field(examples=[date(1970,1, 1)])

class Energy(BaseModel):
    calories: float = Field(examples=[2000])
    fat: float = Field(examples=[60])
    carbohydrates: float = Field(examples=[60])
    protein: float = Field(examples=[60])
    
class UserCreate(BaseUser):
    target_energy: Energy
    password: str = Field(examples=["secretkitten65"])

class User(BaseUser):
    id: int
    created: datetime
    target_energy: Energy

# Health service

class BaseHealthEntry(BaseModel):
    dateStamp: datetime
    height: Optional[float] = None
    weight: Optional[float] = None
    fatPercentage: Optional[float] = None
    musclePercentage:Optional[float] = None
    waterPercentage: Optional[float] = None
        
class CreateHealthEntry(BaseHealthEntry):
    userID: int  

class HealthEntry(CreateHealthEntry):
    id: int