import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardized enterprise API exception handler.
    Provides consistent error payloads across all endpoints.
    """
    # Call REST framework's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    view = context.get("view")
    request = context.get("request")
    view_name = view.__class__.__name__ if view else "UnknownView"

    if response is not None:
        # Standardize known API error payload
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "error_type": exc.__class__.__name__,
            "message": response.data.get("detail", "An error occurred processing the request.")
            if isinstance(response.data, dict)
            else "Validation error.",
            "errors": response.data,
        }
        response.data = custom_data
        return response

    # Handle unhandled server exceptions (HTTP 500)
    logger.exception(
        "Unhandled exception in %s on path %s: %s",
        view_name,
        getattr(request, "path", "unknown"),
        exc,
    )

    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_type": "InternalServerError",
            "message": "An unexpected internal server error occurred.",
            "errors": None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

