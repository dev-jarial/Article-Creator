import uuid
from app.db.base_class import Base

from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, JSON, TEXT, DateTime
from sqlalchemy.orm import relationship

def generate_uuid():
    return str(uuid.uuid4())

class File(Base):
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    file_url = Column(String(200))
    prediction_id = Column(String, ForeignKey("predictions.id"))

    prediction = relationship("Prediction", back_populates="files")


    __tablename__ = 'files'