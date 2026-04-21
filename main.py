from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
import joblib
import os
import sqlite3
import pandas as pd
from datetime import datetime
from google import genai
from werkzeug.security import generate_password_hash, check_password_hash


# ✅ Resolve paths relative to this file
app_dir = os.path.dirname(os.path.abspath(__file__))   # .../app
project_dir = os.path.dirname(app_dir)                  # .../MINI_PROJECT

# ✅ Database path — users.db sits at the project root
DB_PATH = os.path.join(project_dir, 'users.db')

# ✅ Initialize Flask app, specifying static & template folders
app = Flask(
    __name__,
    static_folder='static',       # folder for CSS, JS, images
    template_folder='templates',  # folder for HTML files
)
app.secret_key = "your_secret_key"

# ✅ Gemini AI setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD2iU3vUsjH5RZIq2w818D1m0EhA-JMFbY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def init_db():
    """Create users.db, user_inputs table, and users table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Prediction records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            age REAL,
            gender TEXT,
            cholesterol REAL,
            blood_pressure REAL,
            heart_rate REAL,
            smoking TEXT,
            alcohol_intake TEXT,
            exercise_hours REAL,
            family_history TEXT,
            diabetes TEXT,
            obesity TEXT,
            stress_level REAL,
            blood_sugar REAL,
            exercise_induced_angina TEXT,
            chest_pain_type TEXT,
            prediction TEXT
        )
    ''')
    # Registered users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialised at: {DB_PATH}")

init_db()

# ✅ Disable caching for development
@app.after_request
def set_no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ✅ Load your trained model and preprocessor
model_path = os.path.join(app_dir, "heart_disease_model.pkl")
preprocessor_path = os.path.join(app_dir, "preprocessor.pkl")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at: {model_path}")
if not os.path.exists(preprocessor_path):
    raise FileNotFoundError(f"Preprocessor file not found at: {preprocessor_path}")

print(f"Loading model from: {model_path}")
model = joblib.load(model_path)
preprocessor = joblib.load(preprocessor_path)
print(f"Model and preprocessor loaded successfully!")

# Verify the model is fitted
if not hasattr(model, 'n_estimators') or model.n_estimators is None:
    raise ValueError("Model is not properly trained. Please run train_model.py first.")



@app.route("/")
def home():
    user = None
    if 'user_id' in session:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
    return render_template("index.html", user=user)

# ✅ Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        confirm  = request.form['confirm_password']
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        conn = sqlite3.connect(DB_PATH)
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')
        hashed = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
            (name, email, hashed, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        conn.close()
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ✅ Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name'].split()[0]}!", 'success')
            return redirect(url_for('home'))
        flash('Incorrect email or password.', 'error')
    return render_template('login.html')

# ✅ Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('home'))

# ✅ Profile route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    # Get this user's last 5 predictions
    history = conn.execute(
        'SELECT * FROM user_inputs ORDER BY id DESC LIMIT 5'
    ).fetchall()
    conn.close()
    return render_template('profile.html', user=user, history=history)

@app.route('/about')
def about():
    return render_template('about.html')  # optional

@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    return render_template('symptoms.html')


# ✅ AI Chatbot route — powered by Gemini
# Reference medicine data embedded directly in the prompt per disease
DISEASE_MEDICINE_CONTEXT = {
    "Angina": """
**Commonly used medicines for Angina (for educational reference):**
- Nitrates: Nitroglycerin (GTN), Isosorbide Mononitrate — for acute chest pain relief
- Beta-blockers: Metoprolol, Atenolol — reduce heart workload
- Calcium channel blockers: Amlodipine, Diltiazem — relax blood vessels
- Antiplatelet agents: Aspirin, Clopidogrel — prevent blood clots
- Statins: Atorvastatin, Rosuvastatin — lower cholesterol
- ACE inhibitors: Ramipril, Lisinopril — protect the heart
""",
    "Arrhythmia": """
**Commonly used medicines for Arrhythmia (for educational reference):**
- Antiarrhythmics: Amiodarone, Flecainide, Sotalol — restore normal rhythm
- Beta-blockers: Metoprolol, Bisoprolol — slow heart rate
- Calcium channel blockers: Verapamil, Diltiazem — control rate
- Anticoagulants: Warfarin, Apixaban (Eliquis), Rivaroxaban — prevent stroke from clots
- Digoxin — slows ventricular rate in atrial fibrillation
""",
    "Coronary Artery Disease": """
**Commonly used medicines for Coronary Artery Disease (for educational reference):**
- Statins: Atorvastatin (Lipitor), Rosuvastatin (Crestor) — reduce plaque buildup
- Antiplatelet agents: Aspirin, Clopidogrel (Plavix) — prevent clotting
- Beta-blockers: Metoprolol, Carvedilol — reduce cardiac workload
- ACE inhibitors/ARBs: Ramipril, Losartan — protect heart muscle
- Nitrates: Isosorbide Mononitrate — relieve chest pain
- Ranolazine — reduces angina frequency
""",
    "Heart Failure": """
