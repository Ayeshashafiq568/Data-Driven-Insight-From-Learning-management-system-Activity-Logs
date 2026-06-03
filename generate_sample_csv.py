import csv
import random
from datetime import datetime, timedelta

students = [
    {"id": "STU001", "name": "Ayesha Shafiq", "email": "ayesha.shafiq@iub.edu.pk", "profile": "active"},
    {"id": "STU002", "name": "Muhammad Usman", "email": "muhammad.usman@iub.edu.pk", "profile": "active"},
    {"id": "STU003", "name": "Fatima Bibi", "email": "fatima.bibi@iub.edu.pk", "profile": "at-risk"},
    {"id": "STU004", "name": "Ahmed Ali", "email": "ahmed.ali@iub.edu.pk", "profile": "active"},
    {"id": "STU005", "name": "Zainab Jamil", "email": "zainab.jamil@iub.edu.pk", "profile": "moderate"},
    {"id": "STU006", "name": "Bilal Khan", "email": "bilal.khan@iub.edu.pk", "profile": "at-risk"},
    {"id": "STU007", "name": "Sana Malik", "email": "sana.malik@iub.edu.pk", "profile": "active"},
    {"id": "STU008", "name": "Hamza Yousaf", "email": "hamza.yousaf@iub.edu.pk", "profile": "moderate"},
    {"id": "STU009", "name": "Ali Hassan", "email": "ali.hassan@iub.edu.pk", "profile": "active"},
    {"id": "STU010", "name": "Maryam Nawaz", "email": "maryam.nawaz@iub.edu.pk", "profile": "at-risk"},
]

# Courses data
courses = [
    {"code": "CS101", "name": "Introduction to Computer Science"},
    {"code": "CS102", "name": "Data Structures & Algorithms"},
    {"code": "MATH101", "name": "Calculus & Analytical Geometry"},
    {"code": "PHY101", "name": "Applied Physics for Engineers"},
]

actions = ["access_resource", "post_forum", "submit_quiz"]

def generate_lms_csv(filename="sample_lms_logs.csv", num_records=300):
    start_time = datetime.now() - timedelta(days=14)
    records = []

    for _ in range(num_records):
        # Pick a random student
        student = random.choice(students)
        # Pick a random course
        course = random.choice(courses)
        
        # Determine duration & actions based on profile to simulate real-world behaviors
        profile = student["profile"]
        
        if profile == "active":
            action = random.choice(["access_resource", "access_resource", "post_forum", "submit_quiz"])
            duration = random.randint(600, 7200) # 10 mins to 2 hours
        elif profile == "moderate":
            action = random.choice(["access_resource", "access_resource", "post_forum"])
            duration = random.randint(300, 3600) # 5 mins to 1 hour
        else: # at-risk
            action = "access_resource" # rarely posts or submits
            duration = random.randint(30, 900) # 30 secs to 15 mins
            # 10% chance of quiz submission
            if random.random() < 0.1:
                action = "submit_quiz"
            # 5% chance of forum post
            elif random.random() < 0.05:
                action = "post_forum"

        # Timestamp distribution over last 14 days
        random_days = random.randint(0, 13)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)
        timestamp = start_time + timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
        
        records.append({
            "student_id": student["id"],
            "student_name": student["name"],
            "student_email": student["email"],
            "course_code": course["code"],
            "course_name": course["name"],
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "duration": duration
        })

    # Sort records by timestamp
    records.sort(key=lambda x: x["timestamp"])

    # Write to CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["student_id", "student_name", "student_email", "course_code", "course_name", "timestamp", "action", "duration"])
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    print(f"Generated {num_records} mock records in '{filename}'.")

if __name__ == "__main__":
    generate_lms_csv()
