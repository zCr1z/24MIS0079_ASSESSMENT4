"""
Hospital Appointment and Billing System - QA Program
HospitalManagementQA.py

Run: python3 -m unittest HospitalManagementQA -v
"""
import unittest
from HospitalManagement import HospitalManagement, Patient, HospitalValidationError


class TestHospitalManagement(unittest.TestCase):

    def setUp(self):
        self.hms = HospitalManagement()

    # Regular general patient
    def test_general_patient_consultation_fee(self):
        patient = Patient("P1", "Anita", 30)
        fee = self.hms.calculate_consultation_fee(patient, "GENERAL")
        self.assertEqual(fee, 500)

    # Specialist consultation
    def test_specialist_consultation_fee(self):
        patient = Patient("P2", "Ramesh", 40)
        fee = self.hms.calculate_consultation_fee(patient, "SPECIALIST")
        self.assertEqual(fee, 1000)

    # Emergency patient always billed as emergency, no discounts
    def test_emergency_patient_fee_overrides_type(self):
        patient = Patient("P3", "Suresh", 70, is_emergency=True)
        fee = self.hms.calculate_consultation_fee(patient, "GENERAL")
        self.assertEqual(fee, 2000)  # no senior discount applied during emergency

    # Senior citizen discount
    def test_senior_citizen_discount(self):
        patient = Patient("P4", "Lakshmi", 65)
        fee = self.hms.calculate_consultation_fee(patient, "GENERAL")
        self.assertEqual(fee, 400)  # 20% off 500

    # Senior by explicit flag under 60
    def test_senior_flag_explicit(self):
        patient = Patient("P5", "Kumar", 55, is_senior=True)
        fee = self.hms.calculate_consultation_fee(patient, "GENERAL")
        self.assertEqual(fee, 400)

    # Follow-up consultation discount
    def test_followup_consultation_discount(self):
        patient = Patient("P6", "Devi", 35, is_followup=True)
        fee = self.hms.calculate_consultation_fee(patient, "SPECIALIST")
        self.assertEqual(fee, 500)  # 50% off 1000

    # Senior + follow-up compounding discount
    def test_senior_and_followup_compounding_discount(self):
        patient = Patient("P7", "Ganesh", 65, is_followup=True)
        fee = self.hms.calculate_consultation_fee(patient, "GENERAL")
        # 500 -> followup 50% -> 250 -> senior 20% -> 200
        self.assertEqual(fee, 200.0)

    # Insurance patient coverage applied
    def test_insurance_patient_coverage(self):
        patient = Patient("P8", "Meena", 40, has_insurance=True, insurance_coverage_percent=50)
        bill = self.hms.generate_bill(patient, "GENERAL", lab_tests=["BLOOD_TEST"], raw_medicine_cost=100)
        self.assertEqual(bill["insurance_coverage"], round(bill["gross_total"] * 0.5, 2))

    # Patient without insurance has zero coverage
    def test_no_insurance_zero_coverage(self):
        patient = Patient("P9", "Arjun", 40)
        bill = self.hms.generate_bill(patient, "GENERAL")
        self.assertEqual(bill["insurance_coverage"], 0.0)

    # Lab charges - multiple tests
    def test_lab_charges_multiple_tests(self):
        charges = self.hms.calculate_lab_charges(["BLOOD_TEST", "MRI"])
        self.assertEqual(charges, 5300)

    # Lab charges - no tests
    def test_lab_charges_empty_list(self):
        charges = self.hms.calculate_lab_charges([])
        self.assertEqual(charges, 0)

    # Invalid lab test raises
    def test_invalid_lab_test_raises(self):
        with self.assertRaises(HospitalValidationError):
            self.hms.calculate_lab_charges(["DNA_TEST"])

    # Medicine markup calculation
    def test_medicine_markup_calculation(self):
        charges = self.hms.calculate_medicine_charges(1000)
        self.assertEqual(charges, 1100.0)

    # Negative medicine cost raises
    def test_negative_medicine_cost_raises(self):
        with self.assertRaises(HospitalValidationError):
            self.hms.calculate_medicine_charges(-50)

    # Invalid doctor/appointment type raises
    def test_invalid_appointment_type_raises(self):
        patient = Patient("P10", "Vijay", 30)
        with self.assertRaises(HospitalValidationError):
            self.hms.calculate_consultation_fee(patient, "DENTIST")

    # Invalid patient age raises
    def test_invalid_patient_age_raises(self):
        with self.assertRaises(HospitalValidationError):
            Patient("P11", "Test", -5)

    # Invalid insurance coverage percent raises
    def test_invalid_insurance_percent_raises(self):
        with self.assertRaises(HospitalValidationError):
            Patient("P12", "Test", 40, has_insurance=True, insurance_coverage_percent=150)

    # End-to-end bill totals reconcile
    def test_bill_totals_reconcile(self):
        patient = Patient("P13", "Priya", 45, has_insurance=True, insurance_coverage_percent=20)
        bill = self.hms.generate_bill(patient, "SPECIALIST", lab_tests=["XRAY"], raw_medicine_cost=200)
        expected_gross = bill["consultation_fee"] + bill["lab_charges"] + bill["medicine_charges"]
        self.assertEqual(bill["gross_total"], round(expected_gross, 2))
        self.assertEqual(bill["payable_amount"], round(bill["gross_total"] - bill["insurance_coverage"], 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
