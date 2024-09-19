"""
Handle AUTH endpoints.
create a route object to handle the authentication endpoints.
exports a route object to be used in the main app.

Methods:
- sign_in: sign in a user in the system
- sign_up: sign up a user in the system
- sign_out: sign out a user in the system

Author: Einar Jhordany Serna Valdivia
Version: 1.0.0
Date: November 7th, 2022
"""

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from .. import database
from ..middlewares.auth import denylist
from ..middlewares.responses import Responses
from ..models.users import Users

response = Responses()


bearer = HTTPBearer()
auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Security dependency for basic authentication
security = HTTPBasic()


@auth.get("/sign-in")
async def sign_in(
    db: Session = Depends(database.valuaciones),
    credentials: HTTPBasicCredentials = Depends(security),
):
    # credentials = await request.json()

    username = credentials.username
    password = credentials.password

    try:
        user = Users(db=db, Schema="BASE")
        if user.filter(email=username) is None:
            return response.error(status_code=404, message="Usuario no encontrado")
        if user.current.estatus == 0:
            return response.error(status_code=401, message="Usuario inactivo")
        if not user.check_password(password):
            return response.error(status_code=401, message="Credenciales Incorrectas")
        if (token := user.encode()) is None:
            return response.error(
                status_code=422, message="No se pudo generar el token"
            )

        return response.success(
            message=f"Bienvenido {user.current.nombre}!",
            data=user.dict(),
            headers={"Authorization": f"Bearer {token}"},
        )

    except Exception as e:
        print(f"----------> Unexpected error:\n {str(e)}")
        return response.error(message=str(e))
