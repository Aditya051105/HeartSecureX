import joblib

# Load your trained model
model = joblib.load("heart_disease_model.pkl")

def predict_heart_disease(data):
    """
    data: list of feature values
    """
    prediction = model.predict([data])
    return int(prediction[0])
