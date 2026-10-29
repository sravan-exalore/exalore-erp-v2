"""
Root URL Configuration for Exalore Multi-Tenant ERP.
"""

from django.contrib import admin
from django.urls import path, include
from core.views import HealthCheckView

urlpatterns = [
    # Administration Portal
    path("admin/", admin.site.urls),

    # System Health & Monitoring
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("api/health/", HealthCheckView.as_view(), name="api_health_check"),

    # Enterprise Versioned API (v1)
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/products/", include("apps.testapp.urls")),

    # Backward-compatible Legacy Routes
    path("user/", include("apps.authentication.urls")),
    path("prod/", include("apps.testapp.urls")),
]
