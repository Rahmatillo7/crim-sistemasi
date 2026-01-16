from django.db import models
from django.utils.translation import gettext_lazy as _

from akademk.models import Student
from yadro.models import Center


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("click", "Click"),
        ("payme", "Payme"),
        ("bank_transfer", "Bank Transfer"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    center = models.ForeignKey(
        Center,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="center_payments",
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendances"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.name if self.student else 'Unknown Student'} - {self.amount}"


class Debt(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="debts"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "debts"
        verbose_name = _("Debt")
        verbose_name_plural = _("Debts")
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.student.user.name if self.student else 'Unknown Student'} - {self.amount}"
