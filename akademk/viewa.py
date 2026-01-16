from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Course, Group, Schedule, Student, Enrollment
from .ruxsatnomalar import IsManager
from .serializers import (
    CourseSerializer,
    GroupSerializer,
    ScheduleSerializer,
    StudentSerializer,
    EnrollmentSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsManager]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["center"]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Course.objects.all()
        return Course.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsManager]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["center", "branch", "course", "teacher", "status"]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Group.objects.all()
        elif user.role == "teacher":
            return Group.objects.filter(teacher=user)
        return Group.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        group = self.get_object()
        enrollments = Enrollment.objects.filter(group=group, status="active")
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["group", "day_of_week"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Schedule.objects.all()
        elif user.role == "teacher":
            return Schedule.objects.filter(group__teacher=user)
        return Schedule.objects.filter(group__center=user.center)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsManager]
    search_fields = [
        "user__name",
        "user__email",
        "user__phone",
        "parent_name",
        "parent_phone",
    ]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Student.objects.all()
        return Student.objects.filter(user__center=user.center)

    @action(detail=True, methods=["get"])
    def enrollments(self, request, pk=None):
        student = self.get_object()
        enrollments = Enrollment.objects.filter(student=student)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["student", "group", "status"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Enrollment.objects.all()
        return Enrollment.objects.filter(group__center=user.center)
