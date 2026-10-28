from .context import set_current_database, reset_current_database


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        database = None

        if hasattr(request, "session"):
            database = request.session.get("selected_database")

        token = None

        if database:
            token = set_current_database(database)

        try:
            response = self.get_response(request)

        finally:
            if token:
                reset_current_database(token)

        return response
