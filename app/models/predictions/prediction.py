import uuid

from app.db.base_class import Base

from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, JSON, TEXT, DateTime
from sqlalchemy.orm import relationship
from app.models.predictions.tool import Tool



def generate_uuid():
    return str(uuid.uuid4())

class Prediction(Base):
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    status = Column(String(20), nullable=False)
    inputs = Column(JSON(), nullable=False)
    outputs = Column(JSON(), nullable=False)
    extra_data = Column(JSON(), nullable=False)
    logs = Column(TEXT())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    starting_at = Column(DateTime())
    completed_at = Column(DateTime())
    tool: str = Column(ForeignKey("tools.name"))
    tool_detail = relationship(Tool)

    files = relationship("File", back_populates="prediction")


    __tablename__ = 'predictions'

class File(Base):
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    file_url = Column(String(200))
    prediction_id = Column(String, ForeignKey("predictions.id"))

    prediction = relationship("Prediction", back_populates="files")

    params = Column(JSON(), nullable=False)

    __tablename__ = 'files'
