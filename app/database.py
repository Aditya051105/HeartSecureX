from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///../users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserInput(Base):
    __tablename__ = "user_inputs"
    id = Column(Integer, primary_key=True, index=True)
    Age = Column(Integer)
    Gender = Column(Integer)
    Cholesterol = Column(Integer)
    Blood_pressure = Column(Integer)
    Heart_rate = Column(Integer)
    exercise_hours = Column(Integer)
    stress_level = Column(Integer)
    blood_sugar = Column(Integer)
    smoking = Column(Integer)
    alcohol_intake = Column(Integer)
    family_history = Column(Integer)
    diabetes = Column(Integer)
    obesity = Column(Integer)
    exercise_induced_angina = Column(Integer)
    chest_pain_type = Column(Integer)
    prediction = Column(Integer)

Base.metadata.create_all(bind=engine)
