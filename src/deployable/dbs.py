from abc import ABC, abstractmethod
from typing import Any


class DBService(ABC):
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def disconnect(self):
        pass
    @abstractmethod
    def create_db(self, db_name: str, username: str) -> str:
        pass
    @abstractmethod
    def drop_db(self, db_name: str) -> None:
        pass
    @abstractmethod
    def get_db(self, db_name: str) -> Any:
        pass
    @abstractmethod
    def update_db(self, db_current_name: str, db_new_db_name: str) -> str:
        pass
