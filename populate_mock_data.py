import os
import csv
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_insights.settings')
django.setup()

from django.utils.dateparse import parse_datetime
from django.utils import timezone
from analytics.models import Course, Student, ActivityLog
from analytics.machine_learning import run_ml_pipeline

def populate_from_csv(filename="sample_lms_logs.csv"):
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist. Run 'generate_sample_csv.py' first.")
        return

    print("Clearing old LMS log database entries...")
    ActivityLog.objects.all().delete()
    
    # Keep courses and students if they exist, or clear them to start fresh
    # Course.objects.all().delete()
    # Student.objects.all().delete()

    print(f"Reading logs from {filename}...")
    
    logs_created = 0
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            s_id = row['student_id']
            s_name = row['student_name']
            s_email = row['student_email']
            c_code = row['course_code']
            c_name = row['course_name']
            timestamp_str = row['timestamp']
            action = row['action']
            duration_str = row['duration']

            # Get or create
            course, _ = Course.objects.get_or_create(
                course_code=c_code,
                defaults={'course_name': c_name}
            )

            student, _ = Student.objects.get_or_create(
                student_id=s_id,
                defaults={'name': s_name, 'email': s_email}
            )

            # DateTime parsing
            parsed_dt = parse_datetime(timestamp_str)
            if not parsed_dt:
                try:
                    parsed_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    parsed_dt = timezone.now()

            if parsed_dt and timezone.is_naive(parsed_dt):
                parsed_dt = timezone.make_aware(parsed_dt)

            # Create log entry
            ActivityLog.objects.create(
                student=student,
                course=course,
                timestamp=parsed_dt,
                action=action,
                duration=int(duration_str)
            )
            logs_created += 1

    print(f"Imported {logs_created} activity logs.")
    
    print("Running Machine Learning model pipeline on imported logs...")
    predictions_updated = run_ml_pipeline()
    print(f"ML Pipeline complete. Generated/updated {predictions_updated} student risk predictions.")

if __name__ == '__main__':
    populate_from_csv()
