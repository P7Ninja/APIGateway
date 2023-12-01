from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
import json
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .Service import Service, ResponseType
from .Authentication import JWTEncoder
from . import schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class APIGateway:
    def __init__(self, app: FastAPI, cfg: dict, jwtencoder: JWTEncoder, services: dict[str, Service], origins: list[str]) -> None:
        self.__app = app
        self.__cfg = cfg
        self.__jwt = jwtencoder
        self.__services = services
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def configure_routes(self):
        self.__app.add_api_route("/user", self.get_user, methods=["GET"], status_code=200, response_model=schema.User, tags=["users"])
        self.__app.add_api_route("/user", self.create_user, methods=["POST"], status_code=201, tags=["users"])
        self.__app.add_api_route("/user", self.delete_user, methods=["DELETE"], status_code=200, tags=["users"])
        self.__app.add_api_route("/login", self.login, methods=["POST"], status_code=200, tags=["users"])

        # health service
        self.__app.add_api_route("/health", self.create_health, methods=["POST"], status_code=201, tags=["health"])
        self.__app.add_api_route("/health/{id}", self.delete_health, methods=["DELETE"], status_code=200, tags=["health"])
        self.__app.add_api_route("/health/history", self.get_health_history, methods=["GET"], status_code=200, tags=["health"])

        # inventory service
        self.__app.add_api_route("/inventories", self.get_invs, methods=["GET"], status_code=200, tags=["inventory"])
        self.__app.add_api_route("/inventories/{inv_id}", self.post_to_inv, methods=["POST"], status_code=200, tags=["inventory"])
        self.__app.add_api_route("/inventories", self.post_inv, methods=["POST"], status_code=200, tags=["inventory"])
        self.__app.add_api_route("/inventories/{inv_id}", self.delete_inv, methods=["DELETE"], status_code=200, tags=["inventory"])
        self.__app.add_api_route("/inventories/{inv_id}/{item_id}", self.delete_inv_item, methods=["DELETE"], status_code=200, tags=["inventory"])

        # food service
        self.__app.add_api_route("/foods", self.get_foods, methods=["GET"], status_code=200, tags=["food"])
        self.__app.add_api_route("/foods/{id}", self.get_food_item, methods=["GET"], status_code=200, tags=["food"])
        self.__app.add_api_route("/foods/discounted", self.get_foods_discounted, methods=["GET"], status_code=200, tags=["food"])

        # mealplan service
        self.__app.add_api_route("/meal", self.create_meal_plan, methods=["POST"], status_code=201, tags=["mealplan"])
        self.__app.add_api_route("/mealRecipe", self.create_meal_plan_recipe, methods=["POST"], status_code=201, tags=["mealplan"])
        self.__app.add_api_route("/mealsPerDay", self.create_meals_per_day, methods=["POST"], status_code=201, tags=["mealplan"])
        self.__app.add_api_route("/generate", self.generate_meal_plan, methods=["POST"], status_code=201, tags=["mealplan"])
        self.__app.add_api_route("/mealPlan", self.get_current_meal_plan, methods=["GET"], status_code=200, tags=["mealplan"])
        self.__app.add_api_route("/mealPlan/all", self.get_all_meal_plans, methods=["GET"], status_code=200, tags=["mealplan"])
        self.__app.add_api_route("/mealPlan", self.delete_meal_plan, methods=["DELETE"], status_code=200, tags=["mealplan"])
    

    def auth(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            )
        decoded = self.__jwt.decode_token(token)
        if not decoded:
            raise credentials_exception
        return decoded

    async def get_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        id = self.auth(token)["id"]
        user_service = self.__services["user"]
        res = await user_service.request("get", f"/user/{id}", dict)
        return res
    async def login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        user_service = self.__services["user"]
        res = await user_service.request(
            "post", 
            "/validate", 
            dict,
            data=json.dumps({"username": form_data.username, "password": form_data.password}),
            )
            
        if not res["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
                )
        
        token = self.__jwt.encode(form_data.username, res["id"], timedelta(days=float(self.__cfg["EXPIRE"])))
        return {"access_token": token, "token_type": "bearer"}
    
    async def create_user(self, account: schema.UserCreate):
        user_service = self.__services["user"]
        res = await user_service.request(
            "post", "/user",
            dict,
            data=account.model_dump_json()
        )
        return {"success": res["success"]}

    async def delete_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        id = self.auth(token)["id"]
        user_service = self.__services["user"]
        return await user_service.request("delete", f"/user/{id}", dict)


    async def get_foods(self, query: str):
        food_service = self.__services["food"]
        res = await food_service.request(
            "get", f"/api/foods?query={query}",
            list,
            ResponseType.PRIM
        )
        return res
    
    async def get_food_item(self, id: int):
        food_service = self.__services["food"]
        res = await food_service.request(
            "get", f"/api/foods/{id}",
            schema.Food,
            dict
        )
        return res
    
    async def get_foods_discounted(self):
        food_service = self.__services["food"]
        res = await food_service.request(
            "get", f"/api/foods/discounted",
            schema.Food,
            dict
        )
        return res
    
    async def post_to_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inv_id: int, inv_item: schema.InventoryItem):
        id = self.auth(token)["id"]
        inv_service = self.__services["inventory"]
        res = await inv_service.request("post", f"/api/inventories/{inv_id}", schema.Inventory, dict, inv_item.model_dump_json())
        return res
    
    async def get_invs(self, token: Annotated[str, Depends(oauth2_scheme)]):
        id = self.auth(token)["id"]
        inv_service = self.__services["inventory"]
        food_service = self.__services["food"]
        invs = await inv_service.request("get", f"/api/inventories/user/{id}", list, ResponseType.PRIM)

        food_ids = []
        for inv in invs:
            for item in inv["items"]:
                food_ids.append(item["foodId"])
        foods = await food_service.request("post", f"/api/foods/list", list, ResponseType.PRIM, json.dumps(food_ids))
        for inv in invs:
            for i in inv["items"]:
                matching_food = next((f for f in foods if f["id"] == i["foodId"]), None)
                i["food"] = matching_food
        return invs
    
    async def post_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inventory: schema.Inventory):
        id = self.auth(token)["id"]
        inv_service = self.__services["inventory"]
        inventory.userId = id
        res = await inv_service.request("post", f"/api/inventories", schema.Inventory, ResponseType.DICT, inventory.model_dump_json())
        return res
    
    async def delete_inv(self, inv_id: int, inventory: schema.Inventory, token: Annotated[str, Depends(oauth2_scheme)]):
        id = self.auth(token)["id"]
 
        if id != inventory.userId:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if inventory.id != inv_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        inventory_service = self.__services["inventory"]
        return await inventory_service.request("delete", f"/api/inventories/{inv_id}", dict, ResponseType.DICT)
    
    async def delete_inv_item(self, token: Annotated[str, Depends(oauth2_scheme)], inv_id: int, item_id: int):
        id = self.auth(token)["id"]
        inventory_service = self.__services["inventory"]
        return await inventory_service.request("delete", f"/api/inventories/{inv_id}/{item_id}", dict)
    
    async def put_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inventory: schema.Inventory):
        id = self.auth(token)["id"]
        inventory_service = self.__services["inventory"]
        return await inventory_service.request("put", f"/api/inventories/{inventory.id}", dict)

    
    async def create_health(self, token: Annotated[str, Depends(oauth2_scheme)], health: schema.BaseHealthEntry):
        id = self.auth(token)["id"]
        create_health = schema.CreateHealthEntry(userID=id, **health.model_dump())
        health_service = self.__services["health"]
        res = await health_service.request(
            "post", "/insertHealth",
            dict,
            data=create_health.model_dump_json()
        )
        return {"success": res["success"]}
    
    async def delete_health(self, token: Annotated[str, Depends(oauth2_scheme)], id: int):
        user_id = self.auth(token)["id"]
        health_service = self.__services["health"]
        res = await health_service.request(
            "delete", f"/deleteHealth?id={id}&userID={user_id}",
            dict
        )
        return {"success": res["success"]}

    async def get_health_history(self, token: Annotated[str, Depends(oauth2_scheme)]):
        id = self.auth(token)["id"]
        health_service = self.__services["health"]
        return await health_service.request("get", f"/UserHealthHistory?userID={id}", list, res_type=ResponseType.PRIM)

    async def create_meal_plan(self, token: Annotated[str, Depends(oauth2_scheme)], meal: schema.BaseMealPlan):
        user_id = self.auth(token)["id"]
        meal_plan = schema.CreateBaseMealPlan(userID=user_id, **meal.model_dump())
        mealplan_service = self.__services["mealplan"]
        await mealplan_service.request(
            "post", "/mealPlan",
            int,
            data=meal_plan.model_dump_json(),
            res_type=ResponseType.PRIM
        )
        return {"success": True}
    
    async def create_meal_plan_recipe(self, mealRecipe: schema.MealPlanRecipe):
        mealplan_service = self.__services["mealplan"]
        await mealplan_service.request(
            "post", "/mealPlanRecipe",
            str,
            data=mealRecipe.model_dump_json(),
            res_type=ResponseType.PRIM
        )
        return {"success": True}
    
    async def create_meals_per_day(self, mealsPerDay: schema.MealsPerDay):
        mealplan_service = self.__services["mealplan"]
        await mealplan_service.request(
            "post", "/mealsPerDay",
            str,
            data=mealsPerDay.model_dump_json(),
            res_type=ResponseType.PRIM
        )
        return {"success": True}
    

    async def generate_meal_plan(self, token: Annotated[str, Depends(oauth2_scheme)], generate_meal: schema.GenerateMealPlan):
        user_id = self.auth(token)["id"]
        mealplan_service = self.__services["mealplan"]
        generate_meal_plan = schema.CreateGenerateMealplan(userID=user_id, **generate_meal.model_dump())
        await mealplan_service.request(
            "post", "/generate",
            dict,
            data=generate_meal_plan.model_dump_json()
        )
        return {"success": True}
    
    async def get_current_meal_plan(self, token: Annotated[str, Depends(oauth2_scheme)]):
        user_id = self.auth(token)["id"]
        mealplan_service = self.__services["mealplan"]
        return await mealplan_service.request("get", f"/mealPlan/{user_id}", dict, res_type=ResponseType.PRIM)

    async def get_all_meal_plans(self, token: Annotated[str, Depends(oauth2_scheme)]):
        user_id = self.auth(token)["id"]
        mealplan_service = self.__services["mealplan"]
        return await mealplan_service.request("get", f"/mealPlans/{user_id}", dict, res_type=ResponseType.PRIM)

    async def delete_meal_plan(self, token: Annotated[str, Depends(oauth2_scheme)], planID: int):
        user_id = self.auth(token)["id"]
        mealplan_service = self.__services["mealplan"]
        await mealplan_service.request(
            "delete", f"/mealPlan/{planID}/{user_id}",
            str,
            res_type=ResponseType.PRIM
        )
        return {"success": True}
        

