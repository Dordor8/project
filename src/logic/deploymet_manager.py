import configparser
import datetime
from abc import ABC, abstractmethod
from uuid import uuid1

from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, BOOLEAN, TIMESTAMP, and_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from src.exceptions import DeploymentException

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
    def get_deployment_info(self, deployment_id: str) -> dict:
        pass

    @abstractmethod
    def update_database_name(self, deployment_id: str, new_db_name: str, username: str) -> str:
        pass

    @abstractmethod
    def drop_deployment(self, deployment_id: str, username: str) -> None:
        pass

    @abstractmethod
    def get_deployment_connection_string(self, db_name: str, username: str) -> str:
        pass


class MongoDBService(DBService):
    def __init__(self):
        self.mongo_client = MongoClient(
            f"mongodb://{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}")
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    @staticmethod
    def check_deployment_exist(deployment: Deployment | None):
        if not deployment:
            raise DeploymentException("Deployment id not found")

    @staticmethod
    def check_deployment_username(deployment: Deployment, username: str):
        if deployment.username != username:
            raise DeploymentException("Username not create this deployment")

    @staticmethod
    def check_name_startwith_username(db_name: str, username: str):
        if not db_name.startswith(username):
            raise DeploymentException("Deployment name must start with the username")

    def check_deployment_name_availability(self, db_name: str):
        if self.session.query(Deployment).filter(and_(Deployment.db_name == db_name, Deployment.status == True)).first():
            raise DeploymentException("Deployment name do not exists")

    def get_deployment_by_id(self, deployment_id: str) -> Deployment | None:
        return self.session.query(Deployment).filter(and_(Deployment.id == deployment_id,
                                                           Deployment.status == True)).first()

    def new_deployment(self, db_name: str, username: str) -> str:
        if self.session.query(Deployment).filter(and_(Deployment.db_name == db_name, Deployment.status == True)).first():
            raise DeploymentException("Deployment name already exists")

        self.check_name_startwith_username(db_name, username)

        deployment_id: str = str(uuid1())
        self.session.add(Deployment(id=deployment_id, db_name=db_name, status=True, username=username,
                                    created_at=datetime.datetime.now()))

        db = self.mongo_client[db_name]
        db.create_collection('holder')  # temp table so the db will create

        self.session.commit()
        return deployment_id

    def get_deployment_info(self, deployment_id: str) -> dict:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)

        return {'id': deployment.id, 'db_name': deployment.db_name, 'created_at': deployment.created_at}



    def update_database_name(self, deployment_id: str, new_db_name: str, username: str) -> str:
        deployment = self.get_deployment_by_id(deployment_id)

        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)
        self.check_deployment_name_availability(new_db_name)
        self.check_name_startwith_username(new_db_name, username)

        db = self.mongo_client[str(deployment.db_name)]
        # TODO : change db name

        deployment.db_name = new_db_name
        self.session.commit()

        return deployment_id

    def drop_deployment(self, deployment_id: str, username: str) -> None:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)

        deployment.status = False
        self.mongo_client.drop_database(str(deployment.db_name))

        self.session.commit()

    def get_deployment_connection_string(self, deployment_id: str, username: str) -> str:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)

        return f"mongodb://{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}/{deployment.db_name}"