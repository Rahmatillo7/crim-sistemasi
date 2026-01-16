from django.db import models
from django.utils.translation import gettext_lazy as _

from hisoblar.models import User


class Course(models.Model):
    center = models.ForeignKey(
        "yadro.Center", on_delete=models.CASCADE, related_name="courses"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.name


class Group(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    ]
    center = models.ForeignKey(
        "yadro.Center", on_delete=models.CASCADE, related_name="groups"
    )
    branch = models.ForeignKey(
        "yadro.Branch", on_delete=models.CASCADE, related_name="groups"
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="groups")
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "groups"
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    def __str__(self):
        return f"{self.name} - {self.course.name}"


class Schedule(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(
        "yadro.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
    )

    class Meta:
        db_table = "schedules"
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        unique_together = [["group", "day_of_week", "start_time"]]

    def __str__(self):
        return f"{self.group.name} - {self.get_day_of_week_display()}"


class Student(models.Model):
    center = models.ForeignKey(
        "yadro.Center", on_delete=models.CASCADE, related_name="students"
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    parent_name = models.CharField(max_length=255, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self):
        return f"Student from {self.center.name}"


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("finished", "Finished"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="enrollments"
    )
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        db_table = "enrollments"
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        unique_together = [["student", "group"]]

    def __str__(self):
        return f"{self.student.user.name} - {self.group.name}"
