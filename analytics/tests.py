from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Course, Student, ActivityLog, Prediction
from .machine_learning import run_ml_pipeline
from . import views

User = get_user_model()


class LMSAnalyticsTestCase(TestCase):
    def setUp(self):
        # Create Test Users for Role Based Access Control
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin_test@iub.edu.pk',
            password='password123',
            role=User.ROLE_ADMIN
        )
        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            email='instructor_test@iub.edu.pk',
            password='password123',
            role=User.ROLE_INSTRUCTOR
        )
        self.advisor_user = User.objects.create_user(
            username='advisor_test',
            email='advisor_test@iub.edu.pk',
            password='password123',
            role=User.ROLE_ADVISOR
        )

        self.factory = RequestFactory()

        # Create Test Course
        self.course = Course.objects.create(
            course_code='CS999',
            course_name='Test Software Engineering'
        )

        # Create Test Student
        self.student = Student.objects.create(
            student_id='STU999',
            name='Test Student Name',
            email='test.student@iub.edu.pk'
        )

        # Create Activity Logs
        # Active behavior: 5 logs, 1 submit_quiz, 1 post_forum
        ActivityLog.objects.create(
            student=self.student,
            course=self.course,
            action='access_resource',
            timestamp=timezone.now(),
            duration=1200
        )
        ActivityLog.objects.create(
            student=self.student,
            course=self.course,
            action='submit_quiz',
            timestamp=timezone.now(),
            duration=1800
        )
        ActivityLog.objects.create(
            student=self.student,
            course=self.course,
            action='post_forum',
            timestamp=timezone.now(),
            duration=600
        )

    def test_role_based_permissions(self):
        # Verify custom user methods
        self.assertTrue(self.admin_user.is_admin())
        self.assertTrue(self.instructor_user.is_instructor())
        self.assertTrue(self.advisor_user.is_advisor())

    def test_ml_pipeline_execution(self):
        # Execute pipeline
        predictions_count = run_ml_pipeline()
        
        # Verify prediction object is created
        self.assertEqual(predictions_count, 1)
        pred = Prediction.objects.get(student=self.student, course=self.course)
        
        # Verify calculations
        self.assertGreater(pred.engagement_score, 0.0)
        self.assertIn(pred.predicted_risk, ['Low Risk', 'Medium Risk', 'High Risk'])
        self.assertIsNotNone(pred.recommendation)

    def test_export_views(self):
        client = Client()
        client.login(username='instructor_test', password='password123')

        # Test PDF Export Endpoint
        pdf_response = client.get(reverse('export_pdf'))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')

        # Test Excel Export Endpoint
        excel_response = client.get(reverse('export_excel'))
        self.assertEqual(excel_response.status_code, 200)
        self.assertEqual(excel_response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_risk_alerts_filtering(self):
        # Run pipeline to ensure predictions exist
        run_ml_pipeline()

        # 1. Fetch risk alerts view without filters
        request = self.factory.get(reverse('risk_alerts'))
        request.user = self.advisor_user
        response = views.risk_alerts_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Active Risk Alerts', response.content.decode())

        # 2. Filter by search query (matching name)
        request = self.factory.get(reverse('risk_alerts'), {'search': 'Test Student'})
        request.user = self.advisor_user
        response_search = views.risk_alerts_view(request)
        self.assertEqual(response_search.status_code, 200)
        self.assertIn('Active Risk Alerts', response_search.content.decode())

        # 3. Filter by search query (non-matching name)
        request = self.factory.get(reverse('risk_alerts'), {'search': 'NonExistentStudentName'})
        request.user = self.advisor_user
        response_no_match = views.risk_alerts_view(request)
        self.assertEqual(response_no_match.status_code, 200)
        self.assertIn('No Alerts Match Your Filters', response_no_match.content.decode())

        # 4. Filter by course ID
        request = self.factory.get(reverse('risk_alerts'), {'course': self.course.id})
        request.user = self.advisor_user
        response_course = views.risk_alerts_view(request)
        self.assertEqual(response_course.status_code, 200)
        self.assertIn('Active Risk Alerts', response_course.content.decode())

        # 5. Filter by risk level
        request = self.factory.get(reverse('risk_alerts'), {'risk_level': 'High Risk'})
        request.user = self.advisor_user
        response_risk = views.risk_alerts_view(request)
        self.assertEqual(response_risk.status_code, 200)

