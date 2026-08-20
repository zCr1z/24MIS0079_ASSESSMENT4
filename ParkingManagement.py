"""
Smart Parking Management System
Development Program: ParkingManagement.java equivalent in Python
"""
import datetime
import uuid


class ParkingError(Exception):
    pass


class ParkingFullError(ParkingError):
    pass


class InvalidVehicleSlotError(ParkingError):
    pass


class DuplicateVehicleError(ParkingError):
    pass


class InvalidTicketError(ParkingError):
    pass


class ParkingManagement:
    VEHICLE_TYPES = ["BIKE", "CAR", "SUV", "TRUCK", "EV"]

    # base hourly rate per vehicle type
    HOURLY_RATE = {
        "BIKE": 10,
        "CAR": 30,
        "SUV": 40,
        "TRUCK": 60,
        "EV": 35,
    }

    # slot type compatible with each vehicle type
    VEHICLE_SLOT_MAP = {
        "BIKE": "BIKE_SLOT",
        "CAR": "CAR_SLOT",
        "SUV": "CAR_SLOT",
        "TRUCK": "TRUCK_SLOT",
        "EV": "EV_SLOT",
    }

    EV_CHARGING_RATE_PER_HOUR = 20
    LOST_TICKET_PENALTY = 500
    PEAK_HOUR_SURCHARGE_PERCENT = 25
    PEAK_HOURS = range(8, 11)  # 8 AM - 11 AM
    VIP_DISCOUNT_PERCENT = 30

    def __init__(self, slot_capacity):
        """slot_capacity: dict like {'BIKE_SLOT': 10, 'CAR_SLOT': 20, 'TRUCK_SLOT': 5, 'EV_SLOT': 5}"""
        self.slot_capacity = dict(slot_capacity)
        self.occupied_slots = {slot_type: 0 for slot_type in slot_capacity}
        self.active_tickets = {}  # ticket_id -> record
        self.vehicles_inside = {}  # vehicle_number -> ticket_id

    def _slot_type_for(self, vehicle_type):
        if vehicle_type not in self.VEHICLE_SLOT_MAP:
            raise InvalidVehicleSlotError(f"Unknown vehicle type: {vehicle_type}")
        return self.VEHICLE_SLOT_MAP[vehicle_type]

    def vehicle_entry(self, vehicle_number, vehicle_type, entry_time, is_vip=False):
        if vehicle_number in self.vehicles_inside:
            raise DuplicateVehicleError(f"Vehicle {vehicle_number} is already parked")

        slot_type = self._slot_type_for(vehicle_type)
        if slot_type not in self.slot_capacity:
            raise InvalidVehicleSlotError(f"No slots configured for {slot_type}")

        if self.occupied_slots[slot_type] >= self.slot_capacity[slot_type]:
            raise ParkingFullError(f"No available slots for vehicle type {vehicle_type}")

        self.occupied_slots[slot_type] += 1
        ticket_id = str(uuid.uuid4())
        record = {
            "ticket_id": ticket_id,
            "vehicle_number": vehicle_number,
            "vehicle_type": vehicle_type,
            "slot_type": slot_type,
            "entry_time": entry_time,
            "is_vip": is_vip,
            "exit_time": None,
            "fee": None,
            "lost_ticket": False,
        }
        self.active_tickets[ticket_id] = record
        self.vehicles_inside[vehicle_number] = ticket_id
        return record

    def _is_peak_hour(self, dt):
        return dt.hour in self.PEAK_HOURS

    def calculate_fee(self, record, exit_time):
        entry_time = record["entry_time"]
        duration = exit_time - entry_time
        hours = duration.total_seconds() / 3600
        billable_hours = max(1, int(hours) + (1 if hours % 1 > 0 else 0))  # round up, min 1 hour

        rate = self.HOURLY_RATE[record["vehicle_type"]]
        fee = billable_hours * rate

        if self._is_peak_hour(entry_time):
            fee *= (1 + self.PEAK_HOUR_SURCHARGE_PERCENT / 100)

        if record["vehicle_type"] == "EV":
            fee += billable_hours * self.EV_CHARGING_RATE_PER_HOUR

        if record["is_vip"]:
            fee *= (1 - self.VIP_DISCOUNT_PERCENT / 100)

        if record.get("lost_ticket"):
            fee += self.LOST_TICKET_PENALTY

        return round(fee, 2)

    def vehicle_exit(self, ticket_id, exit_time, lost_ticket=False):
        if ticket_id not in self.active_tickets:
            raise InvalidTicketError(f"Invalid or already closed ticket: {ticket_id}")

        record = self.active_tickets[ticket_id]

        if exit_time < record["entry_time"]:
            raise ParkingError("Exit time cannot be before entry time")

        record["lost_ticket"] = lost_ticket
        fee = self.calculate_fee(record, exit_time)
        record["exit_time"] = exit_time
        record["fee"] = fee

        self.occupied_slots[record["slot_type"]] -= 1
        del self.active_tickets[ticket_id]
        del self.vehicles_inside[record["vehicle_number"]]

        return record


if __name__ == "__main__":
    parking = ParkingManagement(slot_capacity={"BIKE_SLOT": 5, "CAR_SLOT": 5, "TRUCK_SLOT": 2, "EV_SLOT": 2})
    entry_time = datetime.datetime(2026, 8, 20, 9, 0)
    ticket = parking.vehicle_entry("TN01AB1234", "CAR", entry_time)
    print(ticket)
    exit_time = datetime.datetime(2026, 8, 20, 12, 30)
    result = parking.vehicle_exit(ticket["ticket_id"], exit_time)
    print(result)
