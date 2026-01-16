from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Role
from akademk.ruxsatnomalar import IsSuperAdmin, IsManager
from potential.serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    RoleSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    Login, Logout va hozirgi user ma'lumotlarini olish
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user.status != "active":
            return Response(
                {"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user, context={"request": request}).data,
            }
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="logout",
    )
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"})
        except Exception:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Userlarni ko'rish, yaratish, o'chirish va yangilash
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["role", "status", "center", "branch"]
    search_fields = ["name", "email", "phone"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return User.objects.all()
        return User.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()


class RoleViewSet(viewsets.ModelViewSet):
    """
    Rolelarni ko'rish va boshqarish
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
