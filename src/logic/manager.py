from abc import ABC, abstractmethod
from src.exceptions import DeploymentException
from pymongo import MongoClient
import configparser
from sqlalchemy import create_engine, Column, INT, String, BOOLEAN, TIMESTAMP, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from uuid import uuid1
import datetime

config = configparser.ConfigParser()
config.read('config.ini')

engine = create_engine(
    f"postgresql+psycopg2://{config['POSTGRES']['user']}:{config['POSTGRES']['password']}@{config['POSTGRES']['host']}:{config['POSTGRES']['port']}")

Base = declarative_base()


class Deployment(Base):
    __tablename__ = 'deployments'
    id = Column(String, primary_key=True)
    db_name = Column(String)
    status = Column(BOOLEAN)
    username = Column(String)
    created_at = Column(TIMESTAMP)


class DBService(ABC):
    @abstractmethod
    def new_deployment(self, db_name: str, username: str) -> str:
        pass

    @abstractmethod
    def get_deployment_info(self, deployment_id: str) -> str:
        pass

    @abstractmethod
    def update_database_name(self, current_db_name: str, new_db_name: str, username: str) -> str:
        pass

    @abstractmethod
    def drop_deployment(self, db_name: str, username: str) -> str:
        pass

    @abstractmethod
    def get_deployment_connection_string(self, db_name: str, username: str) -> str:
        pass


class MongoDBService(DBService):
    def __init__(self):
        self.client = MongoClient(
            f"mongodb://{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}")
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def new_deployment(self, db_name: str, username: str) -> str:
        if self.session.query(Deployment).filter(Deployment.db_name == db_name).first():
            raise DeploymentException("Deployment name already exists")

        if not db_name.startswith(username):
            raise DeploymentException("Deployment name must start with the username")

        deployment_id: str = str(uuid1())
        self.session.add(Deployment(id=deployment_id, db_name=db_name, status=True, username=username,
                                    created_at=datetime.datetime.now()))

        db = self.client[deployment_id]
        db.create_collection('holder')  # temp table so the db will create

        self.session.commit()
        return deployment_id

    def get_deployment_info(self, deployment_id: str) -> dict:
        deployment = self.session.query(Deployment).filter(Deployment.id == deployment_id).first()
        if deployment:
            return {'id': deployment.id, 'db_name': deployment.db_name, 'created_at': deployment.created_at}
        else:
            raise DeploymentException("Deployment id not found")

    def update_database_name(self, current_db_name: str, new_db_name: str, username: str) -> str:
        pass

    def drop_deployment(self, db_name: str, username: str) -> str:
        pass

    def get_deployment_connection_string(self, db_name: str, username: str) -> str:
        pass
