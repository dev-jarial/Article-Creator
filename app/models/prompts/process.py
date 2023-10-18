import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.authentications.user import User
from app.models.prompts.article import Article

def generate_uuid():
    return str(uuid.uuid4())


class Process(Base):
    __tablename__ = "process_tbl"
    section_id = Column(String(255))
    status = Column(Enum('pending', 'progress', 'completed', name='status_enum'), default='pending')
    response = Column(Text, nullable=True)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime)
    prompt_format = Column(Text)
    article_id = Column(String(255), ForeignKey('articles.article_id', name='process_ibfk_1'))
    article = relationship(Article, back_populates="processes")

    prompt_id = Column(String(255), ForeignKey('prompts.prompt_id', name='process_ibfk_1'))
    article = relationship(Article, back_populates="processes")
    # article_id = Column(String(255), ForeignKey('articles.article_id', name='process_ibfk_1'))
    id = Column(String(255), primary_key=True, default=generate_uuid )
    

