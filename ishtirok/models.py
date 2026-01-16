from django.db import models
from django.utils.translation import gettext_lazy as _
from akademk.models import Student, Group
from hisoblar.models import User


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="attendances"
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_payments"
    )
    lesson_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="marked_attendances"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance"
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")
        unique_together = [["group", "student", "lesson_date"]]

    def __str__(self):
        return f"{self.student.user.name} - {self.lesson_date} - {self.status}"


class Homework(models.Model):
    group = models.ForeignKey(
        "akademk.Group", on_delete=models.CASCADE, related_name="homeworks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_homeworks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "homeworks"
        verbose_name = _("Homework")
        verbose_name_plural = _("Homeworks")

    def __str__(self):
        group_name = self.group.name if self.group else "Unknown Group"
        return f"{group_name} - {self.title}"


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
    ]

    homework = models.ForeignKey(
        Homework, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="homework_submissions"
    )
    file_path = models.FileField(upload_to="homeworks/", blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "homework_submissions"
        verbose_name = _("Homework Submission")
        verbose_name_plural = _("Homework Submissions")
        unique_together = [["homework", "student"]]

    def __str__(self):
        return f"{self.student.user.name} - {self.homework.title}"


class Score(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="scores"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="scores")
    score = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_scores"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scores"
        verbose_name = _("Score")
        verbose_name_plural = _("Scores")

    def __str__(self):
        return f"{self.student.user.name} - {self.score}"
