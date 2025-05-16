from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route, Airport

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


def sample_airport(**params):
    defaults = {"name": "Test Airport", "closest_big_city": "Test City"}
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport(name="Source Airport")
    destination = sample_airport(name="Destination Airport")
    defaults = {"source": source, "destination": destination, "distance": 1234}
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthenticatedRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_list_routes_allowed(self):
        sample_route()
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_route_forbidden(self):
        source = sample_airport(name="Kyiv Airport")
        destination = sample_airport(name="Lviv Airport")

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 800
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        route = Route.objects.create(source=source, destination=destination, distance=1234)

        self.client.force_authenticate(user=self.user)
        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["source"], "Source Airport")
        self.assertEqual(res.data["results"][0]["destination"], "Destination Airport")
        self.assertEqual(res.data["results"][0]["distance"], 1234)

    def test_retrieve_route(self):
        source = sample_airport(name="Source Airport", closest_big_city="Kyiv")
        destination = sample_airport(name="Destination Airport", closest_big_city="Lviv")
        route = Route.objects.create(source=source, destination=destination, distance=1234)

        self.client.force_authenticate(user=self.user)
        url = detail_url(route.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["source_id"], source.id)
        self.assertEqual(res.data["source_name"], "Source Airport")
        self.assertEqual(res.data["source_closest_big_city"], "Kyiv")
        self.assertEqual(res.data["destination_id"], destination.id)
        self.assertEqual(res.data["destination_name"], "Destination Airport")
        self.assertEqual(res.data["destination_closest_big_city"], "Lviv")
        self.assertEqual(res.data["distance"], 1234)

    def test_create_route(self):
        source = sample_airport(name="Kyiv Airport")
        destination = sample_airport(name="Lviv Airport")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 800
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(route.source.id, payload["source"])
        self.assertEqual(route.destination.id, payload["destination"])
        self.assertEqual(route.distance, payload["distance"])
