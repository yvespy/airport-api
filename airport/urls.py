from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirportViewSet, RouteViewSet

router = DefaultRouter()
router.register(r"airports", AirportViewSet)
router.register(r"routes", RouteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
