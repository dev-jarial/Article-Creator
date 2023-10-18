import uuid

from app.db.base_class import Base

from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, JSON, TEXT, DateTime, Float
from sqlalchemy.orm import relationship
from app.models.authentications.user import User


def generate_uuid():
    return str(uuid.uuid4())


class Prompt(Base):
    __tablename__ = "prompts"

    prompt_id = Column(String(255), primary_key=True, default=generate_uuid)
    name = Column(String(length=255))
    description = Column(TEXT)
    text_area = Column(TEXT)
    gpt_model = Column(String(length=255))
    temperature = Column(Float)
    max_length = Column(Integer)
    top_p = Column(Float)
    frequency_penalty = Column(Float)
    presence_penalty = Column(Float)
    created_at = Column(DateTime)
    user = relationship(User, backref="prompt")
    user_id = Column(String(255), ForeignKey('users.id', name='prompt_ibfk_1'))

