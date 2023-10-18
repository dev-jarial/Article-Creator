import uuid

from app.db.base_class import Base

from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Text, DateTime, Float, Integer
from sqlalchemy.orm import relationship
from app.models.authentications.user import User


def generate_uuid():
    return str(uuid.uuid4())


class Article(Base):
    __tablename__ = "articles"
    article_id = Column(String(255), primary_key=True, default=generate_uuid)
    language = Column(String(length=255))
    main_keywords = Column(String(length=255))
    urls = Column(String)
    status = Column(Enum('active', 'inactive', 'draft', name='status_enum'), default='draft')
    keywords = Column(Text, nullable=True)
    heading_data = Column(JSON(none_as_null=True), nullable=True)
    parsed_prompt = Column(Text, nullable = True)
    created_at = Column(DateTime)
    total_words = Column(Integer)
    cost = Column(Float, default=0.0)
    user = relationship(User, backref="article")
    user_id = Column(String(255), ForeignKey('users.id', name='article_ibfk_1'))

    processes = relationship("Process", back_populates="article")