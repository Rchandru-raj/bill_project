from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import generate_invoice, billing_page,ProductViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('billing/', billing_page, name='billing_page'),
    path('generate_invoice/', generate_invoice, name='generate_invoice'),
]
