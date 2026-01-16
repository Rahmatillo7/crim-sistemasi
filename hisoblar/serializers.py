from rest_framework import serializers
from .models import User, Role, RolePermission


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ["id", "permission_key"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions"]


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing users"""

    center_name = serializers.CharField(source="center.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "phone",
            "role",
            "status",
            "center",
            "center_name",
            "branch",
            "branch_name",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Full serializer for user details"""

    password = serializers.CharField(write_only=True, required=False)
    center_name = serializers.CharField(source="center.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "phone",
            "role",
            "status",
            "center",
            "center_name",
            "branch",
            "branch_name",
            "password",
            "is_staff",
            "is_active",
            "last_login",
        ]
        read_only_fields = ["last_login"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
