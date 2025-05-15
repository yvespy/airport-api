from django.db.models import Count, F
from drf_spectacular.utils import extend_schema
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

    @extend_schema(summary="List all airports")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve airport details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create a new airport")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update an airport")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete an airport")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(summary="List all routes")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve route details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create a new route")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update a route")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete a route")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminUserOnly,)

    @extend_schema(summary="List all airplane types")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve airplane type details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create airplane type")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update airplane type")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete airplane type")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(summary="List all airplanes")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve airplane details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create an airplane")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update an airplane")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete an airplane")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(summary="List all crews")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve crew details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create crew")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update crew")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete crew")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(
        summary="List of flights",
        description="Returns a list of available flights with available tickets.",
        responses={200: FlightListSerializer},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve flight",
        description="Returns detailed information about a flight, including route, airplane, crew and taken seats.",
        responses={200: FlightDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create flight",
        description="Create a new flight by referencing existing route and airplane. Crew must also be specified.",
        request=FlightSerializer,
        responses={201: FlightSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Delete flight")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(summary="List current user's orders")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve order with tickets and flights")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create new order with tickets")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)