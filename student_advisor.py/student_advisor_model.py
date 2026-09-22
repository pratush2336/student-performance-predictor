from datetime import datetime, timedelta
import json
import os
import random

# FILE FOR DAILY SCHEDULE
SCHEDULE_FILE = "daily_schedule.json"


# 
# 1. STUDY SCORE PREDICTOR
#

def predict_score(hours_studied, difficulty="medium", consistency=0.8):
    """
    Simple study score predictor.

    hours_studied: total hours prepared for the subject
    difficulty: easy / medium / hard
    consistency: 0.0 to 1.0
    """

    base = min(hours_studied * 8, 85)

    difficulty_factor = {
        "easy": 1.15,
        "medium": 1.0,
        "hard": 0.85
    }.get(difficulty.lower(), 1.0)

    consistency_bonus = consistency * 12

    predicted = base * difficulty_factor + consistency_bonus

    predicted = max(
        25,
        min(98, round(predicted + random.uniform(-4, 4), 1))
    )

    return predicted


def give_advice(score):
    if score >= 85:
        return "Excellent! Maintain consistency and do light revision."
    elif score >= 70:
        return "Good progress. Focus on weak topics + past papers."
    elif score >= 55:
        return "Average. Increase focused hours and reduce distractions."
    else:
        return "Needs serious improvement. Start with fundamentals + daily practice."



# 2. WEEKLY TIMETABLE GENERATOR


def generate_timetable(subjects, daily_hours=6, start_time="09:00", days=7):
    """
    Creates a weekly timetable with study blocks and short breaks.
    """

    if not subjects:
        return "No subjects provided."

    num_subjects = len(subjects)

    session_length = min(
        1.5,
        max(0.75, daily_hours / num_subjects)
    )

    start = datetime.strptime(start_time, "%H:%M")

    timetable = {}

    for day in range(1, days + 1):

        day_name = (
            datetime.now() + timedelta(days=day - 1)
        ).strftime("%A")

        sessions = []
        current = start

        day_subjects = subjects.copy()
        random.shuffle(day_subjects)

        remaining_hours = daily_hours

        for subject in day_subjects:

            if remaining_hours <= 0.3:
                break

            duration = min(session_length, remaining_hours)

            end = current + timedelta(hours=duration)

            sessions.append({
                "subject": subject,
                "start": current.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "duration": round(duration, 1)
            })

            remaining_hours -= duration

            # 10-minute break
            current = end + timedelta(minutes=10)

        timetable[f"Day {day} ({day_name})"] = sessions

    return timetable


def print_timetable(timetable):

    print("\n" + "=" * 55)
    print("           YOUR PERSONALIZED STUDY TIMETABLE")
    print("=" * 55)

    for day, sessions in timetable.items():

        print(f"\n{day}")
        print("-" * 45)

        for session in sessions:
            print(
                f"  {session['start']} - {session['end']}  |  "
                f"{session['subject']:<18} "
                f"({session['duration']}h)"
            )

        print()



# 3. DAILY SCHEDULE MANAGER


def load_schedule():

    if os.path.exists(SCHEDULE_FILE):

        with open(SCHEDULE_FILE, "r") as file:
            return json.load(file)

    return {
        "date": str(datetime.now().date()),
        "tasks": []
    }


def save_schedule(schedule):

    with open(SCHEDULE_FILE, "w") as file:
        json.dump(schedule, file, indent=2)


def calculate_study_benefit(tasks):

    study_minutes = 0
    study_blocks = 0
    break_count = 0

    for task in tasks:

        duration = task.get("duration_minutes", 0)
        category = task.get("category", "").lower()

        if category == "study":
            study_minutes += duration
            study_blocks += 1

        elif category == "break":
            break_count += 1

    study_hours = study_minutes / 60

    score = 0

    score += min(study_hours * 15, 60)
    score += min(study_blocks * 5, 20)
    score += min(break_count * 3, 15)

    if 3 <= study_hours <= 6:
        score += 5

    return round(min(score, 100), 1), study_hours


def show_schedule(schedule):

    print("\n" + "=" * 50)
    print(f"  DAILY SCHEDULE — {schedule['date']}")
    print("=" * 50)

    if not schedule["tasks"]:

        print("  No tasks yet. Add some!")
        return []

    sorted_tasks = sorted(
        schedule["tasks"],
        key=lambda task: task["start"]
    )

    for i, task in enumerate(sorted_tasks, 1):

        print(
            f"{i}. {task['start']} - {task['end']}  |  "
            f"{task['title']}"
        )

        print(
            f"   Category: {task['category']}  |  "
            f"Duration: {task['duration_minutes']} min"
        )

        if task.get("notes"):
            print(f"   Notes: {task['notes']}")

        print("-" * 45)

    score, hours = calculate_study_benefit(
        schedule["tasks"]
    )

    print(f"\n Total Study Time : {hours:.1f} hours")
    print(f" Study Benefit Score: {score}/100")

    if score >= 80:
        print(" Excellent! Very beneficial day for studying.")

    elif score >= 60:
        print(" Good progress. Keep it up!")

    elif score >= 40:
        print(" Average. Try to add more focused study blocks.")

    else:
        print(" Low study benefit. Plan more study time tomorrow.")

    return sorted_tasks


