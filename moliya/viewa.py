from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .serializers import PaymentSerializer, DebtSerializer
from akademk.ruxsatnomalar import IsManager
from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Payment, Debt


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["center", "student", "method", "status"]
    search_fields = ["transaction_id"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Payment.objects.all()
        return Payment.objects.filter(center=user.center)

    def perform_create(self, serializer):
        if self.request.user.role != "superadmin":
            serializer.save(center=self.request.user.center)
        else:
            serializer.save()

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        user = request.user

        if user.role == "superadmin":
            payments = Payment.objects.filter(status="paid")
        else:
            payments = Payment.objects.filter(center=user.center, status="paid")

        total_revenue = payments.aggregate(total=Sum("amount"))["total"] or 0

        by_method = {}
        for method, _ in Payment.METHOD_CHOICES:
            amount = (
                payments.filter(method=method).aggregate(total=Sum("amount"))["total"]
                or 0
            )
            by_method[method] = amount

        return Response(
            {
                "total_revenue": total_revenue,
                "by_method": by_method,
                "total_transactions": payments.count(),
            }
        )

    @action(detail=False, methods=["post"])
    def click_init(self, request):
        """Initialize Click payment"""
        student_id = request.data.get("student_id")
        amount = request.data.get("amount")

        payment = Payment.objects.create(
            center=request.user.center,
            student_id=student_id,
            amount=amount,
            method="click",
            status="pending",
        )

        return Response(
            {
                "payment_id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
            }
        )

    @action(detail=False, methods=["post"], permission_classes=[])
    def click_callback(self, request):
        """Handle Click payment callback"""
        click_trans_id = request.data.get("click_trans_id")
        merchant_trans_id = request.data.get("merchant_trans_id")
        error_code = request.data.get("error")

        try:
            payment = Payment.objects.get(id=merchant_trans_id)

            if error_code == 0:
                payment.status = "paid"
                payment.transaction_id = click_trans_id
            else:
                payment.status = "failed"

            payment.save()

            return Response({"status": "success"})
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated, IsManager]
    filterset_fields = ["student", "status"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Debt.objects.all()
        return Debt.objects.filter(student__user__center=user.center)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        debt = self.get_object()
        debt.status = "closed"
        debt.save()

        serializer = self.get_serializer(debt)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all payments"),
    retrieve=extend_schema(summary="Get payment by ID"),
    create=extend_schema(summary="Create new payment"),
    update=extend_schema(summary="Update payment"),
    partial_update=extend_schema(summary="Partially update payment"),
    destroy=extend_schema(summary="Delete payment"),
)
class PaymentViewSet(viewsets.ModelViewSet):
    """
    To'lovlar boshqaruvi - Celery bilan
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["student", "status", "method"]
    search_fields = ["student__user__name", "transaction_id"]

    def perform_create(self, serializer):
        """To'lov yaratilganda asinxron bildirishnoma yuborish"""
        from .tasks import process_payment_notification

        payment = serializer.save()
        process_payment_notification.delay(payment.id)

    @extend_schema(
        summary="Confirm payment",
        description="To'lovni tasdiqlash va bildirishnoma yuborish",
    )
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """To'lovni tasdiqlash"""
        from .tasks import process_payment_notification

        payment = self.get_object()

        if payment.status != "pending":
            return Response(
                {"error": "Only pending payments can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = "completed"
        payment.save()

        process_payment_notification.delay(payment.id)

        return Response(
            {
                "message": "Payment confirmed successfully",
                "payment": PaymentSerializer(payment).data,
            }
        )

    @extend_schema(
        summary="Send bulk payment reminders",
        description="Ko'p o'quvchilarga to'lov eslatmasi yuborish",
    )
    @action(detail=False, methods=["post"])
    def send_reminders(self, request):
        """Qarzdorlar uchun eslatma yuborish"""
        days_before = request.data.get("days_before", 3)

        task = send_payment_reminder_before_due.delay(days_before)

        return Response({"message": "Reminders are being sent", "task_id": task.id})


@extend_schema_view(
    list=extend_schema(summary="List all debts"),
    retrieve=extend_schema(summary="Get debt by ID"),
    create=extend_schema(summary="Create new debt"),
    update=extend_schema(summary="Update debt"),
    partial_update=extend_schema(summary="Partially update debt"),
    destroy=extend_schema(summary="Delete debt"),
)
class DebtViewSet(viewsets.ModelViewSet):
    """
    Qarzlar boshqaruvi
    """

    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["student", "status"]
    search_fields = ["student__user__name"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "superadmin":
            return Debt.objects.all()
        elif user.role == "student":
            return Debt.objects.filter(student__user=user)
        return Debt.objects.filter(student__user__center=user.center)

    @extend_schema(
        summary="Send reminder to student",
        description="Bitta o'quvchiga qarzdorlik eslatmasi yuborish",
    )
    @action(detail=True, methods=["post"])
    def send_reminder(self, request, pk=None):
        """Qarzdorlikka eslatma yuborish"""
        from notification.tasks import send_payment_reminder

        debt = self.get_object()

        task = send_payment_reminder.delay(debt.student.id)

        return Response({"message": "Reminder is being sent", "task_id": task.id})
