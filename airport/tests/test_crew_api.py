from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from airport.models import Crew, Airplane, Flight, AirplaneType, Airport, Route

CREW_URL = reverse("airport:crew-list")


def detail_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe"
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = params.pop("airplane_type", None)
    if not airplane_type:
        airplane_type = AirplaneType.objects.create(name="DefaultType")
    defaults = {
        "name": "Test Airplane",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_route():
    source = Airport.objects.create(name="Source", closest_big_city="Test city 1")
    destination = Airport.objects.create(name="Destination", closest_big_city="Test city 2")
    return Route.objects.create(source=source, destination=destination, distance=500)


class CrewApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "user@example.com",
            "password123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@example.com",
            "adminpass123"
        )

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_crews_admin_only(self):
        crew = sample_crew()
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["first_name"], crew.first_name)

    def test_retrieve_crew_with_flights(self):
        crew = sample_crew()
        route = sample_route()

        airplane = sample_airplane(name="Boeing 747")
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2030-01-01T10:00:00Z",
            arrival_time="2030-01-01T14:00:00Z"
        )
        flight.crew.add(crew)

        self.client.force_authenticate(user=self.admin_user)
        url = detail_url(crew.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["first_name"], crew.first_name)
        self.assertEqual(len(res.data["flights"]), 1)
        self.assertEqual(res.data["flights"][0]["airplane"], airplane.name)
