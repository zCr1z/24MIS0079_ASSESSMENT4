import unittest
from datetime import datetime
from ParkingManagement import ParkingManagement


class ParkingQA(unittest.TestCase):

    def setUp(self):
        self.parking = ParkingManagement()
        self.entry = datetime(2026, 8, 20, 10, 0)

    def test_vehicle_entry(self):
        ticket = self.parking.enter_vehicle("V1", "car", self.entry)
        self.assertTrue(ticket.startswith("T"))

    def test_full_parking_lot(self):
        for i in range(3):
            self.parking.enter_vehicle(f"B{i}", "bike", self.entry)

        with self.assertRaises(ValueError):
            self.parking.enter_vehicle("B4", "bike", self.entry)

    def test_wrong_vehicle_slot_combination(self):
        # All truck slots can hold only trucks in this implementation.
        self.parking.enter_vehicle("T1", "truck", self.entry)

        with self.assertRaises(ValueError):
            self.parking.enter_vehicle("T2", "truck", self.entry)

    def test_duplicate_vehicle(self):
        self.parking.enter_vehicle("V1", "car", self.entry)

        with self.assertRaises(ValueError):
            self.parking.enter_vehicle("V1", "car", self.entry)

    def test_lost_ticket(self):
        ticket = self.parking.enter_vehicle("V1", "car", self.entry)
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 20, 12, 0),
            lost_ticket=True
        )
        self.assertEqual(fee, 500)

    def test_early_exit(self):
        ticket = self.parking.enter_vehicle("V1", "car", self.entry)
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 20, 10, 15)
        )
        self.assertEqual(fee, 50)

    def test_overnight_parking(self):
        ticket = self.parking.enter_vehicle("V1", "car", self.entry)
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 21, 10, 0)
        )
        self.assertEqual(fee, 1200)

    def test_peak_hour_pricing(self):
        ticket = self.parking.enter_vehicle("V1", "car", self.entry)
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 20, 18, 0)
        )
        self.assertEqual(fee, 600)

    def test_ev_charging_fee(self):
        ticket = self.parking.enter_vehicle("EV1", "electric", self.entry)
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 20, 12, 0),
            ev_charging=True
        )
        self.assertEqual(fee, 180)

    def test_vip_parking(self):
        ticket = self.parking.enter_vehicle(
            "VIP1", "car", self.entry, vip=True
        )
        fee = self.parking.exit_vehicle(
            ticket,
            datetime(2026, 8, 20, 12, 0)
        )
        self.assertEqual(fee, 50)

    def test_invalid_vehicle_type(self):
        with self.assertRaises(ValueError):
            self.parking.enter_vehicle("V1", "bus", self.entry)

    def test_invalid_ticket(self):
        with self.assertRaises(ValueError):
            self.parking.exit_vehicle(
                "BAD", datetime(2026, 8, 20, 12, 0)
            )

    def test_suv_slot(self):
        ticket = self.parking.enter_vehicle("S1", "suv", self.entry)
        self.assertEqual(self.parking.occupied["S1"], "S1")

    def test_truck_slot(self):
        ticket = self.parking.enter_vehicle("TR1", "truck", self.entry)
        self.assertEqual(self.parking.occupied["TR1"], "T1")

    def test_bike_slot(self):
        ticket = self.parking.enter_vehicle("BK1", "bike", self.entry)
        self.assertEqual(self.parking.occupied["BK1"], "B1")

    def test_car_slot(self):
        ticket = self.parking.enter_vehicle("C1", "car", self.entry)
        self.assertEqual(self.parking.occupied["C1"], "C1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
