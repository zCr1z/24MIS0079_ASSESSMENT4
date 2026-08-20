"""
Airline Reservation System
Development Program: AirlineReservation.java equivalent in Python
"""
import datetime


class FlightBookingError(Exception):
    pass


class SeatUnavailableError(FlightBookingError):
    pass


class DoubleBookingError(FlightBookingError):
    pass


class InvalidPassengerError(FlightBookingError):
    pass


class Flight:
    CLASS_MULTIPLIER = {
        "ECONOMY": 1.0,
        "BUSINESS": 2.5,
        "FIRST": 4.0,
    }

    def __init__(self, flight_no, base_fare, total_seats, travel_date):
        self.flight_no = flight_no
        self.base_fare = base_fare
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.travel_date = travel_date  # datetime.date
        self.bookings = {}  # passenger_id -> booking dict


class AirlineReservation:
    BAGGAGE_FREE_LIMIT_KG = 20
    BAGGAGE_EXCESS_RATE_PER_KG = 500
    REFUND_POLICY = [
        # (min_days_before_travel, refund_percent)
        (7, 90),
        (3, 50),
        (1, 20),
        (0, 0),
    ]

    def __init__(self):
        self.flights = {}

    def add_flight(self, flight: Flight):
        self.flights[flight.flight_no] = flight

    def search_flights(self, min_available_seats=1):
        return [f for f in self.flights.values() if f.available_seats >= min_available_seats]

    def calculate_dynamic_fare(self, flight: Flight, passenger_class, booking_date):
        if passenger_class not in Flight.CLASS_MULTIPLIER:
            raise InvalidPassengerError(f"Invalid class: {passenger_class}")

        occupancy = 1 - (flight.available_seats / flight.total_seats)
        # fare increases up to 50% as flight fills up
        demand_surcharge = 1 + (occupancy * 0.5)

        days_to_travel = (flight.travel_date - booking_date).days
        # last-minute booking surcharge
        urgency_surcharge = 1.3 if days_to_travel <= 2 else (1.1 if days_to_travel <= 7 else 1.0)

        fare = flight.base_fare * Flight.CLASS_MULTIPLIER[passenger_class] * demand_surcharge * urgency_surcharge
        return round(fare, 2)

    def book_ticket(self, flight_no, passenger_id, passenger_class, booking_date, age=None, baggage_kg=0):
        if flight_no not in self.flights:
            raise FlightBookingError(f"Flight {flight_no} not found")
        flight = self.flights[flight_no]

        if age is not None and (age < 0 or age > 120):
            raise InvalidPassengerError("Invalid passenger age")

        if passenger_id in flight.bookings:
            raise DoubleBookingError(f"Passenger {passenger_id} already booked on {flight_no}")

        if flight.available_seats <= 0:
            raise SeatUnavailableError(f"Flight {flight_no} is fully booked")

        fare = self.calculate_dynamic_fare(flight, passenger_class, booking_date)
        baggage_charge = self.calculate_baggage_charge(baggage_kg)
        total_fare = round(fare + baggage_charge, 2)

        flight.available_seats -= 1
        booking = {
            "passenger_id": passenger_id,
            "flight_no": flight_no,
            "class": passenger_class,
            "fare": fare,
            "baggage_charge": baggage_charge,
            "total_fare": total_fare,
            "status": "CONFIRMED",
        }
        flight.bookings[passenger_id] = booking
        return booking

    def calculate_baggage_charge(self, baggage_kg):
        if baggage_kg <= self.BAGGAGE_FREE_LIMIT_KG:
            return 0.0
        excess = baggage_kg - self.BAGGAGE_FREE_LIMIT_KG
        return round(excess * self.BAGGAGE_EXCESS_RATE_PER_KG, 2)

    def calculate_refund(self, flight: Flight, cancellation_date):
        days_before_travel = (flight.travel_date - cancellation_date).days
        for min_days, percent in self.REFUND_POLICY:
            if days_before_travel >= min_days:
                return percent
        return 0

    def cancel_booking(self, flight_no, passenger_id, cancellation_date):
        if flight_no not in self.flights:
            raise FlightBookingError(f"Flight {flight_no} not found")
        flight = self.flights[flight_no]

        if passenger_id not in flight.bookings:
            raise FlightBookingError(f"No booking found for passenger {passenger_id} on {flight_no}")

        booking = flight.bookings[passenger_id]
        if booking["status"] == "CANCELLED":
            raise FlightBookingError("Booking already cancelled")

        refund_percent = self.calculate_refund(flight, cancellation_date)
        refund_amount = round(booking["total_fare"] * (refund_percent / 100), 2)

        booking["status"] = "CANCELLED"
        booking["refund_percent"] = refund_percent
        booking["refund_amount"] = refund_amount
        flight.available_seats += 1

        return booking


if __name__ == "__main__":
    reservation = AirlineReservation()
    flight = Flight("AI101", base_fare=3000, total_seats=100, travel_date=datetime.date(2026, 9, 1))
    reservation.add_flight(flight)
    booking = reservation.book_ticket(
        "AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 20), baggage_kg=25
    )
    print(booking)
    cancelled = reservation.cancel_booking("AI101", "PAX001", cancellation_date=datetime.date(2026, 8, 22))
    print(cancelled)