def add_task(schedule):

    print("\n--- Add New Task ---")

    title = input(
        "Task title (e.g. Math Chapter 5): "
    ).strip()

    if not title:

        print("Title cannot be empty.")
        return

    category = input(
        "Category (study / break / meal / exercise / other): "
    ).strip().lower()

    if category not in [
        "study",
        "break",
        "meal",
        "exercise",
        "other"
    ]:
        category = "other"

    start = input(
        "Start time (HH:MM, 24-hour format, e.g. 09:30): "
    ).strip()

    duration_str = input(
        "Duration in minutes (e.g. 90): "
    ).strip()

    try:

        duration = int(duration_str)

        if duration <= 0:

            print("Duration must be a positive number.")
            return

        start_dt = datetime.strptime(start, "%H:%M")

        end_dt = start_dt + timedelta(
            minutes=duration
        )

        end = end_dt.strftime("%H:%M")

    except ValueError:

        print("Invalid time or duration. Please try again.")
        return

    notes = input(
        "Notes (optional): "
    ).strip()

    task = {
        "title": title,
        "category": category,
        "start": start,
        "end": end,
        "duration_minutes": duration,
        "notes": notes
    }

    schedule["tasks"].append(task)

    save_schedule(schedule)

    print("Task added successfully!")


def delete_task(schedule):

    if not schedule["tasks"]:

        print("No tasks to delete.")
        return

    sorted_tasks = show_schedule(schedule)

    try:

        idx = int(
            input("\nEnter task number to delete: ")
        ) - 1

        if 0 <= idx < len(sorted_tasks):

            task_to_remove = sorted_tasks[idx]

            schedule["tasks"].remove(
                task_to_remove
            )

            save_schedule(schedule)

            print(
                f"Deleted: {task_to_remove['title']}"
            )

        else:

            print("Invalid number.")

    except ValueError:

        print("Please enter a valid number.")


def reset_schedule():

    confirm = input(
        "Are you sure you want to clear today's schedule? (yes/no): "
    ).lower()

    if confirm == "yes":

        schedule = {
            "date": str(datetime.now().date()),
            "tasks": []
        }

        save_schedule(schedule)

        print("Schedule reset.")

        return schedule

    return load_schedule()



# 4. STUDENT ADVISOR


def student_advisor():

    print("\n--- STUDENT ADVISOR ---")

    try:

        marks = float(
            input(
                "Enter your marks/previous grade (0-100): "
            ) or 60
        )

        marks = max(0, min(100, marks))

    except ValueError:

        marks = 60

    try:

        attendance = float(
            input(
                "Enter your attendance percentage (0-100): "
            ) or 75
        )

        attendance = max(0, min(100, attendance))

    except ValueError:

        attendance = 75

    try:

        study_hours = float(
            input("Study hours per day: ") or 3
        )

        study_hours = max(0, study_hours)

    except ValueError:

        study_hours = 3

    # Performance assessment
    if marks >= 80:

        performance = "Excellent"

    elif marks >= 60:

        performance = "Good"

    elif marks >= 40:

        performance = "Needs Improvement"

    else:

        performance = "Needs Immediate Improvement"

    print("\n" + "=" * 50)
    print("          STUDENT ADVISORY REPORT")
    print("=" * 50)

    print(
        f"\nAcademic Performance : {performance}"
    )

    print(
        f"Marks                 : {marks:.1f}%"
    )

    print(
        f"Attendance            : {attendance:.1f}%"
    )

    print(
        f"Study Hours/Day       : {study_hours:.1f}"
    )

    
    # KEY OBSERVATIONS
   

    print("\n" + "-" * 50)
    print("KEY OBSERVATIONS")
    print("-" * 50)

    if marks >= 80:

        print("✓ Academic performance is strong.")

    elif marks >= 60:

        print("• Academic performance is satisfactory.")

    elif marks >= 40:

        print("⚠ Academic performance needs improvement.")

    else:

        print(
            "⚠ Academic performance needs significant improvement."
        )

    if attendance < 75:

        print(
            "⚠ Attendance is the main area requiring attention."
        )

    else:

        print(
            "✓ Attendance is at an acceptable level."
        )

    if study_hours >= 4:

        print("✓ Study commitment is good.")

    elif study_hours >= 2:

        print("• Study time is reasonable.")

    else:

        print(
            "⚠ Daily study time should be increased."
        )

   
    # ADVICE
    

    print("\n" + "-" * 50)
    print("ADVICE")
    print("-" * 50)

    if marks >= 80:

        print(
            "Your academic performance is strong."
        )

        print(
            "Focus on maintaining consistency and deeper understanding."
        )

    elif marks >= 60:

        print(
            "Your performance is good."
        )

        print(
            "Focus on weak topics and regular revision."
        )

    elif marks >= 40:

        print(
            "You should give more attention to your studies."
        )

        print(
            "Strengthen your fundamentals and practice regularly."
        )

    else:

        print(
            "Your studies need significant improvement."
        )

        print(
            "Start with basic concepts and follow a consistent routine."
        )

    if attendance < 75:

        print(
            "Improve your attendance by attending classes more regularly."
        )

    elif attendance < 85:

        print(
            "Try to improve your attendance toward 85% or above."
        )

    else:

        print(
            "Maintain your good attendance."
        )

    if study_hours < 2:

        print(
            "Gradually increase your daily study time."
        )

    elif study_hours < 4:

        print(
            "Maintain your study routine and add regular revision."
        )

    else:

        print(
            "Good study commitment. Make sure your sessions are effective."
        )

    
    # PRIORITY AREA
    

    if attendance < 75:

        priority = "Attendance"

    elif marks < 60:

        priority = "Academic Performance"

    elif study_hours < 2:

        priority = "Study Consistency"

    else:

        priority = "Maintaining Overall Performance"

    target_score = min(100, marks + 10)

    print("\n" + "-" * 50)
    print(f"Priority Area: {priority}")
    print(
        f"Suggested Next Target: {target_score:.1f}%"
    )
    print("-" * 50)


