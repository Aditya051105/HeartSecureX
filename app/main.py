from flask import Flask, render_template, request, url_for
import joblib
from app.database import SessionLocal, UserInput
import os


# ✅ Initialize Flask app, specifying static & template folders
app = Flask(
    __name__,
    static_folder='static',       # folder for CSS, JS, images
    template_folder='templates'   # folder for HTML files
)

# ✅ Load your trained model
model_path = "heart_disease_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at: {model_path}")
model = joblib.load(model_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')  # optional

@app.route('/symptoms', methods=['POST'])
def symptoms():
    return render_template('symptoms.html')


# ✅ Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect form inputs
        features = [
            float(request.form['Age']),
            float(request.form['Gender']),
            float(request.form['Cholesterol']),
            float(request.form['BloodPressure']),
            float(request.form['HeartRate']),
            float(request.form['Smoking']),
            float(request.form['AlcoholIntake']),
            float(request.form['ExerciseHours']),
            float(request.form['FamilyHistory']),
            float(request.form['Diabetes']),
            float(request.form['Obesity']),
            float(request.form['StressLevel']),
            float(request.form['BloodSugar']),
            float(request.form['ExerciseInducedAngina']),
            float(request.form['ChestPainType'])
        ]

        # Make prediction
        prediction = model.predict([features])[0]

        # Map prediction (integer or string) to disease name
        disease_map = {
            0: "No Disease",
            1: "Coronary Artery Disease",
            2: "Myocardial Infarction",
            3: "Cardiomyopathy",
            4: "Heart Failure"
        }

        # Handle output type
        if isinstance(prediction, (int, float)):
            result = disease_map.get(int(prediction), "Unknown Disease")
        else:
            result = str(prediction)

        # ✅ Render result.html and pass the prediction
        return render_template('result.html', prediction=result)

    except Exception as e:
        return f"Error: {e}"


# ✅ Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
