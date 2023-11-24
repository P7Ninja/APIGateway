from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
import json
from fastapi.middleware.cors import CORSMiddleware

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
        self.__app.add_api_route("/user", self.get_user, methods=["GET"], status_code=200)
        self.__app.add_api_route("/user", self.create_user, methods=["POST"], status_code=201)
        self.__app.add_api_route("/user", self.delete_user, methods=["DELETE"], status_code=200)
        self.__app.add_api_route("/login", self.login, methods=["POST"], status_code=200)

        # inventory service
        self.__app.add_api_route("/inventories", self.get_invs, methods=["GET"], status_code=200)
        self.__app.add_api_route("/inventories/{inv_id}", self.post_to_inv, methods=["POST"], status_code=200)
        self.__app.add_api_route("/inventories/{inv_id}", self.delete_inv, methods=["DELETE"], status_code=200)
        self.__app.add_api_route("/inventories/{inv_id}/{item_id}", self.delete_inv_item, methods=["DELETE"], status_code=200)
        self.__app.add_api_route("/inventories/{inv_id}", self.put_inv, methods=["PUT"], status_code=200)

        # foodService
        self.__app.add_api_route("/foods", self.get_foods, methods=["GET"], status_code=200)
        self.__app.add_api_route("/foods/{id}", self.get_food_item, methods=["GET"], status_code=200)
        self.__app.add_api_route("/foods/discounted", self.get_foods_discounted, methods=["GET"], status_code=200)
        self.__app.add_api_route("/foods/list", self.post_foods_list, methods=["POST"], status_code=200)
    

        

        


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

    async def get_foods(self, query: str):
        food_service = self.__services["food"]
        res = await food_service.request(
            "get", f"/api/foods?query={query}",
            schema.Food,
            dict
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

    async def post_foods_list(self, food_ids: list[int] ):
        food_service = self.__services["food"]
        res = await food_service.request(
            "post", f"/api/foods/list",
            schema.Food,
            dict,
            food_ids
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
        res = await inv_service.request("get", f"/api/inventories/user/{id}", list, ResponseType.PRIM)
        return res
    
    async def post_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inventory: schema.Inventory):
        id = self.auth(token)["id"]
        inv_service = self.__services["inventory"]
        res = await inv_service.request("post", f"/api/inventories", schema.Inventory, dict, inventory.model_dump_json())
        return res
    
    async def delete_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inventory: schema.Inventory):
        id = self.auth(token)["id"]
        user_service = self.__services["user"]
        return await user_service.request("delete", f"/inventories/{id}", dict)
    
    async def delete_inv_item(self, token: Annotated[str, Depends(oauth2_scheme)],inv_id: int, inv_item: schema.Inventory):
        id = self.auth(token)["id"]
        user_service = self.__services["user"]
        return await user_service.request("delete", f"/inventories/{inv_id}/{inv_item.id}", dict)
    
    async def put_inv(self, token: Annotated[str, Depends(oauth2_scheme)], inventory: schema.Inventory):
        id = self.auth(token)["id"]
        user_service = self.__services["user"]
        return await user_service.request("put", f"/inventories/{inventory.id}", dict)

    

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
