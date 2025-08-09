# accounts/urls.py
from django.urls import path
from . import views
from .views import ProfileView, DashboardView

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
