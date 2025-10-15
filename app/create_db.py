import sqlite3

# 1. Create/connect to a database file
conn = sqlite3.connect('heart_disease.db')  # this creates the file if it doesn't exist

# 2. Create a cursor object to execute SQL commands
cursor = conn.cursor()

# 3. Create a table
cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
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
    stress_level TEXT,
    blood_sugar REAL,
    exercise_induced_angina TEXT,
    chest_pain_type TEXT,
    heart_disease TEXT
)
''')

# 4. Commit changes and close connection
conn.commit()
conn.close()

print("Database and table created successfully!")
