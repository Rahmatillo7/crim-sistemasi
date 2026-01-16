from rest_framework import serializers
from .models import Course, Group, Schedule, Student, Enrollment
from hisoblar.serializers import UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "center", "name", "description", "price", "created_at"]
        read_only_fields = ["id", "created_at"]


class ScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id",
            "group",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "room",
            "room_name",
        ]
        read_only_fields = ["id"]


class GroupSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "center",
            "branch",
            "branch_name",
            "course",
            "course_name",
            "teacher",
            "teacher_name",
            "name",
            "start_date",
            "end_date",
            "status",
            "schedules",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Student
        fields = ["id", "user", "user_id", "parent_name", "parent_phone", "created_at"]
        read_only_fields = ["id", "created_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    course_name = serializers.CharField(source="group.course.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "group",
            "group_name",
            "course_name",
            "start_date",
            "status",
        ]
        read_only_fields = ["id"]
