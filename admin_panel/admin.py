from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from akademk.models import Course, Group, Schedule, Student, Enrollment
from hisoblar.models import User, Role, RolePermission
from ishtirok.models import Attendance, Homework, HomeworkSubmission, Score
from moliya.models import Payment, Debt
from potential.models import Lead
from yadro.models import Center, Branch, Room, ActivityLog


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "domain",
        "plan",
        "status",
    ]
    list_filter = ["plan", "status"]
    search_fields = ["name", "domain"]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "center",
        "phone",
    ]
    list_filter = ["center"]
    search_fields = ["name", "address"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "branch", "capacity"]
    list_filter = ["center", "branch"]
    search_fields = ["name"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "action",
        "target_table",
        "target_id",
    ]
    list_filter = [
        "action",
        "target_table",
    ]
    search_fields = ["action"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "name", "role", "center", "status"]
    list_filter = ["role", "status", "center"]
    search_fields = ["email", "name", "phone"]
    ordering = ["email"]  # ← username o'rniga email

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "center",
                    "branch",
                    "status",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "role", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ["last_login"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["role", "permission_key"]
    list_filter = ["role"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "center",
        "price",
    ]
    list_filter = ["center"]
    search_fields = ["name", "description"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "course", "teacher", "branch", "status", "start_date"]
    list_filter = ["center", "branch", "status"]
    search_fields = ["name"]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["group", "day_of_week", "start_time", "end_time", "room"]
    list_filter = ["day_of_week"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "parent_name",
        "parent_phone",
    ]
    search_fields = ["user__name", "parent_name", "parent_phone"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "group", "start_date", "status"]
    list_filter = ["status", "group"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "group", "lesson_date", "status", "marked_by"]
    list_filter = ["status", "lesson_date", "group"]
    search_fields = ["student__user__name"]


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ["title", "group", "due_date", "created_by"]
    list_filter = ["group", "due_date"]
    search_fields = ["title"]


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ["student", "homework", "status", "grade", "submitted_at"]
    list_filter = ["status", "homework"]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "group",
        "score",
        "created_by",
    ]
    list_filter = [
        "group",
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "amount",
        "method",
        "status",
    ]
    list_filter = [
        "method",
        "status",
    ]
    search_fields = ["transaction_id", "student__user__name"]


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ["student", "amount", "due_date", "status"]
    list_filter = ["status", "due_date"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "status",
        "source",
        "assigned_to",
    ]
    list_filter = [
        "status",
        "source",
    ]
    search_fields = ["name", "phone", "email"]
