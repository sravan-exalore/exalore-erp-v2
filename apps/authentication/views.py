from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.general.models import GnUser
from rest_framework.response import Response
from core.context import tenant_context
from core.tenancy.registry import register_tenant_database


class LoginView(APIView):
    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]

        # Authenticate default DB
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        database = register_tenant_database(user.tenant)

        with tenant_context(database):
            gn_user = GnUser.objects.get(default_user_id=user.id)

        refresh = RefreshToken.for_user(user)

        refresh["tenant_id"] = user.tenant.id
        refresh["database_name"] = database
        refresh["gn_user_id"] = gn_user.id

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
