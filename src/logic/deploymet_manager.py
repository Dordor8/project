import configparser
import datetime
from abc import ABC, abstractmethod
from uuid import uuid1

from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, BOOLEAN, TIMESTAMP, and_, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from src.exceptions import DeploymentException, UserException
from hashlib import sha256
from sqlalchemy import Enum

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


class UserPermission(Base):
    __tablename__ = 'user_permissions'
    id = Column(String, primary_key=True)
    deployment_id = Column(ForeignKey('deployments.id'), nullable=False)
    username = Column(String)
    hashed_password = Column(String)
    permission_level = Column(String)


class DBService(ABC):
    @abstractmethod
    def new_deployment(self, db_name: str, username: str, password: str) -> str:
        pass

    @abstractmethod
    def get_deployment_info(self, deployment_id: str) -> dict:
        pass

    @abstractmethod
    def update_database_name(self, deployment_id: str, new_db_name: str, username: str, password: str) -> str:
        pass

    @abstractmethod
    def drop_deployment(self, deployment_id: str, username: str, password: str) -> None:
        pass

    @abstractmethod
    def get_deployment_connection_string(self, db_name: str, username: str, password: str) -> str:
        pass

    @abstractmethod
    def add_permissions_to_user(self, username: str, password: str, deployment_id: str, permission) -> None:
        pass


class MongoDBService(DBService):
    def __init__(self):
        self.mongo_client = MongoClient(
            f"mongodb://{config['DEPLOYMENTS_PRAM']['mongo_admin_user']}:{config['DEPLOYMENTS_PRAM']['mongo_admin_password']}@{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}")
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
        if self.session.query(Deployment).filter(
                and_(Deployment.db_name == db_name, Deployment.status == True)).first():
            raise DeploymentException("Deployment name do not exists")

    def get_deployment_by_id(self, deployment_id: str) -> Deployment | None:
        return self.session.query(Deployment).filter(and_(Deployment.id == deployment_id,
                                                          Deployment.status == True)).first()

    @staticmethod
    def check_password_valid(password: str) -> None:
        if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password)):
            raise UserException("Invalid password, must have at least 8 letters, 1 upper and 1 lower case letters")

    @staticmethod
    def check_username_valid(username: str) -> None:
        if len(username) < 3:
            raise UserException("Invalid username, must have at least 3 letters")

    @staticmethod
    def hash_password(password: str) -> str:
        return sha256(password.encode()).hexdigest()

    @staticmethod
    def check_editing_permission(permission: type[UserPermission]) -> None:
        if permission.permission_level != config['MONGO_PERMISSION']['read_and_write']:
            raise UserException("User dont have editing permission")

    def get_checked_permission(self, username: str, deployment_id: str, password: str) -> type[UserPermission]:
        permission = self.session.query(UserPermission).filter(
            and_(UserPermission.username == username,
                 UserPermission.deployment_id == deployment_id,
                 UserPermission.hashed_password == self.hash_password(password))).first()

        if not permission:
            raise UserException("Permission not found")
        else:
            return permission

    def check_permission_exist(self, username: str, password: str, deployment_id: str, permission):
        if self.session.query(UserPermission).filter(
                and_(UserPermission.username == username,
                     UserPermission.deployment_id == deployment_id,
                     UserPermission.permission_level == permission,
                     UserPermission.hashed_password == self.hash_password(password))
        ).first():
            raise UserException("Permission already exists")

    def new_deployment(self, db_name: str, username: str, password: str) -> str:
        if self.session.query(Deployment).filter(
                and_(Deployment.db_name == db_name, Deployment.status == True)).first():
            raise DeploymentException("Deployment name already exists")

        self.check_name_startwith_username(db_name, username)
        self.check_username_valid(username)

        deployment_id: str = str(uuid1())

        self.session.add(Deployment(id=deployment_id, db_name=db_name, status=True, username=username,
                                    created_at=datetime.datetime.now()))

        db = self.mongo_client[db_name]
        db.create_collection('holder')  # temp table so the db will create

        self.session.commit()

        self.add_permissions_to_user(username, password, deployment_id, config['MONGO_PERMISSION']['read_and_write'])

        self.session.commit()
        return deployment_id

    def get_deployment_info(self, deployment_id: str) -> dict:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)

        return {'id': deployment.id, 'db_name': deployment.db_name, 'created_at': deployment.created_at}


    def update_database_name(self, deployment_id: str, new_db_name: str, username: str, password: str) -> str:
        deployment = self.get_deployment_by_id(deployment_id)

        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)
        self.check_deployment_name_availability(new_db_name)
        self.check_name_startwith_username(new_db_name, username)

        permission = self.get_checked_permission(username, deployment_id, password)
        self.check_editing_permission(permission)

        db = self.mongo_client[str(deployment.db_name)]
        # TODO : change db name

        deployment.db_name = new_db_name

        self.session.commit()

        return deployment_id

    def drop_deployment(self, deployment_id: str, username: str, password: str) -> None:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)

        permission = self.get_checked_permission(username, deployment_id, password)
        self.check_editing_permission(permission)

        deployment_permissions = self.session.query(UserPermission).filter(UserPermission.deployment_id == deployment_id)
        deployment_permissions.delete()

        deployment.status = False
        self.mongo_client.drop_database(str(deployment.db_name))

        self.session.commit()

    def get_deployment_connection_string(self, deployment_id: str, username: str, password: str) -> str:
        deployment = self.get_deployment_by_id(deployment_id)
        self.check_deployment_exist(deployment)
        self.check_deployment_username(deployment, username)
        self.get_checked_permission(username, deployment_id, password)

        return f"mongodb://{username}:{password}@{config['DEPLOYMENTS_PRAM']['mongo_host']}:{config['DEPLOYMENTS_PRAM']['mongo_port']}/{deployment.db_name}"

    def add_permissions_to_user(self, username: str, password: str, deployment_id: str, permission: str) -> None:
        deployment = self.get_deployment_by_id(deployment_id)

        self.check_deployment_exist(deployment)
        self.check_password_valid(password)
        self.check_username_valid(username)
        self.check_permission_exist(username, password, deployment_id, permission)

        self.session.add(UserPermission(id=str(uuid1()) ,username=username, deployment_id=deployment_id, permission_level=permission, hashed_password=self.hash_password(password)))

        self.mongo_client[str(deployment.db_name)].command(
            'createUser', username,
            pwd=password,
            roles=[{'role': permission, 'db': str(deployment.db_name)}]
        )

        self.session.commit()