from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.logic.deploymet_manager import DBService, MongoDBService
from src.requests_objects import DBNameRequest

router = APIRouter()
security = HTTPBasic()

mongo_deployment: DBService = MongoDBService()


@router.post("/deployments/")
def create_new_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], request: DBNameRequest):
    mongo_deployment.new_deployment(request.db_name, credentials.username)


@router.get('/deployments/{deployment_id}')
def get_deployment(deployment_id: str):
    mongo_deployment.get_deployment_info(deployment_id)


@router.put('/deployments/{deployment_id}')
def update_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str,
                      request: DBNameRequest):
    mongo_deployment.update_database_name(deployment_id, request.db_name, credentials.username)


@router.delete('/deployments/{deployment_id}')
def delete_deployment(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str):
    mongo_deployment.drop_deployment(deployment_id, credentials.username)


@router.get('/deployments/connection_string/{deployment_id}')
def get_connection_string(credentials: Annotated[HTTPBasicCredentials, Depends(security)], deployment_id: str):
    mongo_deployment.get_deployment_connection_string(deployment_id, credentials.username)
