from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_path = Column(String, nullable=False)
    http_method = Column(String, nullable=False)
    source_file = Column(String, nullable=False)
    is_deprecated = Column(Boolean, nullable=False, default=False)
