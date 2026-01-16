from datetime import date
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from akademk.models import Course, Group, Student, Enrollment
from hisoblar.models import User
from moliya.models import Payment
from yadro.models import Center, Branch


class UserAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.center = Center.objects.create(
            name="Test Center", domain="test.uz", plan="basic", status="active"
        )

        self.user = User.objects.create_user(
            email="test@test.uz",
            password="testpass123",
            name="Test User",
            role="manager",
            center=self.center,
        )

    def test_user_login(self):
        """Test user can login with correct credentials"""
        url = reverse("auth-login")
        data = {"email": "test@test.uz", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_wrong_password(self):
        """Test login fails with wrong password"""
        url = reverse("auth-login")
        data = {"email": "test@test.uz", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me(self):
        """Test authenticated user can get their info"""
        # Login first
        login_url = reverse("auth-login")
        login_data = {"email": "test@test.uz", "password": "testpass123"}
        login_response = self.client.post(login_url, login_data, format="json")
        token = login_response.data["access"]

        # Get user info
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("auth-me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@test.uz")


class CourseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.center = Center.objects.create(
            name="Test Center", domain="test.uz", status="active"
        )

        self.manager = User.objects.create_user(
            email="manager@test.uz",
            password="pass123",
            name="Manager",
            role="manager",
            center=self.center,
        )

        self.client.force_authenticate(user=self.manager)

    def test_create_course(self):
        """Test manager can create course"""
        data = {
            "center": self.center.id,
            "name": "Python Course",
            "description": "Learn Python",
            "price": "1000000.00",
        }
        response = self.client.post("/api/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_list_courses(self):
        """Test manager can list courses"""
        Course.objects.create(center=self.center, name="Course 1", price=1000000)
        Course.objects.create(center=self.center, name="Course 2", price=2000000)

        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)


class GroupTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.center = Center.objects.create(
            name="Test Center", domain="test.uz", status="active"
        )

        self.branch = Branch.objects.create(center=self.center, name="Main Branch")

        self.course = Course.objects.create(
            center=self.center, name="Python", price=1000000
        )

        self.teacher = User.objects.create_user(
            email="teacher@test.uz",
            password="pass123",
            name="Teacher",
            role="teacher",
            center=self.center,
        )

        self.manager = User.objects.create_user(
            email="manager@test.uz",
            password="pass123",
            name="Manager",
            role="manager",
            center=self.center,
        )

        self.client.force_authenticate(user=self.manager)

    def test_create_group(self):
        """Test manager can create group"""
        data = {
            "center": self.center.id,
            "branch": self.branch.id,
            "course": self.course.id,
            "teacher": self.teacher.id,
            "name": "Python-01",
            "start_date": date.today().isoformat(),
            "status": "active",
        }
        response = self.client.post("/api/groups/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AttendanceTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.center = Center.objects.create(name="Test Center", domain="test.uz")

        self.branch = Branch.objects.create(center=self.center, name="Branch")

        self.course = Course.objects.create(
            center=self.center, name="Python", price=1000000
        )

        self.teacher = User.objects.create_user(
            email="teacher@test.uz",
            password="pass123",
            name="Teacher",
            role="teacher",
            center=self.center,
        )

        self.group = Group.objects.create(
            center=self.center,
            branch=self.branch,
            course=self.course,
            teacher=self.teacher,
            name="Python-01",
            start_date=date.today(),
            status="active",
        )

        student_user = User.objects.create_user(
            email="student@test.uz",
            password="pass123",
            name="Student",
            role="student",
            center=self.center,
        )

        self.student = Student.objects.create(user=student_user, parent_name="Parent")

        Enrollment.objects.create(
            student=self.student,
            group=self.group,
            start_date=date.today(),
            status="active",
        )

        self.client.force_authenticate(user=self.teacher)

    def test_mark_attendance(self):
        """Test teacher can mark attendance"""
        data = {
            "group": self.group.id,
            "student": self.student.id,
            "lesson_date": date.today().isoformat(),
            "status": "present",
        }
        response = self.client.post("/api/attendance/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_bulk_mark_attendance(self):
        """Test bulk attendance marking"""
        data = {
            "group_id": self.group.id,
            "lesson_date": date.today().isoformat(),
            "attendances": [{"student_id": self.student.id, "status": "present"}],
        }
        response = self.client.post("/api/attendance/bulk_mark/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.center = Center.objects.create(name="Test Center", domain="test.uz")

        self.manager = User.objects.create_user(
            email="manager@test.uz",
            password="pass123",
            name="Manager",
            role="manager",
            center=self.center,
        )

        student_user = User.objects.create_user(
            email="student@test.uz",
            password="pass123",
            name="Student",
            role="student",
            center=self.center,
        )

        self.student = Student.objects.create(user=student_user)

        self.client.force_authenticate(user=self.manager)

    def test_create_payment(self):
        """Test manager can create payment"""
        data = {
            "center": self.center.id,
            "student": self.student.id,
            "amount": "1000000.00",
            "method": "cash",
            "status": "paid",
        }
        response = self.client.post("/api/payments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_payment_statistics(self):
        """Test payment statistics endpoint"""
        Payment.objects.create(
            center=self.center,
            student=self.student,
            amount=1000000,
            method="cash",
            status="paid",
        )

        response = self.client.get("/api/payments/statistics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_revenue", response.data)
