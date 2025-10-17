// Save registration data and go to symptoms page
document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      let user = {
        name: document.getElementById("name").value,
        age: document.getElementById("age").value,
        mobile: document.getElementById("mobile").value,
        email: document.getElementById("email").value,
      };
      localStorage.setItem("user", JSON.stringify(user));
      window.location.href = "symptoms.html";
    });
  }

  const symptomsForm = document.getElementById("symptomsForm");
  if (symptomsForm) {
    symptomsForm.addEventListener("submit", (e) => {
      e.preventDefault();
      let symptoms = {
        Gender: document.getElementById("Gender").value,
        Cholesterol: document.getElementById("Cholesterol").value,
        BloodPressure: document.getElementById("BloodPressure").value,
        HeartRate: document.getElementById("HeartRate").value,
        Smoking: document.getElementById("Smoking").value,
        AlcoholIntake: document.getElementById("AlcoholIntake").value,
        ExerciseHours: document.getElementById("ExerciseHours").value,
        FamilyHistory: document.getElementById("FamilyHistory").value,
        Diabetes: document.getElementById("Diabetes").value,
        Obesity: document.getElementById("Obesity").value,
        StressLevel: document.getElementById("StressLevel").value,
        BloodSugar: document.getElementById("BloodSugar").value,
        ExerciseInducedAngina: document.getElementById("ExerciseInducedAngina").value,
        ChestPainType: document.getElementById("ChestPainType").value,
      };
      localStorage.setItem("symptoms", JSON.stringify(symptoms));

      // TODO: Replace this mock prediction with backend API call
      let prediction = Math.random() > 0.5 ? "High Risk of Heart Disease 💔" : "Low Risk ✅";
      localStorage.setItem("prediction", prediction);

      window.location.href = "result.html";
    });
  }

  const predictionText = document.getElementById("predictionText");
  if (predictionText) {
    let user = JSON.parse(localStorage.getItem("user"));
    let prediction = localStorage.getItem("prediction");
    document.getElementById("userInfo").innerText = 
      `${user.name} (Age: ${user.age}, Mobile: ${user.mobile}, Email: ${user.email})`;
    predictionText.innerText = prediction;
  }
});
