# Student Performance Predictor
A beginner-friendly machine learning project that predicts a student's performance score based on study hours, attendance, and previous grade.

## About the Project
This project uses Linear Regression from scikit-learn to learn the relationship between student study habits, attendance, previous grades, and performance scores.

## Features
- Takes student name as input
- Takes daily study hours
- Takes attendance percentage
- Takes previous grade
- Uses a trained Linear Regression model
- Predicts a performance score
- Classifies performance as Excellent, Good, or Needs Improvement

## Technologies Used
- Python
- Pandas
- Scikit-learn
- Linear Regression
- CSV Dataset

## How It Works
1. The student dataset is loaded from a CSV file.
2. Study hours, attendance, and previous grade are used as input features.
3. A Linear Regression model is trained using the dataset.
4. The user enters a student's details.
5. The trained model predicts the student's performance score.
6. The predicted score is classified into a performance category.

## Project Structure
```text
 student-performance-predictor/
 │
 ├── student-performance.py
 ├── students.csv
 ├── .gitignore
 └── README.md

## Learning Objective
This project was created as a beginner machine learning project to understand how a dataset can be used to train a model and make predictions from new data.
