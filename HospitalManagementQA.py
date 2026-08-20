import unittest
from HospitalManagement import HospitalManagement


class HospitalManagementQA(unittest.TestCase):

    def patient(self, **changes):
        data = {
            "patient_name": "John",
            "age": 45,
            "doctor": "Dr. Smith",
            "department": "Cardiology",
            "appointment_type": "specialist",
            "duration": 30,
            "lab_tests": [500, 800],
            "medicines": [300, 200],
            "insurance": False,
            "follow_up": False
        }
        data.update(changes)
        return HospitalManagement(**data)

    def test_general_consultation(self):
        result = self.patient(appointment_type="general").calculate_bill()
        self.assertEqual(result["consultation_fee"], 500)

    def test_specialist_consultation(self):
        result = self.patient(appointment_type="specialist").calculate_bill()
        self.assertEqual(result["consultation_fee"], 1000)

    def test_emergency_patient(self):
        result = self.patient(appointment_type="emergency").calculate_bill()
        self.assertEqual(result["consultation_fee"], 2000)

    def test_senior_citizen_discount(self):
        result = self.patient(age=60).calculate_bill()
        self.assertEqual(result["consultation_fee"], 800)

    def test_follow_up_discount(self):
        result = self.patient(follow_up=True).calculate_bill()
        self.assertEqual(result["consultation_fee"], 500)

    def test_insurance_coverage(self):
        result = self.patient(insurance=True).calculate_bill()
        total = (1000 + 500 + 800 + 300 + 200)
        self.assertEqual(result["insurance_coverage"], total * 0.70)

    def test_lab_charges(self):
        result = self.patient().calculate_bill()
        self.assertEqual(result["lab_charges"], 1300)

    def test_medicine_charges(self):
        result = self.patient().calculate_bill()
        self.assertEqual(result["medicine_charges"], 500)

    def test_patient_payable_without_insurance(self):
        result = self.patient().calculate_bill()
        self.assertEqual(result["patient_payable"], 2800)

    def test_patient_payable_with_insurance(self):
        result = self.patient(insurance=True).calculate_bill()
        self.assertEqual(result["patient_payable"], 840)

    def test_long_consultation(self):
        result = self.patient(duration=60).calculate_bill()
        self.assertEqual(result["consultation_fee"], 1600)

    def test_invalid_age(self):
        with self.assertRaises(ValueError):
            self.patient(age=-1).calculate_bill()

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            self.patient(duration=0).calculate_bill()

    def test_invalid_appointment_type(self):
        with self.assertRaises(ValueError):
            self.patient(appointment_type="unknown").calculate_bill()

    def test_emergency_with_insurance(self):
        result = self.patient(
            appointment_type="emergency",
            insurance=True
        ).calculate_bill()
        self.assertGreater(result["insurance_coverage"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
