from abc import ABC, abstractmethod
from src.exceptions import DeploymentException
from pymongo import MongoClient
import configparser
from sqlalchemy import create_engine, Column, INT, String, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import declarative_base

config = configparser.ConfigParser()
config.read('config.ini')

engine = create_engine(
    f"postgresql+psycopg2://{config['POSTGRES']['user']}:{config['POSTGRES']['password']}@{config['POSTGRES']['host']}:{config['POSTGRES']['port']}")

Base = declarative_base()


class Deployment(Base):
    __tablename__ = 'deployments'
    id = Column(INT, primary_key=True)
    db_name = Column(String)
    status = Column(BOOLEAN)
    username = Column(String)
    created_at = Column(TIMESTAMP)


class DBService(ABC):
    @abstractmethod
    def new_deployment(self, db_name: str, username: str) -> str:
        pass

    @abstractmethod
    def get_deployment_info(self, db_name: str, username: str) -> str:
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
        self.client = MongoClient(f"mongodb://{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}")
        Base.metadata.create_all(bind=engine)
        print(Base.metadata.tables.keys())

    def new_deployment(self, db_name: str, username: str) -> str:
        pass

    def get_deployment_info(self, db_name: str, username: str) -> str:
        pass

    def update_database_name(self, current_db_name: str, new_db_name: str, username: str) -> str:
        pass

    def drop_deployment(self, db_name: str, username: str) -> str:
        pass

    def get_deployment_connection_string(self, db_name: str, username: str) -> str:
        pass
