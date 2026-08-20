from datetime import datetime


class ParkingManagement:
    SLOT_TYPES = {
        "bike": ["B1", "B2", "B3"],
        "car": ["C1", "C2", "C3"],
        "suv": ["S1", "S2"],
        "truck": ["T1"],
        "electric": ["E1", "E2"]
    }

    HOURLY_RATES = {
        "bike": 20,
        "car": 50,
        "suv": 70,
        "truck": 100,
        "electric": 40
    }

    def __init__(self):
        self.occupied = {}
        self.tickets = {}

    def enter_vehicle(self, vehicle_no, vehicle_type,
                       entry_time, vip=False):
        vehicle_type = vehicle_type.lower()

        if vehicle_type not in self.SLOT_TYPES:
            raise ValueError("Invalid vehicle type")

        if vehicle_no in self.occupied:
            raise ValueError("Duplicate vehicle")

        slot = next(
            (s for s in self.SLOT_TYPES[vehicle_type]
             if s not in self.occupied.values()),
            None
        )

        if slot is None:
            raise ValueError("No suitable parking slot")

        ticket = f"T{len(self.tickets) + 1}"

        self.occupied[vehicle_no] = slot
        self.tickets[ticket] = {
            "vehicle_no": vehicle_no,
            "vehicle_type": vehicle_type,
            "entry_time": entry_time,
            "vip": vip,
            "slot": slot
        }

        return ticket

    def exit_vehicle(self, ticket, exit_time, lost_ticket=False,
                      ev_charging=False):
        if ticket not in self.tickets:
            raise ValueError("Invalid ticket")

        data = self.tickets.pop(ticket)
        self.occupied.pop(data["vehicle_no"])

        if lost_ticket:
            return 500

        duration = (exit_time - data["entry_time"]).total_seconds() / 3600
        hours = max(1, int(duration + 0.9999))

        rate = self.HOURLY_RATES[data["vehicle_type"]]

        if data["vip"]:
            rate *= 0.50

        # Peak hours: 8-10 AM and 5-8 PM
        peak = exit_time.hour in {8, 9, 17, 18, 19}
        if peak:
            rate *= 1.50

        fee = rate * hours

        if ev_charging and data["vehicle_type"] == "electric":
            fee += 100

        return round(fee, 2)


if __name__ == "__main__":
    parking = ParkingManagement()
    ticket = parking.enter_vehicle(
        "KL01AB1234",
        "car",
        datetime(2026, 8, 20, 10, 0)
    )
    fee = parking.exit_vehicle(
        ticket,
        datetime(2026, 8, 20, 12, 0)
    )
    print("Ticket:", ticket)
    print("Parking Fee:", fee)
