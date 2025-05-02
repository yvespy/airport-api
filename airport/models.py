from django.conf import settings
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(Airport,
                               on_delete=models.CASCADE,
                               related_name="departing_routes"
                               )
    destination = models.ForeignKey(Airport,
                                    on_delete=models.CASCADE,
                                    related_name="arriving_routes"
                                    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.distance} km)"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}: ({self.airplane_type})"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    def __str__(self):
        return (f"{self.route} - {self.airplane}: "
                f"{self.departure_time} - {self.arrival_time}"
                )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE
                             )

    def __str__(self):
        return f"Order #{self.id} created by {self.user}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight,
                               on_delete=models.CASCADE,
                               related_name="tickets"
                               )
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="tickets"
                              )

    class Meta:
        unique_together = ("row", "seat", "flight")

    def __str__(self):
        return f"Row {self.row}, Seat {self.seat} - {self.flight.id}"
