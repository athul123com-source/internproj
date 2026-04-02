from django.contrib import admin

from .models import AnalysisRun


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ("filename", "role", "resume_score", "created_at")
    search_fields = ("filename", "role")
