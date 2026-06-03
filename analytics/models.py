from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_ADVISOR = 'advisor'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_INSTRUCTOR, 'Instructor'),
        (ROLE_ADVISOR, 'Advisor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_INSTRUCTOR,
        help_text="Designates the role and dashboard permissions of the user."
    )

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR

    def is_advisor(self):
        return self.role == self.ROLE_ADVISOR


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True, db_index=True)
    course_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class ActivityLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_logs')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='activity_logs')
    timestamp = models.DateTimeField(db_index=True)
    action = models.CharField(max_length=50, db_index=True) # e.g. login, access_resource, submit_quiz, post_forum, view_grade
    duration = models.IntegerField(default=0, help_text="Time spent in seconds")

    def __str__(self):
        return f"{self.student.student_id} | {self.course.course_code} | {self.action} | {self.timestamp}"


class Prediction(models.Model):
    RISK_LOW = 'Low Risk'
    RISK_MEDIUM = 'Medium Risk'
    RISK_HIGH = 'High Risk'

    RISK_CHOICES = [
        (RISK_LOW, 'Low Risk'),
        (RISK_MEDIUM, 'Medium Risk'),
        (RISK_HIGH, 'High Risk'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='predictions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='predictions')
    engagement_score = models.FloatField()
    predicted_risk = models.CharField(max_length=20, choices=RISK_CHOICES, db_index=True)
    recommendation = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.student_id} | {self.course.course_code} | {self.predicted_risk} ({self.engagement_score:.1f}%)"
