from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.GetProduct.as_view(), name='prod'),
]