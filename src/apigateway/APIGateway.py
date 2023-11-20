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
        self.__app.add_api_route("/user", self.get_user, methods=["GET"], status_code=200, response_model=schema.User, tags=["users"])
        self.__app.add_api_route("/user", self.create_user, methods=["POST"], status_code=201, tags=["users"])
        self.__app.add_api_route("/user", self.delete_user, methods=["DELETE"], status_code=200, tags=["users"])
        self.__app.add_api_route("/login", self.login, methods=["POST"], status_code=200, tags=["auth"])

        self.__app.add_api_route("/health", self.create_health, methods=["POST"], status_code=201, tags=["health"])
        self.__app.add_api_route("/health/{id}", self.delete_health, methods=["DELETE"], status_code=200, tags=["health"])
        self.__app.add_api_route("/health/history", self.get_health_history, methods=["GET"], status_code=200, tags=["health"])

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
        return await user_service.request("get", f"/user/{id}", dict)


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

