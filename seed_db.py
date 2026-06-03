import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_insights.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def seed_users():
    # 1. Create Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@iub.edu.pk',
            password='admin123',
            role=User.ROLE_ADMIN
        )
        print("Created Superuser/Admin: admin | Password: admin123")
    else:
        print("Admin user already exists.")

    # 2. Create Instructor
    if not User.objects.filter(username='instructor').exists():
        instructor = User.objects.create_user(
            username='instructor',
            email='instructor@iub.edu.pk',
            password='instructor123',
            role=User.ROLE_INSTRUCTOR
        )
        print("Created Instructor User: instructor | Password: instructor123")
    else:
        print("Instructor user already exists.")

    # 3. Create Advisor
    if not User.objects.filter(username='advisor').exists():
        advisor = User.objects.create_user(
            username='advisor',
            email='advisor@iub.edu.pk',
            password='advisor123',
            role=User.ROLE_ADVISOR
        )
        print("Created Advisor User: advisor | Password: advisor123")
    else:
        print("Advisor user already exists.")

if __name__ == '__main__':
    seed_users()
