"""
Smart Parking Management System - QA Program
ParkingQA.py

Run: python3 -m unittest ParkingQA -v
"""
import unittest
import datetime
from ParkingManagement import (
    ParkingManagement, ParkingFullError, InvalidVehicleSlotError,
    DuplicateVehicleError, InvalidTicketError, ParkingError
)


def new_system():
    return ParkingManagement(slot_capacity={
        "BIKE_SLOT": 2, "CAR_SLOT": 2, "TRUCK_SLOT": 1, "EV_SLOT": 1
    })


class TestParkingManagement(unittest.TestCase):

    # Full parking lot
    def test_full_parking_lot_raises(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        parking.vehicle_entry("CAR1", "CAR", entry_time)
        parking.vehicle_entry("CAR2", "CAR", entry_time)
        with self.assertRaises(ParkingFullError):
            parking.vehicle_entry("CAR3", "CAR", entry_time)

    # Wrong vehicle-slot combination (unknown vehicle type)
    def test_wrong_vehicle_slot_combination_raises(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        with self.assertRaises(InvalidVehicleSlotError):
            parking.vehicle_entry("BUS1", "BUS", entry_time)

    # Duplicate vehicle
    def test_duplicate_vehicle_raises(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        parking.vehicle_entry("CAR1", "CAR", entry_time)
        with self.assertRaises(DuplicateVehicleError):
            parking.vehicle_entry("CAR1", "CAR", entry_time)

    # Lost ticket handling
    def test_lost_ticket_penalty_applied(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 13, 0)  # non-peak
        ticket = parking.vehicle_entry("CAR1", "CAR", entry_time)
        exit_time = datetime.datetime(2026, 8, 20, 14, 0)
        record = parking.vehicle_exit(ticket["ticket_id"], exit_time, lost_ticket=True)
        self.assertGreaterEqual(record["fee"], parking.LOST_TICKET_PENALTY)

    # Invalid ticket id raises
    def test_invalid_ticket_id_raises(self):
        parking = new_system()
        with self.assertRaises(InvalidTicketError):
            parking.vehicle_exit("nonexistent-ticket", datetime.datetime(2026, 8, 20, 10, 0))

    # Early exit (less than 1 hour) still charged minimum 1 hour
    def test_early_exit_minimum_one_hour_billed(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 13, 0)  # non-peak
        ticket = parking.vehicle_entry("BIKE1", "BIKE", entry_time)
        exit_time = datetime.datetime(2026, 8, 20, 13, 10)  # 10 minutes later
        record = parking.vehicle_exit(ticket["ticket_id"], exit_time)
        self.assertEqual(record["fee"], parking.HOURLY_RATE["BIKE"])

    # Overnight parking - multiple hours billed
    def test_overnight_parking_multiple_hours_billed(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 22, 0)
        ticket = parking.vehicle_entry("CAR1", "CAR", entry_time)
        exit_time = datetime.datetime(2026, 8, 21, 7, 0)  # 9 hours later
        record = parking.vehicle_exit(ticket["ticket_id"], exit_time)
        self.assertEqual(record["fee"], 9 * parking.HOURLY_RATE["CAR"])

    # Peak-hour pricing surcharge
    def test_peak_hour_pricing_surcharge(self):
        parking = new_system()
        peak_entry = datetime.datetime(2026, 8, 20, 9, 0)  # within 8-11 peak hours
        offpeak_entry = datetime.datetime(2026, 8, 20, 14, 0)
        ticket_peak = parking.vehicle_entry("CAR1", "CAR", peak_entry)
        exit_time_peak = datetime.datetime(2026, 8, 20, 10, 0)
        record_peak = parking.vehicle_exit(ticket_peak["ticket_id"], exit_time_peak)

        parking2 = new_system()
        ticket_offpeak = parking2.vehicle_entry("CAR1", "CAR", offpeak_entry)
        exit_time_offpeak = datetime.datetime(2026, 8, 20, 15, 0)
        record_offpeak = parking2.vehicle_exit(ticket_offpeak["ticket_id"], exit_time_offpeak)

        self.assertGreater(record_peak["fee"], record_offpeak["fee"])

    # EV charging fee added
    def test_ev_charging_fee_added(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 13, 0)  # non-peak
        ticket = parking.vehicle_entry("EV1", "EV", entry_time)
        exit_time = datetime.datetime(2026, 8, 20, 14, 0)
        record = parking.vehicle_exit(ticket["ticket_id"], exit_time)
        expected = parking.HOURLY_RATE["EV"] + parking.EV_CHARGING_RATE_PER_HOUR
        self.assertEqual(record["fee"], expected)

    # VIP discount applied
    def test_vip_discount_applied(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 13, 0)  # non-peak
        ticket = parking.vehicle_entry("CAR1", "CAR", entry_time, is_vip=True)
        exit_time = datetime.datetime(2026, 8, 20, 14, 0)
        record = parking.vehicle_exit(ticket["ticket_id"], exit_time)
        expected = round(parking.HOURLY_RATE["CAR"] * (1 - parking.VIP_DISCOUNT_PERCENT / 100), 2)
        self.assertEqual(record["fee"], expected)

    # SUV maps to CAR_SLOT correctly
    def test_suv_uses_car_slot(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        ticket = parking.vehicle_entry("SUV1", "SUV", entry_time)
        self.assertEqual(ticket["slot_type"], "CAR_SLOT")
        self.assertEqual(parking.occupied_slots["CAR_SLOT"], 1)

    # Exit frees up the slot
    def test_exit_frees_slot(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        ticket = parking.vehicle_entry("TRUCK1", "TRUCK", entry_time)
        self.assertEqual(parking.occupied_slots["TRUCK_SLOT"], 1)
        parking.vehicle_exit(ticket["ticket_id"], datetime.datetime(2026, 8, 20, 11, 0))
        self.assertEqual(parking.occupied_slots["TRUCK_SLOT"], 0)

    # Exit time before entry time raises
    def test_exit_before_entry_raises(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        ticket = parking.vehicle_entry("CAR1", "CAR", entry_time)
        with self.assertRaises(ParkingError):
            parking.vehicle_exit(ticket["ticket_id"], datetime.datetime(2026, 8, 20, 8, 0))

    # After exit, vehicle can re-enter (not marked duplicate anymore)
    def test_vehicle_can_reenter_after_exit(self):
        parking = new_system()
        entry_time = datetime.datetime(2026, 8, 20, 9, 0)
        ticket = parking.vehicle_entry("CAR1", "CAR", entry_time)
        parking.vehicle_exit(ticket["ticket_id"], datetime.datetime(2026, 8, 20, 10, 0))
        new_ticket = parking.vehicle_entry("CAR1", "CAR", datetime.datetime(2026, 8, 20, 15, 0))
        self.assertIsNotNone(new_ticket["ticket_id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
