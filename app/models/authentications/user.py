import uuid

from app.db.base_class import Base

from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, JSON, TEXT, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    name = Column(String, name="name", nullable=True)
    email = Column(EmailType, name="email", unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, name="username", unique=True, nullable=False)
    status = Column(String, name="status", default="active")
    createdAt = Column(DateTime, name="created_at", default=func.now())
    updatedAt = Column(DateTime, name="updated_at", default=func.now(), onupdate=func.now())

    api_keys = relationship('APIKey', back_populates='user')

    __tablename__ = 'users'

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str) -> None:
        self.password = pwd_context.hash(password)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    expiration = Column(DateTime)  # Add the expiration field
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="api_keys")

