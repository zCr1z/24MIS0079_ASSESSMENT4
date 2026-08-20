"""
Airline Reservation System - QA Program
AirlineReservationQA.py

Run: python3 -m unittest AirlineReservationQA -v
"""
import unittest
import datetime
from AirlineReservation import (
    AirlineReservation, Flight, SeatUnavailableError,
    DoubleBookingError, InvalidPassengerError, FlightBookingError
)


class TestAirlineReservation(unittest.TestCase):

    def setUp(self):
        self.system = AirlineReservation()
        self.flight = Flight("AI101", base_fare=3000, total_seats=2, travel_date=datetime.date(2026, 9, 1))
        self.system.add_flight(self.flight)

    # Successful booking
    def test_successful_booking(self):
        booking = self.system.book_ticket(
            "AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1)
        )
        self.assertEqual(booking["status"], "CONFIRMED")
        self.assertEqual(self.flight.available_seats, 1)

    # Double booking
    def test_double_booking_raises(self):
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        with self.assertRaises(DoubleBookingError):
            self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))

    # Cancellation
    def test_cancellation_frees_seat(self):
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.system.cancel_booking("AI101", "PAX001", cancellation_date=datetime.date(2026, 8, 10))
        self.assertEqual(self.flight.available_seats, 2)

    # Cancel already cancelled booking raises
    def test_cancel_already_cancelled_raises(self):
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.system.cancel_booking("AI101", "PAX001", cancellation_date=datetime.date(2026, 8, 10))
        with self.assertRaises(FlightBookingError):
            self.system.cancel_booking("AI101", "PAX001", cancellation_date=datetime.date(2026, 8, 11))

    # Refund - more than 7 days before travel -> 90%
    def test_refund_more_than_7_days(self):
        percent = self.system.calculate_refund(self.flight, cancellation_date=datetime.date(2026, 8, 20))
        self.assertEqual(percent, 90)

    # Refund - within 3 days -> 50%
    def test_refund_within_3_days(self):
        percent = self.system.calculate_refund(self.flight, cancellation_date=datetime.date(2026, 8, 29))
        self.assertEqual(percent, 50)

    # Refund - day of travel -> 0%
    def test_refund_on_travel_day(self):
        percent = self.system.calculate_refund(self.flight, cancellation_date=datetime.date(2026, 9, 1))
        self.assertEqual(percent, 0)

    # Fully booked flight
    def test_fully_booked_flight_raises(self):
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.system.book_ticket("AI101", "PAX002", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        with self.assertRaises(SeatUnavailableError):
            self.system.book_ticket("AI101", "PAX003", "ECONOMY", booking_date=datetime.date(2026, 8, 1))

    # Invalid passenger (bad class)
    def test_invalid_class_raises(self):
        with self.assertRaises(InvalidPassengerError):
            self.system.book_ticket("AI101", "PAX001", "PREMIUM_ECONOMY", booking_date=datetime.date(2026, 8, 1))

    # Invalid passenger age
    def test_invalid_passenger_age_raises(self):
        with self.assertRaises(InvalidPassengerError):
            self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1), age=200)

    # Excess baggage charge
    def test_excess_baggage_charge(self):
        charge = self.system.calculate_baggage_charge(30)
        self.assertEqual(charge, 5000)  # 10kg excess * 500

    # No baggage charge within free limit
    def test_no_baggage_charge_within_limit(self):
        charge = self.system.calculate_baggage_charge(15)
        self.assertEqual(charge, 0.0)

    # Dynamic fare increases with class
    def test_dynamic_fare_business_higher_than_economy(self):
        eco_fare = self.system.calculate_dynamic_fare(self.flight, "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        biz_fare = self.system.calculate_dynamic_fare(self.flight, "BUSINESS", booking_date=datetime.date(2026, 8, 1))
        self.assertGreater(biz_fare, eco_fare)

    # Dynamic fare increases with occupancy (fewer seats available -> higher fare)
    def test_dynamic_fare_increases_with_occupancy(self):
        fare_before = self.system.calculate_dynamic_fare(self.flight, "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        fare_after = self.system.calculate_dynamic_fare(self.flight, "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.assertGreaterEqual(fare_after, fare_before)

    # Last-minute booking surcharge
    def test_last_minute_booking_surcharge(self):
        far_fare = self.system.calculate_dynamic_fare(self.flight, "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        last_minute_fare = self.system.calculate_dynamic_fare(self.flight, "ECONOMY", booking_date=datetime.date(2026, 8, 31))
        self.assertGreater(last_minute_fare, far_fare)

    # Booking on nonexistent flight raises
    def test_booking_nonexistent_flight_raises(self):
        with self.assertRaises(FlightBookingError):
            self.system.book_ticket("XX999", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))

    # Search flights returns only flights with available seats
    def test_search_flights_returns_available(self):
        self.system.book_ticket("AI101", "PAX001", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        self.system.book_ticket("AI101", "PAX002", "ECONOMY", booking_date=datetime.date(2026, 8, 1))
        results = self.system.search_flights(min_available_seats=1)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
