from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer, AirplaneDetailSerializer

AIRPLANE_URL = reverse("airport:airplane-list")

def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=(airplane_id, ))

def sample_airplane_type(name="Test_Type") -> AirplaneType:
    return AirplaneType.objects.create(name=name)

def sample_airplane(**params) -> Airplane:
    airplane_type = AirplaneType.objects.create(name="Test_Type")

    defaults = {
        "name": "Airbus A319",
        "rows": 2,
        "seats_in_row": 10,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminAirplaneTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="test_password",
            is_staff=False
        )
        self.client.force_authenticate(user)

    def test_airplane_list_forbidden_for_non_admin(self):
        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            res.data["detail"],
            "You do not have permission to perform this action."
        )

    def test_create_airplane_forbidden_for_non_admin(self):
        payload = {
            "name": "Airbus A319",
            "rows": 2,
            "seats_in_row": 10,
            "airplane_type": 1,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="test_password",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_airplanes_list(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(
            airplanes,
            many=True,
            context={"request": res.wsgi_request}
        )

        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)

        res = self.client.get(url)
        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane(self):
        airplane_type = sample_airplane_type()

        payload = {
            "name": "Airbus A319",
            "rows": 2,
            "seats_in_row": 10,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=res.data["id"])
        self.assertEqual(airplane.name, payload["name"])
        self.assertEqual(airplane.rows, payload["rows"])
        self.assertEqual(airplane.seats_in_row, payload["seats_in_row"])
        self.assertEqual(airplane.airplane_type.id, payload["airplane_type"])
