from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Course, Student, ActivityLog, Prediction
from .machine_learning import run_ml_pipeline

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
        client = Client()
        # Log in as advisor
        self.assertTrue(client.login(username='advisor_test', password='password123'))

        # Run pipeline to ensure predictions exist
        run_ml_pipeline()

        # 1. Fetch risk alerts view without filters
        response = client.get(reverse('risk_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Risk Alerts')
        self.assertIn('alerts', response.context)
        initial_alerts_count = len(response.context['alerts'])

        # 2. Filter by search query (matching name)
        response_search = client.get(reverse('risk_alerts'), {'search': 'Test Student'})
        self.assertEqual(response_search.status_code, 200)
        self.assertEqual(len(response_search.context['alerts']), initial_alerts_count)

        # 3. Filter by search query (non-matching name)
        response_no_match = client.get(reverse('risk_alerts'), {'search': 'NonExistentStudentName'})
        self.assertEqual(response_no_match.status_code, 200)
        self.assertEqual(len(response_no_match.context['alerts']), 0)
        self.assertContains(response_no_match, 'No Alerts Match Your Filters')

        # 4. Filter by course ID
        response_course = client.get(reverse('risk_alerts'), {'course': self.course.id})
        self.assertEqual(response_course.status_code, 200)
        self.assertEqual(len(response_course.context['alerts']), initial_alerts_count)

        # 5. Filter by risk level
        response_risk = client.get(reverse('risk_alerts'), {'risk_level': 'High Risk'})
        self.assertEqual(response_risk.status_code, 200)

