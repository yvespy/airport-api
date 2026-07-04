from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import timedelta
from django.utils.timezone import now

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight

FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def sample_airport(**params):
    defaults = {"name": "Test Airport", "closest_big_city": "Test City"}
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport(name="Source Airport")
    destination = sample_airport(name="Destination Airport")
    defaults = {"source": source, "destination": destination, "distance": 1000}
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_airplane_type(name="Boeing 737"):
    return AirplaneType.objects.create(name=name)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {"name": "Test Plane", "rows": 10, "seats_in_row": 6, "airplane_type": airplane_type}
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_crew(**params):
    defaults = {"first_name": "John", "last_name": "Doe"}
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    departure = now() + timedelta(days=1)
    arrival = departure + timedelta(hours=2)
    flight = Flight.objects.create(route=route, airplane=airplane,
                                   departure_time=departure, arrival_time=arrival)
    flight.crew.set([sample_crew()])
    return flight


class UnauthenticatedFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_list_flights_allowed(self):
        sample_flight()
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        departure = now() + timedelta(days=1)
        arrival = departure + timedelta(hours=2)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
            "crew": [crew.id],
        }

        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@example.com", password="adminpass123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        sample_flight()
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_retrieve_flight(self):
        flight = sample_flight()
        url = detail_url(flight.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], flight.id)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        departure = now() + timedelta(days=1)
        arrival = departure + timedelta(hours=2)

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
            "crew": [crew.id],
        }

        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route.id, route.id)
        self.assertEqual(flight.airplane.id, airplane.id)
        self.assertEqual(flight.crew.count(), 1)

    def test_create_flight_with_same_departure_and_arrival_time_invalid(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        time = now() + timedelta(days=1)

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": time.isoformat(),
            "arrival_time": time.isoformat(),
            "crew": [crew.id],
        }

        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Departure time and arrival time cannot be the same.", str(res.data))

    def test_create_flight_with_overlapping_time_invalid(self):
        flight = sample_flight()
        route = flight.route
        airplane = flight.airplane
        crew = sample_crew()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (flight.departure_time + timedelta(minutes=30)).isoformat(),
            "arrival_time": (flight.arrival_time + timedelta(minutes=30)).isoformat(),
            "crew": [crew.id],
        }

        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already assigned to another flight", str(res.data))

