"""
Hospital Appointment and Billing System
Development Program: HospitalManagement.java equivalent in Python
"""


class HospitalValidationError(Exception):
    pass


class Patient:
    def __init__(self, patient_id, name, age, is_senior=False, is_emergency=False,
                 is_followup=False, has_insurance=False, insurance_coverage_percent=0):
        if age < 0 or age > 130:
            raise HospitalValidationError("Invalid patient age")
        if has_insurance and not (0 <= insurance_coverage_percent <= 100):
            raise HospitalValidationError("Insurance coverage percent must be between 0 and 100")

        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.is_senior = is_senior or age >= 60
        self.is_emergency = is_emergency
        self.is_followup = is_followup
        self.has_insurance = has_insurance
        self.insurance_coverage_percent = insurance_coverage_percent if has_insurance else 0


class HospitalManagement:
    CONSULTATION_FEE = {
        "GENERAL": 500,
        "SPECIALIST": 1000,
        "EMERGENCY": 2000,
    }
    LAB_TEST_PRICES = {
        "BLOOD_TEST": 300,
        "XRAY": 800,
        "MRI": 5000,
        "CT_SCAN": 4000,
    }
    SENIOR_DISCOUNT_PERCENT = 20
    FOLLOWUP_DISCOUNT_PERCENT = 50
    MEDICINE_MARKUP = 1.10  # 10% pharmacy markup applied to raw medicine cost

    def calculate_consultation_fee(self, patient: Patient, doctor_type):
        if doctor_type not in self.CONSULTATION_FEE:
            raise HospitalValidationError(f"Invalid doctor/appointment type: {doctor_type}")

        if patient.is_emergency:
            fee = self.CONSULTATION_FEE["EMERGENCY"]
        else:
            fee = self.CONSULTATION_FEE[doctor_type]

        if patient.is_followup and not patient.is_emergency:
            fee = fee * (1 - self.FOLLOWUP_DISCOUNT_PERCENT / 100)

        if patient.is_senior and not patient.is_emergency:
            fee = fee * (1 - self.SENIOR_DISCOUNT_PERCENT / 100)

        return round(fee, 2)

    def calculate_lab_charges(self, lab_tests):
        total = 0
        for test in lab_tests:
            if test not in self.LAB_TEST_PRICES:
                raise HospitalValidationError(f"Unknown lab test: {test}")
            total += self.LAB_TEST_PRICES[test]
        return round(total, 2)

    def calculate_medicine_charges(self, raw_medicine_cost):
        if raw_medicine_cost < 0:
            raise HospitalValidationError("Medicine cost cannot be negative")
        return round(raw_medicine_cost * self.MEDICINE_MARKUP, 2)

    def calculate_insurance_coverage(self, patient: Patient, total_amount):
        if not patient.has_insurance:
            return 0.0
        return round(total_amount * (patient.insurance_coverage_percent / 100), 2)

    def generate_bill(self, patient: Patient, doctor_type, lab_tests=None, raw_medicine_cost=0):
        lab_tests = lab_tests or []

        consultation_fee = self.calculate_consultation_fee(patient, doctor_type)
        lab_charges = self.calculate_lab_charges(lab_tests)
        medicine_charges = self.calculate_medicine_charges(raw_medicine_cost)

        gross_total = round(consultation_fee + lab_charges + medicine_charges, 2)
        insurance_coverage = self.calculate_insurance_coverage(patient, gross_total)
        payable = round(gross_total - insurance_coverage, 2)

        return {
            "patient_id": patient.patient_id,
            "consultation_fee": consultation_fee,
            "lab_charges": lab_charges,
            "medicine_charges": medicine_charges,
            "gross_total": gross_total,
            "insurance_coverage": insurance_coverage,
            "payable_amount": payable,
        }


if __name__ == "__main__":
    hms = HospitalManagement()
    patient = Patient("PT001", "Ravi Kumar", 65, has_insurance=True, insurance_coverage_percent=30)
    bill = hms.generate_bill(patient, "SPECIALIST", lab_tests=["BLOOD_TEST", "XRAY"], raw_medicine_cost=400)
    print(bill)
