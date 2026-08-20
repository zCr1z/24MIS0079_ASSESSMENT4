import unittest
from datetime import date
from AirlineReservation import AirlineReservation


class AirlineReservationQA(unittest.TestCase):

    def setUp(self):
        self.flight = AirlineReservation(
            "AI101",
            date(2026, 12, 20),
            3
        )

    def test_successful_booking(self):
        result = self.flight.book("P1", "adult", "economy")
        self.assertIn("total", result)
        self.assertEqual(self.flight.available_seats, 2)

    def test_double_booking(self):
        self.flight.book("P1", "adult", "economy")
        with self.assertRaises(ValueError):
            self.flight.book("P1", "adult", "economy")

    def test_cancellation(self):
        self.flight.book("P1", "adult", "economy")
        refund = self.flight.cancel("P1")
        self.assertGreater(refund, 0)
        self.assertEqual(self.flight.available_seats, 3)

    def test_refund_calculation(self):
        booking = self.flight.book("P1", "adult", "economy")
        refund = self.flight.cancel("P1")
        self.assertEqual(refund, round(booking["total"] * 0.80, 2))

    def test_fully_booked(self):
        self.flight.book("P1", "adult", "economy")
        self.flight.book("P2", "adult", "economy")
        self.flight.book("P3", "adult", "economy")

        with self.assertRaises(ValueError):
            self.flight.book("P4", "adult", "economy")

    def test_invalid_passenger(self):
        with self.assertRaises(ValueError):
            self.flight.book("P1", "unknown", "economy")

    def test_excess_baggage(self):
        result = self.flight.book("P1", "adult", "economy", baggage_kg=20)
        self.assertEqual(result["baggage_charge"], 2500)

    def test_dynamic_fare_class(self):
        economy = self.flight.dynamic_fare(
            self.flight.travel_date, "adult", "economy"
        )
        business = self.flight.dynamic_fare(
            self.flight.travel_date, "adult", "business"
        )
        self.assertGreater(business, economy)

    def test_child_discount(self):
        adult = self.flight.dynamic_fare(
            self.flight.travel_date, "adult", "economy"
        )
        child = self.flight.dynamic_fare(
            self.flight.travel_date, "child", "economy"
        )
        self.assertLess(child, adult)

    def test_senior_discount(self):
        adult = self.flight.dynamic_fare(
            self.flight.travel_date, "adult", "economy"
        )
        senior = self.flight.dynamic_fare(
            self.flight.travel_date, "senior", "economy"
        )
        self.assertLess(senior, adult)

    def test_invalid_class(self):
        with self.assertRaises(ValueError):
            self.flight.dynamic_fare(
                self.flight.travel_date, "adult", "premium"
            )

    def test_negative_baggage(self):
        with self.assertRaises(ValueError):
            self.flight.book("P1", "adult", "economy", baggage_kg=-1)

    def test_invalid_cancellation(self):
        with self.assertRaises(ValueError):
            self.flight.cancel("UNKNOWN")

    def test_last_minute_fare(self):
        fare = self.flight.dynamic_fare(
            date(2026, 8, 25), "adult", "economy",
            booking_date=date(2026, 8, 20)
        )
        self.assertGreater(fare, 5000)

    def test_business_class(self):
        result = self.flight.book("P1", "adult", "business")
        self.assertGreater(result["fare"], 5000)

    def test_first_class(self):
        result = self.flight.book("P1", "adult", "first")
        self.assertGreater(result["fare"], 12000)

    def test_booking_date_effect(self):
        early = self.flight.dynamic_fare(
            date(2026, 12, 20), "adult", "economy",
            booking_date=date(2026, 8, 20)
        )
        late = self.flight.dynamic_fare(
            date(2026, 12, 20), "adult", "economy",
            booking_date=date(2026, 12, 15)
        )
        self.assertGreater(late, early)


if __name__ == "__main__":
    unittest.main(verbosity=2)
