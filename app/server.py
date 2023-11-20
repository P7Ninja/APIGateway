from apigateway import APIGateway, Service
from apigateway.Authentication import JWTEncoder
from fastapi import FastAPI
from dotenv import dotenv_values
import os

if os.path.exists(".env"):
    cfg = dotenv_values(".env")

cfg["DB_CONN"] = os.environ.get("DB_CONN", cfg["DB_CONN"])

cfg["CLIENT"] = os.environ.get("CLIENT", cfg["CLIENT"])
cfg["USER_SERVICE"] = os.environ.get("USER_SERVICE", cfg["USER_SERVICE"])
cfg["HEALTH_SERVICE"] = os.environ.get("HEALTH_SERVICE", cfg["HEALTH_SERVICE"])
cfg["MEALPLAN_SERVICE"] = os.environ.get("MEALPLAN_SERVICE", cfg["MEALPLAN_SERVICE"])
cfg["RECIPE_SERVICE"] = os.environ.get("RECIPE_SERVICE", cfg["RECIPE_SERVICE"])
cfg["FOOD_SERVICE"] = os.environ.get("FOOD_SERVICE", cfg["FOOD_SERVICE"])
cfg["INVENTORY_SERVICE"] = os.environ.get("INVENTORY_SERVICE", cfg["INVENTORY_SERVICE"])

cfg["EXPIRE"] = os.environ.get("EXPIRE", cfg["EXPIRE"])
cfg["JWT_SECRET"] = os.environ.get("JWT_SECRET", cfg["JWT_SECRET"])
cfg["JWT_ALG"] = os.environ.get("JWT_ALG", cfg["JWT_ALG"])

tags_metadata = [
    {"name": "users", "description": "Operations with users"},
    {"name": "health", "description": "Operations with health"},
    {"name": "auth", "description": "Authentication"},
    {"name": "mealplan", "description": "Operations with mealplans"},
    {"name": "recipe", "description": "Operations with recipes"},
    {"name": "food", "description": "Operations with food"},
    {"name": "inventory", "description": "Operations with inventory"}
]


app = FastAPI(title="APIGateway", openapi_tags=tags_metadata)
gateway = APIGateway(app, cfg, JWTEncoder(cfg), {
    "user": Service(cfg["USER_SERVICE"]),
    "health": Service(cfg["HEALTH_SERVICE"])
    },
    [cfg['CLIENT']]
    )
gateway.configure_routes()
