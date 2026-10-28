from django.contrib.auth import get_user_model
from apps.general.models import GnUser
from core.context import tenant_context

User = get_user_model()


def create_tenant_user(tenant_db, username, password, **kwargs):

    # 1. Create default user
    default_user = User.objects.create_user(username=username, password=password)

    # 2. Switch tenant database
    with tenant_context(tenant_db):

        gn_user = GnUser.objects.create(
            default_user_id=default_user.id,
            username=username,
            first_name=kwargs.get("first_name"),
        )

    return gn_user
