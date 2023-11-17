from apigateway import APIGateway, Service
from apigateway.Authentication import JWTEncoder
from fastapi import FastAPI
from dotenv import dotenv_values
import os


cfg = os.environ
app = FastAPI(title="APIGateway")
gateway = APIGateway(app, cfg, JWTEncoder(cfg), {
    "user": Service(cfg["USER_SERVICE"])
    },
    [cfg['CLIENT']]
    )
gateway.configure_routes()
