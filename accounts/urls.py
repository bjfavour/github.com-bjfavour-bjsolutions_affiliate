# accounts/urls.py
from django.urls import path
from . import views
from .views import (
    ProfileView, DashboardView, CashoutRequestCreateView,
    MarketingMaterialsView, ProductListView,
    GetAffiliateLinkView, PlaceOrderView
)

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('cashout/', CashoutRequestCreateView.as_view(), name='cashout-request'),
    path("marketing-materials/", MarketingMaterialsView.as_view(), name="marketing-materials"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("affiliate-link/<int:product_id>/", GetAffiliateLinkView.as_view(), name="get-affiliate-link"),
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),   # ✅ keep only this
]
