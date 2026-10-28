from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

from apps.general.models import GnUser
from core.database.context import set_current_database


class TenantUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        # database = request.auth.get("database_name") or None
        # gn_user_id = request.auth.get("gn_user_id") or None
        database, gn_user_id = None, None

        if not database or not gn_user_id:
            return

        # activate tenant database
        set_current_database(database)

        request.user = GnUser.objects.get(id=gn_user_id)
