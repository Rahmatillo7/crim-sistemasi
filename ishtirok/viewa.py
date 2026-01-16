from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from akademk.models import Student, Group
from hisoblar.models import User
from moliya.models import Payment
from yadro.models import Center
from .models import Attendance, Homework, HomeworkSubmission, Score
from .serializers import (
    AttendanceSerializer,
    HomeworkSerializer,
    HomeworkSubmissionSerializer,
    ScoreSerializer,
)
from akademk.ruxsatnomalar import IsTeacher

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum


class CenterAnalyticsViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        try:
            center = Center.objects.get(id=pk)
        except Center.DoesNotExist:
            return Response({"detail": "Center not found"}, status=404)

        # --- Summary ---
        total_users = User.objects.filter(center=center).count()
        total_students = Student.objects.filter(center=center).count()
        total_groups = Group.objects.filter(center=center).count()
        active_groups = Group.objects.filter(center=center, is_active=True).count()
        total_revenue = (
            Payment.objects.filter(center=center).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        branches_count = center.branches.count()

        attendances = Attendance.objects.filter(group__center=center).select_related(
            "student", "group"
        )
        serializer = AttendanceSerializer(attendances, many=True)

        data = {
            "summary": {
                "total_users": total_users,
                "total_students": total_students,
                "total_groups": total_groups,
                "active_groups": active_groups,
                "total_revenue": total_revenue,
                "branches_count": branches_count,
            },
            "attendances": serializer.data,
        }

        return Response(data)


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    filterset_fields = ["group", "student", "lesson_date", "status"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Attendance.objects.all()
        elif user.role == "teacher":
            return Attendance.objects.filter(group__teacher=user)
        elif user.role == "student":
            return Attendance.objects.filter(student__user=user)
        return Attendance.objects.filter(group__center=user.center)

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

    @action(detail=False, methods=["post"])
    def bulk_mark(self, request):
        """Bulk attendance marking for a lesson"""
        group_id = request.data.get("group_id")
        lesson_date = request.data.get("lesson_date")
        attendances = request.data.get("attendances", [])

        created = []
        for item in attendances:
            att, _ = Attendance.objects.update_or_create(
                group_id=group_id,
                student_id=item["student_id"],
                lesson_date=lesson_date,
                defaults={"status": item["status"], "marked_by": request.user},
            )
            created.append(att)

        serializer = self.get_serializer(created, many=True)
        return Response(serializer.data)


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    filterset_fields = ["group"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Homework.objects.all()
        elif user.role == "teacher":
            return Homework.objects.filter(group__teacher=user)
        elif user.role == "student":
            from akademk.models import Enrollment

            student_groups = Enrollment.objects.filter(
                student__user=user, status="active"
            ).values_list("group_id", flat=True)
            return Homework.objects.filter(group_id__in=student_groups)
        return Homework.objects.filter(group__center=user.center)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    queryset = HomeworkSubmission.objects.all()
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["homework", "student", "status"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return HomeworkSubmission.objects.all()
        elif user.role == "teacher":
            return HomeworkSubmission.objects.filter(homework__group__teacher=user)
        elif user.role == "student":
            return HomeworkSubmission.objects.filter(student__user=user)
        return HomeworkSubmission.objects.filter(homework__group__center=user.center)

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsTeacher]
    )
    def review(self, request, pk=None):
        submission = self.get_object()
        grade = request.data.get("grade")
        feedback = request.data.get("feedback", "")

        submission.grade = grade
        submission.feedback = feedback
        submission.status = "reviewed"
        submission.reviewed_at = timezone.now()
        submission.save()

        serializer = self.get_serializer(submission)
        return Response(serializer.data)


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    filterset_fields = ["student", "group"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Score.objects.all()
        elif user.role == "teacher":
            return Score.objects.filter(group__teacher=user)
        elif user.role == "student":
            return Score.objects.filter(student__user=user)
        return Score.objects.filter(group__center=user.center)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
