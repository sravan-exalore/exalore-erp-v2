from rest_framework.views import APIView
from apps.testapp.models import Product
from rest_framework.response import Response
from apps.testapp.serializers import ProductSerializer


class GetProduct(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
