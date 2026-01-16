from rest_framework import serializers
from .models import Center, Branch, Room, ActivityLog


class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Center
        fields = ['id', 'name', 'domain', 'plan', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)

    class Meta:
        model = Branch
        fields = ['id', 'center', 'center_name', 'name', 'address', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'center', 'branch', 'branch_name', 'name', 'capacity']
        read_only_fields = ['id']


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action', 'target_table', 'target_id', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']