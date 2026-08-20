from datetime import date


class AirlineReservation:
    BASE_FARES = {
        "economy": 5000,
        "business": 12000,
        "first": 25000
    }

    PASSENGER_DISCOUNTS = {
        "adult": 0,
        "child": 0.20,
        "senior": 0.15
    }

    def __init__(self, flight_no, travel_date, total_seats=100):
        self.flight_no = flight_no
        self.travel_date = travel_date
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.bookings = {}

    def search_flight(self):
        return {
            "flight_no": self.flight_no,
            "travel_date": self.travel_date,
            "available_seats": self.available_seats
        }

    def dynamic_fare(self, travel_date, passenger_type, seat_class,
                     booking_date=None):
        seat_class = seat_class.lower()
        passenger_type = passenger_type.lower()

        if seat_class not in self.BASE_FARES:
            raise ValueError("Invalid class")
        if passenger_type not in self.PASSENGER_DISCOUNTS:
            raise ValueError("Invalid passenger type")

        fare = self.BASE_FARES[seat_class]

        occupancy = 1 - (self.available_seats / self.total_seats)

        if occupancy >= 0.80:
            fare *= 1.50
        elif occupancy >= 0.50:
            fare *= 1.20

        if booking_date is not None:
            days = (travel_date - booking_date).days
            if days < 7:
                fare *= 1.25
            elif days < 30:
                fare *= 1.10

        fare *= (1 - self.PASSENGER_DISCOUNTS[passenger_type])

        return round(fare, 2)

    def book(self, passenger_id, passenger_type, seat_class,
             baggage_kg=0, booking_date=None):
        if passenger_id in self.bookings:
            raise ValueError("Passenger already booked")

        if self.available_seats <= 0:
            raise ValueError("Flight fully booked")

        if baggage_kg < 0:
            raise ValueError("Invalid baggage")

        fare = self.dynamic_fare(
            self.travel_date, passenger_type,
            seat_class, booking_date
        )

        excess = max(0, baggage_kg - 15)
        baggage_charge = excess * 500

        total = fare + baggage_charge

        self.bookings[passenger_id] = {
            "fare": fare,
            "baggage": baggage_kg,
            "baggage_charge": baggage_charge,
            "total": total
        }
        self.available_seats -= 1

        return self.bookings[passenger_id]

    def cancel(self, passenger_id):
        if passenger_id not in self.bookings:
            raise ValueError("Invalid passenger")

        booking = self.bookings.pop(passenger_id)
        self.available_seats += 1

        refund = booking["total"] * 0.80
        return round(refund, 2)


if __name__ == "__main__":
    flight = AirlineReservation(
        "AI101",
        date(2026, 12, 20),
        100
    )
    print(flight.book(
        "P001", "adult", "economy",
        baggage_kg=20,
        booking_date=date(2026, 8, 20)
    ))
