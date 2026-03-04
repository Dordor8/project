from src.deployable.dbs import MongoDBService

if __name__ == '__main__':
    m = MongoDBService()
    m.drop_db('test')
    print(m.client.list_database_names())
