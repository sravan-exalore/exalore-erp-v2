import logging
import time
from django.db import connections
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from core.tenancy.models import Tenant

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Enterprise readiness and liveness probe for load balancers and orchestrators.
    Verifies default database connectivity and caching subsystem.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {},
        }
        all_passed = True

        # Check default PostgreSQL database
        try:
            default_conn = connections["default"]
            with default_conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
            active_tenants = Tenant.objects.using("default").filter(is_active=True).count()
            health_status["checks"]["database"] = {
                "status": "healthy",
                "active_tenants": active_tenants,
            }
        except Exception as exc:
            all_passed = False
            logger.error("Health check database failure: %s", exc)
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(exc),
            }

        # Check cache subsystem
        try:
            cache.set("__health_check__", "ok", 10)
            cached_val = cache.get("__health_check__")
            if cached_val == "ok":
                health_status["checks"]["cache"] = {"status": "healthy"}
            else:
                health_status["checks"]["cache"] = {"status": "degraded"}
        except Exception as exc:
            health_status["checks"]["cache"] = {
                "status": "degraded",
                "error": str(exc),
            }

        if not all_passed:
            health_status["status"] = "unhealthy"
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)

