from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")

def detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])

def sample_airport(name="Test Airport", closest_big_city="Kyiv"):
    return Airport.objects.create(name=name, closest_big_city=closest_big_city)


class UnauthenticatedAirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminAirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user)

    def test_list_allowed(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_forbidden(self):
        payload = {"name": "Borispil", "closest_big_city": "Kyiv"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_list_airports(self):
        sample_airport()
        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(
            airports, many=True, context={"request": res.wsgi_request}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airport(self):
        airport = sample_airport()
        url = detail_url(airport.id)
        res = self.client.get(url)
        serializer = AirportSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport(self):
        payload = {"name": "Borispil", "closest_big_city": "Kyiv"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(airport.name, payload["name"])
        self.assertEqual(airport.closest_big_city, payload["closest_big_city"])
