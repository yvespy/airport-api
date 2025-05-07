from rest_framework import serializers
from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")

    def validate(self, data):
        name = data.get("name")
        city = data.get("closest_big_city")

        if Airport.objects.filter(name__iexact=name, closest_big_city__iexact=city).exists():
            raise serializers.ValidationError("An airport with this name and city already exists.")

        return data


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, data):
        if data["source"] == data["destination"]:
            raise serializers.ValidationError("The departure and destination airports cannot be the same.")

        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")


class RouteDetailSerializer(RouteSerializer):
    source_id = serializers.IntegerField(source="source.id", read_only=True)
    source_name = serializers.CharField(source="source.name")
    source_closest_big_city = serializers.CharField(source="source.closest_big_city")
    destination_id = serializers.IntegerField(source="destination.id", read_only=True)
    destination_name = serializers.CharField(source="destination.name")
    destination_closest_big_city = serializers.CharField(source="destination.closest_big_city")

    class Meta:
        model = Route
        fields = ("id",
                  "source_id",
                  "source_name",
                  "source_closest_big_city",
                  "destination_id",
                  "destination_name",
                  "destination_closest_big_city",
                  "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")

    def validate_name(self, value):
        if AirplaneType.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("An airplane type with this name already exists.")
        return value


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")

    def validate_name(self, value):
        if Airplane.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("An airplane with this name already exists.")
        return value


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewFlightSerializer(serializers.ModelSerializer):
    airplane = serializers.CharField(source="airplane.name")

    class Meta:
        model = Flight
        fields = ("id", "airplane", "departure_time", "arrival_time")


class CrewDetailSerializer(CrewSerializer):
    flights = CrewFlightSerializer(source="flight_set",many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flights")


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")

    def validate(self, data):
        departure = data.get("departure_time")
        arrival = data.get("arrival_time")

        if departure == arrival:
            raise serializers.ValidationError("Departure time and arrival time cannot be the same.")

        route = data.get("route")
        airplane = data.get("airplane")

        if Flight.objects.filter(
            route=route,
            airplane=airplane,
            departure_time__gte=departure,
            departure_time__lte=arrival,
        ).exists():
            raise serializers.ValidationError(
                "A flight with this route, airplane, departure time, and arrival time already exists."
            )

        return data


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(source="route.source.name")
    destination = serializers.CharField(source="route.destination.name")

    class Meta:
        model = Flight
        fields = (
            "id",
            "source",
            "departure_time",
            "destination",
            "arrival_time",
        )


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer()
    airplane = AirplaneDetailSerializer()
    crew = CrewSerializer(many=True)
