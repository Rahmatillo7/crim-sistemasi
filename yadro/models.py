from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Center(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'centers'
        verbose_name = _('Center')
        verbose_name_plural = _('Centers')

    def __str__(self):
        return self.name


class Branch(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')
        unique_together = [['center', 'name']]

    def __str__(self):
        return f"{self.center.name} - {self.name}"


class Room(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='rooms')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=20)

    class Meta:
        db_table = 'rooms'
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)
    target_table = models.CharField(max_length=100)
    target_id = models.IntegerField()
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        verbose_name = _('Activity Log')
        verbose_name_plural = _('Activity Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action}"