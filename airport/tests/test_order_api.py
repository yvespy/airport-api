from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from airport.models import Order, Flight, Airport, Route, AirplaneType, Airplane, Ticket

ORDER_URL = reverse("airport:order-list")


def detail_url(order_id):
    return reverse("airport:order-detail", args=[order_id])


def sample_user(**params):
    defaults = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_order(user, **params):
    defaults = {
        "user": user
    }
    defaults.update(params)
    return Order.objects.create(**defaults)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_orders(self):
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_create_order(self):
        route = sample_route()
        airplane = sample_airplane()
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2024-01-01T10:00:00Z",
            arrival_time="2024-01-01T12:00:00Z"
        )

        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight.id
                }
            ]
        }

        response = self.client.post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.first()
        self.assertEqual(ticket.row, 1)
        self.assertEqual(ticket.seat, 1)
        self.assertEqual(ticket.flight, flight)
        self.assertEqual(ticket.order.user, self.user)

    def test_retrieve_order(self):
        order = sample_order(user=self.user)
        url = detail_url(order.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], order.id)

    def test_user_sees_only_own_orders(self):
        other_user = sample_user(email="other@example.com")
        sample_order(user=self.user)
        sample_order(user=other_user)

        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], Order.objects.filter(user=self.user).first().id)

    def test_create_order_with_duplicate_tickets(self):
        route = sample_route()
        airplane = sample_airplane()
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2024-01-01T10:00:00Z",
            arrival_time="2024-01-01T12:00:00Z"
        )

        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight.id
                },
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight.id
                }
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


def sample_route():
    source = Airport.objects.create(name="Source", closest_big_city="TestCity1")
    destination = Airport.objects.create(name="Destination", closest_big_city="TestCity2")
    return Route.objects.create(source=source, destination=destination, distance=100)


def sample_airplane():
    airplane_type = AirplaneType.objects.create(name="TestType")
    return Airplane.objects.create(
        name="TestPlane",
        rows=10,
        seats_in_row=6,
        airplane_type=airplane_type
    )