from rest_framework import serializers
from .models import Attendance, Homework, HomeworkSubmission, Score


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'group', 'group_name', 'student', 'student_name', 'lesson_date', 'status', 'marked_by',
                  'marked_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'marked_by']


class HomeworkSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Homework
        fields = ['id', 'group', 'group_name', 'title', 'description', 'due_date', 'created_by', 'created_by_name',
                  'created_at']
        read_only_fields = ['id', 'created_at', 'created_by']


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    homework_title = serializers.CharField(source='homework.title', read_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = ['id', 'homework', 'homework_title', 'student', 'student_name', 'file_path', 'status', 'grade',
                  'feedback', 'submitted_at', 'reviewed_at']
        read_only_fields = ['id', 'submitted_at']


class ScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Score
        fields = ['id', 'student', 'student_name', 'group', 'group_name', 'score', 'comment', 'created_by',
                  'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by']