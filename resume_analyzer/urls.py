from django.contrib import admin
from django.urls import include, path

from analyzer.views import logout_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", __import__("django.contrib.auth.views", fromlist=["LoginView"]).LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", logout_view, name="logout"),
    path("", include("analyzer.urls")),
]
