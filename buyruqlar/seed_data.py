from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from akademk.models import Course, Group, Schedule, Student, Enrollment
from hisoblar.models import User
from moliya.models import Payment
from yadro.models import Center, Branch, Room


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # Create Center
        center = Center.objects.create(
            name="IT Academy", domain="itacademy.uz", plan="premium", status="active"
        )
        self.stdout.write(self.style.SUCCESS(f"Created center: {center.name}"))

        # Create Branches
        branch1 = Branch.objects.create(
            center=center,
            name="Chilonzor",
            address="Chilonzor, Tashkent",
            phone="+998901234567",
        )

        branch2 = Branch.objects.create(
            center=center,
            name="Yunusobod",
            address="Yunusobod, Tashkent",
            phone="+998901234568",
        )
        self.stdout.write(self.style.SUCCESS(f"Created {2} branches"))

        # Create Rooms
        Room.objects.create(center=center, branch=branch1, name="Room 101", capacity=20)
        Room.objects.create(center=center, branch=branch1, name="Room 102", capacity=15)
        Room.objects.create(center=center, branch=branch2, name="Room 201", capacity=25)
        self.stdout.write(self.style.SUCCESS(f"Created {3} rooms"))

        # Create Superadmin
        superadmin = User.objects.create_superuser(
            email="admin_panel@mambacrm.uz", password="admin123", name="Super Admin"
        )
        self.stdout.write(self.style.SUCCESS(f"Created superadmin: {superadmin.email}"))

        # Create Director
        director = User.objects.create_user(
            email="director@itacademy.uz",
            password="director123",
            name="John Director",
            role="director",
            center=center,
        )
        self.stdout.write(self.style.SUCCESS(f"Created director: {director.email}"))

        # Create Manager
        manager = User.objects.create_user(
            email="manager@itacademy.uz",
            password="manager123",
            name="Jane Manager",
            role="manager",
            center=center,
            branch=branch1,
        )
        self.stdout.write(self.style.SUCCESS(f"Created manager: {manager.email}"))

        # Create Teachers
        teacher1 = User.objects.create_user(
            email="teacher1@itacademy.uz",
            password="teacher123",
            name="Ali Valiyev",
            role="teacher",
            center=center,
            branch=branch1,
            phone="+998901111111",
        )

        teacher2 = User.objects.create_user(
            email="teacher2@itacademy.uz",
            password="teacher123",
            name="Olga Petrova",
            role="teacher",
            center=center,
            branch=branch2,
            phone="+998902222222",
        )
        self.stdout.write(self.style.SUCCESS(f"Created {2} teachers"))

        # Create Courses
        python_course = Course.objects.create(
            center=center,
            name="Python Programming",
            description="Complete Python course for beginners",
            price=800000,
        )

        web_course = Course.objects.create(
            center=center,
            name="Web Development",
            description="HTML, CSS, JavaScript, React",
            price=1000000,
        )
        self.stdout.write(self.style.SUCCESS(f"Created {2} courses"))

        # Create Groups
        today = timezone.now().date()

        group1 = Group.objects.create(
            center=center,
            branch=branch1,
            course=python_course,
            teacher=teacher1,
            name="Python-01",
            start_date=today,
            end_date=today + timedelta(days=90),
            status="active",
        )

        group2 = Group.objects.create(
            center=center,
            branch=branch2,
            course=web_course,
            teacher=teacher2,
            name="Web-01",
            start_date=today,
            end_date=today + timedelta(days=120),
            status="active",
        )
        self.stdout.write(self.style.SUCCESS(f"Created {2} groups"))

        # Create Schedules
        room1 = Room.objects.filter(branch=branch1).first()
        room2 = Room.objects.filter(branch=branch2).first()

        Schedule.objects.create(
            group=group1,
            day_of_week=1,  # Monday
            start_time="10:00",
            end_time="12:00",
            room=room1,
        )

        Schedule.objects.create(
            group=group1,
            day_of_week=3,  # Wednesday
            start_time="10:00",
            end_time="12:00",
            room=room1,
        )

        Schedule.objects.create(
            group=group2,
            day_of_week=2,  # Tuesday
            start_time="14:00",
            end_time="16:00",
            room=room2,
        )
        self.stdout.write(self.style.SUCCESS(f"Created schedules"))

        # Create Students
        for i in range(1, 6):
            user = User.objects.create_user(
                email=f"student{i}@test.uz",
                password="student123",
                name=f"Student {i}",
                role="student",
                center=center,
                branch=branch1,
                phone=f"+99890{1000000 + i}",
            )

            student = Student.objects.create(
                user=user,
                parent_name=f"Parent {i}",
                parent_phone=f"+99890{2000000 + i}",
            )

            # Enroll to group
            Enrollment.objects.create(
                student=student, group=group1, start_date=today, status="active"
            )

            # Create payment
            Payment.objects.create(
                center=center,
                student=student,
                amount=python_course.price,
                method="cash",
                status="paid",
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {5} students with enrollments and payments")
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
        self.stdout.write(self.style.WARNING(" credentials: "))
        self.stdout.write(
            self.style.WARNING("Superadmin: admin_panel@mambacrm.uz / admin123")
        )
        self.stdout.write(
            self.style.WARNING("Director: director@itacademy.uz / director123")
        )
        self.stdout.write(
            self.style.WARNING("Manager: manager@itacademy.uz / manager123")
        )
        self.stdout.write(
            self.style.WARNING("Teacher: teacher1@itacademy.uz / teacher123")
        )
        self.stdout.write(self.style.WARNING("Student: student1@test.uz / student123"))
