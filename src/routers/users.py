from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse

from src.routers.deployments import mongo_deployment
from src.requests_objects import UserPermissionRequest

router = APIRouter()
security = HTTPBasic()


@router.post("/users/{deployment_id}")
def add_permission(credentials: Annotated[HTTPBasicCredentials, Depends(security)], request: UserPermissionRequest):
    mongo_deployment.add_permissions_to_user(credentials.username, credentials.password, request.deployment_id, request.permission)
    return JSONResponse(
        status_code=200,
        content={"message": "The permission was added"}
    )