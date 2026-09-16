import pandas as pd
data=pd.read_csv("students.csv")
print("\nStudent dataset:")
print(data)

print("\ndataset information:")
print(data.info())

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

score = (study_hours * 5) + (attendance * 0.3) + (previous_grade * 0.4)
print("\nPredicted Performance Score:", score)

if score>=80:
    preformance="Excellent"
elif score>=60:
    preformance="Good"
else:
    preformance="Needs Improvement"

print("Predicted Performance:", preformance)