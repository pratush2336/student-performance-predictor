Student Performance Predictor

A beginner-friendly machine learning project that predicts a student's performance score based on study hours, attendance, and previous grade.

About the Project

This project uses Linear Regression from scikit-learn to learn the relationship between student study habits, attendance, previous grades, and performance scores.

The trained model can then be used to predict the performance score of a new student.

Features

- Takes student name as input
- Takes daily study hours
- Takes attendance percentage
- Takes previous grade
- Uses a trained Linear Regression model
- Predicts a performance score
- Classifies performance as Excellent, Good, or Needs Improvement

Technologies Used

- Python
- Pandas
- Scikit-learn
- Joblib
- Linear Regression
- CSV Dataset

How It Works

1. The student dataset is loaded from a CSV file.
2. Study hours, attendance, and previous grade are used as input features.
3. A Linear Regression model is trained using the dataset.
4. The trained model is saved for later use.
5. The user enters a student's details.
6. The saved model predicts the student's performance score.
7. The predicted score is classified into a performance category.

Project Structure

student-performance-predictor/
│
├── src/
│   ├── predict.py
│   └── student_performance_model.pkl
│
├── student-performance.py
├── students.csv
├── .gitignore
└── README.md

How to Run

1. Train the model

Run:

python student-performance.py

2. Run the prediction program

Run:

python src/predict.py

The program will ask for:

- Student name
- Daily study hours
- Attendance percentage
- Previous grade

It will then display the predicted performance score and performance category.

Example

Student Performance Predictor

Enter student name: Shambhavi
Enter daily study hours: 7.5
Enter attendance percentage: 90
Enter previous grade: 85

Predicted Performance Score: 97.08
Predicted Performance: Excellent

Learning Objective

This project was created as a beginner machine learning project to understand how a dataset can be used to train a model, evaluate it, save the trained model, and make predictions from new data.

Future Improvements

- Add a larger real-world dataset
- Improve model evaluation
- Add data visualizations
- Try other machine learning algorithms
- Create a simple web interface
- Improve prediction accuracy with more data