from apigateway import APIGateway, Service
from apigateway.Authentication import JWTEncoder
from fastapi import FastAPI
from dotenv import dotenv_values
import os


cfg = dict()
if os.path.exists(".env"):
    cfg = dotenv_values(".env")

cfg["CLIENT"] = os.environ.get("CLIENT", cfg.get("CLIENT", None))
cfg["USER_SERVICE"] = os.environ.get("USER_SERVICE", cfg.get("USER_SERVICE", None))
cfg["HEALTH_SERVICE"] = os.environ.get("HEALTH_SERVICE", cfg.get("HEALTH_SERVICE", None))
cfg["MEALPLAN_SERVICE"] = os.environ.get("MEALPLAN_SERVICE", cfg.get("MEALPLAN_SERVICE", None))
cfg["RECIPE_SERVICE"] = os.environ.get("RECIPE_SERVICE", cfg.get("RECIPE_SERVICE", None))
cfg["FOOD_SERVICE"] = os.environ.get("FOOD_SERVICE", cfg.get("FOOD_SERVICE", None))
cfg["INVENTORY_SERVICE"] = os.environ.get("INVENTORY_SERVICE", cfg.get("INVENTORY_SERVICE", None))

cfg["EXPIRE"] = os.environ.get("EXPIRE", cfg.get("EXPIRE", None))
cfg["JWT_SECRET"] = os.environ.get("JWT_SECRET", cfg.get("JWT_SECRET", None))
cfg["JWT_ALG"] = os.environ.get("JWT_ALG", cfg.get("JWT_ALG", None))

tags_metadata = [
    {"name": "users", "description": "Operations with users"},
    {"name": "health", "description": "Operations with health"},
    {"name": "auth", "description": "Authentication"},
    {"name": "mealplan", "description": "Operations with mealplans"},
    {"name": "recipe", "description": "Operations with recipes"},
    {"name": "food", "description": "Operations with food"},
    {"name": "inventory", "description": "Operations with inventory"}
]

app = FastAPI(title="APIGateway", openapi_tags=tags_metadata, version="0.1.0")

gateway = APIGateway(app, cfg, JWTEncoder(cfg), {
    "user": Service(cfg["USER_SERVICE"]),
    "health": Service(cfg["HEALTH_SERVICE"]),
    "mealplan": Service(cfg["MEALPLAN_SERVICE"])
    },
    [cfg['CLIENT']]
    )
gateway.configure_routes()
