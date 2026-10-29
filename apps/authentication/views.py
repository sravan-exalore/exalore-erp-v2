import logging
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.serializers import LoginRequestSerializer
from apps.general.models import GnUser
from core.database.context import tenant_context
from core.tenancy.registry import register_tenant_database

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Authenticates users against the central authentication database,
    verifies tenant membership and operational state,
    and returns JWT tokens embedded with verified tenant routing claims.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials payload.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Authenticate against central authentication database
        user = authenticate(request=request, username=username, password=password)

        if not user:
            return Response(
                {"success": False, "message": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"success": False, "message": "User account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Handle tenant resolution
        tenant = getattr(user, "tenant", None)
        database = None
        gn_user_id = None

        if tenant:
            if not tenant.is_active:
                return Response(
                    {"success": False, "message": "Tenant organization is suspended or inactive."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            database = register_tenant_database(tenant)

            # Sync / verify GnUser record in tenant database
            try:
                with tenant_context(database):
                    gn_user, _ = GnUser.objects.get_or_create(
                        default_user_id=user.id,
                        defaults={
                            "username": user.username,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "is_active": user.is_active,
                        },
                    )
                    gn_user_id = gn_user.id
            except Exception as exc:
                logger.exception("Error syncing GnUser in tenant database %s: %s", database, exc)
                return Response(
                    {"success": False, "message": "Failed to connect to tenant database."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        # Generate SimpleJWT token
        refresh = RefreshToken.for_user(user)

        if tenant and database:
            refresh["tenant_id"] = tenant.id
            refresh["database_name"] = database
            if gn_user_id:
                refresh["gn_user_id"] = gn_user_id
        else:
            refresh["database_name"] = "default"

        return Response(
            {
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "tenant_alias": tenant.db_alias if tenant else None,
                    "company_name": tenant.company_name if tenant else None,
                },
            },
            status=status.HTTP_200_OK,
        )
