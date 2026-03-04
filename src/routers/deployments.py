from fastapi import FastAPI, HTTPException, Depends, APIRouter
from typing  import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.requests_objects import DBNameRequest, DeploymentIdRequest
from src.logic.deploymet_manager import DBService, MongoDBService

router = APIRouter()
security = HTTPBasic()

mongo_deployment: DBService = MongoDBService()

@router.post("/")
def create_new_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], request: DBNameRequest):
    mongo_deployment.new_deployment(request.db_name, credentials.username)


@router.get('/{deployment_id}')
def get_deployment(deployment_id: str):
    mongo_deployment.get_deployment_info(deployment_id)

@router.put('/{deployment_id}')
def update_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str, request: DBNameRequest):
    mongo_deployment.update_database_name(deployment_id, request.db_name, credentials.username)

@router.delete('/{deployment_id}')
def delete_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str):
    mongo_deployment.drop_deployment(deployment_id, credentials.username)

@router.get('/connection_string/{deployment_id}')
def get_connection_string(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str):
    mongo_deployment.get_deployment_connection_string(deployment_id, credentials.username)