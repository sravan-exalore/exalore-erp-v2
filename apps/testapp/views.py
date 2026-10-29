from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.testapp.models import Product
from apps.testapp.serializers import ProductSerializer
from core.permissions import IsTenantUser


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductView(APIView):
    """
    Tenant-isolated product inventory endpoint.
    Requires verified tenant authentication and provides server-side pagination.
    """

    permission_classes = [IsTenantUser]
    pagination_class = StandardResultsPagination

    def get(self, request):
        queryset = Product.objects.all().order_by("id")

        # Optional search query filter
        search = request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=201,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=400,
        )


# Backward compatibility alias
GetProduct = ProductView
