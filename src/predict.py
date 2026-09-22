import pandas as pd
import joblib
from pathlib import Path

model_path = Path(__file__).resolve().parent / "student_performance_model.pkl"
model = joblib.load(model_path)

print("Student Performance Predictor")

name = input("Enter student name: ")
study_hours = float(input("Enter daily study hours: "))
attendance = float(input("Enter attendance percentage: "))
previous_grade = float(input("Enter previous grade: "))

print("\nStudent details:")
print("Name:", name)
print("Daily Study Hours:", study_hours)
print("Attendance:", attendance, "%")
print("Previous Grade:", previous_grade)

student_data = pd.DataFrame(
    [[study_hours, attendance, previous_grade]],
    columns=["study_hours", "attendance", "previous_grade"]
)

score = model.predict(student_data)[0]

score = max(0, min(100, score))
print("\nPredicted Performance Score:", round(score, 2))

if score >= 80:
    performance = "Excellent"
elif score >= 70:
    performance = "Good"
else:
    performance = "Needs Improvement"

print("Predicted Performance:", performance)