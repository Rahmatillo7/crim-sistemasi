from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from .models import Center, Branch, Room, ActivityLog
from .serializers import (
    CenterSerializer,
    BranchSerializer,
    RoomSerializer,
    ActivityLogSerializer,
)
from akademk.models import Student, Group
from akademk.ruxsatnomalar import IsSuperAdmin, IsDirector
from hisoblar.models import User
from moliya.models import Payment


class CenterViewSet(viewsets.ModelViewSet):
    queryset = Center.objects.all()
    serializer_class = CenterSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_fields = ["status", "plan"]
    search_fields = ["name", "domain"]

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        center = self.get_object()

        data = {
            "total_users": User.objects.filter(center=center).count(),
            "total_students": Student.objects.filter(user__center=center).count(),
            "total_groups": Group.objects.filter(center=center).count(),
            "active_groups": Group.objects.filter(
                center=center, status="active"
            ).count(),
            "total_revenue": Payment.objects.filter(
                center=center, status="paid"
            ).aggregate(total=Sum("amount"))["total"]
            or 0,
            "branches_count": Branch.objects.filter(center=center).count(),
        }

        return Response(data)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsDirector]
    filterset_fields = ["center"]
    search_fields = ["name", "address"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Branch.objects.all()
        return Branch.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsDirector]
    filterset_fields = ["center", "branch"]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Room.objects.all()
        return Room.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsDirector]
    filterset_fields = ["user", "action", "target_table"]
    search_fields = ["action", "target_table"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user__center=user.center)
