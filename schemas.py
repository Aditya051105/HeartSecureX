from pydantic import BaseModel

class HeartDiseaseInput(BaseModel):
    Age: int
    Gender: int
    Cholesterol: int
    BloodPressure: int
    HeartRate: int
    Smoking: int
    AlcoholIntake: int
    ExerciseHours: int
    Family_History: int
    Diabetes: int
    Obesity: int
    Stress_Level: int
    Blood_Sugar: int
    Exercise_Induced_Angina: int
    Chest_Pain_Type: int
    Heart_Disease_Type: int