from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse

from src.logic.deploymet_manager import DBService, MongoDBService
from src.requests_objects import DBNameRequest

router = APIRouter()
security = HTTPBasic()

mongo_deployment: DBService = MongoDBService()


@router.post("/users/{deployment_id}")
def create_new_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], request: DBNameRequest):
    deployment_id = mongo_deployment.new_deployment(request.db_name, credentials.username)
    return JSONResponse(
        status_code=200,
        content={"id": deployment_id}
    )