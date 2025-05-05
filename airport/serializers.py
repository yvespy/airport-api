from rest_framework import serializers
from airport.models import Airport, Route


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
    destination_id = serializers.IntegerField(source="destination.id", read_only=True)
    destination_name = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ("id",
                  "source_id",
                  "source_name",
                  "destination_id",
                  "destination_name",
                  "distance")
