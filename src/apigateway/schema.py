from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from typing import List

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
# Food service
class Food(BaseModel):
    id: int
    name: str
    price: float
    priceKg: float
    discount: float
    vendor: str
    category: str
    fat: float
    carbs: float
    protein: float
    cal: float

class Discount(BaseModel):
    id: int
    name: str
    price: float
    discount: float
    vendor: str
    category: str

#Inventory service
class InventoryItem(BaseModel):
    id: int = 0
    foodId: int = 0
    expirationDate: str = ""
    timestamp: str = "2023-01-01"
    food: Food

class Inventory(BaseModel):
    id: int = 0
    userId: int
    name: str
    items: list[InventoryItem] = []


# Mealplan service

class BaseMealPlan(BaseModel):
    startDate: str = Field(examples=["2023-12-11"])
    endDate: str = Field(examples=["2023-12-11"])

class CreateBaseMealPlan(BaseMealPlan):
    userID: int

class MealPlanRecipe(BaseModel):
    planID: int
    recipeID: int

class MealsPerDay(BaseModel):
    planID: int
    meals: int = Field(examples=[1])
    totalCalories: int = Field(examples=[3000])
    totalProtein: float = Field(examples=[200])
    totalCarbohydrates: float = Field(examples=[300])
    totalFat: float = Field(examples=[70])

class GenerateMealPlan(BaseModel):
    targets: List[float]
    split_days: List[float]

class CreateGenerateMealplan(GenerateMealPlan):
    userID: int

class Mealplan(BaseMealPlan):
    id: int
