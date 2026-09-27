from datetime import datetime, timedelta
import json
import os
import random



# CONFIGURATION

SCHEDULE_FILE = "daily_schedule.json"
PROGRESS_FILE = "academic_progress.json"
GOALS_FILE = "study_goals.json"


# 1. STUDY SCORE PREDICTOR

def predict_score(hours_studied, difficulty="medium", consistency=0.8):
    """
    Simple study score predictor.

    hours_studied : total hours prepared for the subject
    difficulty    : easy / medium / hard
    consistency   : value between 0.0 and 1.0
    """

    # Calculate base score
    base = min(hours_studied * 8, 85)

    # Difficulty adjustment
    difficulty_factors = {
        "easy": 1.15,
        "medium": 1.0,
        "hard": 0.85
    }

    difficulty = difficulty.lower()

    if difficulty not in difficulty_factors:
        difficulty = "medium"

    difficulty_factor = difficulty_factors[difficulty]

    # Consistency bonus
    consistency_bonus = consistency * 12

    # Final prediction
    predicted = base * difficulty_factor + consistency_bonus

    # Keep score between 25 and 98
    predicted = max(
        25,
        min(
            98,
            round(predicted + random.uniform(-4, 4), 1)
        )
    )

    return predicted


def give_advice(score):
    """Give basic advice based on predicted score."""

    if score >= 85:
        return "Excellent! Maintain consistency and do light revision."

    elif score >= 70:
        return "Good progress. Focus on weak topics and past papers."

    elif score >= 55:
        return "Average. Increase focused study hours and reduce distractions."

    else:
        return (
            "Needs serious improvement. "
            "Start with fundamentals and daily practice."
        )


# 2. WEEKLY TIMETABLE GENERATOR

def generate_timetable(
    subjects,
    daily_hours=6,
    start_time="09:00",
    days=7
):
    """
    Creates a weekly timetable with study blocks and breaks.
    """

    if not subjects:
        return {}

    # Prevent invalid study hours
    if daily_hours <= 0:
        daily_hours = 6

    if days <= 0:
        days = 7

    num_subjects = len(subjects)

    session_length = min(
        1.5,
        max(0.75, daily_hours / num_subjects)
    )

    try:
        start = datetime.strptime(
            start_time,
            "%H:%M"
        )
    except ValueError:
        start = datetime.strptime(
            "09:00",
            "%H:%M"
        )

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

            duration = min(
                session_length,
                remaining_hours
            )

            end = current + timedelta(
                hours=duration
            )

            sessions.append({
                "subject": subject,
                "start": current.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "duration": round(duration, 1)
            })

            remaining_hours -= duration

            # 10-minute break
            current = end + timedelta(minutes=10)

        timetable[
            f"Day {day} ({day_name})"
        ] = sessions

    return timetable


def print_timetable(timetable):

    print("\n" + "=" * 55)
    print("           YOUR PERSONALIZED STUDY TIMETABLE")
    print("=" * 55)

    for day, sessions in timetable.items():

        print(f"\n{day}")
        print("-" * 45)

        if not sessions:
            print("  No study sessions planned.")
            continue

        for session in sessions:

            print(
                f"  {session['start']} - "
                f"{session['end']}  |  "
                f"{session['subject']:<18} "
                f"({session['duration']}h)"
            )

    print()


def run_timetable_generator():

    print("\n--- WEEKLY TIMETABLE GENERATOR ---")

    subjects_str = input(
        "Enter subjects, comma-separated "
        "(e.g. Math, Physics, Chemistry): "
    ).strip()

    subjects = [
        s.strip() for s in subjects_str.split(",") if s.strip()
    ]

    if not subjects:
        print("No subjects entered. Using default subjects.")
        subjects = ["Math", "Physics", "Chemistry"]

    try:
        daily_hours = float(
            input("Daily study hours available (e.g. 6): ") or 6
        )
        if daily_hours <= 0:
            daily_hours = 6
    except ValueError:
        print("Invalid input. Using 6 hours.")
        daily_hours = 6

    start_time = input(
        "Preferred start time (HH:MM, default 09:00): "
    ).strip() or "09:00"

    try:
        days = int(input("Number of days to plan (default 7): ") or 7)
        if days <= 0:
            days = 7
    except ValueError:
        print("Invalid input. Using 7 days.")
        days = 7

    timetable = generate_timetable(
        subjects,
        daily_hours=daily_hours,
        start_time=start_time,
        days=days
    )

    print_timetable(timetable)