# MAIN MENU


def main():

    print("=" * 55)
    print("     STUDENT STUDY TOOLKIT")
    print("  (Predictor + Timetable + Daily Schedule)")
    print("=" * 55)

    while True:

        print("\nWhat would you like to do?")

        print("1. Study Score Predictor")
        print("2. Student Advisor")
        print("3. Daily Schedule Manager")
        print("4. Generate Weekly Timetable")
        print("5. Exit")

        choice = input(
            "\nEnter choice (1-5): "
        ).strip()

        
        # OPTION 1 — STUDY SCORE PREDICTOR
        

        if choice == "1":

            print("\n--- STUDY PREDICTOR ---")

            subject = input(
                "Enter subject name: "
            ).strip() or "Mathematics"

            try:

                hours = float(
                    input("Hours studied so far: ") or 12
                )

            except ValueError:

                hours = 12

            difficulty = input(
                "Difficulty (easy/medium/hard): "
            ).strip() or "medium"

            score = predict_score(
                hours,
                difficulty
            )

            print(
                f"\nPredicted Score for {subject}: {score}%"
            )

            print(
                "Advice:",
                give_advice(score)
            )

       
        # OPTION 2 — STUDENT ADVISOR
        

        elif choice == "2":

            student_advisor()

       
        # OPTION 3 — DAILY SCHEDULE MANAGER
        

        elif choice == "3":

            schedule = load_schedule()

            if schedule["date"] != str(datetime.now().date()):

                print(
                    "New day detected. Starting fresh schedule."
                )

                schedule = {
                    "date": str(datetime.now().date()),
                    "tasks": []
                }

                save_schedule(schedule)

            while True:

                print("\n--- DAILY SCHEDULE MANAGER ---")

                print(
                    "1. View today's schedule + Study Benefit Score"
                )

                print("2. Add a new task")
                print("3. Delete a task")
                print("4. Reset today's schedule")
                print("5. Back to main menu")

                sub_choice = input(
                    "\nEnter choice (1-5): "
                ).strip()

                if sub_choice == "1":

                    show_schedule(schedule)

                elif sub_choice == "2":

                    add_task(schedule)
                    schedule = load_schedule()

                elif sub_choice == "3":

                    delete_task(schedule)
                    schedule = load_schedule()

                elif sub_choice == "4":

                    schedule = reset_schedule()

                elif sub_choice == "5":

                    break

                else:

                    print(
                        "Invalid choice. Please try again."
                    )

        
        # OPTION 4 — WEEKLY TIMETABLE
        elif choice == "4":

            print("\n--- WEEKLY TIMETABLE GENERATOR ---")

            subjects_input = input(
                "Enter subjects separated by commas: "
            ).strip()

            if not subjects_input:

                print("No subjects entered.")

            else:

                subjects = [
                    subject.strip()
                    for subject in subjects_input.split(",")
                    if subject.strip()
                ]

                try:

                    daily_hours = float(
                        input(
                            "Study hours per day (default 6): "
                        ) or 6
                    )

                    if daily_hours <= 0:

                        daily_hours = 6

                except ValueError:

                    daily_hours = 6

                start_time = input(
                    "Start time (HH:MM, default 09:00): "
                ).strip() or "09:00"

                try:

                    datetime.strptime(
                        start_time,
                        "%H:%M"
                    )

                except ValueError:

                    print(
                        "Invalid time. Using 09:00."
                    )

                    start_time = "09:00"

                timetable = generate_timetable(
                    subjects,
                    daily_hours,
                    start_time,
                    7
                )

                print_timetable(timetable)

        
        # OPTION 5 — EXIT
        elif choice == "5":

            print(
                "\nGood luck with your studies! Stay consistent."
            )

            break

        else:

            print(
                "Invalid choice. Please try again."
            )


# 
# PROGRAM START
# 

if __name__ == "__main__":
    main()