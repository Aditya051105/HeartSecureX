"""
Script to properly train and save the RandomForest model
Run this script once to train and save the model to 'heart_disease_model.pkl'
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import os

# ✅ Load the dataset
csv_path = r"C:\Users\Asus\Downloads\heart_disease_types_dataset.csv"
if not os.path.exists(csv_path):
    print(f"❌ Error: {csv_path} not found!")
    exit(1)

df = pd.read_csv(csv_path)
print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {df.columns.tolist()}")
print(f"Disease categories: {df.iloc[:, -1].unique()}")

# ✅ Handle missing values
df['Alcohol Intake'] = df['Alcohol Intake'].fillna(df['Alcohol Intake'].mode()[0])

# ✅ Define numerical and categorical features
num_features = ['Age', 'Cholesterol', 'Blood Pressure', 'Heart Rate',
                'Exercise Hours', 'Stress Level', 'Blood Sugar']

cat_features = ['Gender', 'Smoking', 'Alcohol Intake', 'Family History', 
                'Diabetes', 'Obesity', 'Exercise Induced Angina', 'Chest Pain Type']

# ✅ Create preprocessor (but we'll apply it directly)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
    ]
)

# ✅ Split features and target
X = df.drop('Heart Disease Type', axis=1)
y = df['Heart Disease Type']

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"✅ Train-test split done: {X_train.shape[0]} train, {X_test.shape[0]} test")

# ✅ Preprocess the data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)
print(f"✅ Data preprocessed: {X_train_processed.shape}")

# ✅ Train the Random Forest model
print("⏳ Training Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train_processed, y_train)
print("✅ Random Forest model trained!")

# ✅ Make predictions and evaluate
y_pred_rf = rf_model.predict(X_test_processed)
accuracy = accuracy_score(y_test, y_pred_rf)
print(f"\n📊 Random Forest Accuracy: {accuracy:.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_rf))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf))

# ✅ Save the model
model_path = "heart_disease_model.pkl"
joblib.dump(rf_model, model_path)
print(f"\n✅ Model saved to: {model_path}")

# Also save the preprocessor so we can use it in the Flask app
preprocessor_path = "preprocessor.pkl"
joblib.dump(preprocessor, preprocessor_path)
print(f"✅ Preprocessor saved to: {preprocessor_path}")
