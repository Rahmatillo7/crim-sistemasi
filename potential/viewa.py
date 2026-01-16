from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Lead
from .serializers import LeadSerializer
from akademk.ruxsatnomalar import IsManager


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["center", "status", "source", "assigned_to"]
    search_fields = ["name", "phone", "email"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Lead.objects.all()
        return Lead.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        user = request.user

        if user.role == "superadmin":
            leads = Lead.objects.all()
        else:
            leads = Lead.objects.filter(center=user.center)

        stats = leads.values("status").annotate(count=Count("id"))

        result = {item["status"]: item["count"] for item in stats}
        result["total"] = leads.count()

        return Response(result)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        lead = self.get_object()
        lead.status = "converted"
        lead.save()

        serializer = self.get_serializer(lead)
        return Response(serializer.data)
