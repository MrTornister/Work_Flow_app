from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from enum import Enum

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserPermission(str, Enum):
    CREATE_PRODUCT = "create_product"
    EDIT_PRODUCT = "edit_product"
    DELETE_PRODUCT = "delete_product"
    VIEW_ORDERS = "view_orders"
    MANAGE_ORDERS = "manage_orders"
    MANAGE_USERS = "manage_users"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [perm.value for perm in UserPermission],
    UserRole.MANAGER: [
        UserPermission.CREATE_PRODUCT,
        UserPermission.EDIT_PRODUCT,
        UserPermission.VIEW_ORDERS,
        UserPermission.MANAGE_ORDERS
    ],
    UserRole.USER: [
        UserPermission.VIEW_ORDERS
    ]
}

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)