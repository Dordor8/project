from pydantic import BaseModel
import configparser
from enum import Enum

config = configparser.ConfigParser()
config.read('config.ini')

class PermissionsEnum(str, Enum):
    READ = config['MONGO_PERMISSION']['read']
    READ_AND_WRITE = config['MONGO_PERMISSION']['read_and_write']

class DBNameRequest(BaseModel):
    db_name: str

class DeploymentIdRequest(BaseModel):
    deployment_id: str

class UserPermissionRequest(BaseModel):
    permission: PermissionsEnum = PermissionsEnum.READ
    deployment_id: str

