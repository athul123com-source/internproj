from django.db import models
from django.contrib.auth.models import User


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
