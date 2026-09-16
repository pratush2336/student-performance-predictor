import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
data=pd.read_csv("students.csv")
print("\nStudent dataset:")
print(data)

print("\ndataset information:")
print(data.info())

X = data[["study_hours", "attendance", "previous_grade"]]
y = data["performance_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

test_predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, test_predictions)
print("\nModel Mean Absolute Error:", mae)

print("Student Performance Predictor")
name=input("Enter student name: ")
study_hours=float(input("Enter daily study hours: "))
attendance=float(input("Enter attendance percentage: "))
previous_grade=float(input("Enter previous grade: "))
print("\nstudent details:")
print("Name:", name)
print("Daily Study Hours:", study_hours)
print("Attendance:", attendance ,"%")
print("Previous Grade:", previous_grade)

score = model.predict(pd.DataFrame([[study_hours, attendance, previous_grade]], columns=["study_hours", "attendance", "previous_grade"]))[0]
print("\nPredicted Performance Score:", score)

if score>=80:
    performance="Excellent"
elif score>=60:
    performance="Good"
else:
    performance="Needs Improvement"

print("Predicted Performance:", performance)