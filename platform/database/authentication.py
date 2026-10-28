from rest_framework_simplejwt.authentication import JWTAuthentication

from .context import set_current_database


class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)

        if result:
            user, token = result
            database = token.get("database_name")

            if database:
                set_current_database(database)

        return result
