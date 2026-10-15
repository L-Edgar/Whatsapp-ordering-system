"""
URL configuration for appConfigs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from businesses.views import BusinessViewSet, RegisterBusinessView
from catalog.views import CategoryViewSet, ProductViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from orders.views import OrderViewSet
from whatsapp.views import WhatsAppWebhookView
from customers.views import CustomerViewSet

router = DefaultRouter()
router.register("businesses", BusinessViewSet, basename="business")
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
router.register("customers", CustomerViewSet, basename="customer")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/register/", RegisterBusinessView.as_view()),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/", include(router.urls)),
]

urlpatterns += [
    path("api/whatsapp/webhook/", WhatsAppWebhookView.as_view()),
]