from src.logic.manager import MongoDBService, engine
from sqlalchemy import inspect

if "__main__" == __name__:
    m = MongoDBService()
    print(m.get_deployment_info('59398f9c-17e9-11f1-a854-70a6cc1ea52c'))
