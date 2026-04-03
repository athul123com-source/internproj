from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    college = models.CharField(max_length=160, blank=True)
    degree = models.CharField(max_length=120, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    target_role = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.full_name or self.user.username


class AnalysisRun(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="analysis_runs")
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=120)
    filename = models.CharField(max_length=255)
    resume_score = models.PositiveIntegerField(default=0)
    analysis_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.role} - {self.filename}"
