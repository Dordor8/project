from pydantic import BaseModel

class DBNameRequest(BaseModel):
    db_name: str

class DeploymentIdRequest(BaseModel):
    deployment_id: str

