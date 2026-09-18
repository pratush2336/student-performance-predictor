import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

data = pd.read_csv("students.csv")

X = data[["study_hours", "attendance", "previous_grade"]]
y = data["performance_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

joblib.dump(model, "student_performance_model.pkl")

test_predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, test_predictions)

print("Model trained successfully!")
print("Model Mean Absolute Error:", mae)
print("Model saved as student_performance_model.pkl")