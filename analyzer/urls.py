from django.urls import path

from .views import detail, export_report, history, home, register, upload_resume


urlpatterns = [
    path("", home, name="home"),
    path("upload/", upload_resume, name="upload"),
    path("history/", history, name="history"),
    path("dashboard/<int:run_id>/", detail, name="detail"),
    path("dashboard/<int:run_id>/export/", export_report, name="export_report"),
    path("register/", register, name="register"),
]