**Commonly used medicines for Heart Failure (for educational reference):**
- ACE inhibitors: Enalapril, Lisinopril, Ramipril — reduce heart strain
- ARBs: Valsartan, Losartan — alternative to ACE inhibitors
- Beta-blockers: Carvedilol, Bisoprolol, Metoprolol — improve heart function
- Diuretics: Furosemide (Lasix), Spironolactone — reduce fluid buildup
- SGLT2 inhibitors: Empagliflozin (Jardiance), Dapagliflozin — newer agents shown to reduce hospitalisation
- Digoxin — strengthens heart contractions
- Sacubitril/Valsartan (Entresto) — reduces hospitalisation and death
""",
    "Healthy": """
**Preventive medicines sometimes recommended for low-risk cardiac maintenance:**
- Low-dose Aspirin — only if prescribed by a doctor for specific risk profiles
- Statins — if cholesterol levels are borderline high
- Vitamin D, Omega-3 supplements — general cardiovascular support
- Antihypertensives — only if blood pressure is elevated
"""
}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        disease = data.get('disease', 'an unknown cardiac condition').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get the disease-specific medicine context (fallback to empty string)
        medicine_context = DISEASE_MEDICINE_CONTEXT.get(disease, "")

        system_prompt = f"""You are CardioBot, a medical education assistant within HeartSecureX — a cardiac risk assessment platform.

The patient's AI-predicted condition is: {disease}

{medicine_context}

Using the medicine reference above and your medical knowledge, answer the user's question thoroughly. 

Guidelines:
- When asked about medicines, ALWAYS list the specific drug names from the reference above and explain what each one does
- When asked about treatments, describe both medical procedures and drug-based treatments
- When asked about prevention, give concrete lifestyle and dietary advice
- Use bullet points for clarity
- End every medicine-related answer with: "⚠️ Always consult your doctor before starting or stopping any medication."
- Be warm, clear, and supportive

User's question: {user_message}"""

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=system_prompt
        )
        reply = response.text

        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ✅ Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect form inputs - Create a dictionary matching the dataset columns
        raw_data = {
            'Age': float(request.form['Age']),
            'Gender': request.form['Gender'],
            'Cholesterol': float(request.form['Cholesterol']),
            'Blood Pressure': float(request.form['BloodPressure']),
            'Heart Rate': float(request.form['HeartRate']),
            'Smoking': request.form['Smoking'],
            'Alcohol Intake': request.form['AlcoholIntake'],
            'Exercise Hours': float(request.form['ExerciseHours']),
            'Family History': request.form['FamilyHistory'],
            'Diabetes': request.form['Diabetes'],
            'Obesity': request.form['Obesity'],
            'Stress Level': float(request.form['StressLevel']),
            'Blood Sugar': float(request.form['BloodSugar']),
            'Exercise Induced Angina': request.form['ExerciseInducedAngina'],
            'Chest Pain Type': request.form['ChestPainType']
        }
        
        # Create a DataFrame with proper column order matching the training data
        feature_df = pd.DataFrame([raw_data])
        
        # Preprocess the features using the same preprocessor used during training
        features_processed = preprocessor.transform(feature_df)
        
        # Make prediction
        prediction = model.predict(features_processed)[0]
        print(f"Raw prediction: {prediction} (type: {type(prediction).__name__})")

        # Map prediction to disease name
        disease_map = {
            0: "Angina",
            1: "Arrhythmia",
            2: "Coronary Artery Disease",
            3: "Healthy",
            4: "Heart Failure"
        }

        # Convert prediction to disease name
        if isinstance(prediction, str):
            # If it's already a string, use it directly
            result = prediction
        else:
            # If it's numeric, convert to int and look up
            result = disease_map.get(int(prediction), "Unknown Result")
        
        print(f"Disease Result: {result}")

        # ✅ Save user inputs + prediction to SQLite database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_inputs (
                    timestamp, age, gender, cholesterol, blood_pressure,
                    heart_rate, smoking, alcohol_intake, exercise_hours,
                    family_history, diabetes, obesity, stress_level,
                    blood_sugar, exercise_induced_angina, chest_pain_type, prediction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                raw_data['Age'],
                raw_data['Gender'],
                raw_data['Cholesterol'],
                raw_data['Blood Pressure'],
                raw_data['Heart Rate'],
                raw_data['Smoking'],
                raw_data['Alcohol Intake'],
                raw_data['Exercise Hours'],
                raw_data['Family History'],
                raw_data['Diabetes'],
                raw_data['Obesity'],
                raw_data['Stress Level'],
                raw_data['Blood Sugar'],
                raw_data['Exercise Induced Angina'],
                raw_data['Chest Pain Type'],
                result
            ))
            conn.commit()
            conn.close()
            print(f"User input saved to DB: {DB_PATH}")
        except Exception as db_err:
            print(f"Warning: Could not save to DB — {db_err}")

        # ✅ Render result.html and pass the prediction
        return render_template('result.html', prediction=result)

    except KeyError as e:
        return f"Error: Missing form field - {e}. Please fill all fields."
    except ValueError as e:
        return f"Error: Invalid input value - {e}. Please enter valid numbers."
    except Exception as e:
        return f"Error: {str(e)}"


# ✅ Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
