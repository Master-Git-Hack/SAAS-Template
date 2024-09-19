from fastapi import FastAPI

app = FastAPI()

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}



"""Principal File to handle the app"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT

# from fastapi_pagination import add_pagination
from loguru import logger

from .config import Config

# from fastapi_sqlalchemy import DBSessionMiddleware


config = Config()

from .middlewares.database import Instance


database = Instance()



def create_app() -> FastAPI:
    """Configure the app"""
    current_app = FastAPI(
        **config.fastapi_params,
    )
    current_app.add_middleware(
        CORSMiddleware,
        **config.cors_params,
    )
    # current_app.add_middleware(
    #     DBSessionMiddleware, db_url=config.SQLALCHEMY_DATABASE_URL
    # )
    # add_pagination(current_app)
    return current_app


# Definition of the app
app = create_app()


@AuthJWT.load_config
def get_config():
    """Load configuration"""
    return config.Settings()


from .routes import *
