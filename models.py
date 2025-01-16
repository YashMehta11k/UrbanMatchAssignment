from sqlalchemy import Column, Integer, String
from database import Base
import json

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    _interests = Column("interests", String)

    @property
    def interests(self):
        return json.loads(self._interests) if self._interests else []

    @interests.setter
    def interests(self, value):
        self._interests = json.dumps(value) if value else "[]"