# accounts/urls.py
from django.urls import path
from . import views
from .views import (
    ProfileView, DashboardView, CashoutRequestCreateView,
    MarketingMaterialsView, ProductListView, ProductDetailView,
    GetAffiliateLinkView, PlaceOrderView
)

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # Cashout
    path("cashout/", CashoutRequestCreateView.as_view(), name="cashout-request"),

    # Marketing
    path("marketing-materials/", MarketingMaterialsView.as_view(), name="marketing-materials"),

    # Products (list + detail)
    path("products/", ProductListView.as_view(), name="product-list"),          # requires auth
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),  # public

    # Affiliate links (requires auth)
    path("affiliate-link/<int:product_id>/", GetAffiliateLinkView.as_view(), name="get-affiliate-link"),

    # Orders (public — customers place orders here)
    path("orders/", PlaceOrderView.as_view(), name="place-order"),
]
