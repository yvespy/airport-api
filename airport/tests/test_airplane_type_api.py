from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")

def detail_url(airplane_type_id):
    return reverse("airport:airplanetype-detail", args=(airplane_type_id, ))

def sample_airplane_type(name="Test_Type") -> AirplaneType:
    return AirplaneType.objects.create(name=name)


class UnauthenticatedAirplaneTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminAirplaneTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="test_password",
            is_staff=False
        )
        self.client.force_authenticate(user)

    def test_list_forbidden_for_non_admin(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_forbidden_for_non_admin(self):
        payload = {"name": "Boeing 777"}
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@mail.com",
            password="test_password",
            is_staff=True,
        )
        self.client.force_authenticate(self.admin_user)

    def test_list_airplane_types(self):
        sample_airplane_type(name="Boeing 777")
        sample_airplane_type(name="Airbus A320")

        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.all().order_by("id")
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane_type(self):
        airplane_type = sample_airplane_type(name="Embraer E190")
        url = detail_url(airplane_type.id)

        res = self.client.get(url)

        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type(self):
        payload = {"name": "Concorde"}
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])
        self.assertEqual(airplane_type.name, payload["name"])
