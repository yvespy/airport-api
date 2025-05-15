from django.db.models import Count, F
from rest_framework import viewsets

from airport.models import (Airport,
                            Route,
                            AirplaneType,
                            Airplane,
                            Crew,
                            Flight,
                            Order)
from airport.permissions import (AdminAllOrIsAuthenticatedReadOnly,
                                 IsAdminUserOnly,
                                 IsAuthenticatedOnly)
from airport.serializers import (AirportSerializer,
                                 RouteSerializer,
                                 RouteListSerializer,
                                 RouteDetailSerializer,
                                 AirplaneTypeSerializer,
                                 AirplaneSerializer,
                                 AirplaneListSerializer,
                                 AirplaneDetailSerializer,
                                 CrewSerializer,
                                 CrewDetailSerializer,
                                 FlightSerializer,
                                 FlightListSerializer,
                                 FlightDetailSerializer,
                                 OrderSerializer,
                                 OrderListSerializer,
                                 OrderDetailSerializer)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (AdminAllOrIsAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (AdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("source", "destination")

        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminUserOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminUserOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("airplane_type")

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUserOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewDetailSerializer
        return CrewSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            return queryset.prefetch_related("flight_set__airplane")

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (AdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return (
                queryset
                .select_related("route__source",
                                "route__destination",
                                "airplane",).annotate(available_tickets=F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets", distinct=True))
            )
        elif self.action == "retrieve":
            return (
                queryset.select_related("route__source",
                                        "route__destination",
                                        "airplane")
                .prefetch_related("crew")
            )

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticatedOnly,)

    def get_queryset(self):
        if self.action == "retrieve":
            return self.queryset.prefetch_related("tickets")
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