# 3. DAILY SCHEDULE MANAGER

def load_schedule():

    if os.path.exists(SCHEDULE_FILE):

        try:
            with open(
                SCHEDULE_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (json.JSONDecodeError, OSError):

            print(
                "Warning: Could not read the saved schedule."
            )

    return {
        "date": str(datetime.now().date()),
        "tasks": []
    }


def save_schedule(schedule):

    try:

        with open(
            SCHEDULE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                schedule,
                file,
                indent=2
            )

    except OSError:

        print(
            "Error: Could not save the schedule."
        )


def calculate_study_benefit(tasks):

    study_minutes = 0
    study_blocks = 0
    break_count = 0

    for task in tasks:

        duration = task.get(
            "duration_minutes",
            0
        )

        category = task.get(
            "category",
            ""
        ).lower()

        if category == "study":

            study_minutes += duration
            study_blocks += 1

        elif category == "break":

            break_count += 1

    study_hours = study_minutes / 60

    score = 0

    # Study time contribution
    score += min(
        study_hours * 15,
        60
    )

    # Number of study blocks
    score += min(
        study_blocks * 5,
        20
    )

    # Break contribution
    score += min(
        break_count * 3,
        15
    )

    # Ideal study range bonus
    if 3 <= study_hours <= 6:
        score += 5

    return round(
        min(score, 100),
        1
    ), study_hours


def show_schedule(schedule):

    print("\n" + "=" * 50)
    print(
        f"  DAILY SCHEDULE — {schedule['date']}"
    )
    print("=" * 50)

    if not schedule["tasks"]:

        print("  No tasks yet. Add some!")
        return []

    sorted_tasks = sorted(
        schedule["tasks"],
        key=lambda task: task.get(
            "start",
            "00:00"
        )
    )

    for i, task in enumerate(
        sorted_tasks,
        1
    ):

        print(
            f"{i}. {task['start']} - "
            f"{task['end']}  |  "
            f"{task['title']}"
        )

        print(
            f"   Category: {task['category']}  |  "
            f"Duration: {task['duration_minutes']} min"
        )

        if task.get("notes"):

            print(
                f"   Notes: {task['notes']}"
            )

        print("-" * 45)

    score, hours = calculate_study_benefit(
        schedule["tasks"]
    )

    print(
        f"\n Total Study Time      : "
        f"{hours:.1f} hours"
    )

    print(
        f" Study Benefit Score   : "
        f"{score}/100"
    )

    if score >= 80:

        print(
            " Excellent! Very beneficial day for studying."
        )

    elif score >= 60:

        print(
            " Good progress. Keep it up!"
        )

    elif score >= 40:

        print(
            " Average. Try to add more focused study blocks."
        )

    else:

        print(
            " Low study benefit. Plan more study time tomorrow."
        )

    return sorted_tasks


def add_task(schedule):

    print("\n--- ADD NEW TASK ---")

    title = input(
        "Task title (e.g. Math Chapter 5): "
    ).strip()

    if not title:

        print("Title cannot be empty.")
        return

    category = input(
        "Category "
        "(study / break / meal / exercise / other): "
    ).strip().lower()

    valid_categories = [
        "study",
        "break",
        "meal",
        "exercise",
        "other"
    ]

    if category not in valid_categories:

        print(
            "Invalid category. Using 'other'."
        )

        category = "other"

    start = input(
        "Start time "
        "(HH:MM, 24-hour format, e.g. 09:30): "
    ).strip()

    duration_str = input(
        "Duration in minutes (e.g. 90): "
    ).strip()

    try:

        duration = int(duration_str)

        if duration <= 0:

            print(
                "Duration must be a positive number."
            )

            return

        start_dt = datetime.strptime(
            start,
            "%H:%M"
        )

        end_dt = start_dt + timedelta(
            minutes=duration
        )

        end = end_dt.strftime(
            "%H:%M"
        )

    except ValueError:

        print(
            "Invalid time or duration. Please try again."
        )

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

    print(
        "Task added successfully!"
    )


def delete_task(schedule):

    if not schedule["tasks"]:

        print(
            "No tasks to delete."
        )

        return

    sorted_tasks = show_schedule(
        schedule
    )

    try:

        idx = int(
            input(
                "\nEnter task number to delete: "
            )
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

            print(
                "Invalid task number."
            )

    except ValueError:

        print(
            "Please enter a valid number."
        )


def reset_schedule():

    confirm = input(
        "Are you sure you want to clear "
        "today's schedule? (yes/no): "
    ).strip().lower()

    if confirm == "yes":

        schedule = {
            "date": str(
                datetime.now().date()
            ),
            "tasks": []
        }

        save_schedule(schedule)

        print(
            "Schedule reset."
        )

        return schedule

    return load_schedule()


def daily_schedule_manager():
    """Interactive loop for the Daily Schedule Manager menu."""

    schedule = load_schedule()

    # Check for a new day
    if schedule.get("date") != str(datetime.now().date()):

        print(
            "New day detected. Starting a fresh schedule."
        )

        schedule = {
            "date": str(datetime.now().date()),
            "tasks": []
        }

        save_schedule(schedule)

    while True:

        print("\n--- DAILY SCHEDULE MANAGER ---")
        print("1. View today's schedule")
        print("2. Add a task")
        print("3. Delete a task")
        print("4. Reset today's schedule")
        print("5. Back to main menu")

        sub_choice = input("\nEnter choice (1-5): ").strip()

        if sub_choice == "1":

            show_schedule(schedule)

        elif sub_choice == "2":

            add_task(schedule)

        elif sub_choice == "3":

            delete_task(schedule)

        elif sub_choice == "4":

            schedule = reset_schedule()

        elif sub_choice == "5":

            break

        else:

            print("Invalid choice. Please enter a number from 1-5.")


# 4. STUDENT ADVISOR

def student_advisor():

    print("\n--- STUDENT ADVISOR ---")

    # Marks

    try:

        marks = float(
            input(
                "Enter your marks/previous grade (0-100): "
            ) or 60
        )

        marks = max(
            0,
            min(100, marks)
        )

    except ValueError:

        print(
            "Invalid marks. Using 60."
        )

        marks = 60

    # -------------------------
    # Attendance
    # -------------------------

    try:

        attendance = float(
            input(
                "Enter your attendance percentage (0-100): "
            ) or 75
        )

        attendance = max(
            0,
            min(100, attendance)
        )

    except ValueError:

        print(
            "Invalid attendance. Using 75."
        )

        attendance = 75

    # Study Hours

    try:

        study_hours = float(
            input(
                "Study hours per day: "
            ) or 3
        )

        study_hours = max(
            0,
            study_hours
        )

    except ValueError:

        print(
            "Invalid study hours. Using 3."
        )

        study_hours = 3

    # PERFORMANCE ASSESSMENT

    if marks >= 80:

        performance = "Excellent"

    elif marks >= 60:

        performance = "Good"

    elif marks >= 40:

        performance = "Needs Improvement"

    else:

        performance = "Needs Immediate Improvement"

    # REPORT

    print("\n" + "=" * 50)
    print("          STUDENT ADVISORY REPORT")
    print("=" * 50)

    print(
        f"\nAcademic Performance : "
        f"{performance}"
    )

    print(
        f"Marks                : "
        f"{marks:.1f}%"
    )

    print(
        f"Attendance           : "
        f"{attendance:.1f}%"
    )

    print(
        f"Study Hours/Day      : "
        f"{study_hours:.1f}"
    )

    # KEY OBSERVATIONS

    print("\n" + "-" * 50)
    print("KEY OBSERVATIONS")
    print("-" * 50)

    if marks >= 80:

        print(
            "✓ Academic performance is strong."
        )

    elif marks >= 60:

        print(
            "• Academic performance is satisfactory."
        )

    elif marks >= 40:

        print(
            "⚠ Academic performance needs improvement."
        )

    else:

        print(
            "⚠ Academic performance needs "
            "significant improvement."
        )

    if attendance < 75:

        print(
            "⚠ Attendance is the main area "
            "requiring attention."
        )

    else:

        print(
            "✓ Attendance is at an acceptable level."
        )

    if study_hours >= 4:

        print(
            "✓ Study commitment is good."
        )

    elif study_hours >= 2:

        print(
            "• Study time is reasonable."
        )

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
            "Focus on maintaining consistency "
            "and deeper understanding."
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
            "Strengthen your fundamentals "
            "and practice regularly."
        )

    else:

        print(
            "Your studies need significant improvement."
        )

        print(
            "Start with basic concepts "
            "and follow a consistent routine."
        )

    # Attendance advice
    if attendance < 75:

        print(
            "Improve your attendance by "
            "attending classes more regularly."
        )

    elif attendance < 85:

        print(
            "Try to improve your attendance "
            "toward 85% or above."
        )

    else:

        print(
            "Maintain your good attendance."
        )

    # Study hours advice
    if study_hours < 2:

        print(
            "Gradually increase your daily study time."
        )

    elif study_hours < 4:

        print(
            "Maintain your study routine "
            "and add regular revision."
        )

    else:

        print(
            "Good study commitment. "
            "Make sure your sessions are effective."
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

    target_score = min(
        100,
        marks + 10
    )

    print("\n" + "-" * 50)

    print(
        f"Priority Area: {priority}"
    )

    print(
        f"Suggested Next Target: "
        f"{target_score:.1f}%"
    )

    print("-" * 50)

    # Offer to log this result into the progress tracker
    log_it = input(
        "\nLog this result in your Academic Progress "
        "Tracker? (yes/no): "
    ).strip().lower()

    if log_it == "yes":

        subject = input(
            "Subject/exam name for this record: "
        ).strip() or "General"

        log_progress_entry(subject, marks, attendance, study_hours)

        print("Saved to your progress history.")


# 5. ACADEMIC PROGRESS TRACKER

def load_progress():

    if os.path.exists(PROGRESS_FILE):

        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            print("Warning: Could not read saved progress data.")

    return {"records": []}


def save_progress(progress):

    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
            json.dump(progress, file, indent=2)

    except OSError:
        print("Error: Could not save progress data.")


def log_progress_entry(subject, marks, attendance, study_hours):
    """Add one record to the progress history and save it."""

    progress = load_progress()

    entry = {
        "date": str(datetime.now().date()),
        "subject": subject,
        "marks": round(marks, 1),
        "attendance": round(attendance, 1),
        "study_hours": round(study_hours, 1)
    }

    progress["records"].append(entry)

    save_progress(progress)

    return progress


def add_progress_entry_manual():

    print("\n--- ADD PROGRESS RECORD ---")

    subject = input("Subject/exam name: ").strip()

    if not subject:
        print("Subject name cannot be empty.")
        return

    try:
        marks = float(input("Marks/score obtained (0-100): ") or 0)
        marks = max(0, min(100, marks))
    except ValueError:
        print("Invalid marks. Using 0.")
        marks = 0

    try:
        attendance = float(
            input("Attendance for this period (0-100, optional): ") or 0
        )
        attendance = max(0, min(100, attendance))
    except ValueError:
        print("Invalid attendance. Using 0.")
        attendance = 0

    try:
        study_hours = float(
            input("Average study hours/day for this period: ") or 0
        )
        study_hours = max(0, study_hours)
    except ValueError:
        print("Invalid study hours. Using 0.")
        study_hours = 0

    log_progress_entry(subject, marks, attendance, study_hours)

    print("Progress record added successfully!")


def compute_trend(values):
    """Return a simple trend label by comparing the first half average
    to the second half average of a list of numeric values."""

    if len(values) < 2:
        return "Not enough data"

    midpoint = len(values) // 2

    first_half = values[:midpoint] or values[:1]
    second_half = values[midpoint:]

    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)

    diff = second_avg - first_avg

    if diff > 3:
        return "Improving"
    elif diff < -3:
        return "Declining"
    else:
        return "Stable"


def show_progress_summary(progress):

    records = progress.get("records", [])

    print("\n" + "=" * 55)
    print("          ACADEMIC PROGRESS TRACKER")
    print("=" * 55)

    if not records:
        print("\nNo progress records yet. Add one to get started.")
        return records

    sorted_records = sorted(records, key=lambda r: r.get("date", ""))

    print(f"\n{'#':<3} {'Date':<12} {'Subject':<18} "
          f"{'Marks':<8} {'Attendance':<12} {'Study Hrs'}")
    print("-" * 65)

    for i, record in enumerate(sorted_records, 1):
        print(
            f"{i:<3} {record.get('date', '-'):<12} "
            f"{record.get('subject', '-'):<18} "
            f"{record.get('marks', 0):<8} "
            f"{record.get('attendance', 0):<12} "
            f"{record.get('study_hours', 0)}"
        )

    all_marks = [r.get("marks", 0) for r in sorted_records]
    all_attendance = [
        r.get("attendance", 0) for r in sorted_records if r.get("attendance")
    ]

    avg_marks = sum(all_marks) / len(all_marks)
    best = max(sorted_records, key=lambda r: r.get("marks", 0))
    worst = min(sorted_records, key=lambda r: r.get("marks", 0))

    print("\n" + "-" * 55)
    print("SUMMARY")
    print("-" * 55)
    print(f"Total Records        : {len(sorted_records)}")
    print(f"Average Marks        : {avg_marks:.1f}%")
    print(f"Best Result           : {best['subject']} "
          f"({best['marks']}%) on {best['date']}")
    print(f"Weakest Result        : {worst['subject']} "
          f"({worst['marks']}%) on {worst['date']}")

    if all_attendance:
        avg_attendance = sum(all_attendance) / len(all_attendance)
        print(f"Average Attendance    : {avg_attendance:.1f}%")

    trend = compute_trend(all_marks)
    print(f"Overall Trend          : {trend}")

    if trend == "Improving":
        print("\nGreat momentum — your scores are trending upward!")
    elif trend == "Declining":
        print("\nYour recent scores are dipping. Consider revisiting"
              " study habits or asking for help on weak topics.")
    else:
        print("\nYour performance is holding steady.")

    return sorted_records


def delete_progress_entry(progress, sorted_records):

    if not sorted_records:
        print("No records to delete.")
        return progress

    try:
        idx = int(input("\nEnter record number to delete: ")) - 1

        if 0 <= idx < len(sorted_records):
            record_to_remove = sorted_records[idx]
            progress["records"].remove(record_to_remove)
            save_progress(progress)
            print(f"Deleted record for: {record_to_remove['subject']}")
        else:
            print("Invalid record number.")

    except ValueError:
        print("Please enter a valid number.")

    return progress


def academic_progress_tracker():

    progress = load_progress()

    while True:

        print("\n--- ACADEMIC PROGRESS TRACKER ---")
        print("1. View progress summary")
        print("2. Add a progress record")
        print("3. Delete a progress record")
        print("4. Back to main menu")

        sub_choice = input("\nEnter choice (1-4): ").strip()

        if sub_choice == "1":

            show_progress_summary(progress)

        elif sub_choice == "2":

            add_progress_entry_manual()
            progress = load_progress()

        elif sub_choice == "3":

            sorted_records = show_progress_summary(progress)
            progress = delete_progress_entry(progress, sorted_records)

        elif sub_choice == "4":

            break

        else:

            print("Invalid choice. Please enter a number from 1-4.")


# 6. STUDY GOAL MANAGER

def load_goals():

    if os.path.exists(GOALS_FILE):

        try:
            with open(GOALS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            print("Warning: Could not read saved goals.")

    return {"goals": []}


def save_goals(goals):

    try:
        with open(GOALS_FILE, "w", encoding="utf-8") as file:
            json.dump(goals, file, indent=2)

    except OSError:
        print("Error: Could not save goals.")


def add_goal(goals):

    print("\n--- ADD NEW GOAL ---")

    subject = input("Subject or focus area (e.g. Physics): ").strip()

    if not subject:
        print("Subject cannot be empty.")
        return goals

    goal_type = input(
        "Goal type (target_score / weekly_hours): "
    ).strip().lower()

    if goal_type not in ("target_score", "weekly_hours"):
        print("Invalid type. Using 'target_score'.")
        goal_type = "target_score"

    try:
        if goal_type == "target_score":
            target_value = float(input("Target score (0-100): ") or 80)
            target_value = max(0, min(100, target_value))
        else:
            target_value = float(input("Target study hours/week: ") or 20)
            target_value = max(0, target_value)
    except ValueError:
        print("Invalid number. Using a default value.")
        target_value = 80 if goal_type == "target_score" else 20

    deadline = input(
        "Deadline (YYYY-MM-DD, optional): "
    ).strip()

    if deadline:
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Deadline left blank.")
            deadline = ""

    goal = {
        "id": len(goals["goals"]) + 1,
        "subject": subject,
        "type": goal_type,
        "target_value": target_value,
        "current_value": 0.0,
        "deadline": deadline,
        "status": "in_progress"
    }

    goals["goals"].append(goal)

    save_goals(goals)

    print("Goal added successfully!")

    return goals


def show_goals(goals):

    print("\n" + "=" * 55)
    print("               YOUR STUDY GOALS")
    print("=" * 55)

    if not goals["goals"]:
        print("\nNo goals set yet. Add one to stay on track!")
        return

    for goal in goals["goals"]:

        target = goal.get("target_value", 0)
        current = goal.get("current_value", 0)

        progress_pct = 0
        if target > 0:
            progress_pct = min(100, round((current / target) * 100, 1))

        unit = "%" if goal["type"] == "target_score" else " hrs/week"

        bar_length = 20
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "-" * (bar_length - filled)

        status = "✓ COMPLETE" if progress_pct >= 100 else goal.get(
            "status", "in_progress"
        )

        print(f"\n#{goal['id']} {goal['subject']} "
              f"({goal['type'].replace('_', ' ')})")
        print(f"   [{bar}] {progress_pct}%")
        print(f"   Current: {current}{unit}  |  "
              f"Target: {target}{unit}")

        if goal.get("deadline"):
            print(f"   Deadline: {goal['deadline']}")

        print(f"   Status: {status}")


def update_goal_progress(goals):

    if not goals["goals"]:
        print("No goals to update.")
        return goals

    show_goals(goals)

    try:
        goal_id = int(input("\nEnter goal # to update: "))

        matching = [g for g in goals["goals"] if g["id"] == goal_id]

        if not matching:
            print("Goal not found.")
            return goals

        goal = matching[0]

        new_value = float(
            input(f"Enter new current value for '{goal['subject']}': ")
        )

        goal["current_value"] = max(0, new_value)

        if goal["target_value"] > 0 and (
            goal["current_value"] >= goal["target_value"]
        ):
            goal["status"] = "complete"
            print(f"🎉 Goal '{goal['subject']}' complete!")
        else:
            goal["status"] = "in_progress"

        save_goals(goals)

        print("Goal updated.")

    except ValueError:
        print("Please enter valid numbers.")

    return goals


def delete_goal(goals):

    if not goals["goals"]:
        print("No goals to delete.")
        return goals

    show_goals(goals)

    try:
        goal_id = int(input("\nEnter goal # to delete: "))

        matching = [g for g in goals["goals"] if g["id"] == goal_id]

        if not matching:
            print("Goal not found.")
            return goals

        goals["goals"].remove(matching[0])

        save_goals(goals)

        print("Goal deleted.")

    except ValueError:
        print("Please enter a valid number.")

    return goals


def study_goal_manager():

    goals = load_goals()

    while True:

        print("\n--- STUDY GOAL MANAGER ---")
        print("1. View goals")
        print("2. Add a goal")
        print("3. Update goal progress")
        print("4. Delete a goal")
        print("5. Back to main menu")

        sub_choice = input("\nEnter choice (1-5): ").strip()

        if sub_choice == "1":

            show_goals(goals)

        elif sub_choice == "2":

            goals = add_goal(goals)

        elif sub_choice == "3":

            goals = update_goal_progress(goals)

        elif sub_choice == "4":

            goals = delete_goal(goals)

        elif sub_choice == "5":

            break

        else:

            print("Invalid choice. Please enter a number from 1-5.")


# 7. SMART STUDY RECOMMENDATIONS

def smart_study_recommendations():
    """
    Pulls together data from the schedule, progress tracker and
    goals (where available) to generate rule-based recommendations.
    No internet or AI service is required — this is fully offline
    and rule-based.
    """

    print("\n" + "=" * 55)
    print("          SMART STUDY RECOMMENDATIONS")
    print("=" * 55)

    recommendations = []

    # ---- From today's schedule ----
    schedule = load_schedule()
    tasks = schedule.get("tasks", [])

    if tasks:
        score, hours = calculate_study_benefit(tasks)

        if hours < 2:
            recommendations.append(
                "Your planned study time today is quite low "
                f"({hours:.1f}h). Try adding at least one more "
                "focused study block."
            )
        elif hours > 8:
            recommendations.append(
                f"You've scheduled {hours:.1f}h of study today — "
                "make sure to include enough breaks to avoid burnout."
            )

        break_count = sum(
            1 for t in tasks if t.get("category", "").lower() == "break"
        )

        if break_count == 0 and hours > 2:
            recommendations.append(
                "No breaks are scheduled today. Add short breaks "
                "between study blocks to stay sharp."
            )

    else:
        recommendations.append(
            "You haven't planned today's schedule yet. Use the "
            "Daily Schedule Manager to add study blocks."
        )

    # ---- From progress history ----
    progress = load_progress()
    records = progress.get("records", [])

    if records:
        sorted_records = sorted(records, key=lambda r: r.get("date", ""))
        all_marks = [r.get("marks", 0) for r in sorted_records]

        trend = compute_trend(all_marks)

        if trend == "Declining":
            recommendations.append(
                "Your recent scores are trending down. Revisit your "
                "weakest subjects and consider shorter, more frequent "
                "revision sessions."
            )
        elif trend == "Improving":
            recommendations.append(
                "Your scores are trending upward — keep your current "
                "routine, and gradually raise your targets."
            )

        # Flag weakest subject
        weakest = min(sorted_records, key=lambda r: r.get("marks", 0))

        if weakest.get("marks", 100) < 60:
            recommendations.append(
                f"'{weakest['subject']}' is your weakest recorded "
                f"subject ({weakest['marks']}%). Consider allocating "
                "extra sessions to it this week."
            )

        avg_attendance_vals = [
            r.get("attendance", 0) for r in sorted_records
            if r.get("attendance")
        ]

        if avg_attendance_vals:
            avg_attendance = sum(avg_attendance_vals) / len(
                avg_attendance_vals
            )

            if avg_attendance < 75:
                recommendations.append(
                    "Average recorded attendance is below 75% — "
                    "improving attendance usually has a big impact "
                    "on scores."
                )

    else:
        recommendations.append(
            "No academic progress records yet. Log a result in the "
            "Academic Progress Tracker so recommendations can be "
            "tailored to your performance."
        )

    # ---- From goals ----
    goals_data = load_goals()
    goals = goals_data.get("goals", [])

    if goals:
        for goal in goals:

            target = goal.get("target_value", 0)
            current = goal.get("current_value", 0)

            if target <= 0:
                continue

            progress_pct = (current / target) * 100

            if goal.get("status") == "complete":
                continue

            if goal.get("deadline"):
                try:
                    deadline_date = datetime.strptime(
                        goal["deadline"], "%Y-%m-%d"
                    ).date()

                    days_left = (deadline_date - datetime.now().date()).days

                    if days_left < 0:
                        recommendations.append(
                            f"Goal '{goal['subject']}' is past its "
                            f"deadline ({goal['deadline']}) and only "
                            f"{progress_pct:.0f}% complete. Consider "
                            "resetting the deadline or increasing effort."
                        )
                    elif days_left <= 3 and progress_pct < 80:
                        recommendations.append(
                            f"Goal '{goal['subject']}' is due in "
                            f"{days_left} day(s) and only "
                            f"{progress_pct:.0f}% complete — prioritize "
                            "it this week."
                        )
                except ValueError:
                    pass

            elif progress_pct < 40:
                recommendations.append(
                    f"Goal '{goal['subject']}' is only "
                    f"{progress_pct:.0f}% complete. Break it into "
                    "smaller weekly targets to build momentum."
                )
    else:
        recommendations.append(
            "You haven't set any study goals yet. Use the Study "
            "Goal Manager to set a target score or weekly hours goal."
        )

    # ---- Print all recommendations ----
    if not recommendations:
        recommendations.append(
            "Everything looks on track! Keep up your current routine."
        )

    print()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    print("\n" + "-" * 55)
    print("Tip: recommendations improve as you log more schedule, "
          "progress and goal data.")
    print("-" * 55)


# MAIN MENU

def main():

    print("=" * 55)
    print("           STUDENT ACADEMIC ADVISOR")
    print("   Predictor + Advisor + Timetable + Schedule +")
    print("   Progress Tracker + Goals + Recommendations")
    print("=" * 55)

    while True:

        print("\nWhat would you like to do?")

        print("1. Study Score Predictor")
        print("2. Student Advisor")
        print("3. Daily Schedule Manager")
        print("4. Generate Weekly Timetable")
        print("5. Academic Progress Tracker")
        print("6. Study Goal Manager")
        print("7. Smart Study Recommendations")
        print("8. Exit")

        choice = input(
            "\nEnter choice (1-8): "
        ).strip()

        # OPTION 1 — STUDY SCORE PREDICTOR

        if choice == "1":

            print("\n--- STUDY SCORE PREDICTOR ---")

            subject = input(
                "Enter subject name: "
            ).strip()

            if not subject:
                subject = "Mathematics"

            try:

                hours = float(
                    input(
                        "Hours studied so far: "
                    ) or 12
                )

                if hours < 0:
                    hours = 0

            except ValueError:

                print(
                    "Invalid hours. Using 12."
                )

                hours = 12

            difficulty = input(
                "Difficulty (easy/medium/hard): "
            ).strip().lower()

            if difficulty not in [
                "easy",
                "medium",
                "hard"
            ]:

                print(
                    "Invalid difficulty. "
                    "Using medium."
                )

                difficulty = "medium"

            score = predict_score(
                hours,
                difficulty
            )

            print(
                f"\nPredicted Score for "
                f"{subject}: {score}%"
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

            daily_schedule_manager()

        # OPTION 4 — GENERATE WEEKLY TIMETABLE

        elif choice == "4":

            run_timetable_generator()

        # OPTION 5 — ACADEMIC PROGRESS TRACKER

        elif choice == "5":

            academic_progress_tracker()

        # OPTION 6 — STUDY GOAL MANAGER

        elif choice == "6":

            study_goal_manager()

        # OPTION 7 — SMART STUDY RECOMMENDATIONS

        elif choice == "7":

            smart_study_recommendations()

        # OPTION 8 — EXIT

        elif choice == "8":

            print("\nGoodbye! Keep up the great work. 📚")
            break

        else:

            print(
                "\nInvalid choice. Please enter a number from 1-8."
            )


if __name__ == "__main__":
    main()
