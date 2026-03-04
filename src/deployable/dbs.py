from abc import ABC, abstractmethod
from typing import Any
from pymongo import MongoClient

class DBService(ABC):
    @abstractmethod
    def create_db(self, db_name: str) -> None:
        pass

    @abstractmethod
    def drop_db(self, db_name: str) -> None:
        pass


class MongoDBService(DBService):
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")

    def is_db_exist(self, db_name: str) -> bool:
        return db_name in self.client.list_database_names()

    def create_db(self, db_name: str) -> None:
        if not self.is_db_exist(db_name):
            db = self.client[db_name]
        else:
            raise Exception()

    def drop_db(self, db_name: str) -> None:
        if self.is_db_exist(db_name):
            self.client.drop_database(db_name)
        else:
            raise Exception()
