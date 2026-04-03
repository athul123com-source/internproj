from django.contrib import admin

from .models import AnalysisRun, UserProfile


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ("filename", "role", "resume_score", "created_at")
    search_fields = ("filename", "role")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "college", "target_role", "graduation_year")
    search_fields = ("user__username", "full_name", "college", "target_role")
