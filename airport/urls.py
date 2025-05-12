from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirportViewSet, RouteViewSet, AirplaneTypeViewSet, AirplaneViewSet, CrewViewSet, \
    FlightViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"airports", AirportViewSet)
router.register(r"routes", RouteViewSet)
router.register(r"airplanes_type", AirplaneTypeViewSet)
router.register(r"airplanes", AirplaneViewSet)
router.register(r"crews", CrewViewSet)
router.register(r"flights", FlightViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
