from abc import ABC, abstractmethod
from src.exceptions import DeploymentException
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class DBService(ABC):
    @abstractmethod
    def create_db(self, db_name: str) -> None:
        pass

    @abstractmethod
    def drop_db(self, db_name: str) -> None:
        pass


class MongoDBService(DBService):
    def __init__(self):

        self.client = MongoClient(config['DEPLOYMENTS_URL']['mongodb'])

    def is_db_exist(self, db_name: str) -> bool:
        return db_name in self.client.list_database_names()

    def create_db(self, db_name: str) -> None:
        if not self.is_db_exist(db_name):
            pass
        else:
            raise DeploymentException(f"MongoDB database: {db_name}  already exists")

    def drop_db(self, db_name: str) -> None:
        if self.is_db_exist(db_name):
            self.client.drop_database(db_name)
        else:
            raise DeploymentException(f"MongoDB database: {db_name}  do not exists")
