from app.db.base_class import Base

from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, JSON, TEXT, DateTime
from sqlalchemy.orm import relationship

class Tool(Base):
    name = Column(String(100), primary_key=True, index=True)
    display_name = Column(String(150))
    description = Column(TEXT())

    __tablename__ = 'tools'