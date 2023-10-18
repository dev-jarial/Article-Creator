import uuid
from app.db.base_class import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.authentications.user import User


def generate_uuid():
    return str(uuid.uuid4())

class Setting(Base):
    __tablename__ = "settings"

    setting_id = Column(String(255), primary_key=True, default=generate_uuid)
    api_key = Column(String(length=255))
    user_id = Column(String(255), ForeignKey('users.id'))
    prompt_id = Column(String(255), ForeignKey('prompts.prompt_id'))
    user = relationship(User, backref="settings")