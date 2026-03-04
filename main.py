from src.logic.manager import MongoDBService, engine
from sqlalchemy import inspect

if "__main__" == __name__:
    m = MongoDBService()
    print(m.new_deployment('test-my_db2', 'test'))
