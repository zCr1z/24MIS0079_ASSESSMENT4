class HospitalManagement:
    CONSULTATION_FEES = {
        "general": 500,
        "specialist": 1000,
        "emergency": 2000
    }

    def __init__(self, patient_name, age, doctor, department,
                 appointment_type, duration, lab_tests=None,
                 medicines=None, insurance=False, follow_up=False):
        self.patient_name = patient_name
        self.age = age
        self.doctor = doctor
        self.department = department
        self.appointment_type = appointment_type.lower()
        self.duration = duration
        self.lab_tests = lab_tests or []
        self.medicines = medicines or []
        self.insurance = insurance
        self.follow_up = follow_up

    def consultation_fee(self):
        if self.appointment_type not in self.CONSULTATION_FEES:
            raise ValueError("Invalid appointment type")

        fee = self.CONSULTATION_FEES[self.appointment_type]

        if self.duration > 30:
            fee += (self.duration - 30) * 20

        if self.follow_up:
            fee *= 0.50

        if self.age >= 60:
            fee *= 0.80

        return round(fee, 2)

    def lab_charges(self):
        return round(sum(self.lab_tests), 2)

    def medicine_charges(self):
        return round(sum(self.medicines), 2)

    def insurance_coverage(self, total):
        if not self.insurance:
            return 0
        return round(total * 0.70, 2)

    def calculate_bill(self):
        if self.age < 0:
            raise ValueError("Invalid age")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")

        consultation = self.consultation_fee()
        lab = self.lab_charges()
        medicine = self.medicine_charges()

        total = consultation + lab + medicine
        coverage = self.insurance_coverage(total)
        payable = total - coverage

        return {
            "patient": self.patient_name,
            "consultation_fee": consultation,
            "lab_charges": lab,
            "medicine_charges": medicine,
            "insurance_coverage": coverage,
            "patient_payable": round(payable, 2)
        }


if __name__ == "__main__":
    hospital = HospitalManagement(
        "John", 45, "Dr. Smith", "Cardiology",
        "specialist", 45,
        lab_tests=[500, 800],
        medicines=[300, 250],
        insurance=True
    )
    print(hospital.calculate_bill())
